from datetime import datetime

from django import forms

from mailsender.models import Mail, Message
from recipients.models import Category


class MailForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        uid = kwargs.pop('uid')
        super().__init__(*args, **kwargs)
        self.fields['message'].queryset = Message.objects.all().filter(owner=uid)
        self.fields['category'].queryset = Category.objects.all().filter(owner=uid)

    class Meta:
        model = Mail
        exclude = ('activity', 'owner')

    def clean(self):
        cleaned_data = self.cleaned_data
        start_date = cleaned_data.get('start_date')
        stop_date = cleaned_data.get('stop_date')
        start_time = cleaned_data.get('time')

        start_datetime = datetime.combine(start_date, start_time)
        if datetime.now() >= start_datetime:
            raise forms.ValidationError('Вы указали прошедшую дату')
        if stop_date < start_date:
            raise forms.ValidationError('Дата окончания не может быть раньше даты запуска рассылки')
        return cleaned_data

    # new_message_title = forms.CharField(max_length=100, required=False, label="или СОЗДАТЬ новое сообщение:")
    # new_message_content = forms.CharField(max_length=3000, required=False, label="c содержанием:")


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        exclude = ('owner',)