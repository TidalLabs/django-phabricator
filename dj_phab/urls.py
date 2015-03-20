from django.conf.urls import patterns, include, url
from django.views.generic.base import TemplateView

urlpatterns = patterns('',
    url(r'^smoke/$', TemplateView.as_view(template_name='dj_phab/smoke.html'), name='smoke'),
)
