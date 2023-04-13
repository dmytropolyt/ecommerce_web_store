"""
Tests for accounts app.
"""
import pytest
from pytest_django.asserts import assertContains

from django.urls import reverse
# from django.core.files.uploadedfile import SimpleUploadedFile
# from PIL import Image

from orders.models import Order


@pytest.mark.django_db
class TestAccounts:

    def test_register_and_activation(self, client, django_user_model, mailoutbox, celery_session_worker):
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

    def test_password_reset(self, django_user_model, client_user, mailoutbox):
        """Test user reset password view."""
        url = reverse('password-reset')
        response = client_user.get(url)
        # Test GET request
        assert response.status_code == 200

        response = client_user.post(reverse('password-reset'), {'email': 'test12@example.com'})
        mail = mailoutbox[0]
        # print(mailoutbox[1].subject, mailoutbox[2].subject)
        user = django_user_model.objects.get(email='test12@example.com')
        # Test POST request
        assert response.status_code == 302
        # assert len(mailoutbox) == 1
        assert mail.subject == 'Reset Your Password.'
        assert list(mail.to) == ['test12@example.com']
        assert user.email == 'test12@example.com'

        uid = response.context['uid']
        token = response.context['token']
        response = client_user.get(reverse('password-reset-confirm', args=[uid, token]))
        # Test reset password url
        assert response.status_code == 302

        response = client_user.post(
            reverse('password-reset-confirm', args=[uid, 'set-password']),
            {'new_password1': 'test-pass12q', 'new_password2': 'test-pass12q'}
        )
        # Test password change
        assert response.status_code == 302
        assert response.url == reverse('login')

        client_user.login(email='test12@example.com', password='test-pass12q')
        response = client_user.get(reverse('dashboard'))
        # Test login user with new password
        assert response.status_code == 200
        # Test login with old password
        client_user.logout()
        client_user.login(username='dmytrotest', password='strong-test-pass12')
        response = client_user.get(reverse('dashboard'))

        assert response.status_code == 302

    def test_change_password(self, client, client_user_login):
        """Test change user's password."""
        url = reverse('change-password')
        response = client_user_login.get(url)
        # Test when user is logged in
        assert response.status_code == 200

        response = client_user_login.post(
            url,
            {
                'old_password': 'strong-test-pass12',
                'new_password1': 'test-pass12q',
                'new_password2': 'test-pass12q'
            }
        )
        # Test change password
        assert response.status_code == 302

        client_user_login.logout()
        client.login(email='test12@example.com', password='test-pass12q')
        response = client.get(reverse('dashboard'))
        # Test login and login required url with new password
        assert response.status_code == 200

    def test_edit_profile(self, client_user_login, django_user_model):
        """Test edit profile view."""
        url = reverse('edit-profile')
        response = client_user_login.get(url)
        # Test get request
        assert response.status_code == 200

        # image = Image.new('RGB', (300, 300), color='red')
        #
        # image_file = SimpleUploadedFile('red_image.png', image.tobytes(), content_type='image/png')
        payload = {
            'first_name': 'Testuser',
            'last_name': 'Testuser',
            'phone_number': '+38096 480 8677',
            # 'picture': image_file,
            'address_line_1': 'street Test',
            'address_line_2': '2',
            'city': 'Testcity',
            'state': 'Teststate'
        }

        response = client_user_login.post(url, payload, follow=True)
        # Test post request
        assert response.status_code == 200
        for value in payload.values():
            assertContains(response, value)

    def test_my_orders(self, payment_success_login):
        """Test my orders view."""
        client = payment_success_login[0]
        response = client.get(reverse('my-orders'))
        order_number = Order.objects.get(pk=1).order_number

        assert response.status_code == 200
        assertContains(response, order_number)

    def test_order_detail(self, payment_success_login):
        """Test order detail view."""
        client = payment_success_login[0]
        order = Order.objects.get(pk=1)
        response = client.get(reverse('order-detail', args=[order.order_number]))

        assert response.status_code == 200
        assertContains(response, order.order_number)
        assertContains(response, order.payment.status)
        assertContains(response, 'Coat')
        assertContains(response, 'Jacket')
