from django.contrib import admin
try:
    from django.conf.urls import patterns, include, url
except ImportError:
    from django.conf.urls.defaults import patterns, include, url

admin.autodiscover()

urlpatterns = patterns('message.views',
    url(
        r'^admin/',
        include(admin.site.urls)
    ),
    url(
          r'^receive/$'
        , 'receive'
        , name='receive'
    )
)