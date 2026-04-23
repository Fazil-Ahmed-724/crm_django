"""
URL configuration for crm_django project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.conf.urls.static import static

def home(request):
    return HttpResponse("Welcome to the CRM Django application!")
def about(request):
    return HttpResponse("This is a CRM application built with Django.")
def contact(request):
    return HttpResponse("Contact us at 0343358360 or email us at fazilahmed724@gmail.com.")



urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    # path('', home, name='home'),
    # path('about/', about, name='about'),    
    # path('contact/', contact, name='contact'),

]
