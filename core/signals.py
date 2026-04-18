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
                        "As an Innovator, here is what you can do:\n"
                        "  1. Post your projects and pitch them to investors\n"
                        "  2. Apply for collaboration requests from other users\n"
                        "  3. Track proposals and investor interest on your dashboard\n"
                        "  4. Connect with mentors and enrol in courses via the Training Hub"
                    )
                elif role == 'investor':
                    role_tips = (
                        "As an Investor, here is what you can do:\n"
                        "  1. Browse the Deal Flow and discover top-matched projects\n"
                        "  2. Send investment proposals directly to innovators\n"
                        "  3. Save projects and track your pipeline on your dashboard\n"
                        "  4. Request pitch meetings and review active collaborations"
                    )
                elif role == 'admin':
                    role_tips = (
                        "As an Admin, here is what you have access to:\n"
                        "  1. Manage users, projects, posts, and platform content\n"
                        "  2. Review flagged messages and reported content\n"
                        "  3. Monitor analytics and platform activity\n"
                        "  4. Access the admin panel at /admin-panel/"
                    )
                else:
                    role_tips = (
                        "You can explore the platform, connect with innovators and investors,\n"
                        "join groups, follow pages, and stay updated on upcoming events."
                    )

                Message.objects.create(
                    sender=odu,
                    recipient=instance,
                    conversation=conv,
                    content=(
                        f"Welcome to Oduma Corp, {full_name}.\n\n"
                        f"──────────────────────\n"
                        f"Account Details\n"
                        f"──────────────────────\n"
                        f"Name     : {full_name}\n"
                        f"Username : {instance.username}\n"
                        f"Email    : {instance.email}\n"
                        f"Role     : {role.title()}\n\n"
                        f"──────────────────────\n"
                        f"Getting Started\n"
                        f"──────────────────────\n"
                        f"{role_tips}\n\n"
                        f"Type /help at any time to see everything I can assist you with.\n"
                        f"— Odu, Platform Assistant"
                    ),
                )

                first_name = instance.first_name or full_name.split()[0] if full_name else 'there'
                Message.objects.create(
                    sender=odu,
                    recipient=instance,
                    conversation=conv,
                    content=(
                        f"One more thing, {first_name}.\n\n"
                        f"You've taken the first step by joining Oduma Corp.\n"
                        f"Now take the second — bring in someone you trust.\n\n"
                        f"Someone who:\n"
                        f"  • Challenges your thinking\n"
                        f"  • Adds real value\n"
                        f"  • Sees opportunities where others don't\n\n"
                        f"Ideas grow faster in the right environment.\n"
                        f"And the right environment starts with the right people.\n\n"
                        f"──────────────────────\n"
                        f"Share Oduma Corp\n"
                        f"──────────────────────\n"
                        f"  → Visit odumacorp.com\n"
                        f"  → Build together on odumacorp.com\n"
                        f"  → Grow your reach through odumacorp.com\n\n"
                        f"Forward this to one person today. That's all it takes.\n"
                        f"— Odu, Platform Assistant"
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