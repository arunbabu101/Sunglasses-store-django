from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from .models import *

def validate_phone(value):
    if not (len(str(value)) == 10):
        raise ValidationError("Phone number must be 10 digits.")

class DeliveryForm(forms.Form):
    first_name = forms.CharField(max_length=100, label='First Name')
    last_name = forms.CharField(max_length=100, label='Last Name')
    email = forms.EmailField(label='Email Address')
    phone_number = forms.CharField(max_length=15, label='Phone Number')
    street_address = forms.CharField(max_length=255, label='Street Address')
    city = forms.CharField(max_length=100, label='City')
    postal_code = forms.CharField(max_length=20, label='Postal Code')
    country = forms.CharField(max_length=100, label='Country')


class ReturnForm(forms.ModelForm):
    class Meta:
        model = Return
        fields = ['reason']
        widgets = {
            'reason': forms.Textarea(attrs={'rows': 4, 'cols': 40}),
        }