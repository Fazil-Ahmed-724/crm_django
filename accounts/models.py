from django.db import models
from django.test import tag

# Create your models here.
class Customer (models.Model):
    name = models.CharField(max_length=255,null=True)
    phone = models.CharField(max_length=20, null=True)
    email = models.EmailField(unique=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.name 
class Tag (models.Model):
    name = models.CharField(max_length=255,null=True)
    def __str__(self):
        return self.name 
class Product (models.Model):
    CATEGORY = (
        ('Indoor', 'Indoor'),
        ('Out Door', 'Out Door'),
    )
    name = models.CharField(max_length=255,null=True)
    price = models.FloatField(null=True)
    category = models.CharField(max_length=255,null=True, choices=CATEGORY)
    description = models.TextField(null=True)
    tag = models.ManyToManyField(Tag, null=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.name

class Order (models.Model):
    customer = models.ForeignKey(Customer, null=True, on_delete=models.SET_NULL)
    product = models.ForeignKey(Product, null=True, on_delete=models.SET_NULL)
    STATUS = (
        ('Pending', 'Pending'),
        ('Out for delivery', 'Out for delivery'),
        ('Delivered', 'Delivered'),
    )
    status = models.CharField(max_length=255, null=True, choices=STATUS)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    def __str__(self):
        customer_name = self.customer.name if self.customer else "Unknown customer"
        product_name = self.product.name if self.product else "Unknown product"
        return f"{customer_name} - {product_name}"
