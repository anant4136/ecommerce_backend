from django.contrib.auth import password_validation
from rest_framework import serializers
from backend_api.models import (Bookmark, CartItem, Delivery, Product, Order,
                                User, Product_models)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'name', 'email',
                  'phone', 'is_industry', 'location']
        extra_kwargs = {'password': {'write_only': True}}


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'name',
                  'phone', 'is_industry', 'location']


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'owner', 'name', 'quantity', 'warranty', 'guarantee',
                  'sell_price', 'discount', 'image', 'debit', 'credit', 'upi', 'cash', 'date']
        read_only_fields = ['id', 'owner']


class Product_modelsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product_models
        fields = ['id', 'admin', 'name', 'image1',
                  'image2', 'description', 'details']
        read_only_fields = ['id', 'admin']


class DeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model = Delivery
        fields = '__all__'


class BookmarkSerializer(serializers.ModelSerializer):

    class Meta:
        model = Bookmark
        fields = ['id', 'user', 'machine']
        read_only_fields = ['id', 'user']


class BookmarkDetailSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = Bookmark
        fields = ['id', 'user', 'product']
        read_only_fields = ['id', 'user']


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'customer', 'product', 'quantity', 'status',
                  'name_of_recipient', 'phone', 'state', 'city', 'pincode', 'address', 'date']
        read_only_fields = ['id', 'customer']


class OrderDetailSerializer(serializers.ModelSerializer):
    customer = UserSerializer()
    product = ProductSerializer()

    class Meta:
        model = Order
        fields = ['id', 'customer', 'product', 'quantity', 'status',
                  'name_of_recipient', 'phone', 'state', 'city', 'pincode', 'address', 'date']
        read_only_fields = ['id', 'customer']


class OrderCustomerSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = Order
        fields = ['id', 'product', 'quantity', 'status', 'name_of_recipient',
                  'phone', 'state', 'city', 'pincode', 'address', 'date']


class CartItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['cart', 'product', 'quantity']
        write_only_fields = ['cart']


class CartItemDetailSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity']
        read_only_fields = ['id']


class CartItemUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['product', 'quantity']
        read_only_fields = ['product']


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(
        max_length=128, write_only=True, required=True)
    new_password1 = serializers.CharField(
        max_length=128, write_only=True, required=True)
    new_password2 = serializers.CharField(
        max_length=128, write_only=True, required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        print(value)
        if not user.check_password(value):
            raise serializers.ValidationError(
                ('Your old password was entered incorrectly. Please enter it again.')
            )
        return value

    def validate(self, data):
        if data['new_password1'] != data['new_password2']:
            raise serializers.ValidationError(
                {'new_password2': ("The two password fields didn't match.")})
        password_validation.validate_password(
            data['new_password1'], self.context['request'].user)
        return data

    def save(self, **kwargs):
        password = self.validated_data['new_password1']
        user = self.context['request'].user
        user.set_password(password)
        user.save()
        return user


class ReportSerializer(serializers.Serializer):

    Report = serializers.CharField()
    count = serializers.IntegerField()
