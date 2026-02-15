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

    

##Create user signal
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()

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
        choices=[
            ("tech", "Technology"),
            ("health", "Healthcare"),
            ("finance", "Finance"),
            ("education", "Education"),
            ("energy", "Energy"),
        ],
        default="tech"
    )

    # Default image if none is provided
    image = models.ImageField(upload_to='project_images/', null=True, blank=True, default='project_images/mac.png')

    # Optional website link
    website_link = models.URLField(null=True, blank=True, default="http://example.com")

    # Auto-generated creation date
    created_at = models.DateTimeField(auto_now_add=True)

    # Users who liked the project (Many-to-Many relationship)
    liked_by = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_projects', blank=True)

    # Rating field (default value is 0)
    rating = models.IntegerField(default=0)

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
    # user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, default=get_default_user)
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

    def __str__(self):
        return f"Post by {self.user.username} - {self.industry}"
    



##Notifications
class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('connected', 'Connected'),
        ('message_sent', 'Message Sent'),
        ('other', 'Other')
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='other')
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

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
    name = models.CharField(max_length=255)
    members = models.ManyToManyField(CustomUser)
##user page
class Page(models.Model):
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)

# 

##posts


##comments
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    

##Who viewed your profile
    

##companies that viewed your profile

class Company(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    industry = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='company_logos/', default='default_company.png')

    def __str__(self):
        return self.name


##followers

##Customlogin


##follow requests


##



####Message
from django.conf import settings

class Conversation(models.Model):
    participants = models.ManyToManyField(CustomUser, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)

class Message(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    # conversation = models.ForeignKey(Conversation, related_name='messages', on_delete=models.CASCADE)
    conversation = models.ForeignKey(Conversation, null=True, blank=True, on_delete=models.CASCADE, related_name='messages')


    def __str__(self):
        return f"From {self.sender} to {self.recipient} at {self.timestamp}"


###pagination


##3
