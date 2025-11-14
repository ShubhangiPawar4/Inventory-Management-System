
# Create your views here.
# main/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Product, Inventory, Purchase, Sale, Vendor, Customer, Unit
import numpy as np


def login_view(request):
    """
    Handle user login
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'login.html')


@login_required
def logout_view(request):
    """
    Handle user logout
    """
    logout(request)
    return redirect('login')


@login_required
def welcome(request):
    """
    Simple welcome/hello page with quick stats and links.
    """
    inventory_items = Inventory.objects.select_related('product').all()
    recent_purchases = Purchase.objects.order_by('-purchase_date')[:5]
    recent_sales = Sale.objects.order_by('-sale_date')[:5]

    # Use numpy to calculate totals and low stock detection
    quantities = np.array([item.total_balance_quantity for item in inventory_items]) if inventory_items else np.array([])
    total_products = int(len(inventory_items))
    total_quantity = float(quantities.sum()) if quantities.size else 0.0
    low_stock_threshold = 10
    low_stock_count = int((quantities <= low_stock_threshold).sum()) if quantities.size else 0

    context = {
        'inventory_items': inventory_items,
        'recent_purchases': recent_purchases,
        'recent_sales': recent_sales,
        'total_products': total_products,
        'total_quantity': total_quantity,
        'low_stock_threshold': low_stock_threshold,
        'low_stock_count': low_stock_count,
    }
    return render(request, 'index.html', context)


@login_required
def dashboard(request):
    """
    Renders the main dashboard page with key inventory data.
    """
    # Optional search on dashboard across product titles
    q = request.GET.get('q', '').strip()

    inventory_qs = Inventory.objects.select_related('product')
    if q:
        inventory_qs = inventory_qs.filter(product__title__icontains=q)

    inventory_items = inventory_qs.all()

    # Get recent purchases and sales
    recent_purchases = Purchase.objects.order_by('-purchase_date')[:5]
    recent_sales = Sale.objects.order_by('-sale_date')[:5]

    # Numpy-based calculations
    quantities = np.array([item.total_balance_quantity for item in inventory_items]) if inventory_items else np.array([])
    total_products = int(len(inventory_items))
    total_quantity = float(quantities.sum()) if quantities.size else 0.0
    low_stock_threshold = 10
    low_stock_count = int((quantities <= low_stock_threshold).sum()) if quantities.size else 0

    context = {
        'inventory_items': inventory_items,
        'recent_purchases': recent_purchases,
        'recent_sales': recent_sales,
        'total_products': total_products,
        'total_quantity': total_quantity,
        'low_stock_threshold': low_stock_threshold,
        'low_stock_count': low_stock_count,
        'q': q,
    }
    return render(request, 'dashboard.html', context)


# Products CRUD
@login_required
def products(request):
    """
    Display all products and handle product creation
    """
    q = request.GET.get('q', '').strip()

    products_qs = Product.objects.select_related('unit')
    if q:
        products_qs = products_qs.filter(title__icontains=q)

    products_list = products_qs.all()
    units = Unit.objects.all()
    
    if request.method == 'POST':
        title = request.POST.get('title')
        detail = request.POST.get('detail')
        unit_id = request.POST.get('unit')
        photo = request.FILES.get('photo')
        
        if title and unit_id:
            unit = get_object_or_404(Unit, id=unit_id)
            Product.objects.create(
                title=title,
                detail=detail,
                unit=unit,
                photo=photo
            )
            messages.success(request, 'Product created successfully!')
            return redirect('products')
    
    context = {
        'products': products_list,
        'units': units,
        'q': q,
    }
    return render(request, 'products.html', context)


@login_required
def edit_product(request, product_id):
    """
    Edit a product
    """
    product = get_object_or_404(Product, id=product_id)
    units = Unit.objects.all()
    
    if request.method == 'POST':
        product.title = request.POST.get('title')
        product.detail = request.POST.get('detail')
        product.unit_id = request.POST.get('unit')
        if request.FILES.get('photo'):
            product.photo = request.FILES.get('photo')
        product.save()
        messages.success(request, 'Product updated successfully!')
        return redirect('products')
    
    context = {
        'product': product,
        'units': units,
    }
    return render(request, 'edit_product.html', context)


@login_required
@require_http_methods(["POST"]) 
def delete_product(request, product_id):
    """
    Delete a product
    """
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    return JsonResponse({'success': True})


# Vendors CRUD
@login_required
def vendors(request):
    """
    Display all vendors and handle vendor creation
    """
    q = request.GET.get('q', '').strip()
    vendors_qs = Vendor.objects.all()
    if q:
        vendors_qs = vendors_qs.filter(full_name__icontains=q)
    
    vendors_list = vendors_qs.all()
    
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        address = request.POST.get('address')
        mobile = request.POST.get('mobile')
        status = request.POST.get('status') == 'on'
        
        if full_name and mobile:
            Vendor.objects.create(
                full_name=full_name,
                address=address,
                mobile=mobile,
                status=status
            )
            messages.success(request, 'Vendor created successfully!')
            return redirect('vendors')
    
    context = {'vendors': vendors_list, 'q': q}
    return render(request, 'vendors.html', context)


# Customers CRUD
@login_required
def customers(request):
    """
    Display all customers and handle customer creation
    """
    q = request.GET.get('q', '').strip()
    customers_qs = Customer.objects.all()
    if q:
        customers_qs = customers_qs.filter(customer_name__icontains=q)
    
    customers_list = customers_qs.all()
    
    if request.method == 'POST':
        customer_name = request.POST.get('customer_name')
        customer_mobile = request.POST.get('customer_mobile')
        customer_address = request.POST.get('customer_address')
        
        if customer_name:
            Customer.objects.create(
                customer_name=customer_name,
                customer_mobile=customer_mobile,
                customer_address=customer_address
            )
            messages.success(request, 'Customer created successfully!')
            return redirect('customers')
    
    context = {'customers': customers_list, 'q': q}
    return render(request, 'customers.html', context)


# Units CRUD
@login_required
def units(request):
    """
    Display all units and handle unit creation
    """
    q = request.GET.get('q', '').strip()
    units_qs = Unit.objects.all()
    if q:
        units_qs = units_qs.filter(title__icontains=q)
    
    units_list = units_qs.all()
    
    if request.method == 'POST':
        title = request.POST.get('title')
        short_name = request.POST.get('short_name')
        
        if title and short_name:
            Unit.objects.create(
                title=title,
                short_name=short_name
            )
            messages.success(request, 'Unit created successfully!')
            return redirect('units')
    
    context = {'units': units_list, 'q': q}
    return render(request, 'units.html', context)


# Purchases CRUD
@login_required
def purchases(request):
    """
    Display all purchases and handle purchase creation
    """
    q = request.GET.get('q', '').strip()

    purchases_qs = Purchase.objects.select_related('product', 'vendor')
    if q:
        purchases_qs = purchases_qs.filter(product__title__icontains=q)
    
    purchases_list = purchases_qs.all()
    products = Product.objects.all()
    vendors = Vendor.objects.all()
    
    if request.method == 'POST':
        product_id = request.POST.get('product')
        vendor_id = request.POST.get('vendor')
        quantity = request.POST.get('quantity')
        price = request.POST.get('price')
        
        if product_id and vendor_id and quantity and price:
            product = get_object_or_404(Product, id=product_id)
            vendor = get_object_or_404(Vendor, id=vendor_id)
            Purchase.objects.create(
                product=product,
                vendor=vendor,
                quantity=float(quantity),
                price=float(price)
            )
            messages.success(request, 'Purchase recorded successfully!')
            return redirect('purchases')
    
    context = {
        'purchases': purchases_list,
        'products': products,
        'vendors': vendors,
        'q': q,
    }
    return render(request, 'purchases.html', context)


# Sales CRUD
@login_required
def sales(request):
    """
    Display all sales and handle sale creation
    """
    q = request.GET.get('q', '').strip()

    sales_qs = Sale.objects.select_related('product', 'customer')
    if q:
        sales_qs = sales_qs.filter(product__title__icontains=q)
    
    sales_list = sales_qs.all()
    products = Product.objects.all()
    customers = Customer.objects.all()
    
    if request.method == 'POST':
        product_id = request.POST.get('product')
        customer_id = request.POST.get('customer')
        quantity = request.POST.get('quantity')
        price = request.POST.get('price')
        
        if product_id and quantity and price:
            product = get_object_or_404(Product, id=product_id)
            customer = get_object_or_404(Customer, id=customer_id) if customer_id else None
            Sale.objects.create(
                product=product,
                customer=customer,
                quantity=float(quantity),
                price=float(price)
            )
            messages.success(request, 'Sale recorded successfully!')
            return redirect('sales')
    
    context = {
        'sales': sales_list,
        'products': products,
        'customers': customers,
        'q': q,
    }
    return render(request, 'sales.html', context)


# Inventory view
@login_required
def inventory(request):
    """
    Display inventory levels
    """
    q = request.GET.get('q', '').strip()

    inventory_qs = Inventory.objects.select_related('product')
    if q:
        inventory_qs = inventory_qs.filter(product__title__icontains=q)
    
    inventory_items = inventory_qs.all()

    # numpy-based low stock flag precomputed for template convenience
    low_stock_threshold = 10
    quantities = np.array([item.total_balance_quantity for item in inventory_items]) if inventory_items else np.array([])
    low_stock_count = int((quantities <= low_stock_threshold).sum()) if quantities.size else 0
    
    context = {'inventory_items': inventory_items, 'q': q, 'low_stock_threshold': low_stock_threshold, 'low_stock_count': low_stock_count}
    return render(request, 'inventory.html', context)
