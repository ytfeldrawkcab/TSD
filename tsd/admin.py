from tsd.models import *
from django.contrib import admin

admin.site.register(Size)

class StyleInline(admin.TabularInline):
    model = Style
    extra = 1

class ManufacturerAdmin(admin.ModelAdmin):
    inlines = [StyleInline]

admin.site.register(Manufacturer, ManufacturerAdmin)

class StylePriceAddedCostInline(admin.TabularInline):
    model = StylePriceAddedCost
    extra = 1
    
class StylePriceAdmin(admin.ModelAdmin):
    inlines = [StylePriceAddedCostInline]
    
admin.site.register(StylePrice, StylePriceAdmin)

class StyleSizeInline(admin.TabularInline):
    model = StyleSize
    extra = 1
    
class StyleAdmin(admin.ModelAdmin):
    inlines = [StyleSizeInline]
    
admin.site.register(Style, StyleAdmin)

class CustomerContactInline(admin.StackedInline):
    model = CustomerContact
    extra = 1
    
class CustomerAddressInline(admin.StackedInline):
    model = CustomerAddress
    extra = 1
    
class CustomerAdmin(admin.ModelAdmin):
    inlines = [CustomerContactInline, CustomerAddressInline]

admin.site.register(Customer, CustomerAdmin)

class SetupInline(admin.TabularInline):
    model = Setup
    extra = 1
    
class ImprintAdmin(admin.ModelAdmin):
    inlines = [SetupInline]

admin.site.register(Artwork)
admin.site.register(Placement)
admin.site.register(Imprint, ImprintAdmin)
admin.site.register(Location)
admin.site.register(Service)
admin.site.register(ServiceCategory)
admin.site.register(DyeColor)
admin.site.register(SetupColor)

admin.site.register(ColorFamily)
admin.site.register(InkBase)
admin.site.register(InkIngredient)

class InkRecipeIngredientInline(admin.TabularInline):
    model = InkRecipeIngredient
    extra = 3
    
class InkRecipePantoneInline(admin.TabularInline):
    model = InkRecipePantone
    extra = 1
    
class InkRecipeAdmin(admin.ModelAdmin):
    inlines = [InkRecipeIngredientInline, InkRecipePantoneInline]
    
admin.site.register(InkRecipe, InkRecipeAdmin)
admin.site.register(ArtworkFile)
admin.site.register(ArtworkTaskName)
admin.site.register(ArtworkFileType)
admin.site.register(ArtworkTask)
admin.site.register(ArtworkTaskStatus)
