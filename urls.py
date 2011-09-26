from django.conf import settings
from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^tsdsystem/', include('tsdsystem.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/home/ytfeldrawkcab/TSD/static'}),
    (r'^tsd/login/$', 'django.contrib.auth.views.login'),
    
    # Customers
    (r'^tsd/customers/(?P<customerid>\d+)/edit/$', 'tsd.views.editcustomer'),
    (r'^tsd/customers/add/$', 'tsd.views.editcustomer'),
    (r'^tsd/customers/addcontact/$', 'tsd.views.addcontact'),
    (r'^tsd/customers/addaddress/$', 'tsd.views.addaddress'),
    
    # Artwork
    (r'^tsd/artwork/(?P<artworkid>\d+)/edit/$', 'tsd.views.editartwork'),
    (r'^tsd/artwork/add/$', 'tsd.views.editartwork'),
    (r'^tsd/artwork/addartworkfile/$', 'tsd.views.addartworkfile'),
    (r'^tsd/artwork/addimprint/$', 'tsd.views.addimprint'),
    (r'^tsd/artwork/addplacement/$', 'tsd.views.addplacement'),
    (r'^tsd/artwork/addsetup/$', 'tsd.views.addsetup'),
    (r'^tsd/artwork/addsetupcolor/$', 'tsd.views.addsetupcolor'),
    (r'^tsd/artwork/addsetupflash/$', 'tsd.views.addsetupflash'),
    (r'^tsd/artwork/getinkcolors/$', 'tsd.views.getinkcolors'),
    
    #Artwork Tasks
    (r'^tsd/artwork/tasks/(?P<artworktaskid>\d+)/edit/$', 'tsd.views.editartworktask'),
    (r'^tsd/artwork/tasks/add/(?P<artworkid>\d+)/$', 'tsd.views.editartworktask'),
    (r'^tsd/artwork/tasks/addcomment/$', 'tsd.views.addartworktaskcomment'),
    
    # Orders
    (r'^tsd/orders/(?P<orderid>\d+)/edit/$', 'tsd.views.editorder'),
    (r'^tsd/orders/add/(?P<customerid>\d+)/$', 'tsd.views.editorder'),
    (r'^tsd/orders/addgroup/$', 'tsd.views.addgroup'),
    (r'^tsd/orders/addstyle/$', 'tsd.views.addstyle'),
    (r'^tsd/orders/addimprint/$', 'tsd.views.addorderimprint'),
    (r'^tsd/orders/addgroupimprint/$', 'tsd.views.addgroupimprint'),
    (r'^tsd/orders/addservice/$', 'tsd.views.addorderservice'),
    (r'^tsd/orders/getstyleprices/$', 'tsd.views.getstyleprices'),
    
    # Styles
    (r'^tsd/styles/(?P<styleid>\d+)/edit/$', 'tsd.views.editstyle'),
    (r'^tsd/styles/add/$', 'tsd.views.editstyle'),
    (r'^tsd/styles/addprice/$', 'tsd.views.addprice'),
    (r'^tsd/styles/addaddedcost/$', 'tsd.views.addaddedcost'),
    (r'^tsd/styles/addpricecolor/$', 'tsd.views.addpricecolor'),
    
    # Sizes
    (r'^tsd/sizes/edit/$', 'tsd.views.editsizes'),
    (r'^tsd/sizes/addsize/$', 'tsd.views.addsize'),
    
    # Inks
    (r'^tsd/inks/(?P<inkrecipeid>\d+)/edit/$', 'tsd.views.editinkrecipe'),
    (r'^tsd/inks/addingredient/$', 'tsd.views.addinkrecipeingredient'),
    (r'^tsd/inks/addalias/$', 'tsd.views.addinkrecipealias'),
    
    # Print Setups
    (r'^tsd/print/ordersetups/(?P<orderid>\d+)/$', 'tsd.views.displayordersetups'),
)
