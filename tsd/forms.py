from django import forms
from django.forms import fields

from tsd.models import Customer, Order, Group, OrderStyle, OrderSize

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
    def __init__(self, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)
        self.fields['groupcount'] = forms.IntegerField(initial=0, widget=forms.HiddenInput())
        
class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        widgets = {
            'order':forms.HiddenInput(),
        }
    def __init__(self, *args, **kwargs):
        super(GroupForm, self).__init__(*args, **kwargs)
        self.fields['stylecount'] = forms.IntegerField(initial=0, widget=forms.HiddenInput())
        
class OrderStyleForm(forms.ModelForm):
    class Meta:
        model = OrderStyle
        widgets = {
            'group':forms.HiddenInput(),
            'style':forms.HiddenInput(),
        }
    def __init__(self, *args, **kwargs):
        super(OrderStyleForm, self).__init__(*args, **kwargs)
        self.fields['sizecount'] = forms.IntegerField(widget=forms.HiddenInput())
        
class OrderSizeForm(forms.ModelForm):
    class Meta:
        model = OrderSize
        widgets = {
            'orderstyle':forms.HiddenInput(),
            'stylesize':forms.HiddenInput(),
        }
