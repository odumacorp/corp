from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Returns dictionary[key], or None if missing."""
    if dictionary is None:
        return None
    return dictionary.get(key)
