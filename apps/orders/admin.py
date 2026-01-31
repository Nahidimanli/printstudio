from django.contrib import admin
from .models import Order, OrderItem, OrderFile

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

class OrderFileInline(admin.TabularInline):
    model = OrderFile
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "studio", "status", "total_price", "created_at")
    list_filter = ("status", "created_at", "studio")
    inlines = [OrderItemInline, OrderFileInline]
    search_fields = ("customer__username", "studio__business_name", "id")

@admin.register(OrderFile)
class OrderFileAdmin(admin.ModelAdmin):
    list_display = ("order", "file", "uploaded_at")
