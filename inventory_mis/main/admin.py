
# Register your models here.
# main/admin.py
from django.contrib import admin
from .models import Vendor, Unit, Product, Customer, Purchase, Sale, Inventory

# Register your models here. This makes them visible and editable in the admin panel.

class VendorAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'mobile', 'status')
    list_filter = ('status',)
    search_fields = ('full_name', 'mobile')

class UnitAdmin(admin.ModelAdmin):
    list_display = ('title', 'short_name')

class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'unit')
    list_filter = ('unit',)
    search_fields = ('title',)

class CustomerAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'customer_mobile')
    search_fields = ('customer_name', 'customer_mobile')

class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('product', 'vendor', 'quantity', 'price', 'total_amount', 'purchase_date')
    list_filter = ('purchase_date', 'vendor')
    search_fields = ('product__title', 'vendor__full_name')

class SaleAdmin(admin.ModelAdmin):
    list_display = ('product', 'customer', 'quantity', 'price', 'total_amount', 'sale_date')
    list_filter = ('sale_date', 'customer')
    search_fields = ('product__title', 'customer__customer_name')

class InventoryAdmin(admin.ModelAdmin):
    list_display = ('product', 'total_balance_quantity')
    search_fields = ('product__title',)

admin.site.register(Vendor, VendorAdmin)
admin.site.register(Unit, UnitAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Purchase, PurchaseAdmin)
admin.site.register(Sale, SaleAdmin)
admin.site.register(Inventory, InventoryAdmin)
