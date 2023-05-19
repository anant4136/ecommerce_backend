from django.contrib import admin
from .models import (Bookmark, CartItem, Delivery, Product, Product_models, Order, User
                     )
# Register your models here.
admin.site.register(Product)
admin.site.register(User)
admin.site.register(Product_models)
admin.site.register(Delivery)
admin.site.register(Bookmark)
admin.site.register(Order)
admin.site.register(CartItem)
