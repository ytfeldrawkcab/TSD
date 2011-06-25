from tsd.models import Customer, Manufacturer, Size, Style, StylePriceAddedCost, StylePrice, StyleSize, Color, StyleColorPrice, Imprint, Setup
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

class StyleColorPriceInline(admin.TabularInline):
    model = StyleColorPrice
    extra = 1
    
class ColorAdmin(admin.ModelAdmin):
    inlines = [StyleColorPriceInline]
    
admin.site.register(Color, ColorAdmin)    
admin.site.register(Customer)

class SetupInline(admin.TabularInline):
    model = Setup
    extra = 1
    
class ImprintAdmin(admin.ModelAdmin):
    inlines = [SetupInline]

admin.site.register(Imprint, ImprintAdmin)
