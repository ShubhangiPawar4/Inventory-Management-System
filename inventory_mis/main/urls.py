# main/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Welcome and Dashboard
    path('', views.welcome, name='welcome'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # CRUD Operations
    path('products/', views.products, name='products'),
    path('products/edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('products/delete/<int:product_id>/', views.delete_product, name='delete_product'),
    
    path('vendors/', views.vendors, name='vendors'),
    path('customers/', views.customers, name='customers'),
    path('units/', views.units, name='units'),
    path('purchases/', views.purchases, name='purchases'),
    path('sales/', views.sales, name='sales'),
    path('inventory/', views.inventory, name='inventory'),
]