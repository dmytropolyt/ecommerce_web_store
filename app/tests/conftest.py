"""
Pytest fixtures for tests.
"""
import pytest


@pytest.fixture
def create_user(db, django_user_model):
    def make_user(**kwargs):
        kwargs['password'] = 'strong-test-pass'
        if 'username' not in kwargs:
            kwargs['username'] = 'dmytrotest'
        if 'email' not in kwargs:
            kwargs['email'] = 'test@example.com'
        return django_user_model.objects.create_user(**kwargs)

    return make_user
