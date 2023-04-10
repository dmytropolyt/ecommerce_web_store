"""
Tests for store app.
"""
import pytest
from pytest_django.asserts import assertContains

from django.urls import reverse

from store.models import Product, Variation


@pytest.mark.django_db
class TestStore:

    def test_create_product(self, category, image_for_test):
        """Test create Product model instance."""
        data = {
            'name': 'Test Jeans',
            'slug': 'Test Jeans',
            'description': 'Test Jeans description',
            'price': 25,
            'image': image_for_test,
            'stock': 25,
            'category': category
        }
        product = Product.objects.create(**data)

        data['image'] = 'products/' + image_for_test.name
        data['category'] = category.pk
        product_values = Product.objects.filter(name=data['name']).values(*data.keys())

        for key in data:
            assert data[key] == product_values[0][key]

        product.image.delete()

    def test_create_variation(self, category):
        """Test creating variation."""
        data = {
            'name': 'Test Jeans',
            'slug': 'Test Jeans',
            'description': 'Test Jeans description',
            'price': 25,
            'stock': 25,
            'category': category
        }
        product = Product.objects.create(**data)

        Variation.objects.create(product=product, category='color', value='Red')
        variation = Variation.objects.get(product=product, value='Red')

        assert variation.product == product
        assert variation.category == 'color'
        assert variation.value == 'Red'

    def test_store_list_all(self, client, product):
        """Test store list view with all products."""
        products = [product(name='Coat'), product(name='Jacket'), product(name='Shirt')]
        response = client.get(reverse('store:store'))

        assert response.status_code == 200

        for i in products:
            assertContains(response, i.name)
            assertContains(response, i.name)
            assertContains(response, i.name)
            # Delete product image
            i.image.delete()

    def test_store_list_category(self, client, product):
        """Test store list view by category."""
        products = [product(name='Coat'), product(name='Jacket'), product(name='Shirt')]
        response = client.get(reverse('store:products-by-category', kwargs={'category_slug': 'test'}))

        assert response.status_code == 200

        for i in products:
            assert i.category.name == 'test'
            assertContains(response, i.name)
            assertContains(response, i.name)
            assertContains(response, i.name)
            # Delete product image
            i.image.delete()

    def test_search_products(self, client, product):
        """Test search for product."""
        product = product()
        response = client.get(reverse('store:search'), {'keyword': product.name})

        assert response.status_code == 200
        assertContains(response, product.name)

        product.image.delete()

    def test_product_detail_view(self, client, product):
        """Test product detail view."""
        product = product()
        response = client.get(reverse('store:product-detail', args=[product.category.slug, product.slug]))

        assert response.status_code == 200
        assertContains(response, product.name)
        assertContains(response, product.description)
        assertContains(response, product.price)

    def test_submit_review(self, client_user_login, product):
        """Test submit review on product."""
        product = product()
        response = client_user_login.post(
            reverse('store:submit-review', args=[product.id]),
            {'rating': '5', 'subject': 'Review', 'review': 'review'}
        )
