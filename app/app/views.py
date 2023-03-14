from django.views.generic import ListView
from store.models import Product


class HomeView(ListView):
    """View for list available products."""
    queryset = Product.objects.filter(is_available=True).all().order_by('-created_date')
    context_object_name = 'products'
    template_name = 'home.html'
