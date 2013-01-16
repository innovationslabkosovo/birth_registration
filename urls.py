from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin
from birthreg import views

admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^my-project/', include('my_project.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    (r'^admin/', include(admin.site.urls)),
    ('', include('rapidsms_httprouter.urls')),
    
    # RapidSMS core URLs
    (r'^account/', include('rapidsms.urls.login_logout')),
    url(r'^$', 'rapidsms.views.dashboard', name='rapidsms-dashboard'),

    # Birth Registration app URLs
    (r'^locations/', views.locations),
    (r'^visualization/', views.visualization),
    
    # RapidSMS contrib app URLs
   # (r'^ajax/', include('rapidsms.contrib.ajax.urls')),
    #(r'^export/', include('rapidsms.contrib.export.urls')),
    #(r'^httptester/', include('rapidsms.contrib.httptester.urls')),
    #(r'^messagelog/', include('rapidsms.contrib.messagelog.urls')),
    #(r'^messaging/', include('rapidsms.contrib.messaging.urls')),
    #(r'^scheduler/', include('rapidsms.contrib.scheduler.urls')),
    (r'^rapidsms/login/$', 'rapidsms.views.login'),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        # helper URLs file that automatically serves the 'static' folder in
        # INSTALLED_APPS via the Django static media server (NOT for use in
        # production)
        (r'^', include('rapidsms.urls.static_media')),
    )
