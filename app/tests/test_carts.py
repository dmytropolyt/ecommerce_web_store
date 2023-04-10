"""
Tests for carts app.
"""
import pytest
from pytest_django.asserts import assertNotContains, assertTemplateUsed, assertContains

from django.urls import reverse

import json


@pytest.mark.django_db
class TestCarts:

    def test_add_cart(self, client, product):
        """Test cart add view."""
        product = product()

        response = client.post(reverse('carts:add-cart', args=[product.id]), {'color': 'Red'})
        content = json.loads(response.content.decode())

        assert response.status_code == 200
        assert content['cart_items_count'] == 1

        product.image.delete()

    @pytest.mark.parametrize(
        'cart_products, product_name',
        [('Coat', 'Coat'), ('Jacket', 'Jacket'), ('Shirt', 'Shirt')],
        indirect=['cart_products']
    )
    def test_remove_cart_item(self, cart_products, product_name):
        """Test remove cart item from cart."""
        client = cart_products
        response = client.post(reverse('carts:remove-cart-item', args=[1, 1]))

        assert response.status_code == 302

        response = client.get(reverse('carts:cart'))
        assertNotContains(response, product_name)

    @pytest.mark.parametrize('cart_products', ['Coat', 'Jacket', 'Shirt'], indirect=True)
    def test_remove_cart(self, cart_products):
        """Test remove cart from cart page."""
        client = cart_products
        response = client.post(reverse('carts:remove-cart', args=[1, 1]))

        assert response.status_code == 302

    def test_checkout(self, cart_products):
        """Test checkout view."""
        client = cart_products
        response = client.get(reverse('carts:checkout'))

        assert response.status_code == 200
        assertTemplateUsed(response, 'store/checkout.html')
        assertContains(response, 'Jacket')
        assertContains(response, 'Coat')
        assertContains(response, 'Shirt')
