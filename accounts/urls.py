from django.urls import path
from . import views

urlpatterns = [
    path('a_home/', views.a_home, name='a_home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('products/', views.products, name='products'),
    path('products/add/', views.add_product, name='add_product'),
    path('products/view/<int:product_id>/', views.view_product, name='view_product'),
    path('products/edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('products/delete/<int:product_id>/', views.delete_product, name='delete_product'),
    path('customers/', views.customers, name='customers'),
    

]
