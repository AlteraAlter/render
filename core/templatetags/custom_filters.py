from django import template

register = template.Library()


@register.filter
def remove_whitespace(value):
    if isinstance(value, str):
        return value.replace(" ", "")
    return value
