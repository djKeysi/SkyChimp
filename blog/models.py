from django.db import models

from mailsender.models import NULLABLE


class Article(models.Model):
    title = models.CharField(max_length=250, verbose_name='заголовок')
    content = models.TextField(verbose_name='содержимое')
    preview = models.ImageField(upload_to='blog/', verbose_name='превью', **NULLABLE)
    created_at = models.DateField(auto_now_add=True, verbose_name='дата_создания')
    slug = models.CharField(max_length=250, verbose_name='slug')
    owner = models.ForeignKey('users.User', on_delete=models.CASCADE, **NULLABLE, verbose_name='владелец')
    is_published = models.BooleanField(default=False)
    published_at = models.DateField(verbose_name='дата_публикации', **NULLABLE)
    views_count = models.IntegerField(default=0, verbose_name='просмотры')

    def __str__(self):
        return f'{self.title} ' \
               f'({"опубликовано" if self.is_published else "не опубликовано"})'

    class Meta:
        verbose_name = 'статья'
        verbose_name_plural = 'статьи'
        ordering = ('views_count', 'title', 'published_at',)