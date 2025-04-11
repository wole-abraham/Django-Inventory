from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def replace(value, arg):
    return value.replace(arg, '')

@register.filter
def get_class(value):
    return value.__class__.__name__ 