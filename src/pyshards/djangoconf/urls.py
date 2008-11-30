from django.conf.urls.defaults import *
from djangoconf.shard.views import *
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
     (r'^$', monitor),
     (r'^shards/$', shards),

    # static files - reasonable approach for debugging
     (r'^static_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/opt/pyshards/web/media/',  'show_indexes': True}),

    # Uncomment this for admin:
      (r'^admin/(.*)', admin.site.root),

)
