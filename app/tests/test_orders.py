"""
Tests for orders app.
"""
import pytest
from pytest_django.asserts import assertContains, assertRedirects

from django.urls import reverse
from orders.models import Order

import json
import base64


@pytest.mark.django_db
class TestOrders:

    def test_place_order(self, cart_products):
        """Test place order view."""
        client = cart_products
        payload = {
            'first_name': 'Test',
            'last_name': 'Test',
            'email': 'test1@example.com',
            'phone': '+380999969696',
            'address_line_1': 'street Test',
            'city': 'Kyiv',
            'state': 'Kyiv',
        }
        response = client.post(reverse('orders:place-order'), payload)

        assert response.status_code == 200
        for value in payload.values():
            assertContains(response, value)
        # Assert response contains product names from fixture
        assertContains(response, 'Coat')
        assertContains(response, 'Jacket')
        assertContains(response, 'Shirt')

    def test_payments(self, place_order, celery_app, celery_worker, mailoutbox):
        """
        Test payments view that accepts request from LiQpay.
        """
        client = place_order
        # Get cart_id from Cart model and order_number from Order model,
        order_number = Order.objects.get(pk=1).order_number
        # Create test data, like liqpay creating and sends
        # Info in dict is cart id, because client isn't logged in
        data = {
            'payment_id': 2277196704, 'status': 'success',
            'paytype': 'privat24', 'order_id': order_number,
            'info': 1
        }
        response_url = f"{reverse('orders:order-complete')}" \
                       f"?order_number={data['order_id']}&payment_id={data['payment_id']}"
        data = base64.b64encode(json.dumps(data).encode("utf-8")).decode("ascii")
        response = client.post(reverse('orders:payments'), {'data': data})

        assert response.status_code == 302
        assertRedirects(response, response_url)
        assert len(mailoutbox) == 1

        mail = mailoutbox[0]
        assert mail.subject == 'Thank you for your order!'
        assert order_number in mail.body

    def test_order_complete(self, payment_success):
        """Test order complete view."""
        client = payment_success[0]
        response = payment_success[1]
        order = Order.objects.get(pk=1)
        response = client.get(response.url)

        assertContains(response, order.order_number)
        assertContains(response, order.payment.status)
        assertContains(response, order.full_name())
        assertContains(response, order.full_address())
        assertContains(response, order.city)
        assertContains(response, order.state)
