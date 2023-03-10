from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.StoreView.as_view(), name='store'),
    path('category/<slug:category_slug>/', views.StoreView.as_view(), name='products-by-category'),
    path('category/<slug:category_slug>/<slug:product_slug>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('search/', views.SearchView.as_view(), name='search'),
    path('submit_review/<int:product_id>/', views.SubmitReviewView.as_view(), name='submit-review'),
]