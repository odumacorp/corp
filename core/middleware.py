import time

EXCLUDED_PREFIXES = (
    '/static/', '/media/', '/django-admin/', '/favicon',
    '/accounts/social/', '/__debug__/', '/admin/track-click/',
)

# ── SitePage visibility cache ────────────────────────────────────────────────
# Avoids a DB round-trip on every request. Refreshes every 60 seconds.
_SITEPAGE_CACHE: dict = {}      # key → is_active
_SITEPAGE_CACHE_TS: float = 0.0 # last-populated timestamp
_SITEPAGE_TTL = 60              # seconds

def _sitepage_is_active(key: str) -> bool:
    """Return True if the named page is active (or not registered)."""
    global _SITEPAGE_CACHE, _SITEPAGE_CACHE_TS
    now = time.monotonic()
    if now - _SITEPAGE_CACHE_TS > _SITEPAGE_TTL:
        try:
            from .models import SitePage
            _SITEPAGE_CACHE = {p.key: p.is_active for p in SitePage.objects.only('key', 'is_active')}
            _SITEPAGE_CACHE_TS = now
        except Exception:
            return True
    return _SITEPAGE_CACHE.get(key, True)  # not registered = active


def _parse_ua(ua_string):
    """Returns (device_type, browser, os) from a user-agent string."""
    try:
        import user_agents
        ua = user_agents.parse(ua_string or '')
        if ua.is_bot:
            device = 'bot'
        elif ua.is_mobile:
            device = 'mobile'
        elif ua.is_tablet:
            device = 'tablet'
        elif ua.is_pc:
            device = 'desktop'
        else:
            device = 'other'
        browser = ua.browser.family or ''
        os_name = ua.os.family or ''
        return device, browser[:100], os_name[:100]
    except Exception:
        return '', '', ''


def _get_ip(request):
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR', '')
    return forwarded.split(',')[0].strip() or request.META.get('REMOTE_ADDR') or None


class PageVisibilityMiddleware:
    """Intercepts requests to disabled site pages and returns the page_disabled view."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        # Skip admin paths entirely
        if request.path.startswith('/admin-panel/') or request.path.startswith('/django-admin/'):
            return None
        try:
            url_name = request.resolver_match.url_name if request.resolver_match else None
            if url_name and not _sitepage_is_active(url_name):
                # Fetch label/message only when page is actually disabled (rare)
                try:
                    from .models import SitePage
                    page = SitePage.objects.only('label', 'disabled_message').get(key=url_name)
                    from django.shortcuts import render
                    return render(request, 'page_disabled.html', {
                        'page_label': page.label,
                        'disabled_message': page.disabled_message,
                    }, status=410)
                except Exception:
                    pass
        except Exception:
            pass
        return None


class AnalyticsMiddleware:
    """Records every GET page view to the PageView model."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if (
            request.method == 'GET'
            and response.status_code == 200
            and not any(request.path.startswith(p) for p in EXCLUDED_PREFIXES)
        ):
            try:
                from .models import PageView
                ip = _get_ip(request)
                ua_string = request.META.get('HTTP_USER_AGENT', '')
                device_type, browser, os_name = _parse_ua(ua_string)
                referrer = request.META.get('HTTP_REFERER', '')[:500]
                PageView.objects.create(
                    path=request.path,
                    user=request.user if request.user.is_authenticated else None,
                    session_key=request.session.session_key or '',
                    ip_address=ip or None,
                    device_type=device_type,
                    browser=browser,
                    os=os_name,
                    referrer=referrer,
                )
            except Exception:
                pass

        return response
