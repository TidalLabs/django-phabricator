import sys
from django.conf import settings
from django.conf.urls import patterns, include, url
from django.views.generic.base import TemplateView
from dj_phab import views
from dj_phab.defaults import get_granularities

granularities = '|'.join(get_granularities())

urlpatterns = patterns('',
    url(r'^$', views.IndexView.as_view(), name='djp-index'),
    url(r'^basic/$', views.DataView.as_view(), name='djp-basic'),
    url(r'^basic/(?P<granularity>%s)/$' % granularities, views.DataView.as_view(), name='djp-basic_granular'),
)


if 'test' in sys.argv or getattr(settings, 'DEBUG', False):
    urlpatterns += patterns('',
        url(r'^smoke/$', TemplateView.as_view(template_name='dj_phab/smoke.html'), name='djp-smoke'),
    )
