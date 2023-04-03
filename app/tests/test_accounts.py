"""
Tests for accounts app.
"""
import pytest

from django.urls import reverse

from accounts.tasks import send_activation_email


@pytest.mark.django_db
class TestAccounts:

    @pytest.mark.celery(result_backend='rpc')
    def test_register(self, client, django_user_model, mailoutbox, celery_worker, celery_app):
        """Test user registration, email activation."""
        url = reverse('register')
        response = client.get(url)
        assert response.status_code == 200

        payload = {
            'username': "test1",
            'first_name': "test",
            'last_name': "test",
            'email': "dmyt@example.com",
            'phone_number':	"+380666666666",
            'password1': "testpass12",
            'password2': "testpass12",
        }
        response = client.post('/accounts/register/', payload)

        assert response.status_code == 302
        send_activation_email.delay('subject', 'rap', 'test@example.com')
        print(mailoutbox)
        mail = mailoutbox[0]
        assert mail.subject == 'Please activate your account.'
        assert list(mail.to) == [payload['email']]

        new_user = django_user_model.objects.filter(email=payload['email']).first()
        assert new_user.email == payload['email']
        assert new_user.username == payload['username']
        assert new_user.is_active is False

        uid = response.context['uid']
        token = response.context['token']
        response = client.get(reverse('activate', args=[uid, token]))
        assert response.status_code == 302
        new_user = django_user_model.objects.filter(email=payload['email']).first()
        assert new_user.is_active is True

    def test_login(self, client_user, django_user_model):
        """Test login view."""
        url = reverse('login')
        response = client_user.get(url)

        assert response.status_code == 200

        response = client_user.post(url, {'email': 'test12@example.com', 'password': 'strong-test-pass12'})

        assert response.status_code == 302
        assert response.url == '/accounts/'

    def test_logout(self, client_user_login):
        """Test logout view."""
        response = client_user_login.get(reverse('logout'))

        assert response.status_code == 302
        assert response.url == reverse('login')


