from .models import UserProfile, SiteSettings
from .models import Message
from .models import Notification

# def user_profile(request):
#     if request.user.is_authenticated:
#         try:
#             profile = request.user.userprofile
#         except UserProfile.DoesNotExist:
#             profile = UserProfile.objects.create(user=request.user)
#         return {'profile': profile}
#     return {}
from django.core.exceptions import ObjectDoesNotExist
def user_profile(request):
    if request.user.is_authenticated:
        try:
            profile = request.user.userprofile
        except ObjectDoesNotExist:
            profile = UserProfile.objects.create(user=request.user)
        return {'profile': profile}
    return {}

def unread_message_count(request):
    if request.user.is_authenticated:
        count = Message.objects.filter(recipient=request.user, is_read=False).count()
        return {'unread_count': count}
    return {}

def unread_notification_count(request):
    if request.user.is_authenticated:
        count = Notification.objects.filter(user=request.user, is_read=False).count()
        return {'unread_notification_count': count}
    return {}

def site_settings(request):
    s = SiteSettings.get()
    return {'pricing_enabled': s.pricing_enabled}

def admin_view_mode(request):
    """Exposes admin_view_mode ('admin' or 'user') to every template."""
    if request.user.is_authenticated and getattr(request.user, 'user_type', None) == 'admin':
        mode = request.session.get('admin_view_mode', 'admin')
        return {'admin_view_mode': mode}
    return {'admin_view_mode': None}
