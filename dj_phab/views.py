import logging
from collections import OrderedDict
from django.conf import settings
from django.shortcuts import render
from django.views.generic import ListView
from django.views.generic.base import TemplateView
from dj_phab.models import PullRequest
from dj_phab.util import consolidate_time_period, annotate_dict

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

    def index_rows(self, rows):
        """
        Convert a list (or queryset) of dicts to a dict of dicts, using the
        "friendly" time period representation as the key.

        This is done so we can more easily annotate these dicts with add'l data.

        @param list rows Data to transform
        @return dict Transformed data
        """
        return dict([(consolidate_time_period(row,
                                              granularity=self.granularity,
                                              fieldname='date_opened'),
                       row)
                      for row in rows])

    def get_queryset(self):
        # Filter our data
        exclude_above = getattr(settings, 'PHAB_STATS', {}).get('huge_diff_size', 2500)
        exclude_below = getattr(settings, 'PHAB_STATS', {}).get('small_diff_size', 5)

        diffs_without_outliers = PullRequest.objects.exclude(line_count__gte=exclude_above)\
                                                    .exclude(line_count__lte=exclude_below)

        # Calculate frequency and averages
        diffs = diffs_without_outliers.size_and_frequency_by_granularity(self.granularity)

        # convert to a more convenient format to add annotations
        diffs = self.index_rows(diffs)

        # retrieve various counts
        large_size = getattr(settings, 'PHAB_STATS', {}).get('large_diff_size', 1000)
        xl_size = getattr(settings, 'PHAB_STATS', {}).get('xl_diff_size', 500)
        huge_size = exclude_above

        count_huge = PullRequest.objects.filter(line_count__gte=huge_size).count_by_granularity(self.granularity)
        count_xl = PullRequest.objects.filter(line_count__gte=xl_size).count_by_granularity(self.granularity)
        count_large = PullRequest.objects.filter(line_count__gte=large_size).count_by_granularity(self.granularity)

        # annotate data with counts
        annotate_dict(diffs, 'huge_count', self.index_rows(count_huge), 'review_count')
        annotate_dict(diffs, 'xl_count', self.index_rows(count_xl), 'review_count')
        annotate_dict(diffs, 'large_count', self.index_rows(count_large), 'review_count')

        # And sort everything (not worth doing until now, since we may have new keys)
        diffs = OrderedDict(sorted(diffs.items()))

        return diffs

    def get_context_data(self, **kwargs):
        context = super(DataView, self).get_context_data(**kwargs)
        context['granularity'] = self.granularity
        context['time_period_field'] = 'date_opened'
        return context
