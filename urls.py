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
    (r'^tsd/orders/(?P<orderid>\d+)/edit/', 'tsd.views.editorder'),
    (r'^tsd/orders/addgroup/', 'tsd.views.addgroup'),
    (r'^tsd/orders/addstyle/', 'tsd.views.addstyle'),
)
