from django.urls import path
from . import views


app_name = 'carts'

urlpatterns = [
    path('', views.CartView.as_view(), name='cart'),
    path('add-cart/<int:product_id>/', views.CartAddView.as_view(), name='add-cart'),
    path('remove-cart/<int:product_id>/<int:cart_item_id>/', views.CartRemoveView.as_view(), name='remove-cart'),
    path(
        'remove-cart-item/<int:product_id>/<int:cart_item_id>/',
        views.CartItemRemoveView.as_view(),
        name='remove-cart-item'
    ),

    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
]
