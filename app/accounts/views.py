from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import View, CreateView, TemplateView
from django.contrib.auth.views import PasswordResetConfirmView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.contrib import messages, auth
from .forms import RegistrationForm, ChangePasswordForm

from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

from carts.models import Cart, CartItem
from carts.views import _cart_id
import requests


User = get_user_model()


class RegisterView(CreateView):
    """View for register user and send him a verification email."""
    form_class = RegistrationForm
    template_name = 'accounts/register.html'

    def form_valid(self, form):
        user = form.save(commit=False)

        user.save()

        # User activation
        current_site = get_current_site(self.request)
        mail_subject = 'Please activate your account.'
        message = render_to_string('accounts/account_verification_email.html', {
            'user': user,
            'domain': current_site,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': default_token_generator.make_token(user),
        })
        to_email = user.email
        send_mail = EmailMessage(mail_subject, message, to=[to_email])
        send_mail.send()
        # messages.success(self.request, 'Thank you for registering.'
        #                                'We have sent you a verification email to your email address.'
        #                                'Please verify your email.'
        #                  )

        return redirect('/accounts/login/?command=verification&email='+to_email)


class LoginView(View):
    """View for logging in user."""

    def get(self, request, *args, **kwargs):
        return render(request, 'accounts/login.html')

    def post(self, request, *args, **kwargs):
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)

                    # Getting the product variations by cart id
                    product_variation = [list(item.variations.all()) for item in cart_item]

                    # Get the cart items from the user to access his product variations
                    cart_item = CartItem.objects.filter(user=user)

                    ex_var_list, id_list = [], []
                    for item in cart_item:
                        existing_variation = item.variations.all()
                        ex_var_list.append(list(existing_variation))
                        id_list.append(item.id)

                    for product in product_variation:
                        if product in ex_var_list:
                            index = ex_var_list.index(product)
                            item_id = id_list[index]
                            item = Cart.objects.get(id=item_id)
                            item.quantity += 1
                            item.user = user
                            item.save()
                        else:
                            cart_item = CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                item.user = user
                                item.save()
            except:
                pass

            auth.login(request, user)
            messages.success(request, 'You are now logged in.')

            try:
                url = requests.META.get('HTTP_REFERER')
                query = requests.utils.urlparse(url).query
                params = dict(x.split('-') for x in query.split('g'))
                if 'next' in params:
                    next_page = params['next']
                    return redirect(next_page)
            except:
                return redirect('dashboard')

        else:
            messages.error(request, 'Invalid login credentials')
            return redirect('login')


class LogoutView(LoginRequiredMixin, View):
    """View for process user log out."""

    def get(self, request, *args, **kwargs):
        auth.logout(request)
        messages.success(request, 'You are logged out!')
        return redirect('login')


class ActivateView(View):
    """View for activate user by email."""

    def get(self, request, token, *args, **kwargs):
        try:
            uid = urlsafe_base64_decode(kwargs['uidb64']).decode()
            user = User.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            messages.success(request, 'Your account is activated!')

            return redirect('login')
        else:
            print(default_token_generator.check_token(user, token))
            messages.error(request, 'Invalid activation link.')

            return redirect('register')


class DashboardView(LoginRequiredMixin, TemplateView):
    """View for user's dashboard."""
    template_name = 'accounts/dashboard.html'


class AccountPasswordResetView(TemplateView):
    template_name = 'accounts/password_reset.html'

    # def get(self, request, *args, **kwargs):
    #     return render('acccount/password_reset.html')

    def post(self, request, *args, **kwargs):
        email = request.POST['email']
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email__iexact=email)

            current_site = get_current_site(self.request)
            mail_subject = 'Reset Your Password.'
            message = render_to_string('accounts/password_reset_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = user.email
            send_mail = EmailMessage(mail_subject, message, to=[to_email])
            send_mail.send()

            messages.success(request, 'Password reset email has been sent to your email address.')

            return redirect('login')
        else:
            messages.error(request, 'Account does not exist.')

            return redirect('password-reset')


class AccountPasswordResetConfirmView(PasswordResetConfirmView):
    """View for reset user's password by email link."""
    form_class = ChangePasswordForm
    success_url = reverse_lazy('login')
    template_name = 'accounts/password_reset_confirm.html'

    def form_valid(self, form):
        messages.success(self.request, 'Password reset successful!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Passwords do not match!')
        return super().form_invalid(form)
