from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse, JsonResponse
from .models import *

from django.views.decorators.csrf import csrf_exempt

def a_home(request):
    customers = Customer.objects.all()
    orders = Order.objects.all()
    products = Product.objects.all()
    categories = Product.CATEGORY
    total_orders = orders.count()
    delivered_orders = orders.filter(status='Delivered').count()
    pending_orders = orders.filter(status='Pending').count()
    return render(request, 'accounts/dashboard.html', {
        'customers': customers,
        'orders': orders,
        'products': products,
        'categories': categories,
        'total_orders': total_orders,
        'delivered_orders': delivered_orders,
        'pending_orders': pending_orders
    })

def about(request):
    return render(request, 'accounts/about.html')
def contact(request):   
    return render(request, 'accounts/contact.html')
def products(request):
    products = Product.objects.all()
    categories = Product.CATEGORY
    return render(request, 'accounts/products.html', {
        'products': products,
        'categories': categories,
    })

@csrf_exempt
def add_product(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        name = request.POST.get('name')
        category = request.POST.get('category')
        price = request.POST.get('price')
        product = Product.objects.create(name=name, category=category, price=price)
        return JsonResponse({
            'id': product.id,
            'name': product.name,
            'category': product.category,
            'price': product.price
        })
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        product.name = request.POST.get('name')
        product.category = request.POST.get('category')
        product.price = request.POST.get('price')
        product.save()
        return JsonResponse({
            'id': product.id,
            'name': product.name,
            'category': product.category,
            'price': product.price
        })
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def delete_product(request, product_id):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        product = get_object_or_404(Product, id=product_id)
        product.delete()
        return JsonResponse({'id': product_id, 'deleted': True})
    return JsonResponse({'error': 'Invalid request'}, status=400)

def view_product(request, product_id):
    product = Product.objects.get(id=product_id)
    return render(request, 'accounts/products.html', {'product': product})

def customers(request):
    customers = Customer.objects.all()
    return render(request, 'accounts/customers.html', {'customers': customers})
