from django.shortcuts import render
from django.views.generic import ListView
from django.views.generic.base import TemplateView
from dj_phab.models import PullRequest, UpdatedFile

# Create your views here.
class IndexView(TemplateView):
    allowed_methods = ['get',]
    template_name = 'dj_phab/index.html'


class DataView(ListView):
    context_object_name = 'periods'
    allowed_methods = ['get',]
    template_name = 'dj_phab/data_table.html'

    # SQL regexes to match common filenames that can throw off statistics
    toxic_file_patterns = [
        r'^composer\.json$',
        r'^composer\.lock$',
        r'\/composer\.json$',
        r'\/composer\.lock$',
        r'\.css\.map$',
        [r'\.css$', r'\.scss$',],
    ]

    def get(self, request, granularity=None, **kwargs):
        self.granularity = granularity or 'month'
        return super(DataView, self).get(request, **kwargs)

    def get_queryset(self):
        import logging
        prs = PullRequest.objects.all()
        toxic_files = UpdatedFile.objects.none()
        excludes = PullRequest.objects.none()

        for pattern in self.toxic_file_patterns:
            # string is a single regex; list is a combo
            if hasattr(pattern, 'lower'):
                excludes = excludes | PullRequest.objects.filter(files__filename__regex=pattern)
            else:
                complex_excludes = PullRequest.objects.all()
                for regex in pattern:
                    complex_excludes = complex_excludes.filter(files__filename__regex=regex)
                excludes = excludes | complex_excludes

        prs = prs.exclude(id__in=excludes.values_list('id', flat=True))
        return prs.size_and_frequency_by_granularity(self.granularity)

    def get_context_data(self, **kwargs):
        context = super(DataView, self).get_context_data(**kwargs)
        context['granularity'] = self.granularity
        context['time_period_field'] = 'date_opened'
        return context
