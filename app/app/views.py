from django.views.generic import ListView
from store.models import Product
from django.db.models import Count


class HomeView(ListView):
    """View for list available products."""
    queryset = Product.objects.filter(is_available=True).all()
    context_object_name = 'products'
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['popular_products'] = self.queryset.annotate(
            num_orders=Count('order_product')
        ).order_by('-num_orders')
        context['latest_products'] = self.queryset.order_by('-modified_date')
        return context