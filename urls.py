from django.conf.urls.defaults import *
from django.conf import settings
from django.views.decorators.cache import cache_page
from morebetterer import views

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^morebetterer/$', views.challenge),
    (r'^morebetterer/top/$', views.top),
    (r'^morebetterer/about/$', cache_page(views.about, 60 * 60)),
    (r'^admin/(.*)', admin.site.root),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/usr/local/src/python/apps/media'}),
    )