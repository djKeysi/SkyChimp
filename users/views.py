import random
import secrets

from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, UpdateView
from users.models import User
from users.forms import UserRegisterForm, UserUpdateForm
from users.services import send_verification_code, send_new_password


class RegisterView(CreateView):
    model = User
    form_class = UserRegisterForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('mailsender:mail_list')

    def form_valid(self, form):

        if form.is_valid():
            self.object = form.save(commit=False)
            verification_code = secrets.token_urlsafe(nbytes=8)
            self.object.verification_code = verification_code
            self.object.is_active = False
            self.object = form.save()
            send_verification_code(verification_code, self.object.email)
        return super().form_valid(form)


def user_verify(request, verification_code):
    user = User.objects.get(verification_code=verification_code)
    user.is_active = True
    user.save()
    return redirect(reverse('mailsender:mail_list'))


class ProfileView(UpdateView):
    model = User
    form_class = UserUpdateForm
    success_url = reverse_lazy('users:profile')

    def get_object(self, queryset=None):
        return self.request.user


def update_password(request):
    if request.method == "POST":
        email = request.POST.get('email')
        DB_user = User.objects.get(email=email)
        new_password = secrets.token_urlsafe(nbytes=8)
        DB_user.set_password(new_password)
        DB_user.save()
        send_new_password(new_password, DB_user.email)
        return redirect(reverse_lazy('users:login'))
    return render(request, 'users/update_password.html')