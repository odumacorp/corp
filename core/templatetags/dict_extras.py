import re
from django import template
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from django.templatetags.static import static

register = template.Library()


@register.simple_tag
def avatar_url(profile_or_user):
    """
    Return the best avatar URL for a user or UserProfile.
    Priority: uploaded photo → gender-based default → neutral default.
    """
    profile = None
    if hasattr(profile_or_user, 'userprofile'):
        profile = profile_or_user.userprofile
    elif hasattr(profile_or_user, 'profile_pics'):
        profile = profile_or_user
    if profile and profile.profile_pics:
        return profile.profile_pics.url
    gender = getattr(profile, 'gender', '') if profile else ''
    if gender == 'female':
        return static('images/avatar_female.png')
    return static('images/avatar_default.png')

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
    # A tag is "#" + ASCII letters/digits/_ (what the hashtags/<slug:tag>/ URL accepts), not
    # glued to a preceding word or path ("C#", "page#top") and not cut off mid-word ("#café").
    # re.split with one capturing group puts the matches at odd indices; only those are tags.
    # (Checking startswith('#') on every piece turned "# Heading ..." text into one giant link.)
    parts = re.split(r'(?<![\w/&])(#[A-Za-z0-9_]+)(?!\w)', text)
    out = []
    for i, part in enumerate(parts):
        if i % 2:
            tag = part[1:].lower()
            out.append(f'<a href="/hashtags/{tag}/" class="oc-hashtag">{conditional_escape(part)}</a>')
        else:
            out.append(conditional_escape(part) if autoescape else part)
    return mark_safe(''.join(out))
