from django.conf import settings
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
        exclude_above = getattr(settings, 'PHAB_STATS', {}).get('huge_diff_size', 2500)
        exclude_below = getattr(settings, 'PHAB_STATS', {}).get('small_diff_size', 5)

        diffs_without_outliers = PullRequest.objects.exclude(line_count__gte=exclude_above)\
                                                    .exclude(line_count__lte=exclude_below)

        return diffs_without_outliers.size_and_frequency_by_granularity(self.granularity)

    def get_context_data(self, **kwargs):
        context = super(DataView, self).get_context_data(**kwargs)
        context['granularity'] = self.granularity
        context['time_period_field'] = 'date_opened'
        return context
