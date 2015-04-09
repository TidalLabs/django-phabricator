from django.conf import settings
from django.test import TestCase
from dj_phab.util import consolidate_time_period, annotate_dict


class TestTimePeriod(TestCase):
    def smoke(self):
        pass

    def test_consolidate_time_period(self):
        data = {
            'the_field_year': 2014.0,
            'the_field_month': 9.0,
            'the_field_week': 46.0,
            'the_field_day': 27.0,
        }

        output = consolidate_time_period(data, granularity='year', fieldname='the_field')
        self.assertEqual(output, '2014')
        output = consolidate_time_period(data, granularity='month', fieldname='the_field')
        self.assertEqual(output, '2014-09')
        output = consolidate_time_period(data, granularity='week', fieldname='the_field')
        self.assertEqual(output, '2014-Week-46')
        output = consolidate_time_period(data, granularity='day', fieldname='the_field')
        self.assertEqual(output, '2014-09-27')

    def test_annotate_dict(self):
        entries = { 1: { 'a': 'z', 'c': 'y' },
                    2: { 'a': 'x' },
                    3: { 'b': 'w', 'c': 'v' }, }

        new_data = { 1: { 'd': 10 },
                     2: { 'c': 30, 'd': 40 },
                     4: { 'c': 50, 'd': 60 }, }

        expected = { 1: { 'a': 'z', 'c': 10 },
                     2: { 'a': 'x', 'c': 40 },
                     3: { 'b': 'w', 'c': 'v' },
                     4: { 'c': 60 }, }

        annotate_dict(entries, 'c', new_data, 'd')

        self.assertDictEqual(entries, expected)
