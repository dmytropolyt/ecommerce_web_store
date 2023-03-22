"""
Tests for:
custom user model, email activation, Profile model.
"""
import pytest

from django.contrib.auth import get_user_model


User = get_user_model()


@pytest.mark.django_db
class TestUser:
    data = {
        'email': 'test@example.com',
        'username': 'testuser',
        'first_name': 'test',
        'last_name': 'test',
        'password': 'testpassword12',
    }

    def test_create_user(self):
        User.objects.create_user(**self.data)
        user = User.objects.get(email=self.data['email'])
        assert User.objects.count() == 1
        assert user.username == self.data['username']
        assert user.first_name == self.data['first_name']
        assert user.last_name == self.data['last_name']
        assert user.is_active is False
        assert user.is_staff is False
        assert user.is_admin is False
        assert user.is_superadmin is False

    def test_create_superuser(self):
        User.objects.create_superuser(**self.data)
        user = User.objects.get(email=self.data['email'])
        assert User.objects.count() == 1
        assert user.username == self.data['username']
        assert user.first_name == self.data['first_name']
        assert user.last_name == self.data['last_name']
        assert user.is_active is True
        assert user.is_staff is True
        assert user.is_admin is True
        assert user.is_superadmin is True
