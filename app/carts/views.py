from django.views.generic import TemplateView, CreateView, View, DeleteView
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy

from store.models import Product
from .models import Cart, CartItem


def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()

    return cart


class CartView(TemplateView):
    """View for get cart of items."""
    template_name = 'store/cart.html'

    def get(self, request, *args, **kwargs):
        total, quantity = 0, 0
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
            for cart_item in cart_items:
                total += (cart_item.product.price * cart_item.quantity)
                quantity += cart_item.quantity
            tax = 2 * total / 100
            grand_total = total + tax
        except ObjectNotExist:
            pass

        context = {
            'total': total,
            'quantity': quantity,
            'cart_items': cart_items,
            'grand_total': grand_total,
            'tax': tax,
        }
        return render(request, self.template_name, context)


class CartAddView(View):
    """View for adding cart."""

    def get(self, request, *args, **kwargs):
        product_id = kwargs['product_id']

        product = Product.objects.get(id=product_id)
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id=_cart_id(request)
            )
        cart.save()

        try:
            cart_item = CartItem.objects.get(product=product, cart=cart)
            cart_item.quantity += 1
            cart_item.save()
        except CartItem.DoesNotExist:
            cart_item = CartItem.objects.create(
                product=product,
                quantity=1,
                cart=cart,
            )
            cart_item.save()
        return redirect('carts:cart')


class CartRemoveView(View):
    """View for removing cart."""

    def get(self, request, *args, **kwargs):
        cart = Cart.objects.get(cart_id=_cart_id(request))
        product = get_object_or_404(Product, id=kwargs['product_id'])
        cart_item = CartItem.objects.get(product=product, cart=cart)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
        return redirect('carts:cart')


class CartItemRemoveView(DeleteView):
    """View for removing cart item."""
    success_url = reverse_lazy('carts:cart')
    pk_url_kwarg = 'product_id'

    def get_object(self, queryset=None):
        cart = Cart.objects.get(cart_id=_cart_id(self.request))
        product = get_object_or_404(Product, id=self.kwargs['product_id'])
        cart_item = CartItem.objects.get(product=product, cart=cart)
        return cart_item