from django import template

register = template.Library()

@register.filter
def sum(value, arg):
    return value + arg

@register.filter
def sub(value, arg):
    return value - arg
