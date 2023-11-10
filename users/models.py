from django.contrib.auth.models import AbstractUser
from django.db import models

from mailsender.models import NULLABLE


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True, verbose_name='email')

    phone = models.CharField(max_length=35, verbose_name='телефон', **NULLABLE)
    avatar = models.ImageField(upload_to='users/', verbose_name='аватар', **NULLABLE)
    verification_code = models.CharField(max_length=50, verbose_name='верификационный код', **NULLABLE)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []