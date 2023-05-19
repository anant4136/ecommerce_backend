from backend_api.serializers import *
from backend_api.models import *
from backend_api.permissions import IsCustomer, IsSeller
from rest_framework.views import APIView
from rest_framework.serializers import ValidationError
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.generics import UpdateAPIView
from rest_framework import generics, status
from django_filters.rest_framework import DjangoFilterBackend
import datetime
from django.conf import settings


class registerUser(APIView):
    permission_classes = [AllowAny]

    def post(self, request, format=None):
        data = request.data
        user = User.objects.create_user(
            data["username"], data["email"], data["password"])
        user.name = data["name"]
        user.is_industry = data["is_industry"]
        user.phone = data["phone"]
        user.location = data["location"]
        user.save()
        serializer = UserSerializer(user)
        return Response(serializer.data)


class UsersView(generics.RetrieveAPIView):
    def get_permissions(self):
        method = self.request.method
        if method == 'GET':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    queryset = User.objects.all()
    serializer_class = UserSerializer


class ProfileView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        serializer = UserUpdateSerializer(
            instance=request.user, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        request.user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ChangePasswordView(UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK)


class Product_modelsView(generics.ListCreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = Product_modelsSerializer

    def get_serializer_class(self):
        method = self.request.method

        if method == 'GET':
            return Product_modelsSerializer

        if method == 'POST':
            return Product_modelsSerializer

    def get_queryset(self):

        return Product_models.objects.all()

    def perform_create(self, serializer):

        serializer.save(admin=self.request.user)


class ProductsView(generics.ListCreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [
        'owner__location', 'discount', 'name', 'date']

    def get_serializer_class(self):
        method = self.request.method

        if method == 'GET':
            return ProductSerializer

        if method == 'POST':
            return ProductSerializer

    def get_queryset(self):
        user = self.request.user

        if user.is_anonymous:
            return Product.objects.filter()

        if user.is_industry:
            return user.product_set.all()

        own = self.request.query_params.get('own')
        if own:
            return Product.objects.filter(owner=user)
        return Product.objects.exclude(owner=user)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name', 'discount',  'date']

    def perform_create(self, serializer):

        if self.request.user.is_industry:
            serializer.save(owner=self.request.user)
        else:
            serializer.save(owner=self.request.user,
                            )


class Product_modelsDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = Product_modelsSerializer

    def get_serializer_class(self):

        return Product_modelsSerializer

    def get_queryset(self):

        return Product_models.objects.all()

    def update(self, request, *args, **kwargs):

        product_model = self.get_object()
        if product_model.admin != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)

        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(
            product_model, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):

        product_model = self.get_object()
        if product_model.admin != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)

        product_model.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProductSerializer

    def get_serializer_class(self):

        user = self.request.user
        if self.request.user.is_industry:
            return ProductSerializer

        product = self.get_object()
        method = self.request.method
        if method == 'GET':

            return ProductSerializer

    def get_queryset(self):
        user = self.request.user

        if self.request.user.is_industry:
            return user.product_set.all()
        return Product.objects.all()

    def update(self, request, *args, **kwargs):

        product = self.get_object()
        if product.owner != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)

        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(
            product, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):

        product = self.get_object()
        if product.owner != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)

        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrdersView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):

        method = self.request.method
        user = self.request.user

        if method == 'GET':
            if self.request.user.is_industry:
                return OrderDetailSerializer
            return OrderCustomerSerializer

        return OrderSerializer

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'date']

    def get_queryset(self):

        user = self.request.user
        if self.request.user.is_industry:
            return Order.objects.filter(product__owner=user)

        return Order.objects.filter(customer=user)

    def perform_create(self, serializer):

        product = serializer.validated_data['product']
        product.quantity -= 1
        product.save()

        serializer.save(customer=self.request.user)


class OrderDetailView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer
    queryset = Order.objects.all()

    def update(self, request, *args, **kwargs):

        product = self.get_object().product
        if product.owner != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)

        try:
            data = {"status": request.data['status']}
        except KeyError:
            raise ValidationError()

        order = self.get_object()
        serializer = self.get_serializer(order, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)


class CartView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):

        user = self.request.user
        if not self.request.user.is_industry:
            return CartItemDetailSerializer

    def get_queryset(self):

        user = self.request.user

        return CartItem.objects.filter(cart__user=user)

    def post(self, request, *args, **kwargs):

        cart = self.request.user
        items = request.data['items']

        user = self.request.user

        for item in items:
            existing_item = CartItem.objects.filter(
                product__id=item['product'], rent=False)
            if len(existing_item) > 0:
                existing_item[0].quantity += item['quantity']
                existing_item[0].save()
                continue
            print(cart.id)
            item['cart'] = cart.id
            serializer = CartItemCreateSerializer(data=item)

            serializer.is_valid(raise_exception=True)
            serializer.save(rent=False)

        return Response(status=status.HTTP_201_CREATED)


class CartItemView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CartItemDetailSerializer

    def get_queryset(self):

        user = self.request.user

        return CartItem.objects.filter(cart__user=user)

    def put(self, request, *args, **kwargs):

        item = self.get_object()
        cart = item.cart
        if cart != self.request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)

        try:
            quantity = int(request.data["quantity"])
            if quantity < 1:
                raise ValidationError()
        except (KeyError, TypeError, ValueError, ValidationError):
            return Response({'quantity': ['quantity should be a positive integer']}, status=status.HTTP_400_BAD_REQUEST)

        serializer = CartItemUpdateSerializer(
            instance=item, data={'quantity': quantity})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class CartCheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):

        user = self.request.user
        cart = request.user.cart

        for item in cart.get_items():

            Order.objects.create(customer=request.user, product=item.product, quantity=item.quantity,
                                 phone=request.data['phone'], pincode=request.data['pincode'])
            item.delete()

        return Response(status=status.HTTP_200_OK)


class BookmarkView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BookmarkSerializer

    def get_serializer_class(self):

        method = self.request.method
        if method == 'GET':
            return BookmarkDetailSerializer
        return BookmarkSerializer

    def get_queryset(self):

        return Bookmark.objects.filter(user=self.request.user)

    def perform_create(self, serializer):

        serializer.save(user=self.request.user)


class BookmarkDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BookmarkSerializer
    queryset = Bookmark.objects.all()

    def delete(self, request, **kwargs):

        bookmark = self.get_object()
        if bookmark.user != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)

        bookmark.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class Connections(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):

        user = request.user
        connections = user.get_connections()
        serializer = UserSerializer(connections, many=True)
        return Response(serializer.data)


class Reports(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):

        list = []
        report = request.GET.get('report', False)
        product = request.GET.get('product', False)
        order = request.GET.get('order', False)
        start = request.GET.get('start', None)
        end = request.GET.get('end', None)

        start = datetime.datetime.strptime(
            start, '%Y-%m-%d').strftime('%Y-%m-%d')
        end = datetime.datetime.strptime(
            end, '%Y-%m-%d').strftime('%Y-%m-%d')
        user = self.request.user
        if self.request.user.is_industry:
            if report:
                if order:
                    list1 = Order.objects.filter(
                        product__owner=self.request.user,
                        date__range=[start, end]).order_by('-pk')
                    data = [
                        {"Report": 'product ordered', "count": len(list1)}]
                    results = ReportSerializer(data, many=True).data

                elif product:
                    list1 = Product.objects.filter(
                        owner=self.request.user,
                        date__range=[start, end]).order_by('-pk')
                    data = [
                        {"Report": 'product created', "count": len(list1)}]
                    results = ReportSerializer(data, many=True).data

                return Response(results)
            else:
                if order:
                    list = Order.objects.filter(
                        product__owner=self.request.user,
                        date__range=[start, end]).order_by('-pk')

                    serializer = OrderSerializer(
                        list, many=True, context={'request': request})

                elif product:
                    list = Product.objects.filter(
                        owner=self.request.user,
                        date__range=[start, end]).order_by('-pk')

                    serializer = ProductSerializer(
                        list, many=True, context={'request': request})

                return Response(serializer.data)
