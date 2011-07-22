from django import forms
from django.forms import fields

from tsd.models import *

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
        self.fields['quantity'].widget.attrs['class'] = 'digit'
        
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
        if self.instance.pk:
            if self.instance.service.enteredquantity == True:
                self.fields['specify'].widget.attrs['disabled'] = 'disabled'
            else:
                self.fields['quantity'].widget.attrs['disabled'] = 'disabled'
        
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
        
#style management forms
class StyleForm(forms.ModelForm):
    required_css_class = "required"
    class Meta:
        model = Style
    def __init__(self, *args, **kwargs):
        super(StyleForm, self).__init__(*args, **kwargs)
        self.fields['pk'] = forms.IntegerField(required=False, initial=self.instance.pk, widget=forms.HiddenInput())
        self.fields['sizecount'] = forms.IntegerField(initial=0, widget=forms.HiddenInput())
        self.fields['pricecount'] = forms.IntegerField(initial=0, widget=forms.HiddenInput())
        self.fields['addedcostcount'] = forms.IntegerField(initial=0, widget=forms.HiddenInput())

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
        self.fields['size'].widget = forms.HiddenInput()
        self.fields['label'] = forms.CharField(max_length=5, widget=forms.HiddenInput())
        
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
        
class StylePriceAddedCostForm(forms.ModelForm):
    class Meta:
        model = StylePriceAddedCost
        exclude = {
            'styleprice'
        }
    def __init__(self, *args, **kwargs):
        super(StylePriceAddedCostForm, self).__init__(*args, **kwargs)
        self.fields['pk'] = forms.IntegerField(required=False, initial=self.instance.pk, widget=forms.HiddenInput())
        self.fields['parentprefix'] = forms.CharField(widget=forms.HiddenInput())
        self.fields['delete'] = forms.IntegerField(initial=0, widget=forms.HiddenInput())
        
class StylePriceColorForm(forms.ModelForm):
    class Meta:
        model = StylePriceColor
        exclude = {
            'styleprice'
        }
    def __init__(self, *args, **kwargs):
        super(StylePriceColorForm, self).__init__(*args, **kwargs)
        self.fields['pk'] = forms.IntegerField(required=False, initial=self.instance.pk, widget=forms.HiddenInput())
        self.fields['parentprefix'] = forms.CharField(widget=forms.HiddenInput())
        self.fields['label'] = forms.CharField(widget=forms.HiddenInput())
        self.fields['color'].widget = forms.HiddenInput()
