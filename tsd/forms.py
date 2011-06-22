from django import forms
from django.forms import fields

from tsd.models import Customer, Order

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
