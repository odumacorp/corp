from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os

class Command(BaseCommand):
    help = "Create or update default admin user"

    def handle(self, *args, **kwargs):
        User = get_user_model()

        username = os.getenv("DJANGO_SUPERUSER_USERNAME")
        email = os.getenv("DJANGO_SUPERUSER_EMAIL")
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD")

        if not username or not password:
            self.stdout.write(self.style.ERROR("Missing environment variables"))
            return

        # user, created = User.objects.get_or_create(
        #     username=username,
        #     defaults={
        #         "email": email,
        #         "role": "admin",  # 🔥 CRITICAL if you use roles
        #         "user_type": "Admin",
        #         },
            
            
        # )

        # user.set_password(password)
        # user.is_superuser = True
        # user.is_staff = True
        # # 🔥 force correct role even if user already exists
        # # if hasattr(user, "role"):
        # #     user.role = "admin"
        # if hasattr(user, "user_type"):
        #     user.user_type = "Admin"
        # user.save()


        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "email": email,
                "user_type": "Admin",
            },
        )

        user.set_password(password)
        user.is_superuser = True
        user.is_staff = True

        # Force correct role even if user already exists
        if hasattr(user, "user_type"):
            user.user_type = "Admin"

        user.save()

        if created:
            self.stdout.write(self.style.SUCCESS("Superuser created"))
        else:
            self.stdout.write(self.style.SUCCESS("Superuser updated"))