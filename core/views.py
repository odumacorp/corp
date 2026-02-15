from .models import CustomUser, Company, Project, UserProfile
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Message
from .models import Group, Page, Post
from .models import Post, Comment

from django.core.mail import send_mail
from .forms import ProjectForm, ContactForm, CustomUserCreationForm
from django.utils.timezone import now
from .forms import CustomLoginForm, ProfileUpdateForm, CustomPasswordChangeForm, ProfileEditForm

from django.contrib.auth import update_session_auth_hash

from django.db.models import Count


from .models import Project
# ProjectImage

from .forms import ProjectForm, AttachmentForm
from django.views.generic import ListView

###
from django.shortcuts import render
from django.views.generic import ListView
from .models import Project, Attachment
from django.db.models import Q
from .models import CustomUser

from django.contrib.auth import get_user_model
from django.db.models import Q


@login_required
def project_list(request):
    query = request.GET.get("q", "")
    industry = request.GET.get("industry", "")
    user_id = request.GET.get("user", "")

    projects = Post.objects.all().order_by("-created_at")

    if query:
        projects = projects.filter(Q(title__icontains=query) | Q(content__icontains=query))
    if industry:
        projects = projects.filter(industry=industry)
    if user_id:
        projects = projects.filter(user__id=user_id)

    # Pagination
    paginator = Paginator(projects, 10)  # 10 per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "projects": page_obj.object_list,
        "page_obj": page_obj,
        "paginator": paginator,
        "is_paginated": page_obj.has_other_pages(),
        "current_query": query,
        "current_industry": industry,
        "current_user": user_id,
        "industries": Post.objects.values_list("industry", flat=True).distinct(),
        "users": CustomUser.objects.all(),
        "my_posts": Post.objects.filter(user=request.user),
    }

    return render(request, "project_list.html", context)




from django.shortcuts import render
from django.views.generic import DetailView

class UserProfileView(DetailView):
    model = CustomUser
    template_name = 'user_profile.html'  # Change this to your actual template
    context_object_name = 'user'


##proposals

##user posts

# ##Edit profile pic
@login_required
def edit_profile(request):
    user = request.user

    # Ensure the user has a profile
    if not hasattr(user, 'userprofile'):
        UserProfile.objects.create(user=user)

    profile = user.userprofile  # Get the actual profile

    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully')
            return redirect('profile_view', id=user.id)
    else:
        form = ProfileEditForm(instance=profile)

    return render(request, 'edit_profile.html', {'form': form})




##counts
from .models import Patent
from .models import Connection 
from .models import Like
from .models import Interest



def investors_view(request):
    industry_filter = request.GET.get('industry')
    if industry_filter:
        investors = CustomUser.objects.filter(user_type='investor', userprofile__industry=industry_filter)
    else:
        investors = CustomUser.objects.filter(user_type='investor')

    industries = UserProfile.INDUSTRY_CHOICES

    return render(request, 'investors.html', {
        'investors': investors,
        'industries': industries,
        'selected_industry': industry_filter,
    })

def investors_by_industry(request):
    industry = request.GET.get('industry')
    investors = CustomUser.objects.filter(user_type='investor', userprofile__industry=industry)
    return render(request, 'investors_by_industry.html', {
        'investors': investors,
        'industry_name': industry
    })
@login_required
def investors_by_industry_view(request, industry_name):
    investors = CustomUser.objects.filter(user_type='investor', userprofile__industry=industry_name)
    context = {
        'investors': investors,
        'industry_name': industry_name,
    }
    return render(request, 'investors_by_industry.html', context)

@login_required
def my_profile_view(request):
    return redirect('profile_view', id=request.user.id)

@login_required
def profile_view(request, id):
    user_obj = get_object_or_404(CustomUser, id=id)
    profile = get_object_or_404(UserProfile, user=user_obj)

    # Common stats
    inventor_connections = Connection.objects.filter(target=user_obj, initiator__userprofile__user_type='investor').count()
    investor_connections = Connection.objects.filter(initiator=user_obj, target__userprofile__user_type='innovator').count()

    projects_count = Project.objects.filter(owner=user_obj).count()
    patents_count = Patent.objects.filter(owner=user_obj).count()
    likes_count = Like.objects.filter(user=user_obj).count()
    interests_count = Interest.objects.filter(user=user_obj).count()

    context = {
        'profile': profile,
        'inventor_connections': inventor_connections,
        'investor_connections': investor_connections,
        'projects_count': projects_count,
        'patents_count': patents_count,
        'likes_count': likes_count,
        'interests_count': interests_count
    }

    return render(request, 'profile.html', context)


################

def app_view(request):
    if request.user.is_authenticated:
        profile = request.user  # Since request.user is already the logged-in CustomUser
        print(f"Profile: {profile.username}, Full Name: {profile.get_full_name()}, First Name: {profile.first_name}, Last Name: {profile.last_name}")
    else:
        profile = None
        print("No authenticated user.")

    return render(request, 'app.html', {'profile': profile})


def home_view(request):
    user = request.user

    # Fetch Companies
    companies = Company.objects.all()[:6]

    # Fetch Nodes in Community
    community_nodes = CustomUser.objects.filter(connections_received__user=user).exclude(id=user.id)[:6]

    # Fetch Profile-Based Companies
    profile_based_companies = Company.objects.filter(industry=user.profile.industry)[:6]

    return render(request, "app.html", {
        # "node_suggestions": node_suggestions,
        "companies": companies,
        "community_nodes": community_nodes,
        "profile_based_companies": profile_based_companies
    })

# Views pages
##linkedin
def linkedin(request):
    context = {"page_title": "Linkedin" , "page_name": "Linkedin"}
    return render(request, 'linkedin.html', context)

##index.html
def index(request):
    # context = {"page_title": "Home"}
    return render(request, 'index.html',{"hide_navbar": True})
##about.html
def about(request):
    context = {"page_title": "About" , "page_name": "About"}
    return render(request, 'about.html', context)
##services.html
def services(request):
    context = {"page_title": "Services", "page_name": "Services"}
    return render(request, 'services.html', context)

##dashboard.html
def dashboard(request):
    context = {"page_title": "Dashboard", "page_name": "Dashboard"}
#     return render(request, 'dashboard.html', context)


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Project, Attachment
from .forms import ProjectForm, AttachmentForm

####
@login_required
def dashboard(request, user_id=None):
    if request.method == "POST":
        # EDIT PROJECT logic
        if 'post_id' in request.POST:
            post_id = request.POST.get('post_id')
            project = get_object_or_404(Project, id=post_id, owner=request.user)
            project_form = ProjectForm(request.POST, request.FILES, instance=project)
            attachment_form = AttachmentForm()

            if project_form.is_valid():
                project_form.save()

                for f in request.FILES.getlist('attachments'):
                    Attachment.objects.create(project=project, file=f)

                return redirect('dashboard')

        # ADD PROJECT logic
        elif 'add_project' in request.POST:
            project_form = ProjectForm(request.POST, request.FILES)
            attachment_form = AttachmentForm(request.POST, request.FILES)

            if project_form.is_valid():
                project = project_form.save(commit=False)
                project.owner = request.user
                project.user = request.user
                project.save()

                for f in request.FILES.getlist('attachments'):
                    Attachment.objects.create(project=project, file=f)

                return redirect('dashboard')

        else:
            # Catch-all POST fallback to prevent UnboundLocalError
            project_form = ProjectForm()
            attachment_form = AttachmentForm()

    else:
        project_form = ProjectForm()
        attachment_form = AttachmentForm()

    projects = Project.objects.filter(owner=request.user).order_by('-created_at')
    for project in projects:
        project.main_image = project.get_main_image_url()

    return render(request, 'dashboard.html', {
        'project_form': project_form,
        'attachment_form': attachment_form,
        'projects': projects,
        'industry_choices': Project._meta.get_field('industry').choices,
    })






# View to handle attachment creation
def add_attachment(request, project_id):
    project = Project.objects.get(id=project_id)  # Get the associated project

    if request.method == 'POST':
        form = AttachmentForm(request.POST, request.FILES)
        if form.is_valid():
            # Save the uploaded attachment
            for file in request.FILES.getlist('attachments'):
                attachment = Attachment(project=project, file=file)
                attachment.save()
            # Redirect to the same page to add more attachments
            return redirect('dashboard')  # You may change 'dashboard' to the actual name of your dashboard URL
    else:
        form = AttachmentForm()

    return render(request, 'add_attachment.html', {'form': form, 'project': project})


def user_project_attachments(request, user_id, project_id):
    project = get_object_or_404(Project, id=project_id, user_id=user_id)
    attachments = Attachment.objects.filter(project=project)
    return render(request, 'user_attachments.html', {'attachments': attachments, 'project': project})

##image uploads
from django.shortcuts import render, redirect
from .models import Project, ProjectImage
from .forms import ProjectImageForm

def upload_image(request, project_id):
    project = Project.objects.get(id=project_id)
    
    if request.method == 'POST':
        form = ProjectImageForm(request.POST, request.FILES, project=project)
        if form.is_valid():
            form.save()
            return redirect('project_images', project_id=project.id)
    else:
        form = ProjectImageForm(project=project)
    return render(request, 'upload_image.html', {'form': form, 'project': project})


@login_required
def project_images(request, project_id):
    project = get_object_or_404(Project, id=project_id, user=request.user)
    # project = get_object_or_404(Project, id=project_id, owner=request.user)

    images = project.images.all()
    form = ProjectImageForm()

    if request.method == 'POST':
        if 'upload_image' in request.POST:
            form = ProjectImageForm(request.POST, request.FILES)
            if form.is_valid():
                new_image = form.save(commit=False)
                new_image.project = project
                new_image.save()
                return redirect('project_images', project_id=project_id)

        elif 'main_image' in request.POST:
            image_id = request.POST.get('main_image')
            ProjectImage.objects.filter(project=project, is_main=True).update(is_main=False)
            ProjectImage.objects.filter(id=image_id, project=project).update(is_main=True)
            return redirect('project_images', project_id=project_id)

        elif 'delete_image' in request.POST:
            image_id = request.POST.get('delete_image')
            ProjectImage.objects.filter(id=image_id, project=project).delete()
            return redirect('project_images', project_id=project_id)

    return render(request, 'project_images.html', {
        'project': project,
        'images': images,
        'form': form
    })



##events.html
def events(request):
    context = {"page_title": "Event and News", "page_name": "Event and News"}
    return render(request, 'events.html', context)
##jobs.html
def jobs(request):
    context = {"page_title": "Jobs", "page_name": "Jobs"}
    return render(request, 'jobs.html', context)
##messages.html
def user_messages(request):
    context = {"page_title": "Messages", "page_name": "Messages"}
    return render(request, 'messages.html', context)
##networks.html
def networks(request):
    context = {"page_title": "Networks", "page_name": "Networks"}
    return render(request, 'networks.html', context)
##notifications.html
def notifications(request):
    context = {"page_title": "Notifications", "page_name": "Notifications"}
    return render(request, 'notifications.html', context)


from .models import Notification
@login_required
def notifications_view(request):
    # Fetch the logged-in user's notifications
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')

    # Separate notifications by type (connected, message_sent, etc.)
    connected_notifications = notifications.filter(notification_type='connected')
    message_notifications = notifications.filter(notification_type='message_sent')
    other_notifications = notifications.filter(notification_type='other')

    context = {
        'connected_notifications': connected_notifications,
        'message_notifications': message_notifications,
        'other_notifications': other_notifications,
    }
    return render(request, 'notifications.html', context)



@login_required
def connect_investor(request, investor_id):
    investor = get_object_or_404(CustomUser, id=investor_id)

    if request.user != investor:
        try:
            investor_profile = investor.userprofile
            current_user_profile = request.user.userprofile
            investor_profile.connected_users.add(current_user_profile)
            investor_profile.save()


            # Create a notification for the current user
            Notification.objects.create(
                user=request.user,
                message=f"You are now connected with Investor: {investor.get_full_name() or investor.username}",
                notification_type='connected'
            )
            
            # Create a notification for the investor
            Notification.objects.create(
                user=investor,
                message=f"{request.user.get_full_name() or request.user.username} has connected with you.",
                notification_type='connected'
            )


            messages.success(request, f"You are now connected with {investor.get_full_name()}.")
            
            # Create a notification for the current user
            Notification.objects.create(
                user=request.user,
                message=f"You are now connected with Investor: {investor.get_full_name() or investor.username}"
            )
            
            # Create a notification for the investor
            Notification.objects.create(
                user=investor,
                message=f"{request.user.get_full_name() or request.user.username} has connected with you."
            )
        except AttributeError:
            messages.error(request, "The investor profile does not exist.")
    else:
        messages.warning(request, "You cannot connect with yourself.")

    # Redirect back to the referring page
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return HttpResponseRedirect(referer)
    return redirect('investors')



def get_connected_user_ids(user):
    from core.models import Connection  # adjust the import path to your Connection model
    connections = Connection.objects.filter(
        Q(initiator=user, status='connected') |  # change from 'from_user' to 'initiator'
        Q(target=user, status='connected')      # change from 'to_user' to 'target'
    )

    connected_ids = set()
    for conn in connections:
        if conn.initiator == user:  # change from 'from_user' to 'initiator'
            connected_ids.add(conn.target.id)  # change from 'to_user' to 'target'
        else:
            connected_ids.add(conn.initiator.id)  # change from 'from_user' to 'initiator'
    return connected_ids




##innovators project in app

from django.shortcuts import render
from django.db.models import Prefetch
from .models import CustomUser, Project

def innovators_projects_view(request):
    project_prefetch = Prefetch(
        'projects',
        queryset=Project.objects.order_by('-created_at'),
        to_attr='prefetched_projects'
    )

    innovators = CustomUser.objects.filter(user_type='innovator') \
        .select_related('userprofile') \
        .prefetch_related(project_prefetch)

    all_innovators_with_projects = []

    for innovator in innovators:
        projects = getattr(innovator, 'prefetched_projects', [])
        if projects:
            all_innovators_with_projects.append({
                'innovator': innovator,
                'projects': projects,
                'first_project': projects[0],
            })

    return render(request, 'app.html', {
        'all_innovators_with_projects': all_innovators_with_projects,
        'connected_user_ids': get_connected_user_ids(request.user),
    })



####Placeholder for projects in app
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required

@login_required
def get_projects_data(request):
    innovators = CustomUser.objects.filter(user_type='innovator').prefetch_related('projects', 'userprofile')

    all_innovators_with_projects = []

    for innovator in innovators:
        # Serialize project data manually since we can't pass model instances directly to JSON
        projects_data = innovator.projects.all().order_by('-created_at').values('id', 'title', 'description', 'created_at', 'image')
        
        if projects_data.exists():
            all_innovators_with_projects.append({
                'innovator': {
                    'username': innovator.username,
                    'full_name': innovator.get_full_name(),
                    'industry': innovator.userprofile.industry,
                },
                'projects': list(projects_data),
            })

    # Render the partial template with the context
    html = render_to_string('_partials/project_cards.html', {
        'all_innovators_with_projects': all_innovators_with_projects
    }, request=request)

    return JsonResponse({'html': html})



##innovator_page.html
# def innovators_view(request):
#     innovators = CustomUser.objects.filter(user_type='innovator')
#     for innovator in innovators:
#         innovator.first_project = innovator.projects.first()
#     return render(request, 'innovators.html', {'innovators': innovators})


def innovators_view(request):
    innovators = CustomUser.objects.filter(user_type='innovator').select_related('userprofile')

    for innovator in innovators:
        innovator.first_project = innovator.projects.order_by('-created_at').first()  # assumes related_name='projects'
        # innovator.first_project = innovator.project_set.order_by('-created_at').first()

    return render(request, 'innovators.html', {'innovators': innovators})



@login_required
def inbox(request):
    messages = Message.objects.filter(recipient=request.user).order_by('-timestamp')
    unread_count = messages.filter(is_read=False).count()
    return render(request, 'inbox.html', {'messages': messages, 'unread_count': unread_count, 'page_name': 'Inbox'})

@login_required
def sent_items(request):
    sent = Message.objects.filter(sender=request.user).order_by('-timestamp')
    return render(request, 'sent_items.html', {'messages': sent, 'page_name': 'Sent'})

@login_required
def send_message(request, recipient_id):
    recipient = CustomUser.objects.get(id=recipient_id)
    if request.method == "POST":
        content = request.POST.get("content")
        Message.objects.create(sender=request.user, recipient=recipient, content=content)
        return redirect('sent_items')
    return render(request, 'send_message.html', {'recipient': recipient})

@login_required
def connect_innovator(request, user_id):
    target_user = get_object_or_404(CustomUser, id=user_id)
    target_profile = get_object_or_404(UserProfile, user=target_user)
    current_user = request.user
    current_profile = get_object_or_404(UserProfile, user=current_user)

    if target_profile != current_profile:
        # Check if already connected, if not connect
        if current_profile not in target_profile.connected_users.all():
            target_profile.connected_users.add(current_profile)
            messages.success(request, f"You are now connected to {target_user.get_full_name() or target_user.username}.")
        else:
            target_profile.connected_users.remove(current_profile)
            messages.success(request, f"You have disconnected from {target_user.get_full_name() or target_user.username}.")
        target_profile.save()
    else:
        messages.warning(request, "You cannot connect with yourself.")

    return redirect('innovators')


      
##connect
@login_required
def connect_investor(request, investor_id):
    investor = get_object_or_404(CustomUser, id=investor_id)
    investor_profile = investor.userprofile
    current_user_profile = request.user.userprofile

    if investor != request.user:
        # Check if already connected, if not connect
        if current_user_profile not in investor_profile.connected_users.all():
            investor_profile.connected_users.add(current_user_profile)
            investor_profile.save()
            messages.success(request, f"You are now connected with {investor.get_full_name()}.")
        else:
            investor_profile.connected_users.remove(current_user_profile)
            investor_profile.save()
            messages.success(request, f"You have disconnected from {investor.get_full_name()}.")
    else:
        messages.warning(request, "You cannot connect with yourself.")

    # Redirect back to the referring page
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return HttpResponseRedirect(referer)
    return redirect('investors')



###
from django.http import HttpResponseRedirect

@login_required
def disconnect_user(request, user_id):
    current_user_profile = request.user.userprofile
    user_to_disconnect = get_object_or_404(CustomUser, id=user_id)
    
    # Ensure the user is in the connected_users list before disconnecting
    if user_to_disconnect in current_user_profile.connected_users.all():
        current_user_profile.disconnect_from_user(user_to_disconnect)
        messages.success(request, f'You have disconnected from {user_to_disconnect.username}.')
    else:
        messages.error(request, 'You are not connected to this user.')

    # Redirect back to the referring page
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return HttpResponseRedirect(referer)
    return redirect('networks')  # fallback if no referer is found




from django.contrib import messages

@login_required
def connect_user(request, user_id):
    if request.method == 'POST':
        user_profile = get_object_or_404(UserProfile, user=request.user)
        friend_to_add = get_object_or_404(CustomUser, id=user_id)

        user_profile.friends.add(friend_to_add)
        user_profile.save()

        messages.success(request, f"You are now connected with {friend_to_add.get_full_name()}.")
        return redirect(request.META.get('HTTP_REFERER', 'app'))

    return redirect('app')




from django.core.mail import send_mail  # For email messaging, or use your preferred method.

@login_required
def message_innovator(request, user_id):
    recipient = get_object_or_404(UserProfile, id=user_id)

    # Get or create past conversation
    messages = Message.objects.filter(
        Q(sender=request.user, recipient=recipient.user) |
        Q(sender=recipient.user, recipient=request.user)
    ).order_by('timestamp')

    if request.method == "POST":
        content = request.POST.get("content")
        if content:
            Message.objects.create(sender=request.user, recipient=recipient.user, content=content)
            return redirect('message_innovator', user_id=recipient.id)

    return render(request, 'messages/message_thread.html', {
        'recipient': recipient,
        'messages': messages,
    })


# #  
from django.http import JsonResponse
@login_required
def like_project(request, pk):
    project = get_object_or_404(Project, pk=pk)

    # Toggle the like status
    if request.user in project.liked_by.all():
        project.liked_by.remove(request.user)
        liked = False
    else:
        project.liked_by.add(request.user)
        liked = True

    # Save the project to persist the changes
    project.save()

    # Return the result as JSON
    return JsonResponse({'liked': liked, 'project_id': project.pk})


from django.views.decorators.csrf import csrf_exempt
import json
from .models import Project, Rating
@login_required
@csrf_exempt
def rate_project(request, pk):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            rating_value = int(data.get('rating'))

            project = Project.objects.get(pk=pk)

            # Update or create rating
            rating_obj, created = Rating.objects.update_or_create(
                user=request.user,
                project=project,
                defaults={'value': rating_value}
            )

            # Return new average
            avg = project.average_rating()

            return JsonResponse({'success': True, 'rating': avg})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
  
@login_required
def message_investor(request, investor_id):
    investor = get_object_or_404(CustomUser, id=investor_id)


    # Create a notification for the message sent
    Notification.objects.create(
        user=request.user,
        message=f"You sent a message to Investor: {investor.get_full_name() or investor.username}",
        notification_type='message_sent'
    )

    # Create a notification for the investor
    Notification.objects.create(
        user=investor,
        message=f"{request.user.get_full_name() or request.user.username} sent you a message.",
        notification_type='message_sent'
    )
    messages.success(request, f"Message sent to {investor.get_full_name()}.")

    if request.user != investor:
        # You can redirect to a message form or chat view
        return redirect('start_conversation', user_id=investor.id)  # Example URL name
    
    
    return redirect('investors_list')

####
from .forms import MessageForm
from .models import Conversation, Message

@login_required
def start_conversation(request, user_id):
    other_user = get_object_or_404(CustomUser, pk=user_id)

    # Try to find existing conversation
    conversation = Conversation.objects.filter(participants=request.user).filter(participants=other_user).first()

    # Create new if none found
    if not conversation:
        conversation = Conversation.objects.create()
        conversation.participants.add(request.user, other_user)

    return redirect('chat_page', conversation_id=conversation.id)

@login_required
def chat_page(request, conversation_id):
    # Fetch the conversation
    conversation = get_object_or_404(Conversation, id=conversation_id)

    # Get the participant (other than the current user)
    participant = conversation.participants.exclude(id=request.user.id).first()

    # Get the messages associated with the conversation
    messages = Message.objects.filter(conversation=conversation)

    # Get the participant's full name if available
    participant_name = participant.get_full_name() if participant else "Unknown"

    # Pass the necessary data to the template
    context = {
        'conversation': conversation,
        'participant_name': participant_name,
        'messages': messages,
        'form': MessageForm(),  # Assuming you have a form for sending messages
    }

    return render(request, 'chat_page.html', context)




# def chat_page(request, conversation_id):
#     # conversation = get_object_or_404(Conversation, id=conversation_id)
#     conversation = Conversation.objects.get(id=conversation_id)
#     participant = conversation.participants.exclude(id=request.user.id).first()

#     # Now get the participant's full name
#     participant_name = participant.get_full_name if participant else "Unknown"

#     # Pass this name to the template context
#     context = {
#         'conversation': conversation,
#         'participant_name': participant_name,
#         'messages': messages,
#         'form': form,
#     }

#     if request.user not in conversation.participants.all():
#         return redirect('home')  # Or raise PermissionDenied

#     if request.method == 'POST':
#         form = MessageForm(request.POST)
#         if form.is_valid():
#             message = form.save(commit=False)
#             message.conversation = conversation
#             message.sender = request.user
#             message.save()
#             return redirect('chat_page', conversation_id=conversation.id)
#     else:
#         form = MessageForm()

#     messages = conversation.messages.order_by('timestamp')
#     return render(request, 'chat_page.html', {'conversation': conversation, 'messages': messages, 'form': form})



##contact
def contact(request):
    context = {"page_title": "contact", "page_name": "contact"}
    return render(request, 'contact.html', context)

##app.html
def app_view(request):
    context = {"page_title": "App Center"}
    return render(request, 'app.html', context)

# def my_projects(request):
#     return render(request, 'my_projects.html')
@login_required
def my_projects(request):
    posts = Post.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'my_projects.html', {'posts': posts})



@login_required
def user_projects(request):
    posts = Post.objects.filter(user=request.user).order_by("-created_at")

    context = {
        "page_title": "My Projects",
        "posts": posts,
    }
    return render(request, "project_list.html", context)


##view all projects
from django.core.paginator import Paginator
def all_projects_view(request):
    query = request.GET.get('q', '')
    industry = request.GET.get('industry', '')
    user_id = request.GET.get('user', '')

    projects = Project.objects.all()

    if query:
        projects = projects.filter(title__icontains=query) | projects.filter(description__icontains=query)

    if industry:
        projects = projects.filter(industry=industry)

    if user_id:
        projects = projects.filter(user__id=user_id)

    paginator = Paginator(projects.order_by('-created_at'), 10)  # Show 10 projects per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'projects': page_obj,
        'industries': Project.objects.values_list('industry', flat=True).distinct(),
        'users': CustomUser.objects.filter(project__isnull=False).distinct(),
        'current_query': query,
        'current_industry': industry,
        'current_user': user_id,
        'is_paginated': page_obj.has_other_pages(),
        'page_obj': page_obj,
        'paginator': paginator,
    }
    return render(request, 'all_projects.html', context)
###########################

##########

## Handle 5 images
# views.py
from .forms import ProjectForm
from django.shortcuts import render, redirect
from .forms import ProjectForm
from .models import Project


##post_list

##intentor page


def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    return render(request, 'project_detail.html', {'project': project})

# def project_detail(request, pk):
#     # Get the project by its ID (pk)
#     post = get_object_or_404(Post, pk=pk)
    
#     # Pass the project data to the template
#     return render(request, 'project_detail.html', {'post': post})

###Attachment

def user_attachments(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    attachments = Attachment.objects.filter(project__user=user)
    return render(request, 'user_attachments.html', {
        'user': user,
        'attachments': attachments,
    })


def filter_by_industry(request, industry):
    posts = Post.objects.filter(industry=industry)
    return render(request, 'dashboard.html', {'posts': posts})

def filter_by_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    posts = Post.objects.filter(user=user)
    return render(request, 'dashboard.html', {'posts': posts})

def filter_by_date(request, date):
    posts = Post.objects.filter(created_at__date=date)
    return render(request, 'dashboard.html', {'posts': posts})


#

##profile pic update
def update_profile(request):
    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile picture updated successfully!")
            return redirect('profile')  # Redirect to the profile page
    else:
        form = ProfileUpdateForm()

    return render(request, "update_profile.html", {"form": form})


########################

##edit profile name and pass
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import ProfileUpdateForm, CustomPasswordChangeForm  # Adjust the imports as necessary

@login_required
def profile(request):
    if request.method == 'POST':
        # Profile update form handling
        profile_form = ProfileUpdateForm(request.POST, instance=request.user)
        password_form = CustomPasswordChangeForm(request.user, request.POST)

        # Check if profile update button was pressed
        if 'edit_profile' in request.POST:
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, "Profile updated successfully!")
                return redirect('profile')

        # Check if password update button was pressed
        elif 'update_password' in request.POST:
            if password_form.is_valid():
                user = password_form.save()  # Save the new password
                update_session_auth_hash(request, user)  # Prevent session logout
                messages.success(request, "Password updated successfully!")
                return redirect('profile')
            else:
                messages.error(request, "Please correct the errors below.")

    else:
        profile_form = ProfileUpdateForm(instance=request.user)
        password_form = CustomPasswordChangeForm(request.user)

    return render(request, 'profile.html', {
        'profile_form': profile_form,
        'password_form': password_form
    })

@login_required
def update_password(request):
    if request.method == 'POST':
        password_form = CustomPasswordChangeForm(request.user, request.POST)

        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)  # Keep the user logged in
            messages.success(request, "Password updated successfully!")
            return redirect('profile')  # Redirect back to the profile page
        else:
            messages.error(request, "There was an error updating your password. Please try again.")
    else:
        password_form = CustomPasswordChangeForm(request.user)
    return render(request, 'update_password.html', {'password_form': password_form})



# Delete Project
def delete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.method == "POST":
        project.delete()
        return redirect('innovators')  # Redirect back to the innovator page
    return render(request, 'confirm_delete.html', {'project': project})

# Edit Project
def edit_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    if request.method == "POST":
        form = ProjectForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            form.save()
            return redirect('dashboard') # Redirect back to the innovator page
    else:
        form = ProjectForm(instance=project)

    context = {
        'form': form,
        'project': project,
    }
    return render(request, 'dashboard.html', context)

#####Edit from dashboard
def edit_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    if request.method == "POST":
        form = ProjectForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            form.save()
            return redirect('dashboard')  # Redirect back to the innovator page
    else:
        form = ProjectForm(instance=project)

    context = {
        'form': form,
        'project': project,
    }
    return render(request, 'dashboard.html', context)


# User Registration
###########
from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CustomUserCreationForm
from .models import UserProfile

def register(request):
    context = {"page_title": "App Center"}
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Save the CustomUser form and create the user
            user = form.save()

            # Create the UserProfile for the new user
            if not hasattr(user, 'userprofile'):
                UserProfile.objects.create(user=user)

            # Log the user in
            login(request, user)

            # Success message
            messages.success(request, "Registration successful!")
            return redirect("app")  # or whatever your post-registration redirect is
        else:
            # Error message for invalid form
            messages.error(request, "Registration failed. Please check your details.")
    else:
        # Empty form for GET request
        form = CustomUserCreationForm()

    return render(request, "register.html", {"form": form})

# User login
def login_view(request):
    form = CustomLoginForm(data=request.POST or None)
    
    if request.method == "POST":
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect('app')  # Redirect to a  home page
        else:
            messages.error(request, "Invalid credentials, try again.")

    return render(request, 'login.html', {'form': form})

# User Logout
@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "Logged out successfully.")
    return redirect("login")



##create Project


##to query on search bar

def search(request):
    query = request.GET.get('q')
    results = []

    if query:
        results.extend(Post.objects.filter(Q(title__icontains=query) | Q(content__icontains=query)))
        results.extend(Post.objects.filter(Q(content__icontains=query))) 

    return render(request, 'search_results.html', {'query': query, 'results': results})

##feedback form

###
import logging

from django.core.mail import send_mail

logger = logging.getLogger(__name__)
def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']

            logger.info(f"Received contact form: Name={name}, Email={email}, Message={message}")

            try:
                send_mail(
                    subject=f"Contact Form Message from {name}",
                    message=message,
                    from_email=email,
                    recipient_list=["odumacorp@gmail.com"],
                )
                messages.success(request, "Your message has been sent successfully!")
            except Exception as e:
                logger.error(f"Email sending failed: {e}")
                messages.error(request, "There was an error sending your message.")
            
            form = ContactForm()  # Clear the form after submission
        else:
            messages.error(request, "There was an error with your submission.")
    else:
        form = ContactForm()

    return render(request, "contact.html", {"form": form})

###all users

###investors page view
def investors_view(request):
    investors = CustomUser.objects.filter(user_type='investor')
    return render(request, 'investors.html', {'investors': investors})




def view_innovator(request, user_id):
    innovator = get_object_or_404(CustomUser, pk=user_id)
    projects = Project.objects.filter(user=innovator)
    my_connections = request.user.profile.connections.values_list('id', flat=True) 

    context = {
        'innovator': innovator,
        'projects': projects,
        'my_connections': my_connections,
    }
    return render(request, 'view_innovator.html', context)



###


###########################################

#########################

# views.py


###

from django.db.models import Q


##################


###################

##############################
# 

class UserProfileView(DetailView):
    model = CustomUser
    template_name = 'user_detail.html'

    def get_object(self):
    # Debugging print statement
        print("User pk:", self.kwargs.get('pk'))
        return super().get_object()
###

@login_required
def unfollow_user(request, user_id):
    if request.method == 'POST':
        user_profile = get_object_or_404(UserProfile, user=request.user)
        friend_to_remove = get_object_or_404(CustomUser, id=user_id)

        user_profile.friends.remove(friend_to_remove)
        user_profile.save()

        messages.success(request, f"You have unfollowed {friend_to_remove.get_full_name()}.")
        return redirect(request.META.get('HTTP_REFERER', 'app'))

    return redirect('app')



@login_required
def user_network(request):
    current_user = request.user
    current_profile = current_user.userprofile

    # Get the list of users this user is connected to
    connections = current_profile.connected_users.all()

    context = {
        'connections': connections,
    }

    return render(request, 'network.html', context)

def my_network(request):
    user_profile = request.user.userprofile
    connections = user_profile.connected_users.all()
    return render(request, 'network.html', {'connections': connections})