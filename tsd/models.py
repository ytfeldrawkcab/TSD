from django.db import models
import reversion

class Manufacturer(models.Model):
    name = models.CharField(max_length=30, unique=True)
    def __unicode__(self):
        return self.name
    
class Style(models.Model):
    manufacturer = models.ForeignKey(Manufacturer)
    number = models.CharField('Style Number',max_length=10)
    description = models.CharField(max_length=40)
    note = models.TextField(blank=True)
    def __unicode__(self):
        return self.number + ' ' + self.description
    
class Size(models.Model):
    name = models.CharField(max_length=30)
    abbr = models.CharField(max_length=5)
    def __unicode__(self):
        return self.name
    
class StyleSize(models.Model):
    style = models.ForeignKey(Style)
    size = models.ForeignKey(Size)
    weight = models.FloatField(blank=True)
    def __unicode__(self):
        return self.style.number + " " + str(self.size)
    
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
    
class Color(models.Model):
    manufacturer = models.ForeignKey(Manufacturer)
    name = models.CharField(max_length=50)
    garmentdye = models.BooleanField('Garment Dye Color')
    def __unicode__(self):
        return self.name
    
class StyleColorPrice(models.Model):
    styleprice = models.ForeignKey(StylePrice)
    color = models.ForeignKey(Color)
    
class Customer(models.Model):
    name = models.CharField(max_length=100)
    def __unicode__(self):
        return self.name
    
class Imprint(models.Model):
    customer = models.ForeignKey(Customer)
    name = models.CharField(max_length=60)
    bagnumber = models.IntegerField()
    transcendent = models.BooleanField()
    def __unicode__(self):
        return self.name
    
class Setup(models.Model):
    imprint = models.ForeignKey(Imprint)
    name = models.CharField(max_length=60)
    note = models.TextField(blank=True)
    deprecated = models.BooleanField()
    def __unicode__(self):
        return self.name
    
class Location(models.Model):
    name = models.CharField(max_length=100)
    abbr = models.CharField(max_length=6)
    def __unicode__(self):
        return self.name
    
class Order(models.Model):
    customer = models.ForeignKey(Customer)
    name = models.CharField(max_length=100)
    note = models.TextField()

reversion.register(Order)
    
class Group(models.Model):
    order = models.ForeignKey(Order)
    name = models.CharField(max_length=60)
    note = models.TextField(blank=True)
    
class OrderImprint(models.Model):
    #null = True (for imprint) is necessary because select boxes appear to send 'null' when no choice is made causing validation errors otherwise
    imprint = models.ForeignKey(Imprint, blank=True, null=True)
    location = models.ForeignKey(Location)
    order = models.ForeignKey(Order)
    name = models.CharField(max_length=60, blank=True)
    colorcount = models.IntegerField('Colors')
    specify = models.BooleanField()
    
class GroupSetup(models.Model):
    group = models.ForeignKey(Group)
    orderimprint = models.ForeignKey(OrderImprint)
    setup = models.ForeignKey(Setup, blank=True, null=True)
    
class OrderStyle(models.Model):
    group = models.ForeignKey(Group)
    color = models.ForeignKey(Color)
    style = models.ForeignKey(Style)
    
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
