from django.db import models

NULLABLE = {'blank': True, 'null': True}


class Recipient(models.Model):
    first_name = models.CharField(max_length=100, verbose_name='имя')
    last_name = models.CharField(max_length=100, verbose_name='фамилия', **NULLABLE)
    middle_name = models.CharField(max_length=100, verbose_name='отчество', **NULLABLE)
    email = models.EmailField(verbose_name='почта')
    notes = models.TextField(verbose_name='комментарий', **NULLABLE)
    category = models.ManyToManyField('Category', verbose_name='категория получателя')
    owner = models.ForeignKey('users.User', on_delete=models.CASCADE, **NULLABLE, verbose_name='владелец')

    def __str__(self):
        return f'{self.first_name} {self.last_name} ({self.email})'

    class Meta:
        verbose_name = 'получатель'
        verbose_name_plural = 'получатели'


class Category(models.Model):
    title = models.CharField(max_length=150, verbose_name='наименование')
    description = models.TextField(verbose_name='описание', **NULLABLE)
    owner = models.ForeignKey('users.User', on_delete=models.CASCADE, **NULLABLE, verbose_name='владелец')

    def __str__(self):
        return f'{self.title}'

    class Meta:
        verbose_name = 'категория получателей'
        verbose_name_plural = 'категории получателей'