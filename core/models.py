from django.contrib.auth.models import AbstractUser

from django.db import models
from django.conf import settings
from django.utils import timezone
# from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
# from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

from django.core.exceptions import ValidationError

# ── Canonical industry list (used by all models that have an industry field) ──
INDUSTRY_CHOICES = [
    ('tech',           'Technology'),
    ('finance',        'Finance & Banking'),
    ('health',         'Healthcare'),
    ('edu',            'Education'),
    ('energy',         'Energy & Utilities'),
    ('agriculture',    'Agriculture & Farming'),
    ('manufacturing',  'Manufacturing'),
    ('media',          'Media & Entertainment'),
    ('retail',         'Retail & E-commerce'),
    ('real_estate',    'Real Estate & Construction'),
    ('transport',      'Transportation & Logistics'),
    ('food',           'Food & Beverage'),
    ('hospitality',    'Tourism & Hospitality'),
    ('telecom',        'Telecommunications'),
    ('legal',          'Legal & Compliance'),
    ('consulting',     'Consulting & Professional Services'),
    ('marketing',      'Marketing & Advertising'),
    ('hr',             'Human Resources & Staffing'),
    ('government',     'Government & Public Sector'),
    ('nonprofit',      'Non-Profit & NGO'),
    ('sports',         'Sports & Recreation'),
    ('fashion',        'Fashion & Apparel'),
    ('automotive',     'Automotive'),
    ('aerospace',      'Aerospace & Defense'),
    ('mining',         'Mining & Metals'),
    ('chemicals',      'Chemicals & Materials'),
    ('biotech',        'Biotechnology'),
    ('cybersecurity',  'Cybersecurity'),
    ('ai',             'Artificial Intelligence'),
    ('cleantech',      'Environmental & Clean Tech'),
    ('insurance',      'Insurance'),
    ('pharma',         'Pharmaceuticals'),
    ('design',         'Architecture & Design'),
    ('research',       'Research & Development'),
    ('other',          'Other'),
]


    
class Invention(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


class Event(models.Model):
    EVENT_TYPES = [
        ('general',          'General Event'),
        ('demo_day',         'Demo Day'),
        ('investor_meetup',  'Investor Meetup'),
        ('workshop',         'Workshop'),
        ('conference',       'Conference'),
        ('networking',       'Networking'),
        ('webinar',          'Webinar'),
    ]
    name        = models.CharField(max_length=255)
    date        = models.DateField()
    location    = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    organizer   = models.CharField(max_length=255, blank=True, default='')
    image       = models.ImageField(upload_to='event_images/', blank=True, null=True)
    is_hidden   = models.BooleanField(default=False)
    event_type  = models.CharField(max_length=20, choices=EVENT_TYPES, default='general')
    is_featured = models.BooleanField(default=False)
    max_attendees = models.PositiveIntegerField(null=True, blank=True)
    created_by  = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_events')

# User model with Investor/Innovator roles
    
class CustomUser(AbstractUser):
    USER_TYPES = (
        ('innovator', 'Innovator'),
        ('investor', 'Investor'),
        ('admin', 'Admin'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPES)
    bio = models.TextField(blank=True, null=True)
    profile_pics = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    # first_name = models.CharField(max_length=50)
    # last_name = models.CharField(max_length=50)

    # Use unique related_name
    friends = models.ManyToManyField('self', symmetrical=False, related_name='friend_of', blank=True)
    connected_users = models.ManyToManyField('self', symmetrical=False, related_name='connections_of', blank=True)

    phone_number        = models.CharField(max_length=20, blank=True, null=True)
    must_change_password = models.BooleanField(default=False)
    is_hidden            = models.BooleanField(default=False)

    def __str__(self):
        return self.username


##user profile

class UserProfile(models.Model):
    USER_TYPES = (
        ('innovator', 'Innovator'),
        ('investor', 'Investor'),
    )

    VERIFICATION_STATUS = (
        ('unverified', 'Unverified'),
        ('pending',    'Pending Review'),
        ('verified',   'Verified'),
        ('rejected',   'Rejected'),
    )

    INDUSTRY_CHOICES = INDUSTRY_CHOICES  # noqa: F821 — module-level list above
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='innovator')
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='userprofile')
    profile_pics = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    company = models.CharField(max_length=100, blank=True, null=True)
    industry = models.CharField(max_length=100, choices=INDUSTRY_CHOICES, blank=True, null=True)

    # Avoid using same related_name as in CustomUser
    friends = models.ManyToManyField(CustomUser, related_name='profile_friends', blank=True)
    connected_users = models.ManyToManyField('self', symmetrical=False, related_name='profile_connections', blank=True)

    # ── Verification ────────────────────────────────────────────────────
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_STATUS, default='unverified')
    verified_at         = models.DateTimeField(null=True, blank=True)
    verified_by         = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='verifications_granted'
    )

    # ── Gender ───────────────────────────────────────────────────────────
    GENDER_CHOICES = [('', 'Prefer not to say'), ('male', 'Male'), ('female', 'Female'), ('other', 'Other')]
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, default='')

    # ── Location ─────────────────────────────────────────────────────────
    location = models.CharField(max_length=150, blank=True, default='', help_text='City and/or country (e.g. Nairobi, Kenya)')

    # ── Investor-specific preference fields ──────────────────────────────
    ticket_size_min   = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text='Minimum cheque size in USD')
    ticket_size_max   = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text='Maximum cheque size in USD')
    preferred_sectors = models.CharField(max_length=500, blank=True, default='', help_text='Comma-separated sectors of interest')
    geography_focus   = models.CharField(max_length=255, blank=True, default='', help_text='Geographic markets of interest')
    investment_thesis = models.TextField(blank=True, default='', help_text='Brief investment thesis or mandate')

    # ── Cover / banner style ─────────────────────────────────────────────
    cover_style = models.CharField(max_length=300, blank=True, default='', help_text='CSS background value for profile banner')

    def disconnect_from_user(self, user_to_disconnect):
        self.connected_users.remove(user_to_disconnect)

    def __str__(self):
        return self.user.username

    

##intentor page

    
##
# models.py# core/models.py
from django.conf import settings
from django.db import models

class Project(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    )

    REVIEW_STATUS = (
        ('draft',        'Draft'),
        ('under_review', 'Under Review'),
        ('approved',     'Approved'),
        ('featured',     'Featured'),
        ('rejected',     'Rejected'),
    )

    review_status = models.CharField(max_length=20, choices=REVIEW_STATUS, default='draft')
    reviewed_at   = models.DateTimeField(null=True, blank=True)
    reviewed_by   = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='projects_reviewed'
    )
    review_note   = models.TextField(blank=True, default='')

    PIPELINE_STAGES = (
        ('idea', 'Idea Stage'),
        ('validation', 'Validation Stage'),
        ('investment', 'Investment Stage'),
        ('growth', 'Growth Stage'),
    )

    STAGE_ORDER = ['idea', 'validation', 'investment', 'growth']

    STAGE_STATUS_CHOICES = (
        ('active', 'Active'),
        ('pending_approval', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    pipeline_stage = models.CharField(max_length=20, choices=PIPELINE_STAGES, default='idea')
    stage_status   = models.CharField(max_length=20, choices=STAGE_STATUS_CHOICES, default='active')

    # Main project owner (Innovator)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='projects'
    )

    # Optional sponsor (Investor)
    sponsor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='sponsored_projects'
    )

    # Default status is 'draft'
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    # Default title and description for testing
    title = models.CharField(max_length=255, default="Sample Project Title")
    description = models.TextField(default="This is a sample project description for testing purposes.")

    industry = models.CharField(
        max_length=100,
        choices=INDUSTRY_CHOICES,
        default="tech"
    )

    # Default image if none is provided
    image = models.ImageField(upload_to='project_images/', null=True, blank=True, default='project_images/mac.png')

    # Optional website link
    website_link = models.URLField(null=True, blank=True, default='')

    # Auto-generated creation date
    created_at = models.DateTimeField(auto_now_add=True)

    # Users who liked the project (Many-to-Many relationship)
    liked_by     = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_projects', blank=True)
    interested   = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='interested_projects', blank=True)
    promoted_by  = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='promoted_projects', blank=True)
    shared_by    = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='shared_projects', blank=True)

    # Rating field (default value is 0)
    rating = models.IntegerField(default=0)

    # Additional fields added in migrations
    category          = models.CharField(max_length=20, choices=[('innovation','Innovation'),('invention','Invention')], default='innovation')
    is_hidden         = models.BooleanField(default=False)
    keywords          = models.CharField(max_length=500, blank=True, default='', help_text='Comma-separated keywords')
    video             = models.FileField(upload_to='project_videos/', blank=True, null=True)
    video2            = models.FileField(upload_to='project_videos/', blank=True, null=True)
    video_name        = models.CharField(max_length=255, blank=True, default='')
    video_description = models.TextField(blank=True, default='')

    # ── Funding stage (for investor filtering) ───────────────────────────
    FUNDING_STAGE_CHOICES = (
        ('',          'Not specified'),
        ('pre_seed',  'Pre-Seed'),
        ('seed',      'Seed'),
        ('pre_series_a', 'Pre-Series A'),
        ('series_a',  'Series A'),
        ('series_b',  'Series B+'),
        ('grant',     'Grant / Non-dilutive'),
    )
    funding_stage = models.CharField(max_length=20, choices=FUNDING_STAGE_CHOICES, blank=True, default='')

    # ── Investment Profile / Pitch Deck Fields ────────────────────────────
    problem_statement  = models.TextField(blank=True, default='', verbose_name='Problem Statement')
    solution_overview  = models.TextField(blank=True, default='', verbose_name='Solution Overview')
    market_opportunity = models.TextField(blank=True, default='', verbose_name='Market Opportunity')
    business_model     = models.TextField(blank=True, default='', verbose_name='Business Model')
    traction           = models.TextField(blank=True, default='', verbose_name='Traction / Validation')
    funding_requirement= models.CharField(max_length=255, blank=True, default='', verbose_name='Funding Requirement')
    use_of_funds       = models.TextField(blank=True, default='', verbose_name='Use of Funds')
    team_overview      = models.TextField(blank=True, default='', verbose_name='Team')

    PITCH_FIELDS = [
        'problem_statement', 'solution_overview', 'market_opportunity',
        'business_model', 'traction', 'funding_requirement',
        'use_of_funds', 'team_overview',
    ]

    def completeness_score(self):
        filled = sum(1 for f in self.PITCH_FIELDS if getattr(self, f, '').strip())
        return round((filled / len(self.PITCH_FIELDS)) * 100)

    def investment_readiness(self):
        score = self.completeness_score()
        if score == 100:
            return ('Investment Ready', 'ready')
        elif score >= 75:
            return ('Strong Profile', 'strong')
        elif score >= 50:
            return ('Developing', 'developing')
        elif score >= 25:
            return ('Early Stage', 'early')
        else:
            return ('Getting Started', 'starter')

    # Method to calculate the average rating
    def average_rating(self):
        ratings = self.ratings.all()
        return round(sum(r.value for r in ratings) / ratings.count(), 1) if ratings.exists() else 0

    # Method to get the main image URL
    def get_main_image_url(self):
        # Trying to get the image marked as 'main'
        main_image = self.images.filter(is_main=True).first()
        if main_image and main_image.image:
            return main_image.image.url

        # Fallback: return the first image if no main image is found
        first_image = self.images.first()
        if first_image and first_image.image:
            return first_image.image.url

        # If no image is found, return None
        return None

    class Meta:
        indexes = [
            models.Index(fields=['owner', 'is_hidden'],         name='proj_owner_hidden_idx'),
            models.Index(fields=['industry', 'is_hidden'],      name='proj_industry_hidden_idx'),
            models.Index(fields=['status', 'is_hidden'],        name='proj_status_hidden_idx'),
            models.Index(fields=['pipeline_stage', 'is_hidden'],name='proj_stage_hidden_idx'),
            models.Index(fields=['-created_at'],                name='proj_created_idx'),
        ]

    def __str__(self):
        return self.title


class ProjectImage(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='project_images/')
    name = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    is_main = models.BooleanField(default=False)

    def __str__(self):
        return self.name or f"Image {self.id}"
    
###Attachments
class Attachment(models.Model):
    DOC_TYPE_CHOICES = [('general','General'),('financial','Financial Document'),('legal','Legal / Contract'),('technical','Technical Document'),('presentation','Presentation'),('proposal','Proposal'),('report','Report'),('other','Other')]
    VISIBILITY_CHOICES = [('public','Public — anyone can download'),('connections','Connections only'),('private','Private — only me')]
    project     = models.ForeignKey(Project, related_name='attachments', on_delete=models.CASCADE)
    file        = models.FileField(upload_to='attachments/')
    title       = models.CharField(max_length=200, blank=True, default='')
    description = models.TextField(blank=True, default='')
    doc_type    = models.CharField(max_length=20, choices=DOC_TYPE_CHOICES, default='general')
    visibility  = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='connections')
    uploaded_at = models.DateTimeField(default=timezone.now)




class Rating(models.Model):
    project = models.ForeignKey(Project, related_name='ratings', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    value = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = ('project', 'user')  # prevents multiple ratings from the same user

    def __str__(self):
        return f"{self.user} rated {self.project} {self.value} stars"


def get_default_user():
    CustomUser = get_user_model()
    try:
        return CustomUser.objects.first().id  # Returns the first user in the database
    except ObjectDoesNotExist:
        return None  # Avoids migration issues if no users exist yet


class Post(models.Model):
    POST_TYPE_CHOICES = [
        ('idea',        'Idea'),
        ('article',     'Article'),
        ('update',      'Update'),
        ('announcement','Announcement'),
        ('question',    'Question'),
        ('poll',        'Poll'),
        ('tip',         'Tip'),
        ('resource',    'Resource'),
        ('milestone',   'Milestone'),
        ('opinion',     'Opinion'),
    ]
    REVIEW_STATUS_CHOICES = [
        ('pending',  'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    industry = models.CharField(max_length=100, choices=INDUSTRY_CHOICES, default='tech')
    user         = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts')
    title        = models.CharField(max_length=255)
    content      = models.TextField()
    post_type    = models.CharField(max_length=20, choices=POST_TYPE_CHOICES, default='article')
    website_link = models.URLField(blank=True, null=True)
    image        = models.ImageField(upload_to='post', blank=True, null=True)
    image_name   = models.CharField(max_length=255, blank=True, default='')
    interests    = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='interested_posts', blank=True)
    likes        = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_posts', blank=True)
    reposts      = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='reposted_posts', blank=True)
    share_count  = models.PositiveIntegerField(default=0)
    is_hidden    = models.BooleanField(default=False)
    review_status = models.CharField(max_length=10, choices=REVIEW_STATUS_CHOICES, default='pending', db_index=True)
    created_at   = models.DateTimeField(auto_now_add=True)
    slug         = models.SlugField(max_length=120, unique=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'is_hidden'],     name='post_user_hidden_idx'),
            models.Index(fields=['industry', 'is_hidden'], name='post_industry_hidden_idx'),
            models.Index(fields=['-created_at'],           name='post_created_idx'),
        ]

    def __str__(self):
        return f"Post by {self.user.username} - {self.industry}"

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('post_detail', kwargs={'slug': self.slug})


class PostReaction(models.Model):
    REACTION_CHOICES = [
        ('like',        'Like'),
        ('celebrate',   'Celebrate'),
        ('support',     'Support'),
        ('love',        'Love'),
        ('insightful',  'Insightful'),
        ('funny',       'Funny'),
    ]
    post      = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='reactions')
    user      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='post_reactions')
    reaction  = models.CharField(max_length=20, choices=REACTION_CHOICES, default='like')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user')

    def __str__(self):
        return f"{self.user.username} → {self.reaction} on post {self.post_id}"


class Poll(models.Model):
    post      = models.OneToOneField('Post', on_delete=models.CASCADE, related_name='poll')
    question  = models.CharField(max_length=300, blank=True, default='')
    closes_at = models.DateTimeField(null=True, blank=True)

    def total_votes(self):
        return self.votes.count()

    def is_open(self):
        from django.utils import timezone
        return self.closes_at is None or self.closes_at > timezone.now()


class PollOption(models.Model):
    poll  = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='options')
    text  = models.CharField(max_length=150)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def vote_count(self):
        return self.votes.count()

    def vote_pct(self, total):
        if not total:
            return 0
        return round(self.votes.count() / total * 100)


class PollVote(models.Model):
    poll     = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='votes')
    option   = models.ForeignKey(PollOption, on_delete=models.CASCADE, related_name='votes')
    user     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='poll_votes')
    voted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('poll', 'user')


##Notifications
class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('connected', 'Connected'),
        ('message_sent', 'Message Sent'),
        ('other', 'Other')
    ]

    user              = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    message           = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='other')
    action_type       = models.CharField(max_length=30, blank=True, default='')
    action_id         = models.PositiveIntegerField(blank=True, null=True)
    project_id        = models.PositiveIntegerField(blank=True, null=True)
    link              = models.CharField(max_length=500, blank=True, default='')
    is_read           = models.BooleanField(default=False)
    is_dismissed      = models.BooleanField(default=False)
    created_at        = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'is_read'], name='notif_user_read_idx'),
        ]

    def __str__(self):
        return f"Notification for {self.user.username} - {self.message[:20]}"



#Timezone
class MyModel(models.Model):
    created_at = models.DateTimeField(default=timezone.now)


# Model for connections

class Connection(models.Model):
    STATUS_CHOICES = [('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')]
    initiator  = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='initiated_connections')
    target     = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='received_connections')
    status     = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('initiator', 'target')

    def __str__(self):
        return f"{self.initiator.username} connected with {self.target.username}"


# Model for listing events

##patent model
class Patent(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(default="Description not provided")
    # owner = models.ForeignKey(
    #     CustomUser,
    #     on_delete=models.CASCADE,
    #     related_name='project',
    #     default=1  # Default to the CustomUser with ID 1
    # )
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='patents')

    filed_date = models.DateField(default=timezone.now)  # Use current date as the default

    # Add other fields as needed

    def __str__(self):
        return f"Patent {self.id}: {self.description[:50]}"


##model for number of likes
class Like(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='likes_given')
    target_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='likes_received')
    created_at = models.DateTimeField(auto_now_add=True)


##Model for number interests
class Interest(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='interests_given')
    target_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='interests_received')
    created_at = models.DateTimeField(auto_now_add=True)


##user groups
class Group(models.Model):
    INDUSTRY_CHOICES = INDUSTRY_CHOICES  # noqa: F821
    name        = models.CharField(max_length=255)
    members     = models.ManyToManyField(CustomUser)
    creator     = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_groups')
    description = models.TextField(blank=True, default='')
    industry    = models.CharField(max_length=100, choices=INDUSTRY_CHOICES, default='other')
    cover_image = models.ImageField(upload_to='group_covers/', blank=True, null=True)
    is_private  = models.BooleanField(default=False)
    is_hidden   = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)

##user page
class Page(models.Model):
    INDUSTRY_CHOICES = INDUSTRY_CHOICES  # noqa: F821
    owner       = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title       = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    industry    = models.CharField(max_length=100, choices=INDUSTRY_CHOICES, default='other')
    cover_image = models.ImageField(upload_to='page_covers/', blank=True, null=True)
    logo        = models.ImageField(upload_to='page_logos/', blank=True, null=True)
    website     = models.URLField(blank=True, default='')
    followers   = models.ManyToManyField(CustomUser, related_name='followed_pages', blank=True)
    is_hidden   = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)

# 

##posts


##comments
class Comment(models.Model):
    post       = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    user       = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    parent     = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='replies')
    content    = models.TextField()
    likes      = models.ManyToManyField(CustomUser, related_name='liked_comments', blank=True)
    is_hidden  = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.content[:50]


##Who viewed your profile
    

##companies that viewed your profile

class Company(models.Model):
    COMPANY_TYPE_CHOICES = [('startup','Startup'),('sme','SME'),('enterprise','Enterprise'),('ngo','NGO / Non-Profit'),('government','Government'),('other','Other')]
    SIZE_CHOICES = [('1-10','1–10 employees'),('11-50','11–50 employees'),('51-200','51–200 employees'),('201-500','201–500 employees'),('500+','500+ employees')]
    INDUSTRY_CHOICES = INDUSTRY_CHOICES  # noqa: F821
    owner        = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='companies')
    name         = models.CharField(max_length=255)
    description  = models.TextField()
    industry     = models.CharField(max_length=100, choices=INDUSTRY_CHOICES)
    tagline      = models.CharField(max_length=300, blank=True, default='')
    company_type = models.CharField(max_length=30, choices=COMPANY_TYPE_CHOICES, default='other')
    size         = models.CharField(max_length=20, choices=SIZE_CHOICES, blank=True, default='')
    location     = models.CharField(max_length=255, blank=True, default='')
    website      = models.URLField(blank=True, default='')
    email        = models.EmailField(blank=True, default='')
    phone        = models.CharField(max_length=30, blank=True, default='')
    founded_year = models.PositiveIntegerField(blank=True, null=True)
    logo         = models.ImageField(upload_to='company_logos/', default='default_company.png')
    cover_image  = models.ImageField(upload_to='company_covers/', blank=True, null=True)
    followers    = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='followed_companies', blank=True)
    is_verified  = models.BooleanField(default=False)
    created_at   = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


##followers

##Customlogin


##follow requests


##



####Message
from django.conf import settings
import re as _re

class Conversation(models.Model):
    CONTEXT_TYPE_CHOICES = [('direct','Direct Message'),('post','Post Discussion'),('project','Project Discussion'),('proposal','Proposal Discussion'),('collab','Collaboration Discussion')]
    participants  = models.ManyToManyField(CustomUser, related_name='conversations')
    context_type  = models.CharField(max_length=10, choices=CONTEXT_TYPE_CHOICES, default='direct')
    post          = models.ForeignKey('Post', on_delete=models.SET_NULL, null=True, blank=True, related_name='conversations')
    project       = models.ForeignKey('Project', on_delete=models.SET_NULL, null=True, blank=True, related_name='conversations')
    created_at    = models.DateTimeField(auto_now_add=True)
    is_resolved   = models.BooleanField(default=False)
    resolved_at   = models.DateTimeField(null=True, blank=True)
    auto_replied  = models.BooleanField(default=False)
    slug          = models.CharField(max_length=80, unique=True, blank=True)

    # Matches temp UUID slugs generated before participants are added
    _TEMP_RE = _re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}$|^[0-9a-f]{12}$')

    def build_slug(self):
        from django.utils.text import slugify
        usernames = list(
            self.participants.values_list('username', flat=True).order_by('username')
        )
        parts = []
        if self.context_type == 'project' and self.project_id:
            try:
                title = self.project.title
                parts.append(slugify(title)[:25].strip('-'))
            except Exception:
                parts.append('project')
        elif self.context_type == 'post':
            parts.append('post')
        elif self.context_type == 'proposal':
            parts.append('proposal')
        elif self.context_type == 'collab':
            parts.append('collab')
        for u in usernames[:2]:
            parts.append(slugify(u.replace('.', '-')))
        if not parts:
            import uuid
            h = uuid.uuid4().hex
            return f"{h[:8]}-{h[8:12]}-{h[12:16]}"
        base = '-'.join(p for p in parts if p)[:70]
        slug = base
        n = 2
        qs = Conversation.objects.exclude(pk=self.pk) if self.pk else Conversation.objects.all()
        while qs.filter(slug=slug).exists():
            slug = f'{base}-{n}'
            n += 1
        return slug

    def save(self, *args, **kwargs):
        if not self.slug:
            import uuid
            h = uuid.uuid4().hex
            self.slug = f"{h[:8]}-{h[8:12]}-{h[12:16]}"
            while Conversation.objects.filter(slug=self.slug).exists():
                h = uuid.uuid4().hex
                self.slug = f"{h[:8]}-{h[8:12]}-{h[12:16]}"
        super().save(*args, **kwargs)

class Message(models.Model):
    MSG_TYPE_CHOICES = [
        ('text',            'Text'),
        ('post_share',      'Shared Post'),
        ('project_share',   'Shared Project'),
        ('sticker',         'Sticker'),
        ('file',            'File Attachment'),
    ]
    sender         = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    recipient      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_messages')
    reply_to       = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='replies')
    content        = models.TextField(blank=True, default='')
    message_type   = models.CharField(max_length=20, choices=MSG_TYPE_CHOICES, default='text')
    shared_post    = models.ForeignKey('Post',    on_delete=models.SET_NULL, null=True, blank=True, related_name='chat_shares')
    shared_project = models.ForeignKey('Project', on_delete=models.SET_NULL, null=True, blank=True, related_name='chat_shares')
    timestamp      = models.DateTimeField(auto_now_add=True)
    is_read        = models.BooleanField(default=False)
    is_flagged     = models.BooleanField(default=False)
    flag_reason    = models.TextField(blank=True, null=True)
    flagged_by     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='admin_flagged_messages')
    is_hidden      = models.BooleanField(default=False)
    is_deleted     = models.BooleanField(default=False)
    is_edited      = models.BooleanField(default=False)
    edited_at      = models.DateTimeField(null=True, blank=True)
    is_system      = models.BooleanField(default=False)
    conversation   = models.ForeignKey(Conversation, null=True, blank=True, on_delete=models.CASCADE, related_name='messages')

    class Meta:
        indexes = [
            models.Index(fields=['recipient', 'is_read'], name='msg_recipient_read_idx'),
            models.Index(fields=['conversation', 'timestamp'],  name='msg_conv_ts_idx'),
        ]

    def __str__(self):
        return f"From {self.sender} to {self.recipient} at {self.timestamp}"



from cloudinary_storage.storage import MediaCloudinaryStorage
from django.utils.deconstruct import deconstructible

@deconstructible
class ChatAttachmentStorage(MediaCloudinaryStorage):
    """
    Picks the correct Cloudinary resource_type by file extension so that
    videos are uploaded as 'video', images as 'image', and everything else
    as 'raw'.  The base MediaCloudinaryStorage defaults to 'image', which
    silently rejects video uploads.
    """
    _VIDEO_EXT = {'mp4', 'webm', 'mov', 'avi', 'mkv', 'm4v', 'flv', 'wmv', 'ogv'}
    _IMAGE_EXT = {'jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'svg', 'tiff', 'heic'}

    def _get_resource_type(self, name):
        ext = name.rsplit('.', 1)[-1].lower() if '.' in name else ''
        if ext in self._VIDEO_EXT:
            return 'video'
        if ext in self._IMAGE_EXT:
            return 'image'
        return 'raw'


class MessageAttachment(models.Model):
    ATTACHMENT_TYPES = [
        ('image', 'Image'),
        ('video', 'Video'),
        ('document', 'Document'),
    ]

    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='attachments')

    file = models.FileField(
        storage=ChatAttachmentStorage(),
        upload_to='chat_attachments/%Y/%m/'
    )
    attachment_type = models.CharField(max_length=10, choices=ATTACHMENT_TYPES, default='document')
    filename = models.CharField(max_length=255, blank=True)
    file_size = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def file_url(self):
        """
        Return the correct URL for this attachment.

        Cloudinary strips the file extension from the public_id on upload, so
        the stored name has no extension and att.file.url always returns a
        /raw/upload/ URL regardless of type.  We fix the resource_type segment
        using the stored attachment_type field.

        For local/non-Cloudinary storage the URL is returned unchanged.
        """
        url = self.file.url
        if 'res.cloudinary.com' not in url:
            # Local filesystem or other non-Cloudinary storage — works as-is
            return url
        if self.attachment_type == 'image':
            url = url.replace('/raw/upload/', '/image/upload/', 1)
            url = url.replace('/video/upload/', '/image/upload/', 1)
        elif self.attachment_type == 'video':
            url = url.replace('/raw/upload/', '/video/upload/', 1)
            url = url.replace('/image/upload/', '/video/upload/', 1)
        # 'document' stays as /raw/upload/ — Cloudinary serves raw files fine
        return url

    def __str__(self):
        return f"{self.attachment_type}: {self.filename}"


###pagination


##3



# ── Existing models (match migrations 0031, 0078) ────────────────────────

class Collaboration(models.Model):
    STATUS_CHOICES = [
        ('pending',  'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
    ]
    from_user   = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_collaborations')
    post        = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='collaborations')
    message     = models.TextField(blank=True)
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at  = models.DateTimeField(auto_now_add=True)
    # Agreement fields (added via migration)
    innovator_agreed    = models.BooleanField(default=False)
    innovator_agreed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Collab from {self.from_user} on {self.post} – {self.status}"


class PatentRequest(models.Model):
    STATUS_CHOICES = [
        ('pending',  'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
    ]
    from_investor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_patent_requests')
    post          = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='patent_requests')
    message       = models.TextField(blank=True)
    status        = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at    = models.DateTimeField(auto_now_add=True)
    # Agreement fields
    innovator_agreed    = models.BooleanField(default=False)
    innovator_agreed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"PatentReq from {self.from_investor} – {self.status}"


class Proposal(models.Model):
    STATUS_CHOICES = [
        ('pending',   'Pending'),
        ('accepted',  'Accepted'),
        ('declined',  'Declined'),
        ('countered', 'Countered'),
        ('on_hold',   'On Hold'),
        ('reviewing', 'Reviewing'),
    ]
    from_investor       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_proposals')
    post                = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='proposals')
    message             = models.TextField(blank=True)
    amount              = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    counter_amount      = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    counter_message     = models.TextField(blank=True)
    conversation        = models.OneToOneField('Conversation', on_delete=models.SET_NULL, null=True, blank=True, related_name='proposal')
    status              = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at          = models.DateTimeField(auto_now_add=True)
    # Agreement fields
    innovator_agreed    = models.BooleanField(default=False)
    innovator_agreed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Proposal from {self.from_investor} – {self.status}"


class Meeting(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('active',    'Active'),
        ('ended',     'Ended'),
    ]
    creator      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_meetings')
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='meetings', blank=True)
    conversation = models.ForeignKey('Conversation', null=True, blank=True, on_delete=models.SET_NULL, related_name='meetings')
    title        = models.CharField(max_length=200, blank=True, default='')
    room_id      = models.CharField(max_length=32, unique=True, blank=True)
    scheduled_at = models.DateTimeField(null=True, blank=True)
    status       = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    created_at   = models.DateTimeField(auto_now_add=True)
    # Zoom fields (added via migration 0079)
    duration         = models.PositiveIntegerField(default=60, help_text='Duration in minutes')
    zoom_meeting_id  = models.CharField(max_length=30, blank=True, default='')
    zoom_join_url    = models.URLField(max_length=500, blank=True, default='')
    zoom_start_url   = models.TextField(blank=True, default='')
    zoom_password    = models.CharField(max_length=50, blank=True, default='')
    recording_status = models.CharField(
        max_length=20, blank=True, default='',
        choices=[('', 'None'), ('processing', 'Processing'), ('completed', 'Available')],
    )
    recording_url    = models.URLField(max_length=500, blank=True, default='')

    def __str__(self):
        return f"Meeting '{self.title}' by {self.creator}"


# ── Models added from migrations 0031-0079 (were missing from models.py) ───

# --- Missing fields on existing models are handled above inline ---
# The following ADDS fields that migrations added but models.py never had.
# Django requires models.py to match the current migration state.

# Connection.status was added in 0034 — patch via AlterField in migration;
# it's simpler to ensure the field exists here with the right choices.
# (Already defined above but missing 'status'; we monkey-patch via migration
#  rather than redefine — no action needed here for Connection.)


class MessageReaction(models.Model):
    message    = models.ForeignKey('Message', on_delete=models.CASCADE, related_name='reactions')
    user       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='message_reactions')
    emoji      = models.CharField(max_length=32)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('message', 'user')


class Job(models.Model):
    JOB_TYPE_CHOICES = [
        ('full_time', 'Full Time'), ('part_time', 'Part Time'),
        ('contract', 'Contract'), ('internship', 'Internship'), ('remote', 'Remote'),
    ]
    title        = models.CharField(max_length=255)
    company      = models.CharField(max_length=255)
    location     = models.CharField(max_length=255, blank=True, default='')
    description  = models.TextField()
    salary_range = models.CharField(max_length=100, blank=True, default='')
    job_type     = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES, default='full_time')
    apply_url    = models.URLField(blank=True, default='')
    is_active    = models.BooleanField(default=True)
    is_hidden    = models.BooleanField(default=False)
    created_at   = models.DateTimeField(auto_now_add=True)
    created_by   = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_jobs')
    company_page = models.ForeignKey('Company', on_delete=models.SET_NULL, null=True, blank=True, related_name='jobs')

    def __str__(self):
        return self.title


class JobApplication(models.Model):
    job        = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    applicant  = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='job_applications')
    letter     = models.TextField(blank=True)
    cv         = models.FileField(upload_to='job_cvs/', blank=True, null=True)
    attachment = models.FileField(upload_to='job_attachments/', blank=True, null=True)
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('job', 'applicant')
        ordering = ['-applied_at']


class ContactSubmission(models.Model):
    name         = models.CharField(max_length=255)
    email        = models.EmailField()
    topic        = models.CharField(max_length=100, blank=True, default='General Inquiry')
    subject      = models.CharField(max_length=255, blank=True, default='')
    message      = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_replied   = models.BooleanField(default=False)
    replied_at   = models.DateTimeField(null=True, blank=True)
    admin_reply  = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.name} — {self.email}"


class ProfileView(models.Model):
    profile_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile_views')
    viewer       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='profile_views_given')
    # session_key  = models.CharField(max_length=40)
    session_key  = models.CharField(max_length=255)
    viewed_at    = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [('profile_user', 'session_key'), ('profile_user', 'viewer')]


class ProjectComment(models.Model):
    project    = models.ForeignKey('Project', on_delete=models.CASCADE, related_name='project_comments')
    user       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content    = models.TextField()
    parent     = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='replies')
    likes      = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_project_comments', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_hidden  = models.BooleanField(default=False)

    def __str__(self):
        return self.content[:50]


class ProjectView(models.Model):
    project     = models.ForeignKey('Project', on_delete=models.CASCADE, related_name='views')
    user        = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    session_key = models.CharField(max_length=255, blank=True)
    viewed_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('project', 'session_key')


class StageProgressionRequest(models.Model):
    STATUS_CHOICES = (
        ('pending',  'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    project      = models.ForeignKey('Project', on_delete=models.CASCADE, related_name='stage_requests')
    from_stage   = models.CharField(max_length=20)
    to_stage     = models.CharField(max_length=20)
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='stage_requests_made')
    requested_at = models.DateTimeField(auto_now_add=True)
    reviewed_by  = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='stage_requests_reviewed')
    reviewed_at  = models.DateTimeField(null=True, blank=True)
    status       = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_note   = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['-requested_at']

    def __str__(self):
        return f"{self.project} | {self.from_stage} → {self.to_stage} ({self.status})"


class VerificationRequest(models.Model):
    """User submits documents/info to request a Verified badge."""
    STATUS_CHOICES = (
        ('pending',  'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    user          = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='verification_requests')
    id_document   = models.FileField(upload_to='verification_docs/', blank=True, null=True)
    bio_statement = models.TextField(blank=True, default='', help_text='Why should you be verified?')
    linkedin_url  = models.URLField(blank=True, default='')
    website_url   = models.URLField(blank=True, default='')
    notes         = models.TextField(blank=True, default='')
    status        = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    submitted_at  = models.DateTimeField(auto_now_add=True)
    reviewed_by   = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='verification_reviews')
    reviewed_at   = models.DateTimeField(null=True, blank=True)
    admin_note    = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f"VerificationRequest({self.user} — {self.status})"


class PitchRequest(models.Model):
    """An investor's formal request for a project pitch/meeting."""
    STATUS_CHOICES = (
        ('pending',   'Pending'),
        ('accepted',  'Accepted'),
        ('declined',  'Declined'),
        ('scheduled', 'Scheduled'),
    )
    project       = models.ForeignKey('Project', on_delete=models.CASCADE, related_name='pitch_requests')
    investor      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pitch_requests_sent')
    message       = models.TextField(blank=True, default='')
    status        = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    requested_at  = models.DateTimeField(auto_now_add=True)
    responded_at  = models.DateTimeField(null=True, blank=True)
    response_note = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['-requested_at']
        unique_together = ('project', 'investor')

    def __str__(self):
        return f"Pitch request: {self.investor} → {self.project}"


class AdminPermissions(models.Model):
    admin_user         = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='admin_permissions')
    granted_by         = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='granted_admin_permissions')
    is_superadmin      = models.BooleanField(default=False)
    can_manage_users   = models.BooleanField(default=False)
    can_manage_projects = models.BooleanField(default=False)
    can_manage_posts   = models.BooleanField(default=False)
    can_manage_messages = models.BooleanField(default=False)
    can_manage_events  = models.BooleanField(default=False)
    can_manage_jobs    = models.BooleanField(default=False)
    can_manage_comments = models.BooleanField(default=False)
    can_manage_connections = models.BooleanField(default=False)
    can_view_reports   = models.BooleanField(default=True)
    granted_at         = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Admin Permissions'


class EventRegistration(models.Model):
    event        = models.ForeignKey('Event', on_delete=models.CASCADE, related_name='registrations')
    user         = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='event_registrations')
    full_name    = models.CharField(max_length=200, blank=True)
    email        = models.EmailField(blank=True)
    phone        = models.CharField(max_length=30, blank=True)
    notes        = models.TextField(blank=True)
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('event', 'user')


class PageView(models.Model):
    DEVICE_CHOICES = [('desktop', 'Desktop'), ('mobile', 'Mobile'), ('tablet', 'Tablet'), ('bot', 'Bot'), ('other', 'Other')]
    user        = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    path        = models.CharField(max_length=500)
    session_key = models.CharField(max_length=64, blank=True)
    ip_address  = models.GenericIPAddressField(null=True, blank=True)
    browser     = models.CharField(max_length=100, blank=True)
    os          = models.CharField(max_length=100, blank=True)
    device_type = models.CharField(max_length=10, choices=DEVICE_CHOICES, blank=True)
    referrer    = models.CharField(max_length=500, blank=True)
    city        = models.CharField(max_length=100, blank=True)
    country     = models.CharField(max_length=100, blank=True)
    timestamp   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp'],  name='pv_user_ts_idx'),
            models.Index(fields=['path', 'timestamp'],  name='pv_path_ts_idx'),
        ]


class ClickEvent(models.Model):
    user         = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    path         = models.CharField(max_length=500)
    element_id   = models.CharField(max_length=200, blank=True)
    element_text = models.CharField(max_length=200, blank=True)
    session_key  = models.CharField(max_length=64, blank=True)
    ip_address   = models.GenericIPAddressField(null=True, blank=True)
    timestamp    = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']


class NewsItem(models.Model):
    title        = models.CharField(max_length=300)
    body         = models.TextField()
    icon_url     = models.URLField(blank=True, default='')
    image        = models.ImageField(upload_to='news_images/', blank=True, null=True)
    is_published = models.BooleanField(default=True)
    is_hidden    = models.BooleanField(default=False)
    created_by   = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='news_items')
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class PostImage(models.Model):
    post  = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='extra_images')
    image = models.ImageField(upload_to='post_images')
    name  = models.CharField(max_length=255, blank=True, default='')


class AttachmentDownload(models.Model):
    attachment    = models.ForeignKey('Attachment', on_delete=models.CASCADE, related_name='downloads')
    downloaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='attachment_downloads')
    ip_address    = models.GenericIPAddressField(null=True, blank=True)
    downloaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-downloaded_at']


class GroupMembership(models.Model):
    STATUS_CHOICES = [('invited','Invited'),('pending','Pending'),('accepted','Accepted'),('declined','Declined')]
    group      = models.ForeignKey('Group', on_delete=models.CASCADE, related_name='memberships')
    user       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='group_memberships')
    invited_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_group_invites')
    status     = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('group', 'user')


class GroupDiscussion(models.Model):
    group      = models.ForeignKey('Group', on_delete=models.CASCADE, related_name='discussions')
    author     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='group_discussions')
    title      = models.CharField(max_length=255)
    content    = models.TextField()
    likes      = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_group_discussions', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class GroupDiscussionComment(models.Model):
    discussion = models.ForeignKey(GroupDiscussion, on_delete=models.CASCADE, related_name='comments')
    author     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='group_discussion_comments')
    parent     = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='replies')
    content    = models.TextField()
    likes      = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_group_comments', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']


class GroupDiscussionImage(models.Model):
    discussion = models.ForeignKey(GroupDiscussion, on_delete=models.CASCADE, related_name='images')
    image      = models.ImageField(upload_to='group_discussion_images/')
    name       = models.CharField(max_length=255, blank=True, default='')
    is_cover   = models.BooleanField(default=False)
    order      = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order']


class PagePost(models.Model):
    page       = models.ForeignKey('Page', on_delete=models.CASCADE, related_name='posts')
    content    = models.TextField()
    image      = models.ImageField(upload_to='page_post_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class PagePostReaction(models.Model):
    REACTION_CHOICES = [('like','Like'),('love','Love'),('insightful','Insightful'),('celebrate','Celebrate'),('support','Support')]
    post       = models.ForeignKey(PagePost, on_delete=models.CASCADE, related_name='reactions')
    user       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='page_post_reactions')
    reaction   = models.CharField(max_length=20, choices=REACTION_CHOICES, default='like')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user')


class PagePostShare(models.Model):
    post       = models.ForeignKey(PagePost, on_delete=models.CASCADE, related_name='shares')
    user       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='page_post_shares')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user')


class PagePostImage(models.Model):
    post     = models.ForeignKey(PagePost, on_delete=models.CASCADE, related_name='post_images')
    image    = models.ImageField(upload_to='page_post_images/')
    name     = models.CharField(max_length=255, blank=True, default='')
    is_cover = models.BooleanField(default=False)
    order    = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order']


class ProjectProposal(models.Model):
    STATUS_CHOICES = [
        ('pending',   'Pending'),
        ('accepted',  'Accepted'),
        ('declined',  'Declined'),
        ('countered', 'Countered'),
        ('on_hold',   'On Hold'),
        ('reviewing', 'Reviewing'),
    ]
    project         = models.ForeignKey('Project', on_delete=models.CASCADE, related_name='project_proposals')
    from_user       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='project_proposals_sent')
    message         = models.TextField(blank=True)
    counter_message = models.TextField(blank=True, default='')
    amount          = models.CharField(max_length=100, blank=True)
    equity_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    status          = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at      = models.DateTimeField(auto_now_add=True)


class SurveyResponse(models.Model):
    RECOMMEND_CHOICES = [('yes','Yes'),('maybe','Maybe'),('no','No')]
    FEEDBACK_TYPE_CHOICES = [('bug','Bug / Issue'),('suggestion','Suggestion'),('praise','Praise'),('question','Question'),('other','Other')]
    submitted_by      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='survey_responses')
    ui_design         = models.PositiveSmallIntegerField(null=True, blank=True)
    ui_consistency    = models.PositiveSmallIntegerField(null=True, blank=True)
    ux_navigation     = models.PositiveSmallIntegerField(null=True, blank=True)
    ux_findability    = models.PositiveSmallIntegerField(null=True, blank=True)
    usability_tasks   = models.PositiveSmallIntegerField(null=True, blank=True)
    usability_controls = models.PositiveSmallIntegerField(null=True, blank=True)
    exp_satisfaction  = models.PositiveSmallIntegerField(null=True, blank=True)
    exp_recommend     = models.CharField(max_length=5, choices=RECOMMEND_CHOICES, blank=True)
    func_reliability  = models.PositiveSmallIntegerField(null=True, blank=True)
    func_missing      = models.TextField(blank=True)
    comments          = models.TextField(blank=True)
    feedback_type     = models.CharField(max_length=20, choices=FEEDBACK_TYPE_CHOICES, blank=True, default='')
    feedback_text     = models.TextField(blank=True, default='')
    page              = models.CharField(max_length=100, blank=True, default='')
    section           = models.CharField(max_length=100, blank=True, default='')
    submitted_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-submitted_at']


class ShareEvent(models.Model):
    PLATFORM_CHOICES = [('whatsapp','WhatsApp'),('telegram','Telegram'),('twitter','Twitter / X'),('facebook','Facebook'),('linkedin','LinkedIn'),('instagram','Instagram'),('copy_link','Copy Link'),('other','Other')]
    SHARE_TYPE_CHOICES = [('individual','Individual / DM'),('group','Group / Channel'),('general','General')]
    CONTENT_TYPE_CHOICES = [('project','Project'),('post','Post'),('profile','Profile'),('page','Page'),('other','Other')]
    shared_by    = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='share_events')
    platform     = models.CharField(max_length=20, choices=PLATFORM_CHOICES, default='other')
    share_type   = models.CharField(max_length=20, choices=SHARE_TYPE_CHOICES, default='general')
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPE_CHOICES, blank=True)
    object_id    = models.PositiveIntegerField(null=True, blank=True)
    shared_url   = models.URLField(max_length=600, blank=True)
    ip_address   = models.GenericIPAddressField(null=True, blank=True)
    shared_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-shared_at']


class CompanyMedia(models.Model):
    MEDIA_TYPE_CHOICES = [('image','Image'),('video','Video'),('document','Document')]
    company     = models.ForeignKey('Company', on_delete=models.CASCADE, related_name='media')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    media_type  = models.CharField(max_length=20, choices=MEDIA_TYPE_CHOICES, default='image')
    file        = models.FileField(upload_to='company_media/')
    title       = models.CharField(max_length=200, blank=True)
    caption     = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']


class CompanyUpdate(models.Model):
    company    = models.ForeignKey('Company', on_delete=models.CASCADE, related_name='updates')
    author     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    content    = models.TextField()
    image      = models.ImageField(upload_to='company_update_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class ReadLater(models.Model):
    user     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='read_later_items')
    post     = models.ForeignKey('Post', on_delete=models.SET_NULL, null=True, blank=True, related_name='read_later_saves')
    project  = models.ForeignKey('Project', on_delete=models.SET_NULL, null=True, blank=True, related_name='read_later_saves')
    company  = models.ForeignKey('Company', on_delete=models.SET_NULL, null=True, blank=True, related_name='read_later_saves')
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-saved_at']


class Pin(models.Model):
    """Allows a user to pin a chat conversation, post, or project for quick access."""
    PIN_TYPE_CHOICES = [('chat', 'Chat'), ('post', 'Post'), ('project', 'Project')]
    user         = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pins')
    pin_type     = models.CharField(max_length=10, choices=PIN_TYPE_CHOICES)
    conversation = models.ForeignKey('Conversation', on_delete=models.CASCADE, null=True, blank=True, related_name='pins')
    post         = models.ForeignKey('Post', on_delete=models.CASCADE, null=True, blank=True, related_name='pins')
    project      = models.ForeignKey('Project', on_delete=models.CASCADE, null=True, blank=True, related_name='pins')
    pinned_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-pinned_at']


class ProjectCollaboration(models.Model):
    STATUS_CHOICES = [('pending','Pending'),('accepted','Accepted'),('declined','Declined'),('on_hold','On Hold'),('reviewing','Reviewing')]
    project       = models.ForeignKey('Project', on_delete=models.CASCADE, related_name='collaborations_on_project')
    from_user     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='project_collaborations_sent')
    conversation  = models.OneToOneField('Conversation', on_delete=models.SET_NULL, null=True, blank=True, related_name='project_collab')
    message       = models.TextField(blank=True)
    counter_message = models.TextField(blank=True)
    status        = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('project', 'from_user')


# ══════════════════════════════════════════════════════════════════
#  Oduma Corp Service Modules
# ══════════════════════════════════════════════════════════════════

# ── Training / Courses ────────────────────────────────────────────

class Course(models.Model):
    CATEGORY_CHOICES = [
        ('entrepreneurship', 'Entrepreneurship'),
        ('fundraising',      'Fundraising & Investment'),
        ('innovation',       'Innovation & Design'),
        ('tech',             'Technology & Product'),
        ('finance',          'Finance & Accounting'),
        ('leadership',       'Leadership & Management'),
        ('marketing',        'Marketing & Growth'),
        ('legal',            'Legal & Compliance'),
    ]
    LEVEL_CHOICES = [
        ('beginner',      'Beginner'),
        ('intermediate',  'Intermediate'),
        ('advanced',      'Advanced'),
    ]
    title        = models.CharField(max_length=255)
    slug         = models.SlugField(max_length=270, unique=True)
    description  = models.TextField(blank=True, default='')
    category     = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='entrepreneurship')
    level        = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='beginner')
    instructor   = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='courses_taught')
    instructor_name = models.CharField(max_length=200, blank=True, default='Oduma Corp Team')
    cover_image  = models.ImageField(upload_to='course_covers/', blank=True, null=True)
    duration_hours = models.PositiveIntegerField(default=0, help_text='Estimated hours to complete')
    is_published = models.BooleanField(default=False)
    is_featured  = models.BooleanField(default=False)
    is_free      = models.BooleanField(default=True)
    price        = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_featured', '-created_at']

    def __str__(self):
        return self.title

    def enrolled_count(self):
        return self.enrollments.count()


class CourseModule(models.Model):
    course      = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title       = models.CharField(max_length=255)
    content     = models.TextField(blank=True, default='')
    video_url   = models.URLField(blank=True, default='')
    order       = models.PositiveIntegerField(default=0)
    duration_minutes = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.course.title} — {self.title}"


class CourseEnrollment(models.Model):
    STATUS_CHOICES = [
        ('enrolled',   'Enrolled'),
        ('in_progress','In Progress'),
        ('completed',  'Completed'),
        ('dropped',    'Dropped'),
    ]
    user        = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='course_enrollments')
    course      = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default='enrolled')
    progress    = models.PositiveIntegerField(default=0, help_text='0–100 percent complete')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_module = models.ForeignKey(CourseModule, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')

    class Meta:
        unique_together = ('user', 'course')
        ordering = ['-enrolled_at']

    def __str__(self):
        return f"{self.user.username} → {self.course.title}"


# ── Mentorship ────────────────────────────────────────────────────

class MentorProfile(models.Model):
    EXPERTISE_CHOICES = [
        ('fundraising',     'Fundraising'),
        ('product',         'Product Development'),
        ('strategy',        'Business Strategy'),
        ('tech',            'Technology'),
        ('marketing',       'Marketing & Sales'),
        ('legal',           'Legal & IP'),
        ('finance',         'Finance & Accounting'),
        ('operations',      'Operations & Scaling'),
    ]
    user        = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mentor_profile')
    expertise   = models.CharField(max_length=50, choices=EXPERTISE_CHOICES, default='strategy')
    bio         = models.TextField(blank=True, default='')
    industries  = models.CharField(max_length=500, blank=True, default='', help_text='Comma-separated')
    availability = models.CharField(max_length=200, blank=True, default='', help_text='e.g. Weekends, Tuesdays 6–8pm')
    max_mentees = models.PositiveIntegerField(default=3)
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def current_mentees(self):
        return self.mentorship_assignments.filter(status='active').count()

    def has_capacity(self):
        return self.current_mentees() < self.max_mentees

    def __str__(self):
        return f"Mentor: {self.user.get_full_name() or self.user.username}"


class MentorshipRequest(models.Model):
    STATUS_CHOICES = [
        ('pending',   'Pending'),
        ('accepted',  'Accepted'),
        ('declined',  'Declined'),
        ('completed', 'Completed'),
    ]
    from_user   = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mentorship_requests_sent')
    mentor      = models.ForeignKey(MentorProfile, on_delete=models.CASCADE, related_name='mentorship_requests')
    project     = models.ForeignKey('Project', on_delete=models.SET_NULL, null=True, blank=True, related_name='mentorship_requests')
    message     = models.TextField(blank=True, default='')
    goals       = models.TextField(blank=True, default='', help_text='What do you want to achieve?')
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at  = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    mentor_note  = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['-created_at']
        unique_together = ('from_user', 'mentor', 'project')

    def __str__(self):
        return f"{self.from_user.username} → {self.mentor.user.username}"


class MentorshipAssignment(models.Model):
    STATUS_CHOICES = [
        ('active',    'Active'),
        ('paused',    'Paused'),
        ('completed', 'Completed'),
    ]
    mentor      = models.ForeignKey(MentorProfile, on_delete=models.CASCADE, related_name='mentorship_assignments')
    mentee      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mentorship_assignments')
    project     = models.ForeignKey('Project', on_delete=models.SET_NULL, null=True, blank=True, related_name='mentorship_assignments')
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    assigned_at = models.DateTimeField(auto_now_add=True)
    notes       = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['-assigned_at']

    def __str__(self):
        return f"{self.mentor.user.username} mentors {self.mentee.username}"


# ── Innovation Consulting ─────────────────────────────────────────

class ConsultingRequest(models.Model):
    CATEGORY_CHOICES = [
        ('strategy',        'Business Strategy'),
        ('fundraising',     'Fundraising Preparation'),
        ('technical',       'Technical Advisory'),
        ('market_research', 'Market Research'),
        ('legal',           'Legal & IP'),
        ('pitch_prep',      'Pitch Preparation'),
        ('operations',      'Operations & Scaling'),
        ('other',           'Other'),
    ]
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('reviewing', 'Under Review'),
        ('scheduled', 'Call Scheduled'),
        ('completed', 'Completed'),
        ('declined',  'Declined'),
    ]
    user         = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='consulting_requests')
    project      = models.ForeignKey('Project', on_delete=models.SET_NULL, null=True, blank=True, related_name='consulting_requests')
    category     = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='strategy')
    description  = models.TextField(help_text='Describe the challenge or support needed')
    urgency      = models.CharField(max_length=20, choices=[('low','Low'),('medium','Medium'),('high','High')], default='medium')
    status       = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    submitted_at = models.DateTimeField(auto_now_add=True)
    admin_note   = models.TextField(blank=True, default='')
    scheduled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.user.username} — {self.get_category_display()}"


# ── Subscription Plans ────────────────────────────────────────────

class SubscriptionPlan(models.Model):
    SLUG_CHOICES = [('starter', 'Starter'), ('pro', 'Pro'), ('business', 'Business')]
    slug          = models.CharField(max_length=20, unique=True, choices=SLUG_CHOICES)
    name          = models.CharField(max_length=50)
    tagline       = models.CharField(max_length=120, blank=True)
    description   = models.TextField(blank=True)
    price_monthly = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    price_yearly  = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    max_projects      = models.IntegerField(default=3,  help_text='0 = unlimited')
    max_connections   = models.IntegerField(default=10, help_text='0 = unlimited')
    max_company_pages = models.IntegerField(default=0,  help_text='0 = none, -1 = unlimited')
    features      = models.JSONField(default=list, blank=True,
                                     help_text='List of feature strings shown on pricing page')
    is_active     = models.BooleanField(default=True)
    order         = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name

    @property
    def yearly_savings(self):
        """Monthly * 12 minus yearly price."""
        monthly_total = self.price_monthly * 12
        if monthly_total > 0:
            return monthly_total - self.price_yearly
        return 0


class UserSubscription(models.Model):
    STATUS_CHOICES = [
        ('active',    'Active'),
        ('cancelled', 'Cancelled'),
        ('expired',   'Expired'),
        ('trial',     'Trial'),
    ]
    CYCLE_CHOICES = [('monthly', 'Monthly'), ('yearly', 'Yearly')]

    user          = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                         related_name='subscription')
    plan          = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT,
                                      related_name='subscriptions')
    status        = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    billing_cycle = models.CharField(max_length=10, choices=CYCLE_CHOICES, default='monthly')
    started_at    = models.DateTimeField(auto_now_add=True)
    expires_at    = models.DateTimeField(null=True, blank=True)
    cancelled_at  = models.DateTimeField(null=True, blank=True)
    auto_renew    = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} — {self.plan.name}"

    @property
    def is_active(self):
        if self.status not in ('active', 'trial'):
            return False
        if self.expires_at and self.expires_at < timezone.now():
            return False
        return True

    @property
    def plan_slug(self):
        return self.plan.slug

    @property
    def is_pro_or_higher(self):
        return self.plan.slug in ('pro', 'business')

    @property
    def is_business(self):
        return self.plan.slug == 'business'


class SubscriptionOrder(models.Model):
    """Records an upgrade/downgrade request. Admin can mark paid to activate."""
    STATUS_CHOICES = [
        ('pending',   'Pending Payment'),
        ('paid',      'Paid'),
        ('failed',    'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    user          = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                      related_name='subscription_orders')
    plan          = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT)
    billing_cycle = models.CharField(max_length=10, default='monthly')
    amount        = models.DecimalField(max_digits=8, decimal_places=2)
    status        = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reference     = models.CharField(max_length=100, blank=True, help_text='Payment reference/tx ID')
    created_at    = models.DateTimeField(auto_now_add=True)
    paid_at       = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} → {self.plan.name} ({self.status})"


class CustomIndustry(models.Model):
    """User-submitted industry names that extend the preset choices."""
    name       = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Custom industries'

    def __str__(self):
        return self.name


# ── Site Content Management ───────────────────────────────────────

class SiteSettings(models.Model):
    """Singleton-style model for global site settings."""
    twitter_url    = models.URLField(blank=True, default='')
    linkedin_url   = models.URLField(blank=True, default='')
    instagram_url  = models.URLField(blank=True, default='')
    facebook_url   = models.URLField(blank=True, default='')
    youtube_url    = models.URLField(blank=True, default='')
    contact_email  = models.EmailField(blank=True, default='')
    contact_phone  = models.CharField(max_length=30, blank=True, default='')
    footer_tagline = models.CharField(max_length=200, blank=True, default='')
    pricing_enabled = models.BooleanField(default=False, help_text='Show Pricing page and tabs to users')
    updated_at     = models.DateTimeField(auto_now=True)
    updated_by     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                       null=True, blank=True, related_name='site_settings_updates')

    class Meta:
        verbose_name = 'Site Settings'
        verbose_name_plural = 'Site Settings'

    def __str__(self):
        return 'Site Settings'

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class Announcement(models.Model):
    TYPE_CHOICES = [
        ('info',    'Info'),
        ('success', 'Success'),
        ('warning', 'Warning'),
        ('error',   'Error'),
    ]
    title      = models.CharField(max_length=200)
    body       = models.TextField(blank=True, default='')
    type       = models.CharField(max_length=10, choices=TYPE_CHOICES, default='info')
    is_active  = models.BooleanField(default=True)
    show_from  = models.DateField(null=True, blank=True)
    show_until = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                   null=True, blank=True, related_name='announcements')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class BlogPost(models.Model):
    title       = models.CharField(max_length=300)
    slug        = models.SlugField(max_length=320, unique=True)
    excerpt     = models.CharField(max_length=400, blank=True, default='')
    body        = models.TextField()
    cover_image = models.ImageField(upload_to='blog_images/', blank=True, null=True)
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    author      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                    null=True, blank=True, related_name='blog_posts')
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class SitePage(models.Model):
    """Controls visibility of named pages/sections across the platform."""
    key              = models.CharField(max_length=80, unique=True,
                                        help_text='URL name or section identifier')
    label            = models.CharField(max_length=100)
    is_active        = models.BooleanField(default=True)
    disabled_message = models.CharField(max_length=300, blank=True, default='',
                                        help_text='Shown on the error page when this page is disabled')
    updated_at       = models.DateTimeField(auto_now=True)
    updated_by       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                         null=True, blank=True, related_name='site_page_updates')

    class Meta:
        ordering = ['label']

    def __str__(self):
        return self.label

    @classmethod
    def is_page_active(cls, key):
        try:
            return cls.objects.get(key=key).is_active
        except cls.DoesNotExist:
            return True  # not registered = always active


# ── Event type extension (added via migration) ────────────────────
# event_type field added to existing Event model in migration 0086



# ── Admin 2FA & Login Tracking ────────────────────────────────────
class AdminTOTPSecret(models.Model):
    user       = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='totp_secret')
    secret     = models.CharField(max_length=64)
    is_active  = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"TOTP for {self.user.username}"


class AdminLoginAttempt(models.Model):
    username    = models.CharField(max_length=150)
    ip_address  = models.GenericIPAddressField(null=True, blank=True)
    user_agent  = models.TextField(blank=True)
    success     = models.BooleanField(default=False)
    stage       = models.CharField(max_length=20, default='password',
                                   choices=[('password','Password'),('totp','TOTP')])
    timestamp   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        status = 'OK' if self.success else 'FAIL'
        return f"[{status}] {self.username} @ {self.timestamp:%Y-%m-%d %H:%M}"
