"""
Management command: reset_to_test_users

Wipes ALL app data and creates exactly three users:
  - admin   / Admin@oduma1    (superuser, user_type='admin')
  - investor / Investor@test1  (user_type='investor')
  - innovator / Innovator@test1 (user_type='innovator')

Usage:
    python manage.py reset_to_test_users
    python manage.py reset_to_test_users --yes   # skip confirmation
"""

from django.core.management.base import BaseCommand
from django.db import connection, transaction


class Command(BaseCommand):
    help = "Wipe all app data and seed admin + two test users."

    def add_arguments(self, parser):
        parser.add_argument(
            "--yes", action="store_true",
            help="Skip confirmation prompt"
        )

    def handle(self, *args, **options):
        if not options["yes"]:
            confirm = input(
                "\n⚠️  This will DELETE ALL data in the database and create 3 test users.\n"
                "Type 'yes' to continue: "
            )
            if confirm.strip().lower() != "yes":
                self.stdout.write(self.style.WARNING("Aborted."))
                return

        self.stdout.write("Clearing all data...")
        self._wipe()
        self.stdout.write(self.style.SUCCESS("✓ All data cleared."))

        self.stdout.write("Creating users...")
        self._seed()
        self.stdout.write(self.style.SUCCESS("✓ Done. Users created:"))
        self.stdout.write("  admin      /  Admin@oduma1     (superuser)")
        self.stdout.write("  investor   /  Investor@test1   (investor)")
        self.stdout.write("  innovator  /  Innovator@test1  (innovator)")

    # ------------------------------------------------------------------
    def _wipe(self):
        """Delete all rows from every app table using TRUNCATE CASCADE."""
        with connection.cursor() as cur:
            # Collect every table managed by our app
            cur.execute("""
                SELECT tablename FROM pg_tables
                WHERE schemaname = 'public'
                  AND tablename NOT IN (
                      'django_migrations',
                      'django_content_type',
                      'auth_permission',
                      'auth_group',
                      'auth_group_permissions',
                      'auth_user_groups',
                      'auth_user_user_permissions'
                  )
                ORDER BY tablename;
            """)
            tables = [row[0] for row in cur.fetchall()]
            if tables:
                quoted = ", ".join(f'"{t}"' for t in tables)
                cur.execute(f"TRUNCATE TABLE {quoted} RESTART IDENTITY CASCADE;")

    # ------------------------------------------------------------------
    def _seed(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()

        # --- Admin ---
        admin = User.objects.create_superuser(
            username="admin",
            email="admin@odumacorp.com",
            password="Admin@oduma1",
            first_name="Oduma",
            last_name="Admin",
        )
        admin.user_type = "admin"
        admin.save()

        # --- Investor ---
        investor = User.objects.create_user(
            username="investor",
            email="investor@odumacorp.com",
            password="Investor@test1",
            first_name="Test",
            last_name="Investor",
        )
        investor.user_type = "investor"
        investor.save()

        # --- Innovator ---
        innovator = User.objects.create_user(
            username="innovator",
            email="innovator@odumacorp.com",
            password="Innovator@test1",
            first_name="Test",
            last_name="Innovator",
        )
        innovator.user_type = "innovator"
        innovator.save()

        # Ensure UserProfile exists for each (signals may create them,
        # but we guarantee it here in case signals didn't fire after TRUNCATE)
        from core.models import UserProfile
        for user in [admin, investor, innovator]:
            UserProfile.objects.get_or_create(user=user)

        # Send Odu welcome message to investor + innovator
        try:
            self._send_odu_welcome(investor)
            self._send_odu_welcome(innovator)
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"  (Odu welcome skipped: {e})"))

    def _send_odu_welcome(self, user):
        from django.contrib.auth import get_user_model
        from core.models import Conversation, Message
        User = get_user_model()

        try:
            odu = User.objects.get(username="Odu")
        except User.DoesNotExist:
            # Create Odu bot if missing
            odu = User.objects.create_user(
                username="Odu",
                email="odu@odumacorp.com",
                password=User.objects.make_random_password(),
                first_name="Odu",
                last_name="Bot",
            )
            odu.user_type = "admin"
            odu.save()

        conv, _ = Conversation.objects.get_or_create_for_users(odu, user) if hasattr(
            Conversation.objects, "get_or_create_for_users"
        ) else Conversation.objects.get_or_create(
            **{
                "participants__in": [odu, user],
            }
        )

        # Simpler: just create conversation properly
        conv = Conversation.objects.filter(
            participants=odu
        ).filter(participants=user).first()

        if not conv:
            conv = Conversation.objects.create()
            conv.participants.add(odu, user)

        Message.objects.create(
            conversation=conv,
            sender=odu,
            recipient=user,
            content=(
                f"👋 Welcome to Oduma Corp, {user.first_name}! "
                "I'm Odu, your platform assistant. "
                "Feel free to explore — I'm here if you need guidance."
            ),
        )
