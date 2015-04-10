"""
Custom QuerySet classes

@TODO: Release DateGroupingQuerySet as a totally separate open source module
"""
try:
    # Django 1.8+
    from django.core.exceptions import FieldDoesNotExist
except ImportError:
    # Django 1.7-
    from django.db.models import FieldDoesNotExist

from django.db import models
from dj_phab.defaults import get_granularities

class FieldTypeError(Exception):
    pass


class GranularityError(ValueError):
    pass


class DateGroupingQuerySet(models.QuerySet):
    """
    QuerySet capable of grouping aggregates by a part of a date field
    (e.g. group by year, group by year and month, group by year and week within year,
    etc.)

    Exposes a single ``group_by_date()` method that takes a field name and
    level of grouping granularity and returns a ValuesQuerySet annotated with
    and grouped by the date parts, ready for aggregates to be assigned.
    """

    def _is_datefield(self, fieldname):
        """
        Determine whether the model field with the given name is a date or datetime
        field -- i.e. one that we can actually determine the year, month, etc. of

        @param str fieldname Name of field to check
        @return bool Whether the field is a date/datetime
        """
        try:
            # technically, Options.get_field() was formalized in
            # Django 1.8, but it works in 1.7
            field = self.model._meta.get_field(fieldname)
            return field.get_internal_type() in ['DateField', 'DateTimeField',]
        except FieldDoesNotExist:
            return False

    def _annotate_count(self, fieldname):
        return self

    def _augment_values(self, *fieldnames):
        """
        Add fields to values returned / grouped by in queryset instead of replacing
        list of fields already indicated

        @param str* fieldname Name of field to add to query
        @return ValuesQuerySet
        """
        if hasattr(self, '_fields'):
            # clone fields list
            fields = self._fields[:]
            for fieldname in fieldnames:
                if fieldname not in self.fields:
                    fields.append(fieldname)
        else:
            fields = fieldnames

        return self.values(*fields)

    def _year_select(self, fieldname):
        return ('%s_year' % fieldname), ('EXTRACT(year FROM %s)' % fieldname)

    def _month_select(self, fieldname):
        return ('%s_month' % fieldname), ('EXTRACT(month FROM %s)' % fieldname)

    def _week_select(self, fieldname):
        return ('%s_week' % fieldname), ('EXTRACT(week FROM %s)' % fieldname)

    def _day_select(self, fieldname):
        return ('%s_day' % fieldname), ('EXTRACT(day FROM %s)' % fieldname)

    def _group_by_year(self, fieldname):
        year_part_name, year_sql = self._year_select(fieldname)
        return self.extra(select={ year_part_name: year_sql,})\
                   ._augment_values(year_part_name)\
                   .order_by(year_part_name)

    def _group_by_year_month(self, fieldname):
        year_part_name, year_sql = self._year_select(fieldname)
        month_part_name, month_sql = self._month_select(fieldname)
        return self.extra(select={
                        year_part_name: year_sql,
                        month_part_name: month_sql,
                   })\
                   ._augment_values(year_part_name, month_part_name)\
                   .order_by(year_part_name, month_part_name)

    def _group_by_year_week(self, fieldname):
        year_part_name, year_sql = self._year_select(fieldname)
        week_part_name, week_sql = self._week_select(fieldname)
        return self.extra(select={
                        year_part_name: year_sql,
                        week_part_name: week_sql,
                   })\
                   ._augment_values(year_part_name, week_part_name)\
                   .order_by(year_part_name, week_part_name)

    def _group_by_day(self, fieldname):
        year_part_name, year_sql = self._year_select(fieldname)
        month_part_name, month_sql = self._month_select(fieldname)
        day_part_name, day_sql = self._day_select(fieldname)
        return self.extra(select={
                        year_part_name: year_sql,
                        month_part_name: month_sql,
                        day_part_name: day_sql,
                   })\
                   ._augment_values(year_part_name, month_part_name, day_part_name)\
                   .order_by(year_part_name, month_part_name, day_part_name)

    def group_by_date(self, fieldname, granularity):
        """
        Generate a copy of the queryset with `.values()` adjusted to group aggregates
        by the field indicated, with the granularity indicated.

        If granularity is unrecognized, will raise a GranularityError.

        If fieldname is not a DateTimeField, will raise FieldTypeError.

        @param str fieldname Name of field to group on
        @param str granularity Granularity of grouping: one of "year", "month", "week", "day"
        @return ValuesQuerySet
        """
        valid_granularities = get_granularities()

        if not self._is_datefield(fieldname):
            raise FieldTypeError(u"Cannot group by '%s': not a DateField or DateTimeField" % fieldname)

        if granularity == 'day':
            return self._group_by_day(fieldname)
        elif granularity == 'week':
            return self._group_by_year_week(fieldname)
        elif granularity == 'month':
            return self._group_by_year_month(fieldname)
        elif granularity == 'year':
            return self._group_by_year(fieldname)
        else:
            gran_strings = ['"%s"' % gran for gran in granularities]
        raise GranularityError(u"Granularity '%s' not recognized. Please supply one of %s." % \
                                    ', '.join(gran_strings))
