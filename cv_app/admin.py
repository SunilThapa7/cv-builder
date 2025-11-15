from django.contrib import admin
from .models import CVTemplate, CV


@admin.register(CVTemplate)
class CVTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'active']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(CV)
class CVAdmin(admin.ModelAdmin):
    list_display = ['title', 'owner', 'template', 'updated_at']
    list_filter = ['template', 'created_at']
    search_fields = ['title', 'owner__username']
