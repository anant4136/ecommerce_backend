from django.db import models

# Create your models here.
from email.policy import default
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
import datetime


class User(AbstractUser):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=10)
    location = models.TextField()
    is_industry = models.BooleanField(default=False)
    first_name = None
    last_name = None

    def get_connections(self):
        if self.is_industry:
            return self.get_industry_connections()
        return self.get_farmer_connections()

    def get_seller_connections(self):
        connections = set()

        orders = Order.objects.filter(product__owner=self)
        for order in orders:
            if order.status == Order.ACCEPTED:
                connections.add(order.customer)
        return connections

    def get_customer_connections(self):
        connections = set()

        orders = Order.objects.filter(customer=self)
        for order in orders:
            if order.status == Order.ACCEPTED:
                connections.add(order.product.owner)

        return connections

    def __str__(self):
        return self.username


class Product(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    quantity = models.PositiveIntegerField(default=1)
    warranty = models.IntegerField(default=3)  # number of years
    guarantee = models.IntegerField(default=1)  # number of years
    sell_price = models.IntegerField(default=0)
    discount = models.IntegerField(default=0)  # percentage
    # ask if to be removed??
    date = models.DateField(auto_now_add=True, blank=True)
    image = models.ImageField(upload_to='product_model_images/')
    debit = models.BooleanField(default=True)
    credit = models.BooleanField(default=True)
    upi = models.BooleanField(default=True)
    cash = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Product_models(models.Model):
    admin = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    image1 = models.ImageField(upload_to='product_model_images/')
    image2 = models.ImageField(upload_to='product_model_images/')
    description = models.TextField()
    details = models.JSONField(null=True, blank=True)

    def __str__(self):
        return self.name


class Delivery(models.Model):
    seller = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="seller")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    buyer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="buyer")
    payment = models.BooleanField(default=False)

    def __str__(self):
        return self.buyer + self.product


class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user.name} {self.product.name}'


class Order(models.Model):
    PENDING = 'pending'
    ACCEPTED = 'accepted'
    REJECTED = 'rejected'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (ACCEPTED, 'Accepted'),
        (REJECTED, 'Rejected'),
    ]

    customer = models.ForeignKey(
        User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    status = models.CharField(choices=STATUS_CHOICES,
                              max_length=30, default=PENDING)
    name_of_recipient = models.CharField(max_length=30, default="Reciever")
    phone = models.IntegerField('Phone', validators=[MaxValueValidator(
        9999999999), MinValueValidator(1000000000)])
    state = models.CharField(max_length=30, default="State")
    pincode = models.IntegerField(
        'Pincode', validators=[MaxValueValidator(999999), MinValueValidator(100000)])
    city = models.CharField(max_length=15, default="City")
    address = models.CharField(max_length=300, default="House Address")
    date = models.DateField(auto_now_add=True,
                            blank=True)

    def __str__(self):
        return f'{self.customer.name} {self.product.name} {self.quantity} {str(self.status)} {self.name_of_recipient} {self.phone} {self.state} {self.pincode} {self.city} {self.address} {self.date}'


class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def get_items(self):
        return self.cartitem_set.filter(rent=False)

    def get_residueitems(self):
        return self.cartresidueitem_set.all()

    def get_rentitems(self):
        return self.cartitem_set.filter(rent=True)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    phone = models.IntegerField('Phone', validators=[MaxValueValidator(
        9999999999), MinValueValidator(1000000000)], null=True, blank=True)
    rent = models.BooleanField(default=False)

    def __str__(self):
        return self.product.name + ' ' + str(self.quantity) + ' ' + str(self.rent)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_cart(sender, instance=None,  created=False, *args, **kwargs):
    if created:
        Cart.objects.create(user=instance)
