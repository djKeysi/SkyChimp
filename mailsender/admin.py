from django.contrib import admin
from django.utils.datetime_safe import datetime
from pytils.translit import slugify

from blog.models import Article
from mailsender.models import Message, Mail, Try
from recipients.models import Recipient, Category


@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'middle_name', 'last_name', 'email', 'notes', 'owner')
    list_filter = ('owner', 'category',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'owner')
    list_filter = ('owner', 'mail',)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('title', 'content', 'owner',)
    list_filter = ('mail', 'owner')
    search_fields = ('title', 'content',)


@admin.register(Mail)
class MailAdmin(admin.ModelAdmin):
    list_display = ('title', 'message', 'start_date', 'time', 'stop_date', 'frequency', 'activity', 'job_id',
                    'created_at', 'updated_at', 'owner',)
    list_filter = ('owner', 'activity', 'category', 'message',)


@admin.register(Try)
class TryAdmin(admin.ModelAdmin):
    list_display = ('mail', 'launched_at', 'status', 'error_message', 'pk', 'owner',)
    list_filter = ('status', 'mail',)


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    fields = ['title', 'is_published', 'published_at', 'views_count', 'content', 'owner', 'slug', 'preview']
    list_display = ('title', 'created_at', 'is_published', 'published_at', 'views_count', 'owner', 'preview', 'slug')
    list_filter = ('owner', 'is_published',)
    search_fields = ('title', 'content')
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ['published_at']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """переопределяем поле owner в форме -> устанавливаем значение по умолчанию + в режиме readonly"""
        if db_field.name == "owner":
            # setting the user from the request object
            kwargs["initial"] = request.user
            # making the field readonly
            kwargs['disabled'] = True
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        """автоматически проставляет текущую дату, если поле is_published == True"""
        obj.slug = slugify(obj.title)
        if obj.is_published:
            obj.published_at = datetime.now()
        super().save_model(request, obj, form, change)