from datetime import datetime, timedelta

from django.core.management import BaseCommand

from mailsender.models import Mail
from mailsender.services import run_APScheduler


class Command(BaseCommand):

    def handle(self, *args, **options):
        all_mails = Mail.objects.filter(activity='draft') | Mail.objects.filter(activity='paused')
        all_mails = all_mails.filter(stop_date__gte=datetime.now())
        for mail_item in all_mails:
            send_datetime = datetime.combine(mail_item.start_date, mail_item.time)
            if send_datetime <= datetime.now():
                send_datetime = datetime.now() + timedelta(minutes=1)
            run_APScheduler(mail_item, send_datetime)
            mail_item.activity = 'active'
            mail_item.save()