from django import forms
from django.contrib.auth.forms import UserCreationForm, SetPasswordForm, PasswordChangeForm
from .models import Account, UserProfile

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


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


class ForgotPasswordForm(SetPasswordForm):
    """
    Form to change user's password if he forgot it.
    By email.
    """

    def __init__(self, user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)
        self.fields['new_password1'].widget.attrs['placeholder'] = 'Create Password'
        self.fields['new_password2'].widget.attrs['placeholder'] = 'Confirm Password'
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'


class ChangePasswordForm(ForgotPasswordForm):
    """Form to change user's password."""
    error_messages = {
        **SetPasswordForm.error_messages,
        "password_incorrect": _(
            "Your old password was entered incorrectly. Please enter it again."
        ),
    }
    old_password = forms.CharField(
        label=_("Current password"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "current-password", "autofocus": True,
                "placeholder": "Current password"
            }
        ),
    )

    field_order = ["old_password", "new_password1", "new_password2"]

    def clean_old_password(self):
        """
        Validate that the old_password field is correct.
        """
        old_password = self.cleaned_data["old_password"]
        if not self.user.check_password(old_password):
            raise ValidationError(
                self.error_messages["password_incorrect"],
                code="password_incorrect",
            )
        return old_password


class EditUserForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ('first_name', 'last_name', 'phone_number')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'


class EditUserProfileForm(forms.ModelForm):
    picture = forms.ImageField(
        required=False, error_messages={'invalid': ('Image files only')}, widget=forms.FileInput
    )

    class Meta:
        model = UserProfile
        fields = ('address_line_1', 'address_line_2', 'city', 'state', 'picture')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
