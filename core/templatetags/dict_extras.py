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
    text = str(value)
    parts = re.split(r'(#\w+)', text)
    out = []
    for part in parts:
        if part.startswith('#') and len(part) > 1:
            tag = part[1:].lower()
            out.append(f'<a href="/hashtags/{tag}/" class="oc-hashtag">{part}</a>')
        else:
            out.append(conditional_escape(part) if autoescape else part)
    return mark_safe(''.join(out))
