from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse, JsonResponse
from .models import *

from django.views.decorators.csrf import csrf_exempt

def a_home(request):
    customers = Customer.objects.all()
    orders = Order.objects.all()
    products = Product.objects.all()
    categories = Product.CATEGORY
    statuses = Order.STATUS
    total_orders = orders.count()
    delivered_orders = orders.filter(status='Delivered').count()
    pending_orders = orders.filter(status='Pending').count()
    return render(request, 'accounts/dashboard.html', {
        'customers': customers,
        'orders': orders,
        'products': products,
        'categories': categories,
        'statuses': statuses,
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

@csrf_exempt
def add_customer(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        customer = Customer.objects.create(name=name, phone=phone, email=email)
        return JsonResponse({
            'id': customer.id,
            'name': customer.name,
            'phone': customer.phone,
            'email': customer.email,
            'total_orders': customer.order_set.count(),
        })
    return JsonResponse({'error': 'Invalid request'}, status=400)
@csrf_exempt
def customer_orders(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)

    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        product_ids = request.POST.getlist('product')
        statuses = request.POST.getlist('status')

        if not product_ids or not statuses or len(product_ids) != len(statuses):
            return JsonResponse({'error': 'Each order row needs a product and status.'}, status=400)

        valid_statuses = {key for key, _ in Order.STATUS}
        created_orders = []

        for product_id, status in zip(product_ids, statuses):
            if not product_id or not status:
                return JsonResponse({'error': 'Product and status are required for every row.'}, status=400)
            if status not in valid_statuses:
                return JsonResponse({'error': 'Invalid status selected.'}, status=400)

            product = get_object_or_404(Product, id=product_id)
            order = Order.objects.create(customer=customer, product=product, status=status)
            created_orders.append({
                'id': order.id,
                'customer_id': customer.id,
                'customer_name': customer.name,
                'product_id': product.id,
                'product_name': product.name,
                'status': order.status,
                'date_created': order.date_created.strftime('%Y-%m-%d %H:%M'),
            })

        return JsonResponse({'orders': created_orders})

    if request.method == 'GET':
        products = Product.objects.all()
        statuses = Order.STATUS
        orders = Order.objects.filter(customer=customer).select_related('product').order_by('-date_created')
        return render(request, 'accounts/multiple-orders-customers.html', {
            'customer': customer,
            'products': products,
            'statuses': statuses,
            'orders': orders,
        })

    return JsonResponse({'error': 'Invalid request'}, status=400)


@csrf_exempt
def edit_customer(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        customer.name = request.POST.get('name')
        customer.phone = request.POST.get('phone')
        customer.email = request.POST.get('email')
        customer.save()
        return JsonResponse({
            'id': customer.id,
            'name': customer.name,
            'phone': customer.phone,
            'email': customer.email,
            'total_orders': customer.order_set.count(),
        })
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def delete_customer(request, customer_id):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        customer = get_object_or_404(Customer, id=customer_id)
        customer.delete()
        return JsonResponse({'id': customer_id, 'deleted': True})
    return JsonResponse({'error': 'Invalid request'}, status=400)


def orders(request):
    orders = Order.objects.all()
    products = Product.objects.all()
    customers = Customer.objects.all()
    statuses = Order.STATUS
    return render(request, 'accounts/orders.html', {
        'orders': orders,
        'products': products,
        'customers': customers,
        'statuses': statuses,
    })

@csrf_exempt
def add_order(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        customer_id = request.POST.get('customer')
        product_id = request.POST.get('product')
        status = request.POST.get('status')
        customer = get_object_or_404(Customer, id=customer_id)
        product = get_object_or_404(Product, id=product_id)
        order = Order.objects.create(customer=customer, product=product, status=status)
        return JsonResponse({
            'id': order.id,
            'customer_id': order.customer.id if order.customer else None,
            'customer_name': order.customer.name if order.customer else 'Unknown customer',
            'product_id': order.product.id if order.product else None,
            'product_name': order.product.name if order.product else 'Unknown product',
            'status': order.status,
            'date_created': order.date_created.strftime('%Y-%m-%d %H:%M'),
        })
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def edit_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        customer_id = request.POST.get('customer')
        product_id = request.POST.get('product')
        status = request.POST.get('status')
        order.customer = get_object_or_404(Customer, id=customer_id)
        order.product = get_object_or_404(Product, id=product_id)
        order.status = status
        order.save()
        return JsonResponse({
            'id': order.id,
            'customer_id': order.customer.id if order.customer else None,
            'customer_name': order.customer.name if order.customer else 'Unknown customer',
            'product_id': order.product.id if order.product else None,
            'product_name': order.product.name if order.product else 'Unknown product',
            'status': order.status,
            'date_created': order.date_created.strftime('%Y-%m-%d %H:%M'),
        })
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def delete_order(request, order_id):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        order = get_object_or_404(Order, id=order_id)
        order.delete()
        return JsonResponse({'id': order_id, 'deleted': True})
    return JsonResponse({'error': 'Invalid request'}, status=400)

def view_order(request, order_id):
    order = Order.objects.get(id=order_id)
    return render(request, 'accounts/orders.html', {'order': order})
