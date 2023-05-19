from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from rest_framework.authtoken import views as auth_views

from backend_api.views import *

urlpatterns = [
    path('register/', registerUser.as_view(), name='register'),
    path('users/<int:pk>', UsersView.as_view(), name='user'),
    path('users/change-password',
         ChangePasswordView.as_view(), name='change-password'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('products/', ProductsView.as_view(), name='products'),
    path('products/<int:pk>', ProductDetailView.as_view(), name='product'),
    path('product_models/', Product_modelsView.as_view(), name='product_models'),
    path('product_models/<int:pk>',
         Product_modelsDetailView.as_view(), name='product_model'),
    path('bookmarks/', BookmarkView.as_view(), name='bookmarks'),
    path('bookmarks/<int:pk>', BookmarkDetailView.as_view(),
         name='bookmarksdetails'),
    path('connections/', Connections.as_view(), name='connections'),
    path('reports/', Reports.as_view(), name='reports'),
    path('cart/', CartView.as_view(), name='cart'),
    path('cart-items/<int:pk>', CartItemView.as_view(), name='cart-items'),
    path('cart/checkout', CartCheckoutView.as_view(), name='cart-checkout'),
    path('orders/', OrdersView.as_view(), name='orders'),
    path('orders/<int:pk>', OrderDetailView.as_view(), name='order-detail'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [
    path('token/', auth_views.obtain_auth_token)
]
