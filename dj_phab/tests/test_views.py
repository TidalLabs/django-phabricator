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
#            logging.debug([i, val, base_date + timedelta(val)])
        PullRequest.objects.bulk_create(instances)

    def test_basic(self):
        # 2 each in 2014-01, 2014-02, 2014-03, 2014-04
        # values 0, 16, 32, 48, 64, 80, 96, 112; first is closed and thus filtered out
        # averages 16, 40, 72, 104
        self.make_models(8, 16)
        response = self.client.get(reverse('djp-basic'))
        self.assertEqual(response.status_code, 200)
        periods = response.context['periods']
        self.assertEqual(periods.keys(), ['2014-01', '2014-02', '2014-03', '2014-04',])
        self.assertEqual(periods['2014-01']['avg_lines'], 16)
        self.assertEqual(periods['2014-02']['avg_lines'], 40)
        self.assertEqual(periods['2014-03']['avg_lines'], 72)
        self.assertEqual(periods['2014-04']['avg_lines'], 104)

    @override_settings(PHAB_STATS={
                                      'huge_diff_size': 32,
                                      'small_diff_size': 7,
                                  })
    def test_basic_excludes(self):
        # 2 each in 2014 weeks 1, 2, 3, 4, 5, 6
        # values (rounding down) 0, 3, 7, 10, 14, 18, 21, 25, 28, 32, 36, 39
        # 0th (0) and 10th (36) excluded because closed
        # 0th thru 2nd and 9th thru 11th excluded because too large
        # averages 10, 16, 23, 28
        self.make_models(12, 3.6)
        response = self.client.get(reverse('djp-basic_granular', kwargs={'granularity': 'week'}))
        self.assertEqual(response.status_code, 200)
        periods = response.context['periods']
        self.assertEqual(periods.keys(), [
                                            '2014-Week-02',
                                            '2014-Week-03',
                                            '2014-Week-04',
                                            '2014-Week-05',
                                            '2014-Week-06',])
        self.assertEqual(periods['2014-Week-02']['avg_lines'], 10)
        self.assertEqual(periods['2014-Week-03']['avg_lines'], 16)
        self.assertEqual(periods['2014-Week-04']['avg_lines'], 23)
        self.assertEqual(periods['2014-Week-05']['avg_lines'], 28)
        self.assertNotIn('avg_lines', periods['2014-Week-06'])

    @override_settings(PHAB_STATS={
                                      'huge_diff_size': 46,
                                      'small_diff_size': 7,
                                      'xl_diff_size': 40,
                                      'large_diff_size': 35,
                                  })
    def test_annotation(self):
        # 1 each in 2014 wweks 1, 8, 9; 2 each in 2014 weeks 2, 3, 4, 5, 6, 7
        # this is related to week 1 2014 starting in Dec 2013: http://www.epochconverter.com/date-and-time/weeknumbers-by-year.php?year=2014
        # values (rounding down) 0, 3, 7, 10, 14, 18, 21, 25, 28, 32, 36, 39, 43, 46, 50, 54
        # 0th (0) and 10th (36) excluded because closed
        # 0th thru 2nd and 13th thru 15th excluded because too large
        # averages 10, 16, 23, 30, 39, 43
        # huge count - wk7: 1; wk8: 21, wk 9: 2
        # xl count - wk7: 2, wk8: 1, wk9: 1
        # large count - wk6: 1, wk7: 2, wk8: 1, wk9: 1
        self.make_models(16, 3.6)
        response = self.client.get(reverse('djp-basic_granular', kwargs={'granularity': 'week'}))
        self.assertEqual(response.status_code, 200)

        periods = response.context['periods']
        self.assertEqual(periods.keys(), [
                                            '2014-Week-02',
                                            '2014-Week-03',
                                            '2014-Week-04',
                                            '2014-Week-05',
                                            '2014-Week-06',
                                            '2014-Week-07',
                                            '2014-Week-08',
                                            '2014-Week-09',])

        self.assertEqual(periods['2014-Week-02']['avg_lines'], 10)
        self.assertEqual(periods['2014-Week-03']['avg_lines'], 16)
        self.assertEqual(periods['2014-Week-04']['avg_lines'], 23)
        self.assertEqual(periods['2014-Week-05']['avg_lines'], 30)
        self.assertEqual(periods['2014-Week-06']['avg_lines'], 39)
        self.assertEqual(periods['2014-Week-07']['avg_lines'], 43)
        self.assertNotIn('avg_lines', periods['2014-Week-08'])
        self.assertNotIn('avg_lines', periods['2014-Week-09'])

        self.assertNotIn('huge_count', periods['2014-Week-06'])
        self.assertEqual(periods['2014-Week-07']['huge_count'], 1)
        self.assertEqual(periods['2014-Week-08']['huge_count'], 1)
        self.assertEqual(periods['2014-Week-09']['huge_count'], 1)

        self.assertNotIn('xl_count', periods['2014-Week-06'])
        self.assertEqual(periods['2014-Week-07']['xl_count'], 2)
        self.assertEqual(periods['2014-Week-08']['xl_count'], 1)
        self.assertEqual(periods['2014-Week-09']['xl_count'], 1)

        self.assertNotIn('large_count', periods['2014-Week-05'])
        self.assertEqual(periods['2014-Week-06']['large_count'], 1)
        self.assertEqual(periods['2014-Week-07']['large_count'], 2)
        self.assertEqual(periods['2014-Week-08']['large_count'], 1)
        self.assertEqual(periods['2014-Week-09']['large_count'], 1)
