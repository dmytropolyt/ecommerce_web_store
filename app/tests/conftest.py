"""
Pytest fixtures for tests.
"""
import pytest

from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
import base64
import json

from category.models import Category
from store.models import Product, Variation
from orders.models import Order


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
def cart_products_login(db, product, client_user_login):
    products = [product(name='Coat'), product(name='Jacket'), product(name='Shirt')]
    client = client_user_login
    for i in products:
        client.post(reverse('carts:add-cart', args=[i.id]), {'color': 'Red'})

    yield client

    for i in products:
        i.image.delete()


@pytest.fixture
def place_order(db, cart_products):
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
    client.post(reverse('orders:place-order'), payload)

    return client


@pytest.fixture
def place_order_login(db, cart_products_login):
    client = cart_products_login
    payload = {
        'first_name': 'test',
        'last_name': 'test',
        'email': 'test12@example.com',
        'phone': '+380967899090',
        'address_line_1': 'street Test',
        'city': 'Kyiv',
        'state': 'Kyiv',
    }
    client.post(reverse('orders:place-order'), payload)

    return client


@pytest.fixture
def payment_success(db, place_order):
    client = place_order
    order_number = Order.objects.get(pk=1).order_number
    data = {
        'payment_id': 2277196704, 'status': 'success',
        'paytype': 'privat24', 'order_id': order_number,
        'info': 1
    }

    data = base64.b64encode(json.dumps(data).encode("utf-8")).decode("ascii")
    response = client.post(reverse('orders:payments'), {'data': data})

    return [client, response]


@pytest.fixture
def payment_success_login(db, place_order_login):
    client = place_order_login
    order_number = Order.objects.get(pk=1).order_number
    data = {
        'payment_id': 2277196704, 'status': 'success',
        'paytype': 'privat24', 'order_id': order_number,
    }

    data = base64.b64encode(json.dumps(data).encode("utf-8")).decode("ascii")
    response = client.post(reverse('orders:payments'), {'data': data})

    return [client, response]


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
