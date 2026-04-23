from django.shortcuts import render
from django.http import HttpResponse


def home(request):
    return render(request, 'accounts/dashboard.html')
def about(request):
    return render(request, 'accounts/about.html')
def contact(request):   
    return render(request, 'accounts/contact.html')
def products(request):
    return render(request, 'accounts/products.html')
def customers(request):
    return render(request, 'accounts/customers.html')
