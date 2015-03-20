import logging
import sys
from datetime import datetime, timedelta
from django.conf import settings
from django.db import models
from django.test import TestCase, override_settings
from django.utils import timezone
from dj_phab.queryset import DateGroupingQuerySet


if 'test' in sys.argv:
    # System will fallback to syncdb behavior -- which allows the sample model below
    # to have a DB table built
    settings.MIGRATION_MODULES = {
        'dj_phab': 'dj_phab.migrations_not_used_in_tests'
    }

class DGQSTestModel(models.Model):
    a_date = models.DateTimeField()
    value = models.PositiveIntegerField()

    objects = models.Manager.from_queryset(DateGroupingQuerySet)()


class TestDateGroupingQuerySet(TestCase):
    def setUp(self):
        self.tz = timezone.get_current_timezone()

    def make_models(self, count, interval):
        instances = []
        base_date = timezone.make_aware(datetime(2014, 1, 1), self.tz)
        for i in range(count):
            val = i * interval
            instances.append(DGQSTestModel(**{
                'a_date': base_date + timedelta(val),
                'value': val,
            }))
            logging.debug([i, val, base_date + timedelta(val)])
        DGQSTestModel.objects.bulk_create(instances)

    def test_smoke(self):
        pass

    def test_group_year(self):
        # 2 each in 2014, 2015, 2016, 2017
        # values 0, 200, 400, 600, 800, 1000, 1200, 1400
        # sums 200, 1000, 1800, 2600
        self.make_models(8, 200)
        sums = DGQSTestModel.objects.group_by_date('a_date', 'year')\
                            .annotate(sum=models.Sum('value'))
        tuples = [(row['a_date_year'], row['sum']) for row in sums]
        self.assertItemsEqual(tuples, [(2014, 200), (2015, 1000), (2016, 1800), (2017, 2600)])

    def test_group_month(self):
        # 2 each in 2014-01, 2014-02, 2014-03, 2014-04
        # values 0, 16, 32, 48, 64, 80, 96, 112
        # sums 16, 80, 144, 208
        self.make_models(8, 16)
        sums = DGQSTestModel.objects.group_by_date('a_date', 'month')\
                            .annotate(sum=models.Sum('value'))
        tuples = [(row['a_date_year'], row['a_date_month'], row['sum']) for row in sums]
        self.assertItemsEqual(tuples, [(2014, 1, 16),
                                       (2014, 2, 80),
                                       (2014, 3, 144),
                                       (2014, 4, 208)])

    def test_group_week(self):
        self.fail()

    def test_group_day(self):
        self.fail()

    def test_group_and_filter(self):
        self.fail()
