from django import forms

from recipients.models import Recipient, Category


class RecipientForm(forms.ModelForm):
    class Meta:
        model = Recipient
        exclude = ('owner',)


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        exclude = ('owner',)