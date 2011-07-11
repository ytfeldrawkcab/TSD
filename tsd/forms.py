from django import forms
from django.forms import fields

from tsd.models import Customer, Order, Group, OrderStyle, OrderSize, StyleSize, OrderImprint, GroupSetup

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        widgets = {
            'customer':forms.HiddenInput()
        }
    def __init__(self, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)
        self.fields['groupcount'] = forms.IntegerField(initial=0, widget=forms.HiddenInput())
        self.fields['stylecount'] = forms.IntegerField(initial=0, widget=forms.HiddenInput())
        self.fields['sizecount'] = forms.IntegerField(initial=0, widget=forms.HiddenInput())
        self.fields['imprintcount'] = forms.IntegerField(initial=0, widget=forms.HiddenInput())
        self.fields['setupcount'] = forms.IntegerField(initial=0, widget=forms.HiddenInput())
        self.fields['pk'] = forms.IntegerField(required=False, initial=self.instance.pk, widget=forms.HiddenInput())
        self.fields['delete'] = forms.IntegerField(initial=0, widget=forms.HiddenInput())
        
class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        exclude = ('order',)
    def __init__(self, *args, **kwargs):
        super(GroupForm, self).__init__(*args, **kwargs)
        self.fields['name'] = forms.CharField(widget=forms.TextInput(attrs={'class':'groupname', 'onchange':"changegroupname('" + self.prefix + "', this.value)"}))
        self.fields['pk'] = forms.IntegerField(required=False, initial=self.instance.pk, widget=forms.HiddenInput())
        self.fields['delete'] = forms.IntegerField(initial=0, widget=forms.HiddenInput())
        
class OrderStyleForm(forms.ModelForm):
    class Meta:
        model = OrderStyle
        exclude = ('group','order')
        widgets = {
            'style':forms.HiddenInput(),
        }
    def __init__(self, *args, **kwargs):
        super(OrderStyleForm, self).__init__(*args, **kwargs)
        self.fields['parentprefix'] = forms.CharField(required=False, widget=forms.HiddenInput())
        self.fields['pk'] = forms.IntegerField(required=False, initial=self.instance.pk, widget=forms.HiddenInput())
        self.fields['delete'] = forms.IntegerField(initial=0, widget=forms.HiddenInput())
        
class OrderSizeForm(forms.ModelForm):
    class Meta:
        model = OrderSize
        exclude = ('orderstyle',)
        widgets = {
            'stylesize':forms.HiddenInput(),
        }
    def __init__(self, *args, **kwargs):
        super(OrderSizeForm, self).__init__(*args, **kwargs)
        self.fields['parentprefix'] = forms.CharField(widget=forms.HiddenInput())
        self.fields['pk'] = forms.IntegerField(required=False, initial=self.instance.pk, widget=forms.HiddenInput())
        
class OrderImprintForm(forms.ModelForm):
    class Meta:
        model = OrderImprint
        exclude = ('order',)
    def __init__(self, *args, **kwargs):
        super(OrderImprintForm, self).__init__(*args, **kwargs)
        self.fields['pk'] = forms.IntegerField(required=False, initial=self.instance.pk, widget=forms.HiddenInput())
        self.fields['delete'] = forms.IntegerField(initial=0, widget=forms.HiddenInput())
        self.fields['specify'] = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class':'specify', 'onchange':"togglesetups('" + self.prefix + "')"}))

class GroupSetupForm(forms.ModelForm):
    class Meta:
        model = GroupSetup
        exclude = ('group','orderimprint')
    def __init__(self, *args, **kwargs):
        super(GroupSetupForm, self).__init__(*args, **kwargs)
        self.fields['parentprefix'] = forms.CharField(widget=forms.HiddenInput())
        self.fields['groupprefix'] = forms.ChoiceField(choices=[('','---------')], widget=forms.Select(attrs={'class':'grouplist'}))
        self.fields['pk'] = forms.IntegerField(required=False, initial=self.instance.pk, widget=forms.HiddenInput())
        self.fields['delete'] = forms.IntegerField(initial=0, widget=forms.HiddenInput())
