"""
Management command: python manage.py seed_data

Creates 7 dummy accounts with realistic African tech/innovation profiles:
- 3 innovators, 3 investors, 1 Odu system bot
- 5 posts + 5 projects each (for innovators)
- 5 companies, 5 pages, 5 groups
- Connections, likes, ratings between accounts
- Sends credentials summary to admin via Odu message
"""

import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.text import slugify

User = get_user_model()

INNOVATORS = [
    {
        'first_name': 'Amara', 'last_name': 'Diallo', 'email': 'amara.diallo@example.com',
        'password': 'Oduma2024!', 'user_type': 'innovator',
        'bio': 'Solar energy engineer building off-grid power solutions for rural West Africa.',
    },
    {
        'first_name': 'Chidi', 'last_name': 'Okafor', 'email': 'chidi.okafor@example.com',
        'password': 'Oduma2024!', 'user_type': 'innovator',
        'bio': 'Agri-tech founder developing smart irrigation systems for smallholder farmers.',
    },
    {
        'first_name': 'Zara', 'last_name': 'Mensah', 'email': 'zara.mensah@example.com',
        'password': 'Oduma2024!', 'user_type': 'innovator',
        'bio': 'Health-tech innovator building telemedicine platforms for underserved communities.',
    },
]

INVESTORS = [
    {
        'first_name': 'Kofi', 'last_name': 'Asante', 'email': 'kofi.asante@example.com',
        'password': 'Oduma2024!', 'user_type': 'investor',
        'bio': 'Pan-African impact investor focused on clean energy and agri-tech.',
    },
    {
        'first_name': 'Fatima', 'last_name': 'Ndiaye', 'email': 'fatima.ndiaye@example.com',
        'password': 'Oduma2024!', 'user_type': 'investor',
        'bio': 'VC fund manager specializing in health-tech and education innovations.',
    },
    {
        'first_name': 'Emeka', 'last_name': 'Eze', 'email': 'emeka.eze@example.com',
        'password': 'Oduma2024!', 'user_type': 'investor',
        'bio': 'Angel investor with exits in fintech and logistics across East Africa.',
    },
]

PROJECTS_BY_INDUSTRY = {
    'energy': [
        ('SolarMesh', 'Modular solar micro-grid for villages without grid access'),
        ('WindPulse', 'Small-scale wind turbines designed for coastal communities'),
        ('BioGasKit', 'Affordable biogas kit turning agricultural waste into cooking fuel'),
        ('SunStore', 'Community battery storage system for shared solar power'),
        ('LightGrid', 'IoT-enabled smart grid management for rural electrification'),
    ],
    'agriculture': [
        ('CropSense', 'Soil sensor network providing real-time crop health data'),
        ('IrriBot', 'Automated drip irrigation controlled by mobile SMS'),
        ('FarmLink', 'Marketplace connecting smallholder farmers directly to buyers'),
        ('SeedTrack', 'Blockchain traceability for seed supply chains'),
        ('AgroAI', 'AI crop disease diagnosis via smartphone camera'),
    ],
    'health': [
        ('TeleMed+', 'Low-bandwidth telemedicine platform for rural clinics'),
        ('MalaraGuard', 'Rapid malaria diagnostic kit with AI-assisted reading'),
        ('NutriPath', 'Personalised nutrition app for maternal health tracking'),
        ('VaxChain', 'Cold chain monitoring for vaccine storage in remote areas'),
        ('BirthAid', 'Mobile midwife assistant app for safe home deliveries'),
    ],
}

POSTS_TEMPLATES = [
    ('Looking for co-founders in {industry}',
     'I\'m building in the {industry} space and looking for passionate co-founders. DM me if interested.'),
    ('New milestone reached!',
     'Excited to share that our {industry} project just hit a major development milestone. Team is crushing it!'),
    ('Seeking investment partners',
     'Our {industry} startup is raising a seed round. We have traction and are looking for aligned investors.'),
    ('Lessons from the field',
     'Three things I learned after 6 months building in the {industry} sector in Africa. Thread below.'),
    ('Open to collaboration',
     'Working on a project in {industry} and would love to collaborate with others in the space. Let\'s connect!'),
]

COMPANY_DATA = [
    ('SolarGen Africa', 'energy', 'Renewable energy solutions for off-grid communities'),
    ('AgriTech Hub', 'agriculture', 'Technology-first agriculture advisory and investment platform'),
    ('HealthBridge', 'health', 'Digital health infrastructure for emerging markets'),
    ('FinEdge Capital', 'finance', 'Early-stage venture capital for African tech founders'),
    ('EduForward', 'education', 'EdTech company building adaptive learning for African schools'),
]

GROUP_DATA = [
    ('Solar Innovators Network', 'energy', 'Connecting solar entrepreneurs across Africa'),
    ('Agri-Tech Founders Circle', 'agriculture', 'Community for agri-tech founders and investors'),
    ('HealthTech Africa', 'health', 'Building the future of healthcare technology in Africa'),
    ('Impact Investors Hub', 'finance', 'Pan-African community of impact investors'),
    ('Women in Tech Africa', 'tech', 'Supporting women building tech companies across Africa'),
]

PAGE_DATA = [
    ('Oduma Connect Blog', 'tech', 'Official blog — stories, insights and platform updates'),
    ('African Innovation Weekly', 'tech', 'Curated newsletter on African tech and innovation'),
    ('Clean Energy Africa', 'energy', 'News and resources for clean energy projects in Africa'),
    ('Startup Funding Digest', 'finance', 'Funding news, grant opportunities and investor spotlights'),
    ('Healthtech Pulse Africa', 'health', 'Tracking health innovation across the continent'),
]


class Command(BaseCommand):
    help = 'Seed the database with 7 dummy accounts, posts, projects, companies, pages, and groups'

    def handle(self, *args, **options):
        from core.models import (
            UserProfile, Project, Post, Company, Group, Page,
            Connection, Rating, Notification, Message, Conversation,
            GroupMembership,
        )

        self.stdout.write('Seeding dummy data...')

        # 1. Create / get Odu system bot
        odu, _ = User.objects.get_or_create(
            username='odu',
            defaults={
                'first_name': 'Odu', 'last_name': 'Bot',
                'email': 'odu@odumacorp.com',
                'user_type': 'admin', 'is_staff': False,
            }
        )
        if not odu.has_usable_password():
            odu.set_password('OduBot#Internal9!')
            odu.save()

        # 2. Create innovators
        innovator_users = []
        for data in INNOVATORS:
            username = f"{data['first_name'].lower()}.{data['last_name'].lower()}"
            u, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': data['first_name'],
                    'last_name':  data['last_name'],
                    'email':      data['email'],
                    'user_type':  data['user_type'],
                    'bio':        data['bio'],
                }
            )
            if created:
                u.set_password(data['password'])
                u.save()
            innovator_users.append(u)

        # 3. Create investors
        investor_users = []
        for data in INVESTORS:
            username = f"{data['first_name'].lower()}.{data['last_name'].lower()}"
            u, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': data['first_name'],
                    'last_name':  data['last_name'],
                    'email':      data['email'],
                    'user_type':  data['user_type'],
                    'bio':        data['bio'],
                }
            )
            if created:
                u.set_password(data['password'])
                u.save()
            investor_users.append(u)

        all_users = innovator_users + investor_users

        # 4. Projects for each innovator (5 each)
        industries = list(PROJECTS_BY_INDUSTRY.keys())
        for idx, user in enumerate(innovator_users):
            industry = industries[idx % len(industries)]
            projects = PROJECTS_BY_INDUSTRY[industry]
            for title, desc in projects:
                proj, _ = Project.objects.get_or_create(
                    owner=user,
                    title=title,
                    defaults={
                        'description': desc,
                        'industry':    industry,
                        'status':      random.choice(['draft', 'in_progress', 'completed']),
                    }
                )
                # Ratings from investors
                for inv in investor_users:
                    Rating.objects.get_or_create(
                        project=proj, user=inv,
                        defaults={'value': random.randint(3, 5)}
                    )

        # 5. Posts for each user (5 each)
        for user in all_users:
            industry = random.choice(industries)
            for i, (title_t, content_t) in enumerate(POSTS_TEMPLATES):
                Post.objects.get_or_create(
                    user=user,
                    title=title_t.format(industry=industry),
                    defaults={
                        'content':  content_t.format(industry=industry),
                        'industry': industry,
                    }
                )

        # 6. Connections between users
        for i, u1 in enumerate(all_users):
            for u2 in all_users[i+1:]:
                Connection.objects.get_or_create(
                    initiator=u1, target=u2,
                    defaults={'status': 'accepted'}
                )

        # 7. Companies (5)
        for name, industry, desc in COMPANY_DATA:
            Company.objects.get_or_create(
                name=name,
                defaults={
                    'description': desc,
                    'industry':    industry,
                    'owner':       random.choice(all_users),
                }
            )

        # 8. Groups (5)
        for name, industry, desc in GROUP_DATA:
            grp, _ = Group.objects.get_or_create(
                name=name,
                defaults={
                    'description': desc,
                    'industry':    industry,
                    'creator':     random.choice(all_users),
                }
            )
            for user in all_users:
                grp.members.add(user)

        # 9. Pages (5)
        for title, industry, desc in PAGE_DATA:
            Page.objects.get_or_create(
                title=title,
                defaults={
                    'description': desc,
                    'industry':    industry,
                    'owner':       random.choice(all_users),
                }
            )

        # 10. Notifications welcome for each user
        for user in all_users:
            Notification.objects.get_or_create(
                user=user,
                message__startswith='Welcome',
                defaults={
                    'notification_type': 'other',
                    'message': f'Welcome to Oduma Connect, {user.first_name}! Your profile is set up.',
                    'link': '/app/',
                }
            )

        # 11. Send credentials summary to admin via Odu
        try:
            admin = User.objects.filter(is_superuser=True).first()
            if admin:
                cred_lines = ['Dummy account credentials:\n']
                for u in all_users:
                    cred_lines.append(f'  {u.user_type.upper()}: @{u.username} | {u.email} | Oduma2024!')
                cred_text = '\n'.join(cred_lines)
                conv, _ = Conversation.objects.get_or_create(
                    participants__in=[odu, admin],
                )
                if not conv.participants.filter(pk=odu.pk).exists():
                    conv.participants.add(odu, admin)
                Message.objects.create(
                    sender=odu, recipient=admin,
                    conversation=conv, content=cred_text,
                )
        except Exception:
            pass

        self.stdout.write(self.style.SUCCESS(
            f'Seeded: {len(innovator_users)} innovators, {len(investor_users)} investors, '
            f'5 companies, 5 groups, 5 pages. Done.'
        ))
