from django.contrib import admin
from .models import Conversation, Message


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'buyer', 'seller', 'ad', 'updated_at')
    readonly_fields = ('buyer', 'seller', 'ad', 'created_at', 'updated_at')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'conversation', 'body', 'is_read', 'created_at')
    readonly_fields = ('sender', 'conversation', 'body', 'created_at')
