from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import View, CreateView, TemplateView, ListView, DetailView
from django.contrib.auth.views import PasswordResetConfirmView, PasswordChangeView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.contrib import messages, auth
from .forms import RegistrationForm, ForgotPasswordForm, EditUserForm, EditUserProfileForm, ChangePasswordForm
from .models import UserProfile
from .tasks import send_activation_email

from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

from carts.models import Cart, CartItem
from orders.models import Order, OrderProduct
from carts.views import _cart_id
from functools import reduce
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
        send_activation_email.delay(mail_subject, message, to_email)
        # send_mail = EmailMessage(mail_subject, message, to=[to_email])
        # send_mail.send()
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['orders'] = Order.objects.order_by('-created_at').filter(
            user=self.request.user, is_ordered=True
        )
        context['userprofile'] = UserProfile.objects.get(user=self.request.user)
        return context


class UserOrdersView(LoginRequiredMixin, ListView):
    template_name = 'accounts/my_orders.html'
    context_object_name = 'orders'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user, is_ordered=True).order_by('-created_at')


class EditProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/edit_profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_form'] = EditUserForm(instance=self.request.user)
        context['userprofile'] = get_object_or_404(UserProfile, user=self.request.user)
        context['profile_form'] = EditUserProfileForm(instance=context['userprofile'])
        return context

    def post(self, request, *args, **kwargs):
        userprofile = self.get_context_data()['userprofile']
        user_form = EditUserForm(request.POST, instance=request.user)
        profile_form = EditUserProfileForm(request.POST, request.FILES, instance=userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('edit-profile')


class ChangePasswordView(PasswordChangeView):
    template_name = 'accounts/change_password.html'
    form_class = ChangePasswordForm
    success_url = reverse_lazy('change-password')

    def form_valid(self, form):
        messages.success(self.request, 'Password updated successfully.')
        return super().form_valid(form)


class OrderDetailView(LoginRequiredMixin, DetailView):
    queryset = Order.objects.all()
    template_name = 'accounts/order_detail.html'
    pk_url_kwarg = 'order_id'
    context_object_name = 'order'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['sub_total'] = reduce(
            lambda a, b: a+b, [i.product_price * i.quantity for i in context['order'].order_product.all()]
        )

        return context

    def get_object(self, queryset=None):
        return self.queryset.get(order_number=self.kwargs.get(self.pk_url_kwarg))


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
    form_class = ForgotPasswordForm
    success_url = reverse_lazy('login')
    template_name = 'accounts/password_reset_confirm.html'

    def form_valid(self, form):
        messages.success(self.request, 'Password reset successful!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Passwords do not match!')
        return super().form_invalid(form)
