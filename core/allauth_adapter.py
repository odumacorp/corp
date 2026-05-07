import re
from urllib.parse import urlparse, urlunparse

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


def _rewrite_to_site_url(url: str) -> str:
    """Replace the scheme+host in `url` with settings.SITE_URL so emails
    sent from localhost always contain production links."""
    from django.conf import settings
    site_url = getattr(settings, 'SITE_URL', '').rstrip('/')
    if not site_url:
        return url
    parsed_url = urlparse(url)
    parsed_site = urlparse(site_url)
    rewritten = parsed_url._replace(scheme=parsed_site.scheme, netloc=parsed_site.netloc)
    return urlunparse(rewritten)


class CoreAccountAdapter(DefaultAccountAdapter):
    def get_email_confirmation_url(self, request, emailconfirmation):
        url = super().get_email_confirmation_url(request, emailconfirmation)
        return _rewrite_to_site_url(url)


class CoreSocialAccountAdapter(DefaultSocialAccountAdapter):
    """Auto-generates username from Google name so the signup form never needs to ask for it."""

    def save_user(self, request, sociallogin, form=None):
        u = sociallogin.user

        # Build a unique username from the Google name/email before any adapter writes.
        if not u.username:
            first = (u.first_name or '').strip()
            last = (u.last_name or '').strip()
            base = re.sub(r'[^a-z0-9.]', '', f"{first}.{last}".lower()).strip('.')
            if not base:
                base = re.sub(r'[^a-z0-9]', '', (u.email or '').split('@')[0].lower()) or 'user'
            from core.models import CustomUser
            username = base
            counter = 1
            while CustomUser.objects.filter(username=username).exists():
                username = f"{base}{counter}"
                counter += 1
            u.username = username

        # Inject username/email into form.cleaned_data so account adapter.save_user
        # doesn't overwrite them with empty strings when the fields are absent from the form.
        if form is not None:
            if 'username' not in form.cleaned_data:
                form.cleaned_data['username'] = u.username
            if 'email' not in form.cleaned_data:
                form.cleaned_data['email'] = u.email

        return super().save_user(request, sociallogin, form)
