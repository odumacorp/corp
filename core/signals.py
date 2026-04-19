from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import CustomUser, UserProfile, Notification, Message, Conversation, SubscriptionPlan, UserSubscription
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
                    f"Welcome to Oduma Corp, {instance.first_name or instance.username}! "
                    "Your account is ready. Explore innovators and investors, post your projects, "
                    "and start connecting. Click 'Network' to find your first connection."
                ),
                link='/app/',
            )
        except Exception:
            pass
        # Welcome message from system Odu user
        try:
            odu = CustomUser.objects.filter(username__iexact='odu').first()
            if odu:
                conv = Conversation.objects.create()
                conv.participants.add(odu, instance)

                full_name = instance.get_full_name() or instance.username
                role = instance.user_type or 'member'

                if role == 'innovator':
                    role_tips = (
                        "As an innovator, you can post your projects, pitch to investors, "
                        "collaborate with other builders, and track every proposal through your dashboard. "
                        "The Training Hub also has courses and mentorship to help you grow faster."
                    )
                elif role == 'investor':
                    role_tips = (
                        "As an investor, you can browse the deal flow, discover projects matched to your interests, "
                        "send proposals directly to innovators, and schedule pitch meetings — all in one place. "
                        "Your dashboard keeps your pipeline organised."
                    )
                elif role == 'admin':
                    role_tips = (
                        "You have full access to the admin panel at /admin-panel/ — "
                        "manage users, review projects and content, monitor platform activity, "
                        "and keep the community running smoothly."
                    )
                else:
                    role_tips = (
                        "You can explore the platform, connect with innovators and investors, "
                        "join groups, follow pages, and stay updated on upcoming events."
                    )

                Message.objects.create(
                    sender=odu,
                    recipient=instance,
                    conversation=conv,
                    content=(
                        f"Hey {full_name}, great to have you here.\n\n"
                        f"Your account is live — here are your login details:\n\n"
                        f"Email: {instance.email}\n"
                        f"Username: {instance.username}\n\n"
                        f"{role_tips}\n\n"
                        f"If you ever need help navigating the platform, just send me a message."
                    ),
                )

                first_name = instance.first_name or full_name.split()[0] if full_name else 'there'
                Message.objects.create(
                    sender=odu,
                    recipient=instance,
                    conversation=conv,
                    content=(
                        f"One more thing, {first_name} — the best opportunities on Oduma Corp come through connections.\n\n"
                        f"Think of one person who should be here. A fellow innovator, a potential investor, "
                        f"or someone who would benefit from what this platform offers.\n\n"
                        f"Share your referral link with them: odumacorp.com\n\n"
                        f"The right people make all the difference."
                    ),
                )
        except Exception:
            pass

@receiver(post_save, sender=CustomUser)
def create_user_subscription(sender, instance, created, **kwargs):
    """Auto-assign Starter plan to every new user."""
    if created:
        try:
            free_plan = SubscriptionPlan.objects.get(slug='starter')
            UserSubscription.objects.get_or_create(user=instance, defaults={'plan': free_plan})
        except Exception:
            pass

@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.userprofile.save()  # Save the associated UserProfile after CustomUser is saved
    except UserProfile.DoesNotExist:
        # This ensures that even if the profile doesn't exist, it gets created
        UserProfile.objects.create(user=instance)