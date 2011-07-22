from django.conf.urls.defaults import patterns, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

handler500 = 'djangotoolbox.errorviews.server_error'

# Does not work with django-nonrel
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'saynsee.views.main'),
    url(r'^verify_user$', 'saynsee.views.verify_user'),
    url(r'^verify_wait$', 'saynsee.views.verify_wait'),
    url(r'^chat_(?P<token>.+)$', 'saynsee.views.chat'),
    url(r'^main/$', 'saynsee.views.main'),
    url(r'^invite/$', 'saynsee.views.invite'),
    
    url(r'^accounts/login/$', 'saynsee.views.dologin'),
    
    url(r'^accounts/register/$', r'saynsee.views.register'),
    url(r'^accounts/logout/$', r'saynsee.views.dologout'),
    url(r'^accounts/profile/$', r'saynsee.views.main'),
    
    # Does not work with django-nonrel
    # Uncomment the admin/doc line below to enable admin documentation:
    #url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    # Uncomment the next line to enable the admin:
    #url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += staticfiles_urlpatterns()
