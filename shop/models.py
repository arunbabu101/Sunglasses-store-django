from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from supplier.models import Supplier
from django.utils import timezone

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='category', blank=True) 

    class Meta:
        ordering = ('name', )
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def get_url(self):
        return reverse('shop:products_by_category', args=[self.slug])

    def __str__(self):
        return '{}'.format(self.name)


class Product(models.Model):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE,default=None,null=True)
    image = models.ImageField(upload_to='product', blank=True)
    stock = models.IntegerField()
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    reorder = models.IntegerField(default=5)
    color = models.CharField(max_length=50, default='black') 
    size = models.IntegerField(default=50) 

    def get_url(self):
        return reverse('shop:prodcatdetail', args=[self.category.slug, self.slug])

    class Meta:
        ordering = ('name', )
        verbose_name = 'product'
        verbose_name_plural = 'products'

class Users(models.Model):
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=100)
    first_name = models.CharField(max_length=50, default='John')  # Default value for first name
    last_name = models.CharField(max_length=50, default='Doe')    # Default value for last name

    def __str__(self):
        return self.username

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    STATUS_CHOICES = (
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('returned', 'Returned'),

    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing')
    
    def __str__(self):
        return f"Order {self.id} by {self.user.username} - {self.order_date}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    item_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity}x {self.product.name} in Order {self.order.id}"


class Reorders(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    pieces = models.IntegerField()
    created_at = models.DateTimeField(default=timezone.now)

    STATUS_CHOICES = (
        ('sent', 'Sent'),
        ('canceled', 'Canceled'),
        ('updated', 'Stock Updated'),
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='')
    
    def __str__(self):
        return f"Reorder for {self.product.name} by {self.supplier.name}"
    


class Return(models.Model):
    order_item = models.OneToOneField(OrderItem, on_delete=models.CASCADE)
    reason = models.TextField()
    return_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Return for {self.order_item.product.name} (Order {self.order_item.order.id})'