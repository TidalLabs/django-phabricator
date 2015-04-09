from django import template
from dj_phab.util import consolidate_time_period

register = template.Library()

@register.simple_tag
def time_period(data, granularity='month', fieldname='date_opened'):
    return consolidate_time_period(data, granularity=granularity, fieldname=fieldname)

@register.simple_tag
def lookup(data, key, default=''):
    return data.get(key, default)
