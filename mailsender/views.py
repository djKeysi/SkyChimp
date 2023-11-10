import random

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import AccessMixin, LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView

from blog.models import Article
from mailsender.forms import MessageForm, MailForm
from mailsender.models import Message, Mail, Try
from mailsender.services import scheduler, run_APScheduler, run_job_update
from recipients.models import Recipient

if not settings.SCHEDULER_STARTED:
    try:
        scheduler.start()
        settings.SCHEDULER_STARTED = True
    except KeyboardInterrupt:
        scheduler.shutdown()


class OwnerRequiredMixin(AccessMixin):
    """Кастомный миксин для ограничения прав доступа: при попытке изменения или удаления объекта
    авторизованным пользователем, но не являющимся Суперюзером или автором объекта:
    всплывает сообщение об ограничении доступа и происходит переадресация на страницу входа"""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if request.user.is_authenticated:
            if not request.user.is_superuser:
                if request.user.pk != self.get_object().owner.pk:
                    messages.info(request, 'Изменение и удаление доступно только автору')
                    return redirect('/users/')
        return super().dispatch(request, *args, **kwargs)


class ManagerRequiredMixin(AccessMixin):
    """Кастомный миксин для ограничения прав доступа: при попытке просмотра объекта
    авторизованным пользователем, но не являющимся Менеджером или автором объекта:
    всплывает сообщение об ограничении доступа и происходит переадресация на страницу входа"""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if request.user.is_authenticated:
            if not request.user.is_staff:
                if request.user.pk != self.get_object().owner.pk:
                    messages.info(request, 'Просмотр доступен только автору')
                    return redirect('/users/')
        return super().dispatch(request, *args, **kwargs)


class MessageListView(LoginRequiredMixin, ListView):
    paginate_by = 3
    model = Message

    def get_queryset(self, *args, **kwargs):
        """Если не персонал, то выводим только принадлежащие автору объекты"""
        queryset = super().get_queryset(*args, **kwargs)
        if not self.request.user.is_staff:
            queryset = queryset.filter(owner=self.request.user)
        return queryset


class MessageDetailView(LoginRequiredMixin, ManagerRequiredMixin, DetailView):
    model = Message


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    success_url = reverse_lazy('mailsender:message_list')

    # permission_required = 'mailsender.add_message'

    def form_valid(self, form):
        """При создании сообщения, записываем автора-пользователя в атрибуты объекта"""
        if form.is_valid():
            form.instance.owner = self.request.user
            form.save()
        return super().form_valid(form)


class MessageUpdateView(OwnerRequiredMixin, UpdateView):
    model = Message
    form_class = MessageForm

    def get_success_url(self):
        """При изменении объекта переадресовываем на просмотр измененного объекта"""
        return reverse('mailsender:message_detail', args=[self.kwargs.get('pk')])


class MessageDeleteView(OwnerRequiredMixin, DeleteView):
    model = Message
    success_url = reverse_lazy('mailsender:message_list')

    def form_valid(self, form):
        """При удалении сообщения, удаляем и соответствующую APScheduler job"""
        if form.is_valid():
            mail_items = self.object.mail_set.all()
            for mail_item in mail_items:
                scheduler.remove_job(str(mail_item.job_id))
        return super().form_valid(form)


class MailListView(LoginRequiredMixin, ListView):
    paginate_by = 5
    model = Mail

    def get_queryset(self, *args, **kwargs):
        """Если не персонал, то выводим только принадлежащие автору объекты +
        сортируем по дате обновления (новые - сверху)"""
        queryset = super().get_queryset(*args, **kwargs)
        if not self.request.user.is_staff:
            queryset = queryset.filter(owner=self.request.user)
        queryset = queryset.order_by('updated_at').reverse()
        return queryset


class MailCreateView(LoginRequiredMixin, CreateView):
    model = Mail
    form_class = MailForm
    success_url = reverse_lazy('mailsender:mail_list')

    def form_valid(self, form):
        """При создании рассылки, записываем автора-пользователя в атрибуты объекта"""
        if form.is_valid():
            form.instance.owner = self.request.user
            form.save()
        return super().form_valid(form)

    def get_form_kwargs(self):
        """записываем в kwargs self.request.user.id, чтобы потом в MailForm
        пользователь мог выбрать только те объекты, в которых он является автором"""
        kwargs = super().get_form_kwargs()
        kwargs.update({'uid': self.request.user.id})
        return kwargs


class MailUpdateView(OwnerRequiredMixin, UpdateView):
    """Функия редактирования рассылки доступна только при неактивном статусе рассылки
    (регулируется видимостью кнопки в шаблоне)"""
    model = Mail
    form_class = MailForm
    success_url = reverse_lazy('mailsender:mail_list')

    def form_valid(self, form, *args, **kwargs):
        """Если рассылка когда-то была запущена и создана job, то апдейтим саму job"""
        if form.is_valid():
            self.object = form.save()
            if scheduler.get_job(str(self.object.job_id)) is not None:
                run_job_update(mail_item=self.object)
        return super().form_valid(form)

    def get_form_kwargs(self):
        """Также как и в CreateView записываем в kwargs self.request.user.id, чтобы потом в MailForm
        пользователь мог выбрать только те объекты, в которых он является автором"""
        kwargs = super().get_form_kwargs()
        kwargs.update({'uid': self.request.user.id})
        return kwargs


class MailDeleteView(OwnerRequiredMixin, DeleteView):
    model = Mail
    success_url = reverse_lazy('mailsender:mail_list')

    def form_valid(self, form):
        """При удалении рассылки, удаляем и соответствующую APScheduler job"""
        if form.is_valid():
            scheduler.remove_job(str(self.get_object().job_id))
            scheduler.remove_job(f"delete_{self.get_object().job_id}")
        return super().form_valid(form)


@login_required()
def toggle_mail_activity(request, pk):
    """Функция для смены статуса рассылки: черновик -> активна -> приостановлена -> активна"""
    mail_item = get_object_or_404(Mail, pk=pk)

    if mail_item.activity == 'draft':
        mail_item.activity = 'active'
        run_APScheduler(mail_item=mail_item)

    elif mail_item.activity == 'active':
        mail_item.activity = 'paused'
        scheduler.pause_job(str(mail_item.job_id))

    elif mail_item.activity == 'paused':
        mail_item.activity = 'active'
        scheduler.resume_job(str(mail_item.job_id))

    mail_item.save()
    return redirect(reverse('mailsender:mail_list'))


class TryListView(LoginRequiredMixin, ListView):
    paginate_by = 5
    model = Try

    def get_queryset(self, *args, **kwargs):
        """Если не персонал, то выводим только принадлежащие автору объекты +
        сортируем по дате запуска (новые - сверху)"""
        queryset = super().get_queryset(*args, **kwargs)
        if not self.request.user.is_staff:
            queryset = queryset.filter(owner=self.request.user)
        queryset = queryset.order_by('launched_at').reverse()
        return queryset


class IndexView(TemplateView):
    """Контроллер главной страницы"""
    template_name = 'mailsender/index.html'

    def get_context_data(self, **kwargs):
        """В шаблон подаем 2 статьи (или сколько есть меньше 2),
         количество всего рассылок в БД,
         количество активных рассылок в БД,
         количество уникальных пользователей в БД"""
        context_data = super().get_context_data(**kwargs)

        article_list = list(Article.objects.filter(is_published=True))
        qty = 2 if len(article_list) > 2 else len(article_list)
        context_data['object_list'] = random.sample(article_list, qty)

        context_data['mail_qty'] = Mail.objects.all().count()
        context_data['active_mail_qty'] = Mail.objects.filter(activity='active').count()
        context_data['unique_recipients'] = Recipient.objects.all().values('email').distinct().count()
        return context_data