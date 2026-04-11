import re
from django import template
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Returns dictionary[key], or None if missing."""
    if dictionary is None:
        return None
    return dictionary.get(key)


@register.filter(needs_autoescape=True)
def linkify_hashtags(value, autoescape=True):
    """Convert #hashtag tokens to clickable links."""
    if not value:
        return value
    escaped = conditional_escape(str(value)) if autoescape else str(value)
    def _replace(m):
        tag = m.group(1).lower()
        display = m.group(1)
        return f'<a href="/hashtags/{tag}/" class="oc-hashtag">#{display}</a>'
    return mark_safe(re.sub(r'#(\w+)', _replace, escaped))
