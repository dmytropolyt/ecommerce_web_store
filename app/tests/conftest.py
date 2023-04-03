"""
Pytest fixtures for tests.
"""
import pytest


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


@pytest.fixture(scope='session')
def celery_enable_logging():
    return True


# @pytest.fixture(scope='session')
# def celery_includes():
#     return [
#         'app.accounts.tasks',
#         'app.orders.tasks',
#     ]
# @pytest.fixture(scope='session')
# def celery_app(request):
#     from celery import Celery
#     app = Celery('app')
#     app.config_from_object('django.conf:settings', namespace='CELERY')
#     app.autodiscover_tasks()
#
#     return app

