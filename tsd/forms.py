from django import forms
from django.forms import fields
from django.core import exceptions
from tsd.models import *
import types

def auto_error_class(field, error_class="error"):
    """
       Monkey-patch a Field instance at runtime in order to automatically add a CSS
       class to its widget when validation fails and provide any associated error
       messages via a data attribute
    """

    inner_clean = field.clean

    def wrap_clean(self, *args, **kwargs):
       try:
           return inner_clean(*args, **kwargs)
       except exceptions.ValidationError as ex:
           self.widget.attrs["class"] = self.widget.attrs.get(
               "class", ""
           ) + " " + error_class
           self.widget.attrs["title"] = ", ".join(ex.messages)
           raise ex

    field.clean = types.MethodType(wrap_clean, field, field.__class__)

    return field

#customer management forms
class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        exclude = ('defaultmaincontact', 'defaultshippingcontact', 'defaultbillingcontact', 'defaultshippingaddress', 'defaultbillingaddress')
    def __init__(self, *args, **kwargs):
        super(CustomerForm, self).__init__(*args, **kwargs)
        self.fields['pk'] = forms.IntegerField(required=False, initial=self.instance.pk, widget=forms.HiddenInput())
        self.fields['contactcount'] = forms.IntegerField(initial=0, widget=forms.HiddenInput())
        self.fields['addresscount'] = forms.IntegerField(initial=0, widget=forms.HiddenInput())
        self.fields['maincontactprefix'] = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'mainicon icon contacticon', 'readonly':'readonly'}))
        self.fields['shippingcontactprefix'] = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'shippingicon icon contacticon', 'readonly':'readonly'}))
        self.fields['billingcontactprefix'] = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'billingicon icon contacticon', 'readonly':'readonly'}))
        self.fields['shippingaddressprefix'] = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'shippingicon icon addressicon', 'readonly':'readonly'}))
        self.fields['billingaddressprefix'] = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'billingicon icon addressicon', 'readonly':'readonly'}))
        for f in self.fields:
            self.fields[f] = auto_error_class(self.fields[f])

class CustomerContactForm(forms.ModelForm):
    class Meta:
        model = CustomerContact
        exclude = ('customer',)
    def __init__(self, *args, **kwargs):
        super(CustomerContactForm, self).__init__(*args, **kwargs)
        self.fields['pk'] = forms.IntegerField(required=False, initial=self.instance.pk, widget=forms.HiddenInput())
        self.fields['delete'] = forms.IntegerField(initial=0, widget=forms.HiddenInput())
        for f in self.fields:
            self.fields[f] = auto_error_class(self.fields[f])

class CustomerAddressForm(forms.ModelForm):
    class Meta:
        model = CustomerAddress
        exclude = ('customer',)
    def __init__(self, *args, **kwargs):
        super(CustomerAddressForm, self).__init__(*args, **kwargs)
        self.fields['pk'] = forms.IntegerField(required=False, initial=self.instance.pk, widget=forms.HiddenInput())
        self.fields['delete'] = forms.IntegerField(initial=0, widget=forms.HiddenInput())
        for f in self.fields:
            self.fields[f] = auto_error_class(self.fields[f])

#order management forms
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
        self.fields['groupimprintcount'] = forms.IntegerField(initial=0, widget=forms.HiddenInput())
        self.fields['servicecount'] = forms.IntegerField(initial=0, widget=forms.HiddenInput())
        self.fields['groupservicecount'] = forms.IntegerField(initial=0, widget=forms.HiddenInput())
        self.fields['pk'] = forms.IntegerField(required=False, initial=self.instance.pk, widget=forms.HiddenInput())
        self.fields['delete'] = forms.IntegerField(initial=0, widget=forms.HiddenInput())
        for f in self.fields:
            self.fields[f] = auto_error_class(self.fields[f])
        
class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        exclude = ('order',)
    def __init__(self, *args, **kwargs):
        super(GroupForm, self).__init__(*args, **kwargs)
        self.fields['name'] = forms.CharField(widget=forms.TextInput(attrs={'class':'groupname', 'onchange':"changegroupname('" + self.prefix + "', this.value)"}))
        self.fields['pk'] = forms.IntegerField(required=False, initial=self.instance.pk, widget=forms.HiddenInput())
        self.fields['delete'] = forms.IntegerField(initial=0, widget=forms.HiddenInput())
        for f in self.fields:
            self.fields[f] = auto_error_class(self.fields[f])
        
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
        self.fields['label'] = forms.CharField(widget=forms.HiddenInput())
        if self.instance.garmentdyecolor:
            colorlabel = self.instance.garmentdyecolor
        else:
            colorlabel = self.instance.piecedyecolor
        self.fields['colorlabel'] = forms.CharField(max_length=50, initial=colorlabel, widget=forms.TextInput(attrs={'class':'labelinput pointer', 'readonly':'readonly'}))
        self.fields['styleprice'].widget = forms.HiddenInput()
        self.fields['garmentdyecolor'].widget = forms.HiddenInput()
        self.fields['piecedyecolor'].widget = forms.HiddenInput()
        for f in self.fields:
            self.fields[f] = auto_error_class(self.fields[f])
        
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
        self.fields['quantity'].widget.attrs['class'] = 'digit'
        self.fields['label'] = forms.CharField(widget=forms.HiddenInput())
        for f in self.fields:
            self.fields[f] = auto_error_class(self.fields[f])
        
class OrderImprintForm(forms.ModelForm):
    class Meta:
        model = OrderImprint
        exclude = ('order',)
    def __init__(self, *args, **kwargs):
        super(OrderImprintForm, self).__init__(*args, **kwargs)
        self.fields['pk'] = forms.IntegerField(required=False, initial=self.instance.pk, widget=forms.HiddenInput())
        self.fields['delete'] = forms.IntegerField(initial=0, widget=forms.HiddenInput())
        self.fields['specify'] = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class':'specify', 'onchange':"togglegroups('" + self.prefix + "')"}))
        self.fields['colorcount'].widget.attrs['class'] = 'digit'
        self.fields['imprint'].widget = forms.HiddenInput()
        self.fields['setup'].widget = forms.HiddenInput()
        self.fields['imprintname'] = forms.CharField(required=False, widget=forms.HiddenInput())
        self.fields['setupname'] = forms.CharField(required=False, widget=forms.HiddenInput())
        for f in self.fields:
            self.fields[f] = auto_error_class(self.fields[f])

class GroupImprintForm(forms.ModelForm):
    class Meta:
        model = GroupImprint
        exclude = ('group','orderimprint')
    def __init__(self, *args, **kwargs):
        super(GroupImprintForm, self).__init__(*args, **kwargs)
        self.fields['exists'] = forms.BooleanField(required=False)
        self.fields['parentprefix'] = forms.CharField(widget=forms.HiddenInput())
        self.fields['groupprefix'] = forms.CharField(widget=forms.HiddenInput())
        self.fields['pk'] = forms.IntegerField(required=False, initial=self.instance.pk, widget=forms.HiddenInput())
        self.fields['groupname'] = forms.CharField(widget=forms.HiddenInput(attrs={'class':'groupnameinput'}))
        for f in self.fields:
            self.fields[f] = auto_error_class(self.fields[f])
        
class OrderServiceForm(forms.ModelForm):
    class Meta:
        model = OrderService
        exclude = ('order')
    def __init__(self, *args, **kwargs):
        super(OrderServiceForm, self).__init__(*args, **kwargs)
        self.fields['pk'] = forms.IntegerField(required=False, initial=self.instance.pk, widget=forms.HiddenInput())
        self.fields['delete'] = forms.IntegerField(initial=0, widget=forms.HiddenInput())
        self.fields['service'].widget = forms.HiddenInput()
        self.fields['quantity'].widget.attrs['class'] = 'digit'
        self.fields['specify'].widget.attrs['onChange'] = "togglegroups('" + self.prefix + "')"
        self.fields['specify'].widget.attrs['class'] = 'specify'
        self.fields['label'] = forms.CharField(required=False, widget=forms.HiddenInput())
        if self.instance.pk:
            if self.instance.service.enteredquantity == True:
                self.fields['specify'].widget.attrs['disabled'] = 'disabled'
            else:
                self.fields['quantity'].widget.attrs['disabled'] = 'disabled'
        for f in self.fields:
            self.fields[f] = auto_error_class(self.fields[f])
        
class GroupServiceForm(forms.ModelForm):
    class Meta:
        model = GroupService
        exclude = ('group','orderservice')
    def __init__(self, *args, **kwargs):
        super(GroupServiceForm, self).__init__(*args, **kwargs)
        self.fields['exists'] = forms.BooleanField(required=False)
        self.fields['parentprefix'] = forms.CharField(widget=forms.HiddenInput())
        self.fields['groupprefix'] = forms.CharField(widget=forms.HiddenInput())
        self.fields['pk'] = forms.IntegerField(required=False, initial=self.instance.pk, widget=forms.HiddenInput())
        self.fields['groupname'] = forms.CharField(widget=forms.HiddenInput(attrs={'class':'groupnameinput'}))
        for f in self.fields:
            self.fields[f] = auto_error_class(self.fields[f])
        
#style management forms
class StyleForm(forms.ModelForm):
    required_css_class = "required"
    class Meta:
        model = Style
        exclude = ('garmentdyeprice',)
    def __init__(self, *args, **kwargs):
        super(StyleForm, self).__init__(*args, **kwargs)
        self.fields['pk'] = forms.IntegerField(required=False, initial=self.instance.pk, widget=forms.HiddenInput())
        self.fields['sizecount'] = forms.IntegerField(initial=0, widget=forms.HiddenInput())
        self.fields['pricecount'] = forms.IntegerField(initial=0, widget=forms.HiddenInput())
        self.fields['addedcostcount'] = forms.IntegerField(initial=0, widget=forms.HiddenInput())
        self.fields['garmentdyepriceprefix'] = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'garmentdyeicon icon', 'readonly':'readonly'}))
        for f in self.fields:
            self.fields[f] = auto_error_class(self.fields[f])

class StyleSizeForm(forms.ModelForm):
    class Meta:
        model = StyleSize
        exclude = {
            'style'
        }
    def __init__(self, *args, **kwargs):
        super(StyleSizeForm, self).__init__(*args, **kwargs)
        self.fields['pk'] = forms.IntegerField(required=False, initial=self.instance.pk, widget=forms.HiddenInput())
        self.fields['exists'] = forms.BooleanField(required=False)
        self.fields['exists'].widget.attrs = {'onChange':'togglesizeexists(this)'}
        self.fields['size'].widget = forms.HiddenInput()
        self.fields['label'] = forms.CharField(max_length=5, widget=forms.HiddenInput())
        for f in self.fields:
            self.fields[f] = auto_error_class(self.fields[f])
        
class StylePriceForm(forms.ModelForm):
    class Meta:
        model = StylePrice
        exclude = {
            'style'
        }
    def __init__(self, *args, **kwargs):
        super(StylePriceForm, self).__init__(*args, **kwargs)
        self.fields['pk'] = forms.IntegerField(required=False, initial=self.instance.pk, widget=forms.HiddenInput())
        self.fields['delete'] = forms.IntegerField(initial=0, widget=forms.HiddenInput())
        for f in self.fields:
            self.fields[f] = auto_error_class(self.fields[f])
        
class StylePriceAddedCostForm(forms.ModelForm):
    class Meta:
        model = StylePriceAddedCost
        exclude = {
            'styleprice',
            'stylesize'
        }
    def __init__(self, *args, **kwargs):
        super(StylePriceAddedCostForm, self).__init__(*args, **kwargs)
        self.fields['pk'] = forms.IntegerField(required=False, initial=self.instance.pk, widget=forms.HiddenInput())
        self.fields['parentprefix'] = forms.CharField(widget=forms.HiddenInput())
        self.fields['delete'] = forms.IntegerField(initial=0, widget=forms.HiddenInput())
        self.fields['sizeprefix'] = forms.ChoiceField(choices=[('', '---------')])
        self.fields['sizeprefix'].widget.attrs = {'class':'sizeprefix'}
        for f in self.fields:
            self.fields[f] = auto_error_class(self.fields[f])
        
#size management
class SizeForm(forms.ModelForm):
    class Meta:
        model = Size
    def __init__(self, *args, **kwargs):
        super(SizeForm, self).__init__(*args, **kwargs)
        self.fields['sort'].widget = forms.HiddenInput()
        self.fields['sort'].widget.attrs = {'class':'sort'}
        self.fields['pk'] = forms.IntegerField(required=False, initial=self.instance.pk, widget=forms.HiddenInput())
        self.fields['abbr'].widget.attrs = {'class':'digit'}
        self.fields['delete'] = forms.IntegerField(initial=0, widget=forms.HiddenInput())
        for f in self.fields:
            self.fields[f] = auto_error_class(self.fields[f])
            
#artwork management
class ArtworkForm(forms.ModelForm):
    class Meta:
        model = Artwork
    def __init__(self, *args, **kwargs):
        super(ArtworkForm, self).__init__(*args, **kwargs)
        self.fields['pk'] = forms.IntegerField(required=False, initial=self.instance.pk, widget=forms.HiddenInput())
        self.fields['imprintcount'] = forms.IntegerField(initial=0, widget=forms.HiddenInput())
        self.fields['setupcount'] = forms.IntegerField(initial=0, widget=forms.HiddenInput())
        self.fields['setupcolorcount'] = forms.IntegerField(initial=0, widget=forms.HiddenInput())
        for f in self.fields:
            self.fields[f] = auto_error_class(self.fields[f])
            
class ImprintForm(forms.ModelForm):
    class Meta:
        model = Imprint
        exclude = ('artwork',)
    def __init__(self, *args, **kwargs):
        super(ImprintForm, self).__init__(*args, **kwargs)
        self.fields['pk'] = forms.IntegerField(required=False, initial=self.instance.pk, widget=forms.HiddenInput())
        self.fields['delete'] = forms.IntegerField(initial=0, widget=forms.HiddenInput())
        for f in self.fields:
            self.fields[f] = auto_error_class(self.fields[f])
            
class SetupForm(forms.ModelForm):
    class Meta:
        model = Setup
        exclude = ('imprint',)
    def __init__(self, *args, **kwargs):
        super(SetupForm, self).__init__(*args, **kwargs)
        self.fields['pk'] = forms.IntegerField(required=False, initial=self.instance.pk, widget=forms.HiddenInput())
        self.fields['delete'] = forms.IntegerField(initial=0, widget=forms.HiddenInput())
        self.fields['parentprefix'] = forms.CharField(required=False, widget=forms.HiddenInput())
        self.fields['name'].widget.attrs = {'class':'medium'}
        for f in self.fields:
            self.fields[f] = auto_error_class(self.fields[f])
            
class SetupColorForm(forms.ModelForm):
    class Meta:
        model = SetupColor
        exclude = ('setup',)
    def __init__(self, *args, **kwargs):
        super(SetupColorForm, self).__init__(*args, **kwargs)
        self.fields['pk'] = forms.IntegerField(required=False, initial=self.instance.pk, widget=forms.HiddenInput())
        self.fields['delete'] = forms.IntegerField(initial=0, widget=forms.HiddenInput())
        self.fields['parentprefix'] = forms.CharField(required=False, widget=forms.HiddenInput())
        self.fields['headnumber'].widget = forms.HiddenInput()
        self.fields['positivenumber'].widget.attrs = {'class':'veryshort aligncenter'}
        self.fields['inknumber'].widget.attrs = {'class':'short'}
        self.fields['screenmesh'].widget.attrs = {'class':'short'}
        for f in self.fields:
            self.fields[f] = auto_error_class(self.fields[f])
