from django.urls import path

from recipients.apps import RecipientsConfig
from recipients.views import RecipientCreateView, RecipientListView, RecipientUpdateView, RecipientDeleteView, \
    CategoryListView, CategoryCreateView, CategoryUpdateView, CategoryDeleteView

app_name = RecipientsConfig.name
urlpatterns = [
    path('create/', RecipientCreateView.as_view(), name='create'),
    path('', RecipientListView.as_view(), name='list'),
    path('edit/<int:pk>', RecipientUpdateView.as_view(), name='edit'),
    path('delete/<int:pk>', RecipientDeleteView.as_view(), name='delete'),

    path('view_categories', CategoryListView.as_view(), name='category_list'),
    path('create_category', CategoryCreateView.as_view(), name='create_category'),
    path('edit_category/<int:pk>', CategoryUpdateView.as_view(), name='edit_category'),
    path('delete_category/<int:pk>', CategoryDeleteView.as_view(), name='delete_category'),
]