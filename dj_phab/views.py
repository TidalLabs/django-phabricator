from django.shortcuts import render
from django.views.generic import ListView
from django.views.generic.base import TemplateView
from dj_phab.models import PullRequest

# Create your views here.
class IndexView(TemplateView):
    allowed_methods = ['get',]
    template_name = 'dj_phab/index.html'


class DataView(ListView):
    context_object_name = 'periods'
    allowed_methods = ['get',]
    template_name = 'dj_phab/data_table.html'

    def get(self, request, granularity=None, **kwargs):
        self.granularity = granularity or 'month'
        return super(DataView, self).get(request, **kwargs)

    def get_queryset(self):
        return PullRequest.objects.size_and_frequency_by_granularity(self.granularity)