from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse


def send_verification_code(verification_code, email):
    """Отправляет письмо на почту для верификации почты пользователя"""
    url = reverse('users:verification', args=[verification_code])
    send_mail(
        subject='Регистрация на Mailing',
        message=f'Для регистрации на платформе Mailing пройдите по ссылке {"http://127.0.0.1:8000" + url}',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[email]
    )


def send_new_password(new_password, email):
    """Отправляет письмо на почту с новым паролем"""
    send_mail(
        subject='Смена пароля на платформе Mailsender',
        message=f'Ваш новый пароль {new_password}',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[email]
    )