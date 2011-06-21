from tsd.models import Customer, Manufacturer, Size, Style, StylePriceAddedCost, StylePrice
from django.contrib import admin

admin.site.register(Customer)
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
