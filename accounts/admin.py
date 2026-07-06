from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, ContactMessage, PasswordResetToken


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display  = ('username', 'email', 'phone', 'city', 'is_staff')
    fieldsets     = BaseUserAdmin.fieldsets + (
        ('Extra Info', {'fields': ('phone', 'city', 'address', 'avatar')}),
    )


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display  = ('name', 'email', 'subject', 'created_at')
    readonly_fields = ('name', 'email', 'subject', 'message', 'created_at')
    ordering      = ('-created_at',)


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display  = ('user', 'otp', 'created_at', 'used')
    readonly_fields = ('user', 'otp', 'created_at')
