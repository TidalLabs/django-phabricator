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


class FieldTypeError(Exception):
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
            field = self.model._meta.get_field(fieldname)
            return field.get_internal_type() in ['DateTimeField', 'DateTimeField',]
        except FieldDoesNotExist:
            return False

    def _annotate_count(self, fieldname):
        return self

    def _augment_values(self, fieldname):
        """
        Add field to values returned / grouped by in queryset instead of replacing
        list of fields already indicated

        @param str fieldname Name of field to add to query
        @return ValuesQuerySet
        """
        if hasattr(self, '_fields') and fieldname not in self._fields:
            fields = self._fields
            fields.append(fieldname)
        else:
            fields = [fieldname]
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
        return self.extra(select={ year_part_name: year_sql,})._augment_values(year_part_name)

    def _group_by_year_month(self, fieldname):
        year_part_name, year_sql = self._year_select(fieldname)
        month_part_name, month_sql = self._month_select(fieldname)
        return self.extra(select={
                        year_part_name: year_sql,
                        month_part_name: month_sql,
                   })\
                   ._augment_values(year_part_name, month_part_name)

    def _group_by_year_month_week(self, fieldname):
        year_part_name, year_sql = self._year_select(fieldname)
        week_part_name, week_sql = self._week_select(fieldname)
        return self.extra(select={
                        year_part_name: year_sql,
                        week_part_name: week_sql,
                   })\
                   ._augment_values(year_part_name, week_part_name)

    def _group_by_date(self, fieldname):
        year_part_name, year_sql = self._year_select(fieldname)
        month_part_name, month_sql = self._month_select(fieldname)
        day_part_name, day_sql = self._day_select(fieldname)
        return self.extra(select={
                        year_part_name: year_sql,
                        month_part_name: month_sql,
                        day_part_name: day_sql,
                   })\
                   ._augment_values(year_part_name, month_part_name, day_part_name)

    def group_by_date(self, fieldname, granularity):
        """
        Generate a copy of the queryset with `.values()` adjusted to group aggregates
        by the field indicated, with the granularity indicated.

        If granularity is unrecognized, will be a no-op.

        If fieldname is not a DateTimeField, will raise FieldTypeError.

        @param str fieldname Name of field to group on
        @param str granularity Granularity of grouping: one of "year", "month", "week", "day"
        @return ValuesQuerySet
        """
        if not self._is_datefield(fieldname):
            raise FieldTypeError(u"Cannot group by %s: not a DateField or DateTimeField" % fieldname)

        if granularity == 'day':
            return self._group_by_date(fieldname)
        elif granularity == 'week':
            return self._group_by_week(fieldname)
        elif granularity == 'month':
            return self._group_by_month(fieldname)
        elif granularity == 'year':
            return self._group_by_year(fieldname)
        else:
            return self
