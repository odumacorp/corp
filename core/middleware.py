EXCLUDED_PREFIXES = (
    '/static/', '/media/', '/django-admin/', '/favicon',
    '/accounts/social/', '/__debug__/', '/admin/track-click/',
)


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
