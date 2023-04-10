"""
Pytest fixtures for tests.
"""
import pytest

from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from category.models import Category
from store.models import Product, Variation


pytest_plugins = ("celery.contrib.pytest", )


@pytest.fixture
def create_user(db, django_user_model):
    def make_user(**kwargs):
        if 'password' not in kwargs:
            kwargs['password'] = 'strong-test-pass12'
        if 'username' not in kwargs:
            kwargs['username'] = 'dmytrotest'
        if 'email' not in kwargs:
            kwargs['email'] = 'test12@example.com'
        if 'first_name' not in kwargs:
            kwargs['first_name'] = 'test'
        if 'last_name' not in kwargs:
            kwargs['last_name'] = 'test'

        return django_user_model.objects.create_user(**kwargs)

    return make_user


@pytest.fixture
def client_user(client, create_user):
    user = create_user()
    user.is_active = True
    user.save()

    return client


@pytest.fixture
def client_user_login(client, create_user):
    user = create_user()
    user.is_active = True
    user.save()
    client.force_login(user)

    return client


@pytest.fixture
def category(db):
    category = Category.objects.create(
        name='test', slug='test', description='test description'
    )

    return category


@pytest.fixture
def product(db, category, image_for_test):
    def make_product(**kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = 'Test Jeans'

        kwargs['slug'] = '-'.join(kwargs['name'].lower().split(' '))
        kwargs.update(
            description='Test Jeans description', price=25,
            stock=25, category=category, image=image_for_test
        )

        product = Product.objects.create(**kwargs)
        Variation.objects.create(product=product, category='color', value='Red')

        return product

    return make_product


@pytest.fixture
def cart_products(db, product, client, request):
    try:
        product = product(name=request.param)
        client.post(reverse('carts:add-cart', args=[product.id]), {'color': 'Red'})
        yield client

        product.image.delete()
    except AttributeError:
        products = [product(name='Coat'), product(name='Jacket'), product(name='Shirt')]
        for i in products:
            client.post(reverse('carts:add-cart', args=[i.id]), {'color': 'Red'})

        yield client

        for i in products:
            i.image.delete()


@pytest.fixture
def image_for_test():
    image = Image.new('RGB', (300, 300), color='red')
    image_file = SimpleUploadedFile('red_image.png', image.tobytes(), content_type='image/png')

    return image_file


@pytest.fixture(scope='session')
def celery_config():
    return {
        "broker_url": "memory://",
        "result_backend": "cache+memory://",
        'task_always_eager': True,
    }

