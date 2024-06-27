# supplier/forms.py
from django import forms
from django.contrib.auth.models import User
from .models import Supplier

class SupplierForm(forms.ModelForm):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Supplier
        fields = ['name', 'contact_number', 'address']

    def save(self, commit=True):
        supplier = super().save(commit=False)
        email = self.cleaned_data['email']
        password = self.cleaned_data['password']

        if commit:
            user = User.objects.create_user(username=email, email=email, password=password)
            supplier.user = user
            supplier.status = 'active'  # Set the default status
            supplier.save()
        return supplier


class SupplierLoginForm(forms.Form):
    email = forms.EmailField(label='Email')
    password = forms.CharField(label='Password', widget=forms.PasswordInput)