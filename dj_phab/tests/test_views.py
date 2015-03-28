import logging
from datetime import datetime, timedelta
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils import timezone
from dj_phab.models import PullRequest, PhabUser, UpdatedFile

class TestSmoke(TestCase):
    urls = 'dj_phab.urls'

    def test_smoke(self):
        response = self.client.get(reverse('djp-smoke'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, u"Hi Django-Phabricator!")


class TestDataView(TestCase):
    urls = 'dj_phab.urls'

    good_filenames = [
        'blah-composer.json',
        'blah_composer.lock',
        'whatever/css/map',
        'whatever/css/blah.map',
    ]
    sometimes_good_filenames = [
        'whatever.css',
        'blah.whatever.css',
        'whatever.scss',
        'blah/whatever.scss',
    ]
    bad_filenames = [
        'composer.json',
        'blah/composer.lock',
        'whatever.css.map',
        'blah/whatever.css.map',
        'blah/more-blah.whatever.css.map',
    ]
    combined_filenames = [
        [
            'blah.whatever.css',
            'whatever.scss',
        ],
        [
            'blah-whatever.css',
            'blah/whatever.scss',
        ],
        [
            'blah/whatever.css',
            'blah.whatever.scss',
        ],
    ]

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

    def make_files(self, filenames):
        instances = []
        for file in filenames:
            instances.append(UpdatedFile.objects.create(filename=file))
        return instances

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

    def test_basic_simple_excludes(self):
        # 2 each in 2014-01, 2014-02, 2014-03, 2014-04, 2014-05, 2015-06; 1 in 2015-07
        # values 0:0, 1:16, 2:32, 3:48, 4:64, 5:80, 6:96, 7:112, 8:128, 9:144, 10:160, 11:176, 12:192;
        #   first [0th:0] and 11th [10th:160] are closed and thus filtered out
        #   0th, third, 6th, 9th, 12th have bad files and are filtered out
        #   leaves 1:16, 2:32, 4:64, 5:80, 7:112, 8:128, 11:176
        # averages 16, 32, 72, 112, 128, 176
        self.make_models(13, 16)

        good_files = self.make_files(self.good_filenames)
        good_files.extend(self.make_files(self.sometimes_good_filenames))
        bad_files = self.make_files(self.bad_filenames)

        # assign some files.
        for i, instance in enumerate(PullRequest.objects.order_by('line_count')):
            files = []
            files.append(good_files[i % len(good_files)])
            if not i % 3:
                files.append(bad_files[i/3])
            instance.files = files

        response = self.client.get(reverse('djp-basic'))
        logging.debug(response)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, u"16")
        self.assertContains(response, u"32")
        self.assertContains(response, u"72")
        self.assertContains(response, u"112")
        self.assertContains(response, u"128")
        self.assertContains(response, u"176")
        self.assertNotContains(response, u"192")

    def test_basic_combined_excludes(self):
        # 2 each in 2014-01, 2014-02, 2014-03, 2014-04
        # values 0:0, 1:16, 2:32, 3:48, 4:64, 5:80, 6:96, 7:112
        #   first [0th:0] and 11th [10th:160] are closed and thus filtered out
        #   0th, third, 6th, 9th, 12th have bad files and are filtered out
        #   leaves 1:16, 2:32, 4:64, 5:80, 7:112
        # averages 16, 32, 72, 112
        self.make_models(8, 16)

        good_files = self.make_files(self.good_filenames)
        bad_combinations = [self.make_files(filenames) for filenames in self.combined_filenames]

        # assign some files.
        for i, instance in enumerate(PullRequest.objects.order_by('line_count')):
            files = []
            files.append(good_files[i % len(good_files)])
            if not i % 3:
                files.extend(bad_combinations[i/3])
            instance.files = files

        response = self.client.get(reverse('djp-basic'))
        logging.debug(response)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, u"16")
        self.assertContains(response, u"32")
        self.assertContains(response, u"72")
        self.assertNotContains(response, u"104")



