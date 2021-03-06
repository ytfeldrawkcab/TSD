from django.db import models
import reversion
from django.contrib.auth.models import User
from datetime import datetime

class ColorFamily(models.Model):
    name = models.CharField(max_length=50)
    def __unicode__(self):
        return self.name

class InkBase(models.Model):
    name = models.CharField(max_length=20)
    abbr = models.CharField(max_length=3)
    def __unicode__(self):
        return self.abbr

class InkIngredient(models.Model):
    name = models.CharField(max_length=30)
    def __unicode__(self):
        return self.name

class InkRecipe(models.Model):
    inknumber = models.IntegerField(primary_key=True)
    colorfamily = models.ForeignKey(ColorFamily)
    inkbase = models.ForeignKey(InkBase)
    datecreated = models.DateField(default=datetime.now)
    rehancegrade = models.CharField(max_length=1)
    saveink = models.BooleanField()
    note = models.TextField(blank=True)
    def __unicode__(self):
        return str(self.inknumber)

class InkRecipeIngredient(models.Model):
    inkrecipe = models.ForeignKey(InkRecipe)
    inkingredient = models.ForeignKey(InkIngredient)
    amount = models.DecimalField(max_digits=100, decimal_places=2)
    sort = models.IntegerField()
    class Meta:
        ordering = ["sort"]

class InkRecipeAlias(models.Model):
    inkrecipe = models.ForeignKey(InkRecipe)
    name = models.CharField(max_length=7)

class Manufacturer(models.Model):
    name = models.CharField(max_length=30, unique=True)
    def __unicode__(self):
        return self.name

class DyeColor(models.Model):
    name = models.CharField(max_length=50)
    def __unicode__(self):
        return self.name
    class Meta:
        ordering = ['name']

class Style(models.Model):
    manufacturer = models.ForeignKey(Manufacturer)
    number = models.CharField('Style Number', max_length=10)
    description = models.CharField(max_length=40)
    note = models.TextField(blank=True)
    garmentdyeprice = models.ForeignKey('StylePrice', blank=True, null=True, related_name='+', on_delete=models.SET_NULL)
    def __unicode__(self):
        return self.number + ' ' + self.description

class Size(models.Model):
    name = models.CharField(max_length=30)
    abbr = models.CharField(max_length=5)
    sort = models.IntegerField()
    def __unicode__(self):
        return self.name
    class Meta:
        ordering = ["sort"]

class StyleSize(models.Model):
    style = models.ForeignKey(Style)
    size = models.ForeignKey(Size)
    weight = models.FloatField(blank=True, null=True)
    def __unicode__(self):
        return self.size.abbr
    class Meta:
        ordering = ["size"]

class StylePrice(models.Model):
    style = models.ForeignKey(Style)
    name = models.CharField(max_length=200)
    basecost = models.DecimalField(max_digits=100, decimal_places=2)
    def __unicode__(self):
        return self.style.number + " " + self.name

class StylePriceAddedCost(models.Model):
    styleprice = models.ForeignKey(StylePrice)
    stylesize = models.ForeignKey(StyleSize)
    addedcost = models.DecimalField(max_digits=100, decimal_places=2)

class Customer(models.Model):
    name = models.CharField(max_length=100)
    defaultmaincontact = models.ForeignKey('CustomerContact', blank=True, null=True, related_name='+', on_delete=models.SET_NULL)
    defaultshippingcontact = models.ForeignKey('CustomerContact', blank=True, null=True, related_name='+', on_delete=models.SET_NULL)
    defaultbillingcontact = models.ForeignKey('CustomerContact', blank=True, null=True, related_name='+', on_delete=models.SET_NULL)
    defaultshippingaddress = models.ForeignKey('CustomerAddress', blank=True, null=True, related_name='+', on_delete=models.SET_NULL)
    defaultbillingaddress = models.ForeignKey('CustomerAddress', blank=True, null=True, related_name='+', on_delete=models.SET_NULL)
    def __unicode__(self):
        return self.name

class CustomerContact(models.Model):
    customer = models.ForeignKey(Customer)
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    mobile = models.CharField(max_length=20, blank=True)
    title = models.CharField(max_length=50, blank=True)
    def __unicode__(self):
        return self.name

class CustomerAddress(models.Model):
    customer = models.ForeignKey(Customer)
    name = models.CharField(max_length=100, blank=True)
    address1 = models.CharField(max_length=50, blank=True)
    address2 = models.CharField(max_length=50, blank=True)
    city = models.CharField(max_length=30, blank=True)
    state = models.CharField(max_length=2, blank=True)
    postal = models.CharField(max_length=10, blank=True)
    country = models.CharField(max_length=50, default='United States', blank=True)
    def __unicode__(self):
        return self.name

class Artwork(models.Model):
    customer = models.ForeignKey(Customer)
    name = models.CharField(max_length=60)
    bagnumber = models.IntegerField()
    printready = models.BooleanField()
    def __unicode__(self):
        return self.name

class ArtworkFileType(models.Model):
    name = models.CharField(max_length=50)
    def __unicode__(self):
        return self.name

class ArtworkFile(models.Model):
    artwork = models.ForeignKey(Artwork)
    name = models.CharField(max_length=50)
    filetype = models.ForeignKey(ArtworkFileType)
    file = models.FileField(upload_to='artworkfiles', blank=True)
    note = models.TextField(blank=True)

class ArtworkTaskName(models.Model):
    name = models.CharField(max_length=30)
    def __unicode__(self):
        return self.name
    class Meta:
        ordering = ["name"]

class ArtworkTaskStatus(models.Model):
    name = models.CharField(max_length=30)
    def __unicode__(self):
        return self.name

class ArtworkTask(models.Model):
    artwork = models.ForeignKey(Artwork)
    user = models.ForeignKey(User)
    name = models.ForeignKey(ArtworkTaskName, blank=True, null=True)
    miscname = models.CharField(max_length=40, blank=True)
    status = models.ForeignKey(ArtworkTaskStatus, default=ArtworkTaskStatus.objects.get(pk=1))
    scheduleddate = models.DateField(blank=True, null=True)

class ArtworkTaskComment(models.Model):
    artworktask = models.ForeignKey(ArtworkTask)
    comment = models.TextField()
    user = models.ForeignKey(User)
    created = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ["-created"]

#class ArtworkTaskStatusChange(models.Model):
#    artworktask = models.ForeignKey(ArtworkTask)
#    artworktaskstatus = models.ForeignKey(ArtworkTaskStatus)
#    scheduleddate = models.DateField(blank=True)

class Imprint(models.Model):
    artwork = models.ForeignKey(Artwork)
    name = models.CharField(max_length=60)
    transcendent = models.BooleanField()
    width = models.DecimalField(max_digits=100, decimal_places=2, blank=True, null=True)
    height = models.DecimalField(max_digits=100, decimal_places=2, blank=True, null=True)
    def __unicode__(self):
        return self.name

class Placement(models.Model):
    imprint = models.ForeignKey(Imprint)
    shirttype = models.CharField(max_length=50)
    placement = models.CharField(max_length=100)

class Setup(models.Model):
    imprint = models.ForeignKey(Imprint)
    name = models.CharField(max_length=60)
    note = models.TextField(blank=True)
    image = models.ImageField(upload_to='setupimages', blank=True)
    deprecated = models.BooleanField()
    def __unicode__(self):
        return self.name

class SetupColor(models.Model):
    setup = models.ForeignKey(Setup)
    positivenumber = models.IntegerField()
    headnumber = models.IntegerField(blank=True, null=True)
    inkcolor = models.CharField(max_length=30)
    inknumber = models.ForeignKey(InkRecipe, blank=True, null=True)
    inkbase = models.CharField(choices=[('WA','WA'), ('RH','RH')], max_length=2)
    screenmesh = models.IntegerField(blank=True, null=True)
    squeegeetype = models.CharField(choices=[('Blue Square','Blue Square')], max_length=20, blank=True)

class SetupFlash(models.Model):
    setup = models.ForeignKey(Setup)
    headnumber = models.IntegerField()

class Location(models.Model):
    name = models.CharField(max_length=100)
    abbr = models.CharField(max_length=6)
    def __unicode__(self):
        return self.name

class Order(models.Model):
    customer = models.ForeignKey(Customer)
    user = models.ForeignKey(User)
    name = models.CharField(max_length=100)
    note = models.TextField(blank=True)
    maincontact = models.ForeignKey(CustomerContact, blank=True, null=True, related_name='+', on_delete=models.SET_NULL)
    shippingcontact = models.ForeignKey(CustomerContact, blank=True, null=True, related_name='+', on_delete=models.SET_NULL)
    billingcontact = models.ForeignKey(CustomerContact, blank=True, null=True, related_name='+', on_delete=models.SET_NULL)
    shippingaddress = models.ForeignKey(CustomerAddress, blank=True, null=True, related_name='+', on_delete=models.SET_NULL)
    billingaddress = models.ForeignKey(CustomerAddress, blank=True, null=True, related_name='+', on_delete=models.SET_NULL)

reversion.register(Order)

class Group(models.Model):
    order = models.ForeignKey(Order)
    name = models.CharField(max_length=60)
    note = models.TextField(blank=True)

class OrderImprint(models.Model):
    #null = True (for imprint) is necessary because select boxes appear to send 'null' when no choice is made causing validation errors otherwise
    imprint = models.ForeignKey(Imprint, blank=True, null=True)
    setup = models.ForeignKey(Setup, blank=True,  null=True)
    location = models.ForeignKey(Location)
    order = models.ForeignKey(Order)
    name = models.CharField(max_length=60, blank=True)
    colorcount = models.IntegerField('Colors')
    specify = models.BooleanField()

class GroupImprint(models.Model):
    group = models.ForeignKey(Group)
    orderimprint = models.ForeignKey(OrderImprint)
    setup = models.ForeignKey(Setup, blank=True, null=True)

class OrderStyle(models.Model):
    order = models.ForeignKey(Order)
    group = models.ForeignKey(Group, blank=True, null=True)
    style = models.ForeignKey(Style)
    styleprice = models.ForeignKey(StylePrice)
    garmentdyecolor = models.ForeignKey(DyeColor, blank=True, null=True)
    piecedyecolor = models.CharField(max_length=40, blank=True)
    def _get_quantity(self):
        sizes = OrderSize.objects.filter(orderstyle=self)
        quantity = 0
        for size in sizes:
            quantity += size.quantity
        return quantity
    quantity = property(_get_quantity)

class OrderSize(models.Model):
    orderstyle = models.ForeignKey(OrderStyle)
    stylesize = models.ForeignKey(StyleSize)
    quantity = models.IntegerField(blank=True)

class PriceCategory(models.Model):
    name = models.CharField(max_length=40)

class PriceParameter(models.Model):
    pricecategory = models.ForeignKey(PriceCategory)
    name = models.CharField(max_length=40)
    note = models.TextField(blank=True)
    operator = models.CharField(max_length=3)
    value = models.FloatField()

class StylePriceParameter(models.Model):
    priceparameter = models.ForeignKey(PriceParameter)
    style = models.ForeignKey(Style)
    note = models.TextField(blank=True)
    value = models.FloatField()

class OrderPriceParameter(models.Model):
    priceparameter = models.ForeignKey(PriceParameter)
    order = models.ForeignKey(Order)
    note = models.TextField(blank=True)
    value = models.FloatField()

class ServiceCategory(models.Model):
    name = models.CharField(max_length=50)
    def __unicode__(self):
        return self.name

class Service(models.Model):
    servicecategory = models.ForeignKey(ServiceCategory)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=100, decimal_places=2)
    enteredquantity = models.BooleanField()
    def __unicode__(self):
        return self.name

class OrderService(models.Model):
    service = models.ForeignKey(Service)
    order = models.ForeignKey(Order)
    note = models.CharField(max_length=100, blank=True)
    quantity = models.IntegerField(blank=True, null=True)
    specify = models.BooleanField()

class GroupService(models.Model):
    group = models.ForeignKey(Group)
    orderservice = models.ForeignKey(OrderService)

#class PrintTicket(models.Model):
#    order = models.ForeignKey(Order)
#    imprint = models.ForeignKey(Imprint)
#    setup = models.ForeignKey(Setup)
#    quantity = models.IntegerField(blank=True, null=True)
#    created = models.DateTimeField(auto_now_add=True)
#    scheduledate = models.DateField(blank=True, null=True)
#    sort = models.IntegerField()
#    class Meta:
#        ordering = ["sort"]
