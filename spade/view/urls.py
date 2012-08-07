from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'spade.view.views.dashboard', name='dashboard'),
    url(r'^batch/(?P<batch_id>\d+)/$', 'spade.view.views.batch_report', name='batch_report'),
    url(r'^site/(?P<site_id>\d+)/$', 'spade.view.views.site_report', name='site_report'),
    url(r'^site/(?P<site_id>\d+)/(?P<user_agent>\d+)/$', 'spade.view.views.site_report', name='site_report_with_ua'),

    url(r'^admin/', include(admin.site.urls)),

) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
