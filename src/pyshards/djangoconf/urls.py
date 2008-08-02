from django.conf.urls.defaults import *
from djangoconf.shard.views import *

urlpatterns = patterns('',
     (r'^$', monitor),
     (r'^shards/$', shards),

    # static files - reasonable approach for debugging
     (r'^static_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/opt/pyshards/web/media/',  'show_indexes': True}),

    # Uncomment this for admin:
     (r'^admin/', include('django.contrib.admin.urls')),
)
