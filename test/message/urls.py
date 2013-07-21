try:
    from django.conf.urls import patterns, include, url
except ImportError:
    from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('message.views',
    url(r'^receive1/$', 'receive1', name='receive1'),
    url(r'^receive2/$', 'receive2', name='receive2'),
)