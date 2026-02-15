from .models import UserProfile
from .models import Message

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
