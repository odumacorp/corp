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



class Invention(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


class Event(models.Model):
    name = models.CharField(max_length=255)
    date = models.DateField()
    location = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    organizer = models.CharField(max_length=255, blank=True, default='')
    image = models.ImageField(upload_to='event_images/', blank=True, null=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True,
        on_delete=models.SET_NULL, related_name='created_events'
    )
    is_hidden = models.BooleanField(default=False)

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
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)

    # Use unique related_name
    friends = models.ManyToManyField('self', symmetrical=False, related_name='friend_of', blank=True)
    connected_users = models.ManyToManyField('self', symmetrical=False, related_name='connections_of', blank=True)

    phone_number = models.CharField(max_length=20, blank=True, null=True)
    is_hidden = models.BooleanField(default=False)
    must_change_password = models.BooleanField(default=False)

    def __str__(self):
        return self.username


##user profile

class UserProfile(models.Model):
    USER_TYPES = (
        ('innovator', 'Innovator'),
        ('investor', 'Investor'),
    )
    INDUSTRY_CHOICES = [
        ('tech', 'Technology'),
        ('finance', 'Finance'),
        ('health', 'Healthcare'),
        ('edu', 'Education'),
        ('energy', 'Energy'),
        ('agriculture', 'Agriculture'),
        ('manufacturing', 'Manufacturing'),
        ('other', 'Other'),
    ]
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='innovator')
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='userprofile')
    profile_pics = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    company = models.CharField(max_length=100, blank=True, null=True)
    industry = models.CharField(max_length=50, choices=INDUSTRY_CHOICES, blank=True, null=True)

    # Avoid using same related_name as in CustomUser
    friends = models.ManyToManyField(CustomUser, related_name='profile_friends', blank=True)
    connected_users = models.ManyToManyField('self', symmetrical=False, related_name='profile_connections', blank=True)

    def disconnect_from_user(self, user_to_disconnect):
        self.connected_users.remove(user_to_disconnect)

    def __str__(self):
        return self.user.username



class Project(models.Model):
    STATUS_CHOICES = (
        ('draft',       'Planning'),
        ('design',      'Design'),
        ('development', 'Development'),
        ('testing',     'Testing & QA'),
        ('deployment',  'Deployment'),
        ('maintenance', 'Maintenance'),
    )

    CATEGORY_CHOICES = (
        ('innovation', 'Innovation'),
        ('invention', 'Invention'),
    )

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

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    title = models.CharField(max_length=255, default="Sample Project Title")
    description = models.TextField(default="This is a sample project description for testing purposes.")

    industry = models.CharField(
        max_length=100,
        choices=[
            ("tech", "Technology"),
            ("health", "Healthcare"),
            ("finance", "Finance"),
            ("education", "Education"),
            ("energy", "Energy"),
        ],
        default="tech"
    )

    image = models.ImageField(upload_to='project_images/', null=True, blank=True, default='project_images/mac.png')
    website_link = models.URLField(null=True, blank=True, default="http://example.com")
    created_at = models.DateTimeField(auto_now_add=True)
    liked_by = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_projects', blank=True)
    rating = models.IntegerField(default=0)

    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='innovation')
    interested = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='interested_projects', blank=True)
    promoted_by = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='promoted_projects', blank=True)
    shared_by = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='shared_projects', blank=True)
    video = models.FileField(upload_to='project_videos/', blank=True, null=True)
    video2 = models.FileField(upload_to='project_videos/', blank=True, null=True)
    video_description = models.TextField(blank=True, default='', help_text='Short description of the video content (helps search engines)')
    video_name = models.CharField(max_length=255, blank=True, default='', help_text='Title shown on/near the video (also used for SEO)')
    keywords = models.CharField(max_length=500, blank=True, default='', help_text='Comma-separated keywords for search engines (e.g. solar energy, renewable, off-grid)')
    is_hidden = models.BooleanField(default=False)

    def average_rating(self):
        ratings = self.ratings.all()
        return round(sum(r.value for r in ratings) / ratings.count(), 1) if ratings.exists() else 0

    def get_main_image_url(self):
        main_image = self.images.filter(is_main=True).first()
        if main_image and main_image.image:
            return main_image.image.url
        first_image = self.images.first()
        if first_image and first_image.image:
            return first_image.image.url
        return None

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
    project = models.ForeignKey(Project, related_name='attachments', on_delete=models.CASCADE)
    file = models.FileField(upload_to='attachments/')
    uploaded_at = models.DateTimeField(default=timezone.now)
    title = models.CharField(max_length=200, blank=True, default='')
    doc_type = models.CharField(
        max_length=20,
        choices=[
            ('general',      'General'),
            ('financial',    'Financial Document'),
            ('legal',        'Legal / Contract'),
            ('technical',    'Technical Document'),
            ('presentation', 'Presentation'),
            ('proposal',     'Proposal'),
            ('report',       'Report'),
            ('other',        'Other'),
        ],
        default='general',
    )
    visibility = models.CharField(
        max_length=20,
        choices=[
            ('public',      'Public — anyone can download'),
            ('connections', 'Connections only'),
            ('private',     'Private — only me'),
        ],
        default='connections',
    )
    description = models.TextField(blank=True, default='')


class AttachmentDownload(models.Model):
    attachment = models.ForeignKey(Attachment, on_delete=models.CASCADE, related_name='downloads')
    downloaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True,
        on_delete=models.SET_NULL, related_name='attachment_downloads'
    )
    downloaded_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)

    class Meta:
        ordering = ['-downloaded_at']


class Rating(models.Model):
    project = models.ForeignKey(Project, related_name='ratings', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    value = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = ('project', 'user')

    def __str__(self):
        return f"{self.user} rated {self.project} {self.value} stars"


def get_default_user():
    CustomUser = get_user_model()
    try:
        return CustomUser.objects.first().id
    except ObjectDoesNotExist:
        return None


class Post(models.Model):
    POST_TYPE_CHOICES = [
        ('idea', '💡 Idea'),
        ('article', '📝 Article'),
        ('update', '🚀 Update'),
        ('announcement', '📢 Announcement'),
        ('question', '❓ Question'),
    ]

    industry = models.CharField(
        max_length=255,
        choices=[
            ("tech", "Technology"),
            ("health", "Healthcare"),
            ("finance", "Finance"),
            ("education", "Education"),
            ("engineering", "Engineering"),
            ("energy", "Energy"),
        ], default="tech")

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=255)
    content = models.TextField()
    website_link = models.URLField(blank=True, null=True)
    image = models.ImageField(upload_to='post', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    post_type = models.CharField(max_length=20, choices=POST_TYPE_CHOICES, default='article')
    interests = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='interested_posts', blank=True)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_posts', blank=True)
    reposts = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='reposted_posts', blank=True)
    share_count = models.PositiveIntegerField(default=0)
    image_name = models.CharField(max_length=255, blank=True, default='')
    is_hidden = models.BooleanField(default=False)

    def __str__(self):
        return f"Post by {self.user.username} - {self.industry}"


class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='extra_images')
    image = models.ImageField(upload_to='post_images')
    name = models.CharField(max_length=255, blank=True, default='')


##Notifications
class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('connected', 'Connected'),
        ('message_sent', 'Message Sent'),
        ('collaboration', 'Collaboration'),
        ('project_proposal', 'Project Proposal'),
        ('other', 'Other')
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='other')
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    action_type = models.CharField(max_length=30, blank=True, default='')
    action_id = models.PositiveIntegerField(blank=True, null=True)
    project_id = models.PositiveIntegerField(blank=True, null=True)
    link = models.CharField(max_length=500, blank=True, default='')
    is_dismissed = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user.username} - {self.message[:20]}"


#Timezone
class MyModel(models.Model):
    created_at = models.DateTimeField(default=timezone.now)


# Model for connections

class Connection(models.Model):
    initiator = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='initiated_connections')
    target = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='received_connections')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')],
        default='accepted',
    )

    class Meta:
        unique_together = ('initiator', 'target')

    def __str__(self):
        return f"{self.initiator.username} connected with {self.target.username}"


##patent model
class Patent(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(default="Description not provided")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='patents')
    filed_date = models.DateField(default=timezone.now)

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
    name = models.CharField(max_length=255)
    members = models.ManyToManyField(CustomUser, blank=True)
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True,
        on_delete=models.CASCADE, related_name='created_groups'
    )
    description = models.TextField(blank=True, default='')
    industry = models.CharField(
        max_length=50,
        choices=[
            ('tech', 'Technology'), ('finance', 'Finance'), ('health', 'Healthcare'),
            ('edu', 'Education'), ('energy', 'Energy'), ('agriculture', 'Agriculture'),
            ('manufacturing', 'Manufacturing'), ('other', 'Other'),
        ],
        default='other',
    )
    cover_image = models.ImageField(upload_to='group_covers/', blank=True, null=True)
    is_private = models.BooleanField(default=False, help_text='Private groups require admin approval to join')
    created_at = models.DateTimeField(auto_now_add=True)
    is_hidden = models.BooleanField(default=False)


class GroupMembership(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='group_memberships')
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True,
        on_delete=models.SET_NULL, related_name='sent_group_invites'
    )
    status = models.CharField(
        max_length=20,
        choices=[('invited', 'Invited'), ('pending', 'Pending'), ('accepted', 'Accepted'), ('declined', 'Declined')],
        default='pending',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('group', 'user'),)


class GroupDiscussion(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='discussions')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='group_discussions')
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='liked_group_discussions')

    class Meta:
        ordering = ['-created_at']


class GroupDiscussionComment(models.Model):
    discussion = models.ForeignKey(GroupDiscussion, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='group_discussion_comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', blank=True, null=True, on_delete=models.CASCADE, related_name='replies')
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='liked_group_comments')

    class Meta:
        ordering = ['created_at']


class GroupDiscussionImage(models.Model):
    discussion = models.ForeignKey(GroupDiscussion, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='group_discussion_images/')
    name = models.CharField(max_length=255, blank=True, default='')
    is_cover = models.BooleanField(default=False)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order']


##user page
class Page(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owned_pages'
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    industry = models.CharField(
        max_length=50,
        choices=[
            ('tech', 'Technology'), ('finance', 'Finance'), ('health', 'Healthcare'),
            ('edu', 'Education'), ('energy', 'Energy'), ('agriculture', 'Agriculture'),
            ('manufacturing', 'Manufacturing'), ('media', 'Media & Entertainment'),
            ('retail', 'Retail & Commerce'), ('other', 'Other'),
        ],
        default='other',
    )
    cover_image = models.ImageField(upload_to='page_covers/', blank=True, null=True)
    logo = models.ImageField(upload_to='page_logos/', blank=True, null=True)
    website = models.URLField(blank=True, default='')
    followers = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='followed_pages')
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    is_hidden = models.BooleanField(default=False)


class PagePost(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField()
    image = models.ImageField(upload_to='page_post_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class PagePostReaction(models.Model):
    post = models.ForeignKey(PagePost, on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='page_post_reactions')
    reaction = models.CharField(
        max_length=20,
        choices=[('like', 'Like'), ('love', 'Love'), ('insightful', 'Insightful'),
                 ('celebrate', 'Celebrate'), ('support', 'Support')],
        default='like',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('post', 'user'),)


class PagePostShare(models.Model):
    post = models.ForeignKey(PagePost, on_delete=models.CASCADE, related_name='shares')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='page_post_shares')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('post', 'user'),)


class PagePostImage(models.Model):
    post = models.ForeignKey(PagePost, on_delete=models.CASCADE, related_name='post_images')
    image = models.ImageField(upload_to='page_post_images/')
    name = models.CharField(max_length=255, blank=True, default='')
    is_cover = models.BooleanField(default=False)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order']


##comments
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='liked_comments')
    parent = models.ForeignKey('self', blank=True, null=True, on_delete=models.CASCADE, related_name='replies')
    is_hidden = models.BooleanField(default=False)

    def __str__(self):
        return self.content[:50]


class Company(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    industry = models.CharField(
        max_length=100,
        choices=[
            ('technology', 'Technology'),
            ('finance', 'Finance & Banking'),
            ('health', 'Health & Medicine'),
            ('agriculture', 'Agriculture'),
            ('education', 'Education'),
            ('energy', 'Energy'),
            ('manufacturing', 'Manufacturing'),
            ('retail', 'Retail & E-commerce'),
            ('media', 'Media & Entertainment'),
            ('real_estate', 'Real Estate'),
            ('logistics', 'Logistics & Transport'),
            ('consulting', 'Consulting'),
            ('other', 'Other'),
        ],
        default='other',
    )
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    tagline = models.CharField(max_length=300, blank=True, default='')
    company_type = models.CharField(
        max_length=30,
        choices=[
            ('startup', 'Startup'), ('sme', 'SME'), ('enterprise', 'Enterprise'),
            ('ngo', 'NGO / Non-Profit'), ('government', 'Government'), ('other', 'Other'),
        ],
        default='other',
    )
    size = models.CharField(
        max_length=20, blank=True, default='',
        choices=[
            ('1-10', '1–10 employees'), ('11-50', '11–50 employees'),
            ('51-200', '51–200 employees'), ('201-500', '201–500 employees'),
            ('500+', '500+ employees'),
        ],
    )
    location = models.CharField(max_length=255, blank=True, default='')
    website = models.URLField(blank=True, default='')
    email = models.EmailField(blank=True, default='')
    phone = models.CharField(max_length=30, blank=True, default='')
    founded_year = models.PositiveIntegerField(blank=True, null=True)
    cover_image = models.ImageField(upload_to='company_covers/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True,
        on_delete=models.CASCADE, related_name='companies'
    )
    followers = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='followed_companies')

    def __str__(self):
        return self.name


class CompanyMedia(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='media')
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.SET_NULL
    )
    media_type = models.CharField(
        max_length=20,
        choices=[('image', 'Image'), ('video', 'Video'), ('document', 'Document')],
        default='image',
    )
    file = models.FileField(upload_to='company_media/')
    title = models.CharField(max_length=200, blank=True)
    caption = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']


class CompanyUpdate(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='updates')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.SET_NULL
    )
    content = models.TextField()
    image = models.ImageField(upload_to='company_update_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


####Message

class Conversation(models.Model):
    participants = models.ManyToManyField(CustomUser, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    context_type = models.CharField(
        max_length=10,
        choices=[
            ('direct', 'Direct Message'),
            ('post', 'Post Discussion'),
            ('project', 'Project Discussion'),
            ('proposal', 'Proposal Discussion'),
            ('collab', 'Collaboration Discussion'),
        ],
        default='direct',
    )
    post = models.ForeignKey('Post', blank=True, null=True, on_delete=models.SET_NULL, related_name='conversations')
    project = models.ForeignKey('Project', blank=True, null=True, on_delete=models.SET_NULL, related_name='conversations')


class Message(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    conversation = models.ForeignKey(Conversation, null=True, blank=True, on_delete=models.CASCADE, related_name='messages')
    reply_to = models.ForeignKey('self', blank=True, null=True, on_delete=models.SET_NULL, related_name='replies')
    flag_reason = models.TextField(blank=True, null=True)
    flagged_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True,
        on_delete=models.SET_NULL, related_name='admin_flagged_messages'
    )
    is_flagged = models.BooleanField(default=False)
    is_hidden = models.BooleanField(default=False)

    def __str__(self):
        return f"From {self.sender} to {self.recipient} at {self.timestamp}"


class MessageReaction(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='message_reactions')
    emoji = models.CharField(max_length=8)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('message', 'user', 'emoji'),)


class Job(models.Model):
    JOB_TYPE_CHOICES = [
        ('full_time', 'Full Time'), ('part_time', 'Part Time'),
        ('contract', 'Contract'), ('internship', 'Internship'), ('remote', 'Remote'),
    ]
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True, default='')
    description = models.TextField()
    salary_range = models.CharField(max_length=100, blank=True, default='')
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES, default='full_time')
    apply_url = models.URLField(blank=True, default='')
    is_active = models.BooleanField(default=True)
    is_hidden = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True,
        on_delete=models.SET_NULL, related_name='created_jobs'
    )
    company_page = models.ForeignKey(
        Company, blank=True, null=True, on_delete=models.SET_NULL, related_name='jobs'
    )


class JobApplication(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='job_applications')
    letter = models.TextField(blank=True)
    cv = models.FileField(upload_to='job_cvs/', blank=True, null=True)
    attachment = models.FileField(upload_to='job_attachments/', blank=True, null=True)
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-applied_at']
        unique_together = (('job', 'applicant'),)


class ProfileView(models.Model):
    profile_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile_views'
    )
    viewer = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True,
        on_delete=models.SET_NULL, related_name='profile_views_given'
    )
    session_key = models.CharField(max_length=40)
    viewed_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (('profile_user', 'session_key'), ('profile_user', 'viewer'))


class ProjectComment(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='project_comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='liked_project_comments')
    parent = models.ForeignKey('self', blank=True, null=True, on_delete=models.CASCADE, related_name='replies')
    is_hidden = models.BooleanField(default=False)


class ProjectCollaboration(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='collaborations')
    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='project_collaborations')
    message = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'), ('accepted', 'Accepted'), ('declined', 'Declined'),
            ('countered', 'Countered'), ('on_hold', 'On Hold'), ('reviewing', 'Reviewing'),
        ],
        default='pending',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    counter_message = models.TextField(blank=True)
    conversation = models.OneToOneField(
        Conversation, blank=True, null=True,
        on_delete=models.SET_NULL, related_name='project_collab'
    )

    class Meta:
        unique_together = (('project', 'from_user'),)


class ProjectView(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='views')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.SET_NULL
    )
    session_key = models.CharField(max_length=40, blank=True)
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('project', 'session_key'),)


class ProjectProposal(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='proposals')
    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='project_proposals_sent'
    )
    message = models.TextField(blank=True)
    amount = models.CharField(max_length=100, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('declined', 'Declined')],
        default='pending',
    )
    created_at = models.DateTimeField(auto_now_add=True)


class AdminPermissions(models.Model):
    admin_user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='admin_permissions'
    )
    granted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True,
        on_delete=models.SET_NULL, related_name='granted_admin_permissions'
    )
    is_superadmin = models.BooleanField(default=False)
    can_manage_users = models.BooleanField(default=False)
    can_manage_projects = models.BooleanField(default=False)
    can_manage_posts = models.BooleanField(default=False)
    can_manage_messages = models.BooleanField(default=False)
    can_manage_events = models.BooleanField(default=False)
    can_manage_jobs = models.BooleanField(default=False)
    can_manage_comments = models.BooleanField(default=False)
    can_manage_connections = models.BooleanField(default=False)
    can_view_reports = models.BooleanField(default=True)
    granted_at = models.DateTimeField(auto_now_add=True)


class EventRegistration(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='event_registrations')
    registered_at = models.DateTimeField(auto_now_add=True)
    full_name = models.CharField(max_length=200, blank=True)
    email = models.EmailField(max_length=254, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = (('event', 'user'),)


class PageView(models.Model):
    path = models.CharField(max_length=500)
    session_key = models.CharField(max_length=64, blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    browser = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    device_type = models.CharField(
        max_length=10, blank=True,
        choices=[('desktop', 'Desktop'), ('mobile', 'Mobile'), ('tablet', 'Tablet'),
                 ('bot', 'Bot'), ('other', 'Other')],
    )
    os = models.CharField(max_length=100, blank=True)
    referrer = models.CharField(max_length=500, blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.SET_NULL
    )

    class Meta:
        ordering = ['-timestamp']


class ClickEvent(models.Model):
    path = models.CharField(max_length=500)
    element_id = models.CharField(max_length=200, blank=True)
    element_text = models.CharField(max_length=200, blank=True)
    session_key = models.CharField(max_length=64, blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.SET_NULL
    )

    class Meta:
        ordering = ['-timestamp']


class NewsItem(models.Model):
    title = models.CharField(max_length=300)
    body = models.TextField()
    icon_url = models.URLField(blank=True, default='')
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to='news_images/', blank=True, null=True)
    is_hidden = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True,
        on_delete=models.SET_NULL, related_name='news_items'
    )

    class Meta:
        ordering = ['-created_at']


class ContactSubmission(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=254)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_replied = models.BooleanField(default=False)

    class Meta:
        ordering = ['-submitted_at']


class Collaboration(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='collaborations')
    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_collaborations')
    message = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('declined', 'Declined')],
        default='pending',
    )
    created_at = models.DateTimeField(auto_now_add=True)


class PatentRequest(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='patent_requests')
    from_investor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_patent_requests'
    )
    message = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('declined', 'Declined')],
        default='pending',
    )
    created_at = models.DateTimeField(auto_now_add=True)


class Proposal(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='proposals')
    from_investor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_proposals'
    )
    message = models.TextField(blank=True)
    amount = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'), ('accepted', 'Accepted'), ('declined', 'Declined'),
            ('countered', 'Countered'), ('on_hold', 'On Hold'), ('reviewing', 'Reviewing'),
        ],
        default='pending',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    conversation = models.OneToOneField(
        Conversation, blank=True, null=True, on_delete=models.SET_NULL, related_name='proposal'
    )
    counter_amount = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True)
    counter_message = models.TextField(blank=True)


class SurveyResponse(models.Model):
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True,
        on_delete=models.SET_NULL, related_name='survey_responses'
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    ui_design = models.PositiveSmallIntegerField(blank=True, null=True)
    ui_consistency = models.PositiveSmallIntegerField(blank=True, null=True)
    ux_navigation = models.PositiveSmallIntegerField(blank=True, null=True)
    ux_findability = models.PositiveSmallIntegerField(blank=True, null=True)
    usability_tasks = models.PositiveSmallIntegerField(blank=True, null=True)
    usability_controls = models.PositiveSmallIntegerField(blank=True, null=True)
    exp_satisfaction = models.PositiveSmallIntegerField(blank=True, null=True)
    exp_recommend = models.CharField(
        max_length=5, blank=True,
        choices=[('yes', 'Yes'), ('maybe', 'Maybe'), ('no', 'No')],
    )
    func_reliability = models.PositiveSmallIntegerField(blank=True, null=True)
    func_missing = models.TextField(blank=True)
    comments = models.TextField(blank=True)
    feedback_text = models.TextField(blank=True, default='')
    feedback_type = models.CharField(
        max_length=20, blank=True, default='',
        choices=[
            ('bug', 'Bug / Issue'), ('suggestion', 'Suggestion'), ('praise', 'Praise'),
            ('question', 'Question'), ('other', 'Other'),
        ],
    )
    page = models.CharField(max_length=100, blank=True, default='')
    section = models.CharField(max_length=100, blank=True, default='')

    class Meta:
        ordering = ['-submitted_at']


class ShareEvent(models.Model):
    platform = models.CharField(
        max_length=20,
        choices=[
            ('whatsapp', 'WhatsApp'), ('telegram', 'Telegram'), ('twitter', 'Twitter / X'),
            ('facebook', 'Facebook'), ('linkedin', 'LinkedIn'), ('instagram', 'Instagram'),
            ('copy_link', 'Copy Link'), ('other', 'Other'),
        ],
        default='other',
    )
    share_type = models.CharField(
        max_length=20,
        choices=[('individual', 'Individual / DM'), ('group', 'Group / Channel'), ('general', 'General')],
        default='general',
    )
    content_type = models.CharField(
        max_length=20, blank=True,
        choices=[
            ('project', 'Project'), ('post', 'Post'), ('profile', 'Profile'),
            ('page', 'Page'), ('other', 'Other'),
        ],
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    shared_url = models.URLField(max_length=600, blank=True)
    shared_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    shared_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='share_events'
    )

    class Meta:
        ordering = ['-shared_at']


class ReadLater(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='read_later_items')
    post = models.ForeignKey(Post, blank=True, null=True, on_delete=models.CASCADE, related_name='read_later_saves')
    project = models.ForeignKey(Project, blank=True, null=True, on_delete=models.CASCADE, related_name='read_later_saves')
    company = models.ForeignKey(Company, blank=True, null=True, on_delete=models.CASCADE, related_name='read_later_saves')
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-saved_at']


class Meeting(models.Model):
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_meetings')
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='meetings')
    conversation = models.ForeignKey(
        Conversation, blank=True, null=True, on_delete=models.SET_NULL, related_name='meetings'
    )
    title = models.CharField(max_length=200, blank=True, default='')
    room_id = models.CharField(max_length=32, blank=True, unique=True)
    scheduled_at = models.DateTimeField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=[('scheduled', 'Scheduled'), ('active', 'Active'), ('ended', 'Ended')],
        default='scheduled',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    duration = models.PositiveIntegerField(default=60, help_text='Duration in minutes')
    zoom_meeting_id = models.CharField(max_length=30, blank=True, default='')
    zoom_join_url = models.URLField(max_length=500, blank=True, default='')
    zoom_start_url = models.TextField(blank=True, default='')
    zoom_password = models.CharField(max_length=50, blank=True, default='')
    recording_status = models.CharField(
        max_length=20, blank=True, default='',
        choices=[('', 'None'), ('processing', 'Processing'), ('completed', 'Available')],
    )
    recording_url = models.URLField(max_length=500, blank=True, default='')
