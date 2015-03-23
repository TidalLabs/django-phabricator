from django import template

register = template.Library()

@register.simple_tag
def time_period(data, granularity='month', fieldname='date_opened'):
    """
    Use granularity and field name to output a date in the appropriate format based on
    time period date parts in data.  Output format varies by granularity and is one of:

    * YYYY [year]
    * YYYY-MM [month]
    * YYYY-MM-DD [day]
    * YYYY-W [week]

    @param dict data Row returned by DateGroupingQuerySet
    @param 'year'|'month'|'week'|'day' granularity What time period the data is grouped by
    @param str fieldname Name of the model field from which to calculate dict keys

    @return str Formatted date
    """
    if granularity not in ('year', 'month', 'week', 'day'):
        raise ValueError('Granularity must be one of "year", "month", "week", or "day"')

    year_fieldname = '%s_year' % fieldname
    month_fieldname = '%s_month' % fieldname
    week_fieldname = '%s_week' % fieldname
    day_fieldname = '%s_day' % fieldname

    if (not year_fieldname in data)\
            or (granularity in ('month', 'day') and not month_fieldname in data)\
            or (granularity == 'week' and not week_fieldname in data)\
            or (granularity == 'day' and not day_fieldname in data):
        return ''

    if granularity == 'year':
        return '%d' % data[year_fieldname]
    if granularity == 'month':
        return '%d-%02d' % (data[year_fieldname], data[month_fieldname])
    if granularity == 'week':
        return '%d-Week-%02d' % (data[year_fieldname], data[week_fieldname])
    else:
        # granularity is 'day'
        return '%d-%02d-%02d' % (data[year_fieldname], data[month_fieldname], data[day_fieldname])
