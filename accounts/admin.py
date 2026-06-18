from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display  = ('username', 'email', 'phone', 'city', 'is_staff')
    fieldsets     = BaseUserAdmin.fieldsets + (
        ('Extra Info', {'fields': ('phone', 'city', 'address', 'avatar')}),
    )
