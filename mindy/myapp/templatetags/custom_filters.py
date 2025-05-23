from django import template

register = template.Library()

@register.filter
def get_dynamic(obj, name):
    return getattr(obj, name, '')