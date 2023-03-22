from django.views.generic import ListView, DetailView, View, CreateView
from django.shortcuts import get_object_or_404, render, redirect
from django.db.models import Q
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model

from .models import Product, ReviewRating
from category.models import Category
from carts.models import CartItem
from orders.models import OrderProduct
from carts.views import _cart_id
from .forms import ReviewForm


User = get_user_model()


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

        try:
            context['order_product'] = OrderProduct.objects.filter(
                user=self.request.user, product_id=self.get_object().id
            ).exists()
        except (OrderProduct.DoesNotExist, TypeError):
            context['order_product'] = None

        # Get the reviews
        context['reviews'] = context['single_product'].review

        return context


class SearchView(View):
    """View for searching product."""

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


class SubmitReviewView(CreateView):
    form_class = ReviewForm
    pk_url_kwarg = 'product_id'

    def post(self, request, *args, **kwargs):
        url = request.META.get('HTTP_REFERER')
        try:
            reviews = ReviewRating.objects.get(user__id=request.user.id, product__id=kwargs['product_id'])
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(request, 'Thank you! Your review has been updated.')
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.ip = request.META.get('REMOTE_ADDR')
                review.product_id = kwargs['product_id']
                review.user_id = request.user.id
                review.save()
                messages.success(request, 'Thank you! Your review has been submitted.')
                return redirect(url)


class AddWishListView(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        product_id = request.POST['product']
        product = Product.objects.get(pk=product_id)

        if product.users_wishlist.filter(email=request.user.email).exists():
            product.users_wishlist.remove(request.user)
            data = {'bool': False}
        else:
            product.users_wishlist.add(request.user)
            data = {'bool': True}

        return JsonResponse(data)


class WishListView(ListView):
    model = User
    template_name = 'accounts/wishlist.html'
    context_object_name = 'wishlist'

    def get_queryset(self):
        return self.request.user.wishlist.all().order_by('-id')