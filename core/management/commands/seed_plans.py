"""
Management command: seed subscription plans.
Run once: python manage.py seed_plans
"""
from django.core.management.base import BaseCommand
from core.models import SubscriptionPlan


PLANS = [
    {
        'slug': 'starter',
        'name': 'Starter',
        'tagline': 'Perfect for getting started',
        'description': 'Explore the platform and start building your network.',
        'price_monthly': 0,
        'price_yearly': 0,
        'max_projects': 3,
        'max_connections': 20,
        'max_company_pages': 0,
        'order': 1,
        'features': [
            'Up to 3 projects',
            'Up to 20 connections',
            'Basic profile page',
            'Community feed access',
            'Join up to 3 groups',
            'Basic messaging',
            'Browse innovators & investors',
        ],
    },
    {
        'slug': 'pro',
        'name': 'Pro',
        'tagline': 'For serious innovators & investors',
        'description': 'Unlock unlimited projects, meetings, and advanced networking.',
        'price_monthly': 19,
        'price_yearly': 190,
        'max_projects': 0,
        'max_connections': 0,
        'max_company_pages': 1,
        'order': 2,
        'features': [
            'Unlimited projects',
            'Unlimited connections',
            'Zoom video meetings',
            'Send & receive proposals',
            'Access mentorship',
            'Investment readiness analytics',
            'Priority search placement',
            '1 company page',
            'Advanced profile badge',
            'Email support',
        ],
    },
    {
        'slug': 'business',
        'name': 'Business',
        'tagline': 'For teams, companies & power users',
        'description': 'Full platform access with team collaboration and premium support.',
        'price_monthly': 49,
        'price_yearly': 490,
        'max_projects': 0,
        'max_connections': 0,
        'max_company_pages': -1,
        'order': 3,
        'features': [
            'Everything in Pro',
            'Unlimited company pages',
            'Consulting service access',
            'Featured listing in directories',
            'Team accounts (up to 5 seats)',
            'Advanced analytics dashboard',
            'Priority support',
            'Early access to new features',
            'Custom profile branding',
        ],
    },
]


class Command(BaseCommand):
    help = 'Seed subscription plans (Starter, Pro, Business)'

    def handle(self, *args, **kwargs):
        for data in PLANS:
            plan, created = SubscriptionPlan.objects.update_or_create(
                slug=data['slug'],
                defaults=data,
            )
            status = 'Created' if created else 'Updated'
            self.stdout.write(self.style.SUCCESS(f'{status}: {plan.name}'))

        self.stdout.write(self.style.SUCCESS('\nDone! Subscription plans seeded.'))
