from django.contrib import admin

from users.models import User


class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_staff', 'date_joined', 'first_name', 'last_name', 'phone', 'avatar')
    list_filter = ('is_staff', 'date_joined')


admin.site.register(User, UserAdmin)