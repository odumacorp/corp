from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import CustomUser, UserProfile
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
    if created:  # Only create a UserProfile for newly created users
        if not hasattr(instance, 'userprofile'):  # Ensure no duplicate profile
            UserProfile.objects.create(user=instance)

@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.userprofile.save()  # Save the associated UserProfile after CustomUser is saved
    except UserProfile.DoesNotExist:
        # This ensures that even if the profile doesn't exist, it gets created
        UserProfile.objects.create(user=instance)