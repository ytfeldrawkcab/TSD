from django import forms
from django.forms import fields

from tsd.models import Customer, Order, Group, OrderStyle

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        widgets = {
            'pk':forms.HiddenInput(),
        }
        
class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        widgets = {
            'order':forms.HiddenInput(),
        }
        
class OrderStyleForm(forms.ModelForm):
    class Meta:
        model = OrderStyle
        widgets = {
            'group':forms.HiddenInput(),
        }
