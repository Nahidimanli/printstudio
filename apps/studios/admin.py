from django.contrib import admin
from .models import StudioProfile, Service

class ServiceInline(admin.TabularInline):
    model = Service
    extra = 1

@admin.register(StudioProfile)
class StudioProfileAdmin(admin.ModelAdmin):
    list_display = ("business_name", "user", "latitude", "longitude", "created_at")
    search_fields = ("business_name", "user__username", "user__email")
    inlines = [ServiceInline]

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "studio", "price", "discount_price", "is_active")
    list_filter = ("is_active", "studio")
    search_fields = ("name", "studio__business_name")
