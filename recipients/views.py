from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from mailsender.views import OwnerRequiredMixin
from recipients.forms import RecipientForm, CategoryForm
from recipients.models import Recipient, Category


class RecipientListView(LoginRequiredMixin, ListView):
    model = Recipient

    def get_queryset(self, *args, **kwargs):
        """Если не персонал, то выводим только принадлежащие автору объекты"""
        queryset = super().get_queryset(*args, **kwargs)
        if not self.request.user.is_staff:
            queryset = queryset.filter(owner=self.request.user)
        return queryset


class RecipientCreateView(LoginRequiredMixin, CreateView):
    model = Recipient
    form_class = RecipientForm
    success_url = reverse_lazy('recipients:list')

    def form_valid(self, form):
        """При создании получателя, записываем автора-пользователя в атрибуты объекта"""
        if form.is_valid():
            form.instance.owner = self.request.user
            form.save()
        return super().form_valid(form)


# рассмотреть на будущее: при редактировании адреса почты - модифицировать джобу
class RecipientUpdateView(OwnerRequiredMixin, UpdateView):
    model = Recipient
    form_class = RecipientForm
    success_url = reverse_lazy('recipients:list')


# рассмотреть на будущее: при удалении нужно модифицировать джобу
class RecipientDeleteView(OwnerRequiredMixin, DeleteView):
    model = Recipient
    success_url = reverse_lazy('recipients:list')


class CategoryListView(LoginRequiredMixin, ListView):
    paginate_by = 5
    model = Category

    def get_queryset(self, *args, **kwargs):
        """Если не персонал, то выводим только принадлежащие автору объекты"""
        queryset = super().get_queryset(*args, **kwargs)
        if not self.request.user.is_staff:
            queryset = queryset.filter(owner=self.request.user)
        return queryset


class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    success_url = reverse_lazy('recipients:category_list')

    def form_valid(self, form):
        """При создании получателя, записываем автора-пользователя в атрибуты объекта"""
        if form.is_valid():
            form.instance.owner = self.request.user
            form.save()
        return super().form_valid(form)


class CategoryUpdateView(OwnerRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    success_url = reverse_lazy('recipients:category_list')


class CategoryDeleteView(OwnerRequiredMixin, DeleteView):
    model = Category
    success_url = reverse_lazy('recipients:category_list')