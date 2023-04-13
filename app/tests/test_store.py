"""
Tests for store app.
"""
import pytest
from pytest_django.asserts import assertContains, assertJSONEqual

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

        product.image.delete()

    def test_submit_review(self, payment_success_login):
        """Test submit review on product."""
        client = payment_success_login[0]
        response = client.post(
            reverse('store:submit-review', kwargs={'product_id': 2}),
            {'rating': '5.0', 'subject': 'Review', 'review': 'It is nice product!'},
            HTTP_REFERER=reverse('store:product-detail', args=['test', 'Jacket'])
        )

        review = Product.objects.get(pk=2).review.first()

        assert response.status_code == 302
        assert review.subject == 'Review'
        assert review.rating == 5.0
        assert review.review == 'It is nice product!'

    def test_add_remove_to_wishlist(self, client_user_login, product):
        """Test add and remove to wishlist."""
        product = product(name='Jacket')
        response = client_user_login.post(reverse('store:add-wishlist'), {'product': product.id})

        # Test add to wishlist
        assert response.status_code == 200
        assertJSONEqual(str(response.content, encoding='utf8'), {'bool': True})

        # Test remove from wishlist
        response = client_user_login.post(reverse('store:add-wishlist'), {'product': product.id})
        assert response.status_code == 200
        assertJSONEqual(str(response.content, encoding='utf8'), {'bool': False})

        product.image.delete()

    def test_wishlist(self, client_user_login, product):
        """Test WishListView."""
        product = product(name='Jacket')
        client_user_login.post(reverse('store:add-wishlist'), {'product': product.id})

        response = client_user_login.get(reverse('store:my-wishlist'))
        assert response.status_code == 200
        assertContains(response, product.name)

        product.image.delete()
