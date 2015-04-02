import logging
from datetime import datetime, timedelta
from django.core.urlresolvers import reverse
from django.test import TestCase, override_settings
from django.utils import timezone
from dj_phab.models import PullRequest, PhabUser

class TestSmoke(TestCase):
    urls = 'dj_phab.urls'

    def test_smoke(self):
        response = self.client.get(reverse('djp-smoke'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, u"Hi Django-Phabricator!")


class TestDataView(TestCase):
    urls = 'dj_phab.urls'

    def setUp(self):
        self.tz = timezone.get_current_timezone()
        self.user = PhabUser.objects.create(**{
            'phid': 'asdf',
            'user_name': 'helen',
            'real_name': 'Helen of Troy',
        })

    def make_models(self, count, interval):
        instances = []
        base_date = timezone.make_aware(datetime(2014, 1, 1), self.tz)
        for i in range(count):
            val = i * interval
            instances.append(PullRequest(**{
                'phid': 'phid-diff-%s' % i,
                'phab_id': 1,
                'title': 'PR %s' % i,
                'author': self.user,
                'line_count': val,
                'status': PullRequest.STATUS.closed if i % 10 else PullRequest.STATUS.abandoned,
                'uri': 'http://www.example.com',
                'diff_count': 1,
                'commit_count': 1,
                'date_opened': base_date + timedelta(val),
                'date_updated': timezone.now(),
            }))
            logging.debug([i, val, base_date + timedelta(val)])
        PullRequest.objects.bulk_create(instances)

    def test_basic(self):
        # 2 each in 2014-01, 2014-02, 2014-03, 2014-04
        # values 0, 16, 32, 48, 64, 80, 96, 112; first is closed and thus filtered out
        # averages 16, 40, 72, 104
        self.make_models(8, 16)
        response = self.client.get(reverse('djp-basic'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, u"16")
        self.assertContains(response, u"40")
        self.assertContains(response, u"72")
        self.assertContains(response, u"104")

    @override_settings(PHAB_STATS={
                                      'huge_diff_size': 32,
                                      'small_diff_size': 7,
                                  })
    def test_basic_excludes(self):
        # 2 each in 2014-01 weeks 1, 2, 3, 4, 5, 6
        # values (rounding down) 0, 3, 7, 10, 14, 18, 21, 25, 28, 32, 36, 39
        # 0th (0) and 10th (36) excluded because closed
        # 0th thru 2nd and 9th thru 11th excluded because too large
        # averages 10, 16, 23, 28
        self.make_models(12, 3.6)
        response = self.client.get(reverse('djp-basic_granular', kwargs={'granularity': 'week'}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, u"10")
        self.assertContains(response, u"14")
        self.assertContains(response, u"23")
        self.assertContains(response, u"28")
        self.assertNotContains(response, u"39")
