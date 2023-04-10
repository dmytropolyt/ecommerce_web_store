"""
Tests for orders app.
"""
import pytest
from pytest_django.asserts import assertContains

from django.urls import reverse


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

    # def test_payments(self):