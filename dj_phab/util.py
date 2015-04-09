
def consolidate_time_period(data, granularity='month', fieldname='date_opened'):
    """
    Use granularity and field name to output a date as a single string in the
    appropriate format based on time period date parts in data.  Output format
    varies by granularity and is one of:

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


def annotate_dict(entries, add_key, new_data, new_data_key):
    """
    Adds sub-entries from one dict of dicts (``new_data``) to the entries  in another
    (``entries``) that are indexed by the same key.  Data can be retrieve from
    ``new_data`` sub-entries using a different key from that desired to be used in
    ``entries``.

    If ``entries`` is missing a key, a new entry will be added with that key.

    Example:
    >>> entries = { 1: { 'a': 'z', 'c': 'y' },
    ...             2: { 'a': 'x' },
    ...             3: { 'b': 'w', 'c': 'v' }, }
    >>> new_data = { 1: { 'd': 10 },
    ...              2: { 'c': 30, 'd': 40 },
    ...              4: { 'c': 50, 'd': 60 }, }
    >>> annotate_dict(entries, 'c', new_data, 'd')
    >>> entries
    { 1: { 'a': 'z', 'c': 10 },
      2: { 'a': 'x', 'c': 40 },
      3: { 'b': 'w', 'c': 'v' },
      4: { 'c': 60 }, }

    @param dict entries Dict to which to add data
    @param string add_key Key to be used for field in ``entries``
    @param dict new_data Dict from which to copy data
    @param new_data_key
    """
    for top_key, new in new_data.iteritems():
        entry_exists = False

        # not all keys will already be represented
        entry = entries.get(top_key, {})
        if len(entry.keys()):
            entry_exists = True

        # populate a new sub-entry from the new data
        entry[add_key] = new[new_data_key]

        # and insert the entry into entries if it doesn't already exist
        if not entry_exists:
            entries[top_key] = entry
