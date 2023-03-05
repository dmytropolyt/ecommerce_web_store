from django import forms
from django.contrib.auth.forms import UserCreationForm, SetPasswordForm
from .models import Account


class RegistrationForm(UserCreationForm):
    """Form to register user."""
    password1 = forms.CharField(strip=False, widget=forms.PasswordInput(attrs={
        'autocomplete': 'new-password',
        'placeholder': 'Enter Password',
    }))
    password2 = forms.CharField(strip=False, widget=forms.PasswordInput(attrs={
        'autocomplete': 'new-password',
        'placeholder': 'Confirm Password',
    }))

    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'phone_number', 'email', 'username', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['placeholder'] = 'Enter First Name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Enter Last Name'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'Enter Phone Number'
        self.fields['email'].widget.attrs['placeholder'] = 'Enter Your Email'
        self.fields['username'].widget.attrs['placeholder'] = 'Enter Your Username'
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'


class ChangePasswordForm(SetPasswordForm):
    """Form to change user's password."""

    def __init__(self, user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)
        self.fields['new_password1'].widget.attrs['placeholder'] = 'Create Password'
        self.fields['new_password2'].widget.attrs['placeholder'] = 'Confirm Password'
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'