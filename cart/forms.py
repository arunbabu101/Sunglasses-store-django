from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

def validate_phone(value):
    if not (len(str(value)) == 10):
        raise ValidationError("Phone number must be 10 digits.")

class DeliveryForm(forms.Form):
    name = forms.CharField(label='Your Name', max_length=100)
    address = forms.CharField(label='Delivery Address', max_length=500)
    phone = forms.IntegerField(label='Phone Number', validators=[validate_phone])
    email = forms.EmailField(label='Email Address')
    payment_method = forms.ChoiceField(
        label='Payment Method',
        choices=[('credit_card', 'Credit Card'), ('paypal', 'PayPal'), ('Debit_card', 'Debitcard'), ('Cod', 'COD')]
    )
