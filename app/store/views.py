from django.views.generic import TemplateView, ListView, DetailView
from django.shortcuts import get_object_or_404

from .models import Product
from category.models import Category
from carts.models import CartItem
from carts.views import _cart_id


class StoreView(ListView):
    """List all products of store or filter by category."""
    context_object_name = 'products'
    template_name = 'store/store.html'

    def get_queryset(self):
        try:
            if self.kwargs['category_slug']:
                category = get_object_or_404(Category, slug=self.kwargs['category_slug'])
                return Product.objects.filter(category=category, is_available=True)
        except KeyError:
            return Product.objects.filter(is_available=True)
        else:
            return Product.objects.filter(is_available=True)


class ProductDetailView(DetailView):
    """Product detail view."""
    model = Product
    template_name = 'store/product_detail.html'
    slug_url_kwarg = 'product_slug'
    context_object_name = 'single_product'

    def get_object(self, queryset=None):
        queryset = self.get_queryset()
        try:
            return queryset.get(
                category__slug=self.kwargs['category_slug'], slug=self.kwargs[self.slug_url_kwarg]
            )
        except Exception as e:
            raise e

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['in_cart'] = CartItem.objects.filter(
            cart__cart_id=_cart_id(self.request), product=context['single_product']
        ).exists()

        return context


