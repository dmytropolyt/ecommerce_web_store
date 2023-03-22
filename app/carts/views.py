from django.views.generic import TemplateView, View, DeleteView
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin

from store.models import Product, Variation
from .models import Cart, CartItem

from functools import reduce


def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()

    return cart


class CartView(TemplateView):
    """View for get cart of items."""
    template_name = 'store/cart.html'

    def get(self, request, total=0, quantity=0, *args, **kwargs):
        try:
            tax, grand_total = 0, 0
            if request.user.is_authenticated:
                cart_items = CartItem.objects.filter(user=request.user, is_active=True)
            else:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                cart_items = CartItem.objects.filter(cart=cart, is_active=True)
            for cart_item in cart_items:
                total += (cart_item.product.price * cart_item.quantity)
                quantity += cart_item.quantity
            tax = 2 * total / 100
            grand_total = total + tax
        except ObjectDoesNotExist:
            cart_items = None

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

    def post(self, request, product_id, *args, **kwargs):
        current_user = request.user
        product = Product.objects.get(id=product_id)
        if current_user.is_authenticated:
            product_variation = []
            for key in request.POST:
                value = request.POST[key]

                try:
                    variation = Variation.objects.get(product=product, category__iexact=key, value__iexact=value)
                    product_variation.append(variation)
                except:
                    pass

            if CartItem.objects.filter(product=product, user=current_user).exists():
                cart_item = CartItem.objects.filter(product=product, user=current_user)

                ex_var_list, id_list = [], []
                for item in cart_item:
                    existing_variation = item.variations.all()
                    ex_var_list.append(list(existing_variation))
                    id_list.append(item.id)

                if product_variation in ex_var_list:
                    # Increase the cart item quantity
                    item_id = id_list[ex_var_list.index(product_variation)]
                    item = CartItem.objects.get(product=product, id=item_id)
                    item.quantity += 1
                    item.save()

                else:
                    item = CartItem.objects.create(product=product, quantity=1, user=current_user)
                    if len(product_variation) > 0:
                        item.variations.clear()
                        item.variations.add(*product_variation)

                    item.save()
            else:
                cart_item = CartItem.objects.create(
                    product=product,
                    quantity=1,
                    user=current_user,
                )
                if len(product_variation) > 0:
                    cart_item.variations.clear()
                    cart_item.variations.add(*product_variation)
                cart_item.save()

            cart_items_quantity = [
                i[0] for i in CartItem.objects.filter(user=request.user, is_active=True).values_list('quantity')
            ]
            cart_items_count = reduce(lambda a, b: a[0] + b[0], cart_items_quantity)
            return JsonResponse({'cart_items_count': cart_items_count})

        else:
            product_variation = []
            for key in request.POST:
                value = request.POST[key]

                try:
                    variation = Variation.objects.get(product=product, category__iexact=key, value__iexact=value)
                    product_variation.append(variation)
                except:
                    pass

            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
            except Cart.DoesNotExist:
                cart = Cart.objects.create(
                    cart_id=_cart_id(request)
                )
            cart.save()

            if CartItem.objects.filter(product=product, cart=cart).exists():
                cart_item = CartItem.objects.filter(product=product, cart=cart)

                ex_var_list, id_list = [], []
                for item in cart_item:
                    existing_variation = item.variations.all()
                    ex_var_list.append(list(existing_variation))
                    id_list.append(item.id)

                if product_variation in ex_var_list:
                    # Increase the cart item quantity
                    item_id = id_list[ex_var_list.index(product_variation)]
                    item = CartItem.objects.get(product=product, id=item_id)
                    item.quantity += 1
                    item.save()

                else:
                    item = CartItem.objects.create(product=product, quantity=1, cart=cart)
                    if len(product_variation) > 0:
                        item.variations.clear()
                        item.variations.add(*product_variation)
                    # cart_item.quantity += 1
                    item.save()
            else:
                cart_item = CartItem.objects.create(
                    product=product,
                    quantity=1,
                    cart=cart,
                )
                if len(product_variation) > 0:
                    cart_item.variations.clear()
                    cart_item.variations.add(*product_variation)
                cart_item.save()

            cart_items_count = reduce(
                lambda a, b: a + b, [i[0] for i in cart.cart_item.all().values_list('quantity')]
            )
            return JsonResponse({'cart_items_count': cart_items_count})


class CartRemoveView(View):
    """View for removing cart."""

    def post(self, request, *args, **kwargs):
        product = get_object_or_404(Product, id=kwargs['product_id'])
        try:
            if request.user.is_authenticated:
                cart_item = CartItem.objects.get(product=product, user=request.user, id=kwargs['cart_item_id'])
            else:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                cart_item = CartItem.objects.get(product=product, cart=cart, id=kwargs['cart_item_id'])
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
            else:
                cart_item.delete()
        except Exception as e:
            raise e

        return redirect('carts:cart')


class CartItemRemoveView(DeleteView):
    """View for removing cart item."""
    success_url = reverse_lazy('carts:cart')
    pk_url_kwarg = 'product_id'

    def get_object(self, queryset=None):
        product = get_object_or_404(Product, id=self.kwargs['product_id'])
        if self.request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product, user=self.request.user, id=self.kwargs['cart_item_id'])
        else:
            cart = Cart.objects.get(cart_id=_cart_id(self.request))
            cart_item = CartItem.objects.get(product=product, cart=cart, id=self.kwargs['cart_item_id'])

        return cart_item


class CheckoutView(TemplateView):
    template_name = 'store/checkout.html'

    def get(self, request, total=0, quantity=0, *args, **kwargs):
        try:
            tax, grand_total = 0, 0
            if request.user.is_authenticated:
                cart_items = CartItem.objects.filter(user=request.user, is_active=True)
            else:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                cart_items = CartItem.objects.filter(cart=cart, is_active=True)

            for cart_item in cart_items:
                total += (cart_item.product.price * cart_item.quantity)
                quantity += cart_item.quantity
            tax = 2 * total / 100
            grand_total = total + tax
        except ObjectDoesNotExist:
            pass

        context = {
            'total': total,
            'quantity': quantity,
            'cart_items': cart_items,
            'grand_total': grand_total,
            'tax': tax,
        }
        return render(request, self.template_name, context)
