from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Get an item from a dictionary by key.
    Usage: {{ mydict|get_item:key }}
    """
    return dictionary.get(key) 