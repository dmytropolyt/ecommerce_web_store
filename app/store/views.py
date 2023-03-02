from django.views.generic import TemplateView, ListView, DetailView, View
from django.shortcuts import get_object_or_404, render
from django.db.models import Q

from .models import Product
from category.models import Category
from carts.models import CartItem
from carts.views import _cart_id


class StoreView(ListView):
    """List all products of store or filter by category."""
    context_object_name = 'products'
    template_name = 'store/store.html'
    paginate_by = 6

    def get_queryset(self):
        try:
            if self.kwargs['category_slug']:
                category = get_object_or_404(Category, slug=self.kwargs['category_slug'])
                return Product.objects.filter(category=category, is_available=True).order_by('id')
        except KeyError:
            return Product.objects.filter(is_available=True).order_by('id')
        else:
            return Product.objects.filter(is_available=True).order_by('id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product_count'] = self.get_queryset().count()
        return context


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


class SearchView(View):
    """View for searching """

    def get(self, request, *args, **kwargs):
        if 'keyword' in request.GET:
            keyword = request.GET['keyword']
            if keyword:
                products = Product.objects.filter(
                    Q(description__icontains=keyword) | Q(name__icontains=keyword)
                ).order_by('-created_date')
                product_count = products.count()

        context = {
            'products': products,
            'product_count': product_count,
        }

        return render(request, 'store/store.html', context)


