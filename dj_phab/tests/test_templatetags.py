from django.conf import settings
from django.test import TestCase
from dj_phab.templatetags.date_grouping import time_period


class TestTimePeriod(TestCase):
    def smoke(self):
        pass

    def test_time_period(self):
        data = {
            'the_field_year': 2014.0,
            'the_field_month': 9.0,
            'the_field_week': 46.0,
            'the_field_day': 27.0,
        }

        output = time_period(data, granularity='year', fieldname='the_field')
        self.assertEqual(output, '2014')
        output = time_period(data, granularity='month', fieldname='the_field')
        self.assertEqual(output, '2014-09')
        output = time_period(data, granularity='week', fieldname='the_field')
        self.assertEqual(output, '2014-Week-46')
        output = time_period(data, granularity='day', fieldname='the_field')
        self.assertEqual(output, '2014-09-27')
