from django.apps import AppConfig


class MailsenderConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mailsender'
    verbose_name = 'Сервис рассылок'