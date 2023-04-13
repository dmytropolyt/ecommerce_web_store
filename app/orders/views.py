from django.shortcuts import render, redirect
from django.views.generic import TemplateView, View
from carts.models import CartItem, Cart
from carts.views import _cart_id
from .forms import OrderForm
from .models import Order, Payment, OrderProduct
from store.models import Product
from django.contrib import messages

import datetime
from liqpay import LiqPay
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .tasks import send_order_email


@method_decorator(csrf_exempt, name='dispatch')
class PaymentsView(TemplateView):
    template_name = 'orders/payments.html'

    def post(self, request, *args, **kwargs):
        # Store transaction details to Payment model
        liqpay = LiqPay(settings.LIQPAY_PUBLIC_KEY, settings.LIQPAY_PRIVATE_KEY)
        data = liqpay.decode_data_from_str(request.POST.get('data'))
        if data['status'] == 'success':
            order = Order.objects.get(is_ordered=False, order_number=data['order_id'])
            payment = Payment(
                payment_id=data['payment_id'],
                method=data['paytype'],
                amount_paid=order.order_total,
                status=data['status'],
            )

            if order.user:
                payment.user = order.user
                cart_items = CartItem.objects.filter(user=order.user)
            else:
                cart_items = CartItem.objects.filter(cart=data['info'])

            payment.save()

            order.payment = payment
            order.is_ordered = True
            order.save()

            # Move the cart items to OrderProduct model

            for item in cart_items:
                order_product = OrderProduct()
                order_product.order_id = order.pk
                order_product.payment = payment
                order_product.user = order.user
                order_product.product_id = item.product_id
                order_product.quantity = item.quantity
                order_product.product_price = item.product.price
                order_product.ordered = True
                order_product.save()

                cart_item = CartItem.objects.get(id=item.id)
                product_variation = cart_item.variations.all()
                order_product.variations.set(product_variation)
                order_product.save()

                # Reduce the quantity of the sold products
                product = Product.objects.get(id=item.product_id)
                product.stock -= item.quantity
                product.save()

            # Clear cart
            cart_items.delete()

            # Send order received email to customer
            send_order_email.delay({
                'first_name': order.first_name,
                'order_number': order.order_number,
                'email': order.email
            })

            data = {
                'order_number': order.order_number,
                'payment_id': payment.payment_id,
            }

            return redirect(
                f"/orders/order-complete/?order_number={data['order_number']}&payment_id={data['payment_id']}"
            )

        else:
            messages.error(request, 'Something went wrong, please verify the information and try again.')
            return redirect('orders:place-order')


class PlaceOrderView(TemplateView):
    template_name = ''

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['cart_items'] = CartItem.objects.filter(user=self.request.user)
        else:
            context['cart_items'] = CartItem.objects.filter(cart__cart_id=_cart_id(self.request))

        return context

    def get(self, request, *args, **kwargs):
        cart_items = self.get_context_data()['cart_items']

        if cart_items.count() <= 0:
            return redirect('store:store')
        else:
            return redirect('carts:checkout')

    def post(self, request, total=0, quantity=0, *args, **kwargs):
        cart_items = self.get_context_data()['cart_items']
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = 2 * total / 100
        grand_total = total + tax

        form = OrderForm(request.POST)
        if form.is_valid():
            # Store all the billing information inside Order table
            order = form.save(commit=False)

            # Check user exist
            if request.user.is_authenticated:
                order.user = request.user

            order.order_total = grand_total
            order.tax = tax
            order.ip = request.META.get('REMOTE_ADDR')
            order.save()
            # Generate order number
            current_date = datetime.date.today().strftime('%Y%m%d')
            order_number = current_date + str(order.id)
            order.order_number = order_number
            order.save()

            # LiqPay form
            liqpay = LiqPay(settings.LIQPAY_PUBLIC_KEY, settings.LIQPAY_PRIVATE_KEY)
            result_url = f'http://{str(get_current_site(request))}/orders/payments/'

            liqpay_data = {
                'action': 'pay',
                'amount': order.order_total,
                'currency': 'USD',
                'description': 'description',
                'order_id': order.order_number,
                'version': '3',
                'language': 'en',
                'result_url': result_url,
                'server_url': result_url,
            }
            if not request.user.is_authenticated:
                liqpay_data['info'] = Cart.objects.get(cart_id=_cart_id(request)).pk

            liqpay_form = liqpay.cnb_form(liqpay_data)

            to_context = {
                'order': order,
                'total': total,
                'tax': tax,
                'grand_total': grand_total,
                'liqpay_form': liqpay_form,
            }
            context = self.get_context_data(**to_context)

            return render(request, 'orders/payments.html', context)


class OrderCompleteView(View):

    def get(self, request, *args,  **kwargs):
        order_number = self.request.GET['order_number']
        payment_id = self.request.GET['payment_id']
        try:
            order = Order.objects.get(order_number=order_number, is_ordered=True)
            ordered_products = OrderProduct.objects.filter(order_id=order.id)

            context = {
                'order': order,
                'ordered_products': ordered_products,
                'payment_id': order.payment.payment_id,
                'sub_total': order.order_total - order.tax,
            }
            return render(request, 'orders/order_complete.html', context)
        except (Payment.DoesNotExist, Order.DoesNotExist):
            return redirect('home')
