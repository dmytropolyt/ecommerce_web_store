from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('place-order/', views.PlaceOrderView.as_view(), name='place-order'),
    path('payments/', views.PaymentsView.as_view(), name='payments'),
    path('order-complete/', views.OrderCompleteView.as_view(), name='order-complete'),
]