from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse, JsonResponse
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .models import *
from decimal import Decimal, InvalidOperation

from django.views.decorators.csrf import csrf_exempt


def _validate_product_data(name, category, price):
    name = (name or '').strip()
    category = (category or '').strip()
    price = (price or '').strip()

    if not name:
        return None, 'Product name is required.'
    if category not in dict(Product.CATEGORY):
        return None, 'Please select a valid product category.'
    if not price:
        return None, 'Price is required.'

    try:
        parsed_price = Decimal(price)
    except (InvalidOperation, TypeError):
        return None, 'Price must be a valid number.'

    if parsed_price < 0:
        return None, 'Price cannot be negative.'

    return {
        'name': name,
        'category': category,
        'price': float(parsed_price),
    }, None


def _validate_customer_data(name, phone, email, current_customer=None):
    name = (name or '').strip()
    phone = (phone or '').strip()
    email = (email or '').strip()

    if not name:
        return None, 'Customer name is required.'
    if not phone:
        return None, 'Phone is required.'
    if not email:
        return None, 'Email is required.'

    try:
        validate_email(email)
    except ValidationError:
        return None, 'Please enter a valid email address.'

    existing_customer = Customer.objects.filter(email__iexact=email)
    if current_customer is not None:
        existing_customer = existing_customer.exclude(id=current_customer.id)
    if existing_customer.exists():
        return None, 'This email address is already being used by another customer.'

    return {
        'name': name,
        'phone': phone,
        'email': email,
    }, None


def _validate_order_data(customer_id, product_id, status):
    customer_id = (customer_id or '').strip()
    product_id = (product_id or '').strip()
    status = (status or '').strip()

    if not customer_id:
        return None, 'Customer is required.'
    if not product_id:
        return None, 'Product is required.'
    if status not in dict(Order.STATUS):
        return None, 'Please select a valid order status.'

    customer = Customer.objects.filter(id=customer_id).first()
    if customer is None:
        return None, 'Selected customer was not found.'

    product = Product.objects.filter(id=product_id).first()
    if product is None:
        return None, 'Selected product was not found.'

    return {
        'customer': customer,
        'product': product,
        'status': status,
    }, None

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
        cleaned_data, error = _validate_product_data(
            request.POST.get('name'),
            request.POST.get('category'),
            request.POST.get('price'),
        )
        if error:
            return JsonResponse({'error': error}, status=400)

        product = Product.objects.create(**cleaned_data)
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
        cleaned_data, error = _validate_product_data(
            request.POST.get('name'),
            request.POST.get('category'),
            request.POST.get('price'),
        )
        if error:
            return JsonResponse({'error': error}, status=400)

        product.name = cleaned_data['name']
        product.category = cleaned_data['category']
        product.price = cleaned_data['price']
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
        cleaned_data, error = _validate_customer_data(
            request.POST.get('name'),
            request.POST.get('phone'),
            request.POST.get('email'),
        )
        if error:
            return JsonResponse({'error': error}, status=400)

        customer = Customer.objects.create(**cleaned_data)
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

            product = Product.objects.filter(id=product_id).first()
            if product is None:
                return JsonResponse({'error': 'Selected product was not found.'}, status=400)

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
        cleaned_data, error = _validate_customer_data(
            request.POST.get('name'),
            request.POST.get('phone'),
            request.POST.get('email'),
            current_customer=customer,
        )
        if error:
            return JsonResponse({'error': error}, status=400)

        customer.name = cleaned_data['name']
        customer.phone = cleaned_data['phone']
        customer.email = cleaned_data['email']
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
        cleaned_data, error = _validate_order_data(
            request.POST.get('customer'),
            request.POST.get('product'),
            request.POST.get('status'),
        )
        if error:
            return JsonResponse({'error': error}, status=400)

        order = Order.objects.create(**cleaned_data)
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
        cleaned_data, error = _validate_order_data(
            request.POST.get('customer'),
            request.POST.get('product'),
            request.POST.get('status'),
        )
        if error:
            return JsonResponse({'error': error}, status=400)

        order.customer = cleaned_data['customer']
        order.product = cleaned_data['product']
        order.status = cleaned_data['status']
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
