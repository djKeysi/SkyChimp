import smtplib
from datetime import timedelta, datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from django.conf import settings
from django.core.mail import send_mail
from django_apscheduler import util
from django_apscheduler.jobstores import DjangoJobStore

from mailsender.models import Try
import logging

logger = logging.getLogger(__name__)
scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
scheduler.add_jobstore(DjangoJobStore(), "default")


def send_message(email, title, message):
    """Отправляет сообщение email"""
    send_mail(
        subject=title,
        message=message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=email)


@util.close_old_connections
def create_try(mail_item):
    """APScheduler job: Вытаскивает весь список почт получателей у категорий, которые связаны с рассылкой +
    при отправке email через функцию send_message создает экземпляр Попытки с указанием статуса"""
    emails_list = []
    for cat in mail_item.category.all():
        emails_list.extend([person.email for person in cat.recipient_set.all()])
    emails_list = list(set(emails_list))

    try:
        # print(f"recipients:{emails_list}\ntitle:{mail_item.message.title}\nmessage:{mail_item.message.content}")
        send_message(emails_list, mail_item.message.title, mail_item.message.content)
        Try.objects.create(mail=mail_item, status=True, owner=mail_item.owner)
    # except OSError as error:
    except smtplib.SMTPException as error:
        Try.objects.create(mail=mail_item, status=False, error_message=error, owner=mail_item.owner)


# The `close_old_connections` decorator ensures that database connections, that have become
# unusable or are obsolete, are closed before and after your job has run. You should use it
# to wrap any jobs that you schedule that access the Django database in any way.


@util.close_old_connections
def delete_old_job_executions(mail_item):
    """APScheduler job: Удаляет выполненные jobs и возвращает статус черновика рассылке"""
    scheduler.remove_job(str(mail_item.job_id))
    print('deleted')
    mail_item.activity = 'draft'
    mail_item.save()



def get_job_params(mail_item, *new_start_datetime):
    """Формирует атрибуты рассылки в формат триггера для последующего формирования job:
    Опциональный аргумент new_start_datetime используется при насильном запуске отправки рассылок через
    кастомную команду run_scheduler (на случай, если время старта рассылки прошло)"""
    start_datetime = datetime.combine(mail_item.start_date, mail_item.time)

    if new_start_datetime:
        start_datetime = new_start_datetime[0]

    day = weekday = month = '*'

    if mail_item.frequency == 'ONCE':
        month = start_datetime.month
        day = start_datetime.day
        weekday = start_datetime.weekday()

    elif mail_item.frequency == 'WEEKLY':
        weekday = start_datetime.weekday()
    elif mail_item.frequency == 'MONTHLY':
        day = start_datetime.day
    trigger = CronTrigger.from_crontab(f'{start_datetime.minute} {start_datetime.hour} {day} {month} {weekday}')
    return trigger


def run_APScheduler(mail_item, *new_start_datetime):
    """Планирует job исходя из триггера полученного фугкцией get_job_params()
    Вместе с основной задачей на отправку письма создается задача по удалению job после ее выполнения"""
    upd_trigger = get_job_params(mail_item, *new_start_datetime)

    scheduler.add_job(
        create_try,
        trigger=upd_trigger,
        args=[mail_item],
        id=str(mail_item.job_id),
        max_instances=1,
        replace_existing=True,
        end_date=mail_item.stop_date
    )
    logger.info("Added job 'create_log'.")

    scheduler.add_job(
        delete_old_job_executions,
        trigger=DateTrigger(run_date=datetime.combine(mail_item.stop_date, mail_item.time) + timedelta(minutes=5)),
        args=[mail_item],
        id=f"delete_{mail_item.job_id}",
        max_instances=1,
        replace_existing=True,
    )
    logger.info(
        "Added weekly job: 'delete_old_job_executions'."
    )


def run_job_update(mail_item):
    """Производит обновление задачи при изменении рассылки"""
    job_trigger = get_job_params(mail_item)

    # апдейтим аргументы самой job (т.е. все входные аргументы create_try)
    scheduler.modify_job(job_id=str(mail_item.job_id), args=[mail_item])

    # апдейтим аргументы самой scheduler (т.е. trigger)
    scheduler.reschedule_job(job_id=str(mail_item.job_id), trigger=job_trigger)

    # рескедьюлим job на удаление (т.е. delete_old_job_executions)
    scheduler.reschedule_job(job_id=f"delete_{mail_item.job_id}",
                             trigger=DateTrigger(
                                 run_date=datetime.combine(mail_item.stop_date, mail_item.time) + timedelta(minutes=5))
                             )