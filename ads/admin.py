from django.contrib import admin
from .models import Ad, AdImage


class AdImageInline(admin.TabularInline):
    model = AdImage
    extra = 1


@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    list_display  = ('title', 'seller', 'category', 'price', 'location', 'is_active', 'created_at')
    list_filter   = ('category', 'is_active', 'condition')
    search_fields = ('title', 'description', 'location')
    inlines       = [AdImageInline]
