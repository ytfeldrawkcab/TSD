from django.db import models

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
        return self.number
    
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
    
class Imprint(models.Model):
    customer = models.ForeignKey(Customer)
    bagnumber = models.IntegerField()
    transcendent = models.BooleanField()
    
class Setup(models.Model):
    imprint = models.ForeignKey(Imprint)
    name = models.CharField(max_length=60)
    note = models.TextField(blank=True)
    deprecated = models.BooleanField()
    
class Location(models.Model):
    name = models.CharField(max_length=100)
    abbr = models.CharField(max_length=6)
    
class Order(models.Model):
    customer = models.ForeignKey(Customer)
    name = models.CharField(max_length=100)
    note = models.TextField()
    
class Group(models.Model):
    order = models.ForeignKey(Order)
    name = models.CharField(max_length=60)
    note = models.TextField()
    
class OrderImprint(models.Model):
    imprint = models.ForeignKey(Imprint, blank=True)
    location = models.ForeignKey(Location)
    order = models.ForeignKey(Order)
    name = models.CharField(max_length=60)
    color = models.IntegerField()
    
class GroupSetup(models.Model):
    group = models.ForeignKey(Group)
    setup = models.ForeignKey(Setup)
    
