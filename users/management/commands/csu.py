from django.core.management import BaseCommand

from users.models import User


class Command(BaseCommand):
    def handle(self, *args, **options):
        user = User.objects.create(
            email='djkeysi88@yandex.ru',
            first_name='e',
            last_name='s',
            is_staff=True,
            is_superuser=True,
        )
        user.set_password('128943')
        user.save()