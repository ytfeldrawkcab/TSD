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
    
#extension form to add pk field and find instance on submit
class AutoInstanceModelForm(forms.ModelForm):
    def __init__(self, postdata=None, *args, **kwargs):
        if "instance" in kwargs:
            instance = kwargs.pop("instance")
        elif postdata:
            instance_pk = postdata.get(kwargs.get('prefix') + '-pk', None) if kwargs.get('prefix') else postdata.get('pk', None)
            instance = self.Meta.model.objects.get(pk=instance_pk) if instance_pk else None
        else:
            instance = None
            
        super(AutoInstanceModelForm, self).__init__(postdata, *args, instance=instance, **kwargs)
        self.fields['pk'] = forms.IntegerField(required=False, initial=self.instance.pk, widget=forms.HiddenInput())
        self.fields['delete'] = forms.IntegerField(initial=0, widget=forms.HiddenInput())
        for f in self.fields:
            self.fields[f] = auto_error_class(self.fields[f])

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
class OrderForm(AutoInstanceModelForm):
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
        
class GroupForm(AutoInstanceModelForm):
    class Meta:
        model = Group
        exclude = ('order',)
    def __init__(self, *args, **kwargs):
        super(GroupForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs = {'class':'groupname', 'onchange':"changegroupname('" + self.prefix + "', this.value)"}
        
class OrderStyleForm(AutoInstanceModelForm):
    class Meta:
        model = OrderStyle
        exclude = ('group','order')
        widgets = {
            'style':forms.HiddenInput(),
        }
    def __init__(self, *args, **kwargs):
        super(OrderStyleForm, self).__init__(*args, **kwargs)
        self.fields['parentprefix'] = forms.CharField(required=False, widget=forms.HiddenInput())
        self.fields['label'] = forms.CharField(widget=forms.HiddenInput())
        if self.instance.garmentdyecolor:
            colorlabel = self.instance.garmentdyecolor
        else:
            colorlabel = self.instance.piecedyecolor
        self.fields['colorlabel'] = forms.CharField(max_length=50, initial=colorlabel, widget=forms.TextInput(attrs={'class':'labelinput pointer', 'readonly':'readonly'}))
        self.fields['styleprice'].widget = forms.HiddenInput()
        self.fields['garmentdyecolor'].widget = forms.HiddenInput()
        self.fields['piecedyecolor'].widget = forms.HiddenInput()
        self.fields['quantity'] = forms.IntegerField(widget=forms.HiddenInput())
        
class OrderSizeForm(AutoInstanceModelForm):
    class Meta:
        model = OrderSize
        exclude = ('orderstyle',)
        widgets = {
            'stylesize':forms.HiddenInput(),
        }
    def __init__(self, *args, **kwargs):
        super(OrderSizeForm, self).__init__(*args, **kwargs)
        self.fields['parentprefix'] = forms.CharField(widget=forms.HiddenInput())
        self.fields['quantity'].widget.attrs['class'] = 'digit'
        self.fields['label'] = forms.CharField(widget=forms.HiddenInput())
        
class OrderImprintForm(AutoInstanceModelForm):
    class Meta:
        model = OrderImprint
        exclude = ('order',)
    def __init__(self, *args, **kwargs):
        super(OrderImprintForm, self).__init__(*args, **kwargs)
        self.fields['specify'] = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class':'specify', 'onchange':"togglegroups('" + self.prefix + "')"}))
        self.fields['colorcount'].widget.attrs['class'] = 'digit'
        self.fields['imprint'].widget = forms.HiddenInput()
        self.fields['setup'].widget = forms.HiddenInput()
        self.fields['imprintname'] = forms.CharField(required=False, widget=forms.HiddenInput())
        self.fields['setupname'] = forms.CharField(required=False, widget=forms.HiddenInput())

class GroupImprintForm(AutoInstanceModelForm):
    class Meta:
        model = GroupImprint
        exclude = ('group','orderimprint')
    def __init__(self, *args, **kwargs):
        super(GroupImprintForm, self).__init__(*args, **kwargs)
        self.fields['exists'] = forms.BooleanField(required=False)
        self.fields['parentprefix'] = forms.CharField(widget=forms.HiddenInput())
        self.fields['groupprefix'] = forms.CharField(widget=forms.HiddenInput())
        self.fields['groupname'] = forms.CharField(widget=forms.HiddenInput(attrs={'class':'groupnameinput'}))
        
class OrderServiceForm(AutoInstanceModelForm):
    class Meta:
        model = OrderService
        exclude = ('order')
    def __init__(self, *args, **kwargs):
        super(OrderServiceForm, self).__init__(*args, **kwargs)
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
        
class GroupServiceForm(AutoInstanceModelForm):
    class Meta:
        model = GroupService
        exclude = ('group','orderservice')
    def __init__(self, *args, **kwargs):
        super(GroupServiceForm, self).__init__(*args, **kwargs)
        self.fields['exists'] = forms.BooleanField(required=False)
        self.fields['parentprefix'] = forms.CharField(widget=forms.HiddenInput())
        self.fields['groupprefix'] = forms.CharField(widget=forms.HiddenInput())
        self.fields['groupname'] = forms.CharField(widget=forms.HiddenInput(attrs={'class':'groupnameinput'}))
        
#style management forms
class StyleForm(AutoInstanceModelForm):
    class Meta:
        model = Style
        exclude = ('garmentdyeprice',)
    def __init__(self, *args, **kwargs):
        super(StyleForm, self).__init__(*args, **kwargs)
        self.fields['sizecount'] = forms.IntegerField(initial=0, widget=forms.HiddenInput())
        self.fields['pricecount'] = forms.IntegerField(initial=0, widget=forms.HiddenInput())
        self.fields['addedcostcount'] = forms.IntegerField(initial=0, widget=forms.HiddenInput())
        self.fields['garmentdyepriceprefix'] = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'garmentdyeicon icon', 'readonly':'readonly'}))

class StyleSizeForm(AutoInstanceModelForm):
    class Meta:
        model = StyleSize
        exclude = {
            'style'
        }
    def __init__(self, *args, **kwargs):
        super(StyleSizeForm, self).__init__(*args, **kwargs)
        self.fields['exists'] = forms.BooleanField(required=False)
        self.fields['exists'].widget.attrs = {'onChange':'togglesizeexists(this)'}
        self.fields['size'].widget = forms.HiddenInput()
        self.fields['label'] = forms.CharField(max_length=5, widget=forms.HiddenInput())
        
class StylePriceForm(AutoInstanceModelForm):
    class Meta:
        model = StylePrice
        exclude = {
            'style'
        }
        
class StylePriceAddedCostForm(AutoInstanceModelForm):
    class Meta:
        model = StylePriceAddedCost
        exclude = {
            'styleprice',
            'stylesize'
        }
    def __init__(self, *args, **kwargs):
        super(StylePriceAddedCostForm, self).__init__(*args, **kwargs)
        self.fields['parentprefix'] = forms.CharField(widget=forms.HiddenInput())
        self.fields['sizeprefix'] = forms.ChoiceField(choices=[('', '---------')])
        self.fields['sizeprefix'].widget.attrs = {'class':'sizeprefix'}
        
#size management
class SizeForm(AutoInstanceModelForm):
    class Meta:
        model = Size
    def __init__(self, *args, **kwargs):
        super(SizeForm, self).__init__(*args, **kwargs)
        self.fields['sort'].widget = forms.HiddenInput(attrs={'class':'sort'})
        self.fields['abbr'].widget.attrs = {'class':'digit'}
            
#artwork management
class ArtworkForm(AutoInstanceModelForm):
    class Meta:
        model = Artwork
    def __init__(self, *args, **kwargs):
        super(ArtworkForm, self).__init__(*args, **kwargs)
        self.fields['filecount'] = forms.IntegerField(initial=0, widget=forms.HiddenInput())
        self.fields['imprintcount'] = forms.IntegerField(initial=0, widget=forms.HiddenInput())
        self.fields['placementcount'] = forms.IntegerField(initial=0, widget=forms.HiddenInput())
        self.fields['setupcount'] = forms.IntegerField(initial=0, widget=forms.HiddenInput())
        self.fields['setupcolorcount'] = forms.IntegerField(initial=0, widget=forms.HiddenInput())
        self.fields['setupflashcount'] = forms.IntegerField(initial=0, widget=forms.HiddenInput())

class ArtworkFileForm(AutoInstanceModelForm):
    class Meta:
        model = ArtworkFile
        exclude = ('artwork',)
    def __init__(self, *args, **kwargs):
        super(ArtworkFileForm, self).__init__(*args, **kwargs)
        self.fields['new'] = forms.IntegerField(required=False, initial=0, widget=forms.HiddenInput())
            
class ImprintForm(AutoInstanceModelForm):
    class Meta:
        model = Imprint
        exclude = ('artwork',)
            
class PlacementForm(AutoInstanceModelForm):
    class Meta:
        model = Placement
        exclude = ('imprint',)
    def __init__(self, *args, **kwargs):
        super(PlacementForm, self).__init__(*args, **kwargs)
        self.fields['parentprefix'] = forms.CharField(required=False, widget=forms.HiddenInput())
            
class SetupForm(AutoInstanceModelForm):
    class Meta:
        model = Setup
        exclude = ('imprint',)
    def __init__(self, *args, **kwargs):
        super(SetupForm, self).__init__(*args, **kwargs)
        self.fields['parentprefix'] = forms.CharField(required=False, widget=forms.HiddenInput())
        self.fields['name'].widget.attrs = {'onChange':"updatelabel('" + self.prefix + "', 'name', this.value)"}
            
class SetupColorForm(AutoInstanceModelForm):
    class Meta:
        model = SetupColor
        exclude = ('setup',)
    def __init__(self, *args, **kwargs):
        super(SetupColorForm, self).__init__(*args, **kwargs)
        self.fields['parentprefix'] = forms.CharField(required=False, widget=forms.HiddenInput())
        self.fields['headnumber'].widget = forms.HiddenInput()
        self.fields['positivenumber'].widget.attrs = {'class':'veryshort aligncenter'}
        self.fields['inknumber'].widget.attrs = {'class':'short'}
        self.fields['screenmesh'].widget.attrs = {'class':'short'}
            
class SetupFlashForm(AutoInstanceModelForm):
    class Meta:
        model = SetupFlash
        exclude = ('setup',)
    def __init__(self, *args, **kwargs):
        super(SetupFlashForm, self).__init__(*args, **kwargs)
        self.fields['parentprefix'] = forms.CharField(required=False, widget=forms.HiddenInput())
        self.fields['headnumber'].widget = forms.HiddenInput()
            
#artwork task management
class ArtworkTaskForm(AutoInstanceModelForm):
    class Meta:
        model = ArtworkTask
        exclude = ('user')
    def __init__(self, *args, **kwargs):
        super(ArtworkTaskForm, self).__init__(*args, **kwargs)
        self.fields['commentcount'] = forms.IntegerField(initial=0, widget=forms.HiddenInput())

class ArtworkTaskCommentForm(AutoInstanceModelForm):
    class Meta:
        model = ArtworkTaskComment
        exclude = ('artworktask','user','created')
    def __init__(self, *args, **kwargs):
        super(ArtworkTaskCommentForm, self).__init__(*args, **kwargs)
        self.fields['new'] = forms.IntegerField(required=False, initial=0, widget=forms.HiddenInput())
        self.fields['comment'].widget.attrs = {'class':'rich'}

            
#ink recipe management
class InkRecipeForm(AutoInstanceModelForm):
    class Meta:
        model = InkRecipe
    def __init__(self, *args, **kwargs):
        super(InkRecipeForm, self).__init__(*args, **kwargs)
        self.fields['ingredientcount'] = forms.IntegerField(initial=0, widget=forms.HiddenInput())
        self.fields['pantonecount'] = forms.IntegerField(initial=0, widget=forms.HiddenInput())
        self.fields['rehancegrade'].widget.attrs = {'class':'veryshort aligncenter'}
            
class InkRecipeIngredientForm(AutoInstanceModelForm):
    class Meta:
        model = InkRecipeIngredient
        exclude = ('inkrecipe',)
    def __init__(self, *args, **kwargs):
        super(InkRecipeIngredientForm, self).__init__(*args, **kwargs)
        self.fields['sort'].widget = forms.HiddenInput(attrs={'class':'sort'})
            
class InkRecipePantoneForm(AutoInstanceModelForm):
    class Meta:
        model = InkRecipePantone
        exclude = ('inkrecipe',)
    def __init__(self, *args, **kwargs):
        super(InkRecipePantoneForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs = {'class':'short'}
