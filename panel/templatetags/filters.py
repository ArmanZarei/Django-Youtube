from django import template

register = template.Library()


@register.filter
def split(x, sep):
    return x.split(sep)


@register.filter
def strip(x):
    return x.strip()
