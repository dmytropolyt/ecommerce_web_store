from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

from .forms import ChangePasswordForm


urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('', views.DashboardView.as_view(), name='dashboard'),

    path('activate/<uidb64>/<token>/', views.ActivateView.as_view(), name='activate'),
    path('reset-password/', views.AccountPasswordResetView.as_view(), name='password-reset'),
    path(
        'reset-password-validate/<uidb64>/<token>/',
        views.AccountPasswordResetConfirmView.as_view(),
        name='password-reset-confirm'
    ),
]
