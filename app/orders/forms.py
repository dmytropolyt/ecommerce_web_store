from django import forms
from .models import Order


class OrderForm(forms.ModelForm):

    class Meta:
        model = Order
        fields = [
            'first_name', 'last_name', 'phone', 'email',
            'address_line_1', 'address_line_2',
            'state', 'city', 'order_note'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
            if field != 'address_line_2':
                self.fields[field].widget.attrs['required'] = 'required'

        self.fields['phone'].widget.attrs['id'] = 'id_phone_number'
