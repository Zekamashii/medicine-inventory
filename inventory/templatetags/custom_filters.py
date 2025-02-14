from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def map_inspection_times(value):
    times = set()
    for drug_records in value:
        for record in drug_records:
            times.add(record['inspection_time'])
    return sorted(times, reverse=True)


@register.filter
def abs_value(value):
    return abs(value)
