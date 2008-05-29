from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # Example:
    # (r'^djangoconf/', include('djangoconf.foo.urls')),

    # Uncomment this for admin:
     (r'^admin/', include('django.contrib.admin.urls')),
)
