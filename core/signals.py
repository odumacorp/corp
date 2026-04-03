from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import CustomUser, UserProfile, Notification, Message, Conversation
# from .models import Profile

# @receiver(post_save, sender=User)
# def create_profile(sender, instance, created, **kwargs):
#     if created:
#         UserProfile.objects.create(user=instance)

# @receiver(post_save, sender=User)
# def save_profile(sender, instance, **kwargs):
#     instance.profile.save()


# @receiver(post_save, sender=CustomUser)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         UserProfile.objects.create(user=instance)

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if not hasattr(instance, 'userprofile'):
            UserProfile.objects.create(user=instance)
        # Welcome notification
        try:
            Notification.objects.create(
                user=instance,
                notification_type='other',
                message=(
                    f"Welcome to Oduma Connect, {instance.first_name or instance.username}! "
                    "Your account is ready. Explore innovators and investors, post your projects, "
                    "and start connecting. Click 'Network' to find your first connection."
                ),
                link='/app/',
            )
        except Exception:
            pass
        # Welcome message from system Odu user
        try:
            odu = CustomUser.objects.filter(username='odu').first()
            if odu:
                conv = Conversation.objects.create()
                conv.participants.add(odu, instance)
                Message.objects.create(
                    sender=odu,
                    recipient=instance,
                    conversation=conv,
                    content=(
                        f"Hi {instance.first_name or instance.username}, I'm Odu — your Oduma Connect assistant! "
                        "I'm here to help you navigate the platform, answer questions, and connect you with the right people. "
                        "To get started: post a project, explore the Innovators page, or send a connection request. "
                        "Type /help anytime in this chat to see what I can do."
                    ),
                )
        except Exception:
            pass

@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.userprofile.save()  # Save the associated UserProfile after CustomUser is saved
    except UserProfile.DoesNotExist:
        # This ensures that even if the profile doesn't exist, it gets created
        UserProfile.objects.create(user=instance)