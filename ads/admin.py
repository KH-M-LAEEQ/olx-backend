from django.contrib import admin
from .models import Ad, AdImage, Favourite, AdReport


@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    list_display  = ('title', 'seller', 'price', 'location', 'is_active', 'expires_at', 'created_at')
    list_filter   = ('is_active', 'condition', 'category')
    search_fields = ('title', 'seller__username', 'location')


@admin.register(AdImage)
class AdImageAdmin(admin.ModelAdmin):
    list_display = ('ad', 'is_cover')


@admin.register(Favourite)
class FavouriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'ad', 'created_at')


@admin.register(AdReport)
class AdReportAdmin(admin.ModelAdmin):
    list_display    = ('ad', 'reporter', 'reason', 'created_at')
    list_filter     = ('reason',)
    readonly_fields = ('ad', 'reporter', 'reason', 'details', 'created_at')
