from .models import CustomUser, Company, Project, UserProfile, INDUSTRY_CHOICES
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
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
    from .models import Project, ProjectImage
    from django.db.models import Avg, Count

    query    = request.GET.get("q", "")
    industry = request.GET.get("industry", "")
    status   = request.GET.get("status", "")
    stage    = request.GET.get("stage", "")
    sort     = request.GET.get("sort", "-created_at")

    ALLOWED_SORTS = {
        "-created_at": "-created_at",
        "created_at": "created_at",
        "-rating": "-avg_rating",
        "-likes": "-likes_count",
    }

    projects = (
        Project.objects
        .filter(is_hidden=False)
        .select_related("owner")
        .prefetch_related("images")
        .annotate(
            avg_rating=Avg("ratings__value"),
            likes_count=Count("liked_by", distinct=True),
        )
        .order_by(ALLOWED_SORTS.get(sort, "-created_at"))
    )

    if query:
        projects = projects.filter(
            Q(title__icontains=query) | Q(description__icontains=query) | Q(keywords__icontains=query)
        )
    if industry:
        projects = projects.filter(industry=industry)
    if status:
        projects = projects.filter(status=status)
    if stage:
        projects = projects.filter(pipeline_stage=stage)

    paginator   = Paginator(projects, 12)
    page_number = request.GET.get("page")
    page_obj    = paginator.get_page(page_number)

    # Attach main image to each project to avoid extra queries in template
    for proj in page_obj:
        imgs = list(proj.images.all())
        proj.main_img = next((i for i in imgs if i.is_main), imgs[0] if imgs else None)

    industry_counts = {
        r['industry']: r['cnt']
        for r in Project.objects.filter(is_hidden=False)
            .values('industry')
            .annotate(cnt=Count('id'))
        if r['industry']
    }

    context = {
        "page_obj": page_obj,
        "paginator": paginator,
        "is_paginated": page_obj.has_other_pages(),
        "total_count": projects.count(),
        "current_query": query,
        "current_industry": industry,
        "current_status": status,
        "current_stage": stage,
        "current_sort": sort,
        "industry_choices": INDUSTRY_CHOICES,
        "industry_counts": industry_counts,
    }
    return render(request, "project_list.html", context)




from django.shortcuts import render
from django.views.generic import DetailView

##proposals

##user posts

# ##Edit profile pic
@login_required
def edit_profile(request):
    user = request.user
    up, _ = UserProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=up)
        if form.is_valid():
            form.save()
            # Location field (all user types)
            up.location = request.POST.get('location', '').strip()
            up.save(update_fields=['location'])
            # Investor-specific fields not in ProfileEditForm
            if user.user_type == 'investor':
                up.ticket_size_min   = request.POST.get('ticket_size_min') or None
                up.ticket_size_max   = request.POST.get('ticket_size_max') or None
                up.preferred_sectors = request.POST.get('preferred_sectors', '')
                up.geography_focus   = request.POST.get('geography_focus', '')
                up.investment_thesis = request.POST.get('investment_thesis', '')
                up.save(update_fields=[
                    'ticket_size_min', 'ticket_size_max',
                    'preferred_sectors', 'geography_focus', 'investment_thesis',
                ])
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile_view', id=user.id)
    else:
        form = ProfileEditForm(instance=up)

    # Profile completion
    _pc = [bool(up.bio), bool(up.industry), bool(up.company), bool(up.phone_number),
           bool(up.profile_pics), bool(user.first_name), bool(user.last_name),
           bool(up.investment_thesis or up.preferred_sectors)]
    profile_completion = int(sum(_pc) / len(_pc) * 100)

    return render(request, 'edit_profile.html', {
        'form': form,
        'up': up,
        'profile_completion': profile_completion,
        'industry_choices': INDUSTRY_CHOICES,
    })




##counts
from .models import Patent
from .models import Connection 
from .models import Like
from .models import Interest



def investors_view(request):
    from django.db.models import Count
    industry_filter = request.GET.get('industry')
    base_qs = CustomUser.objects.filter(user_type='investor', is_active=True)
    if industry_filter:
        investors = base_qs.filter(userprofile__industry=industry_filter)
    else:
        investors = base_qs

    industries = UserProfile.INDUSTRY_CHOICES

    # Count per industry for category cards
    counts_qs = base_qs.values('userprofile__industry').annotate(cnt=Count('id'))
    industry_counts = {r['userprofile__industry']: r['cnt'] for r in counts_qs}

    return render(request, 'investors.html', {
        'investors': investors,
        'industries': industries,
        'selected_industry': industry_filter,
        'industry_counts': industry_counts,
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
    from .models import ProfileView as PV, Project, Patent, Like, Interest, Post, Group, Page, Company, Proposal
    user_obj = get_object_or_404(CustomUser, id=id)
    profile  = get_object_or_404(UserProfile, user=user_obj)

    # Block regular users from viewing admin profiles
    if user_obj.user_type == 'admin' or user_obj.is_staff or user_obj.is_superuser:
        if not (request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser or request.user.user_type == 'admin')):
            from django.http import HttpResponseForbidden
            return HttpResponseForbidden("You do not have permission to view this profile.")

    # Track this profile view
    if request.user.is_authenticated and request.user != user_obj:
        pv, created = PV.objects.get_or_create(
            profile_user=user_obj,
            viewer=request.user,
            defaults={'session_key': request.session.session_key or ''}
        )
        if not created:
            pv.session_key = request.session.session_key or ''
            pv.save()
        if created:
            from .models import Notification
            Notification.objects.create(
                user=user_obj,
                message=f"{request.user.get_full_name() or request.user.username} viewed your profile.",
                notification_type='other',
            )

    inventor_connections = Connection.objects.filter(target=user_obj, initiator__user_type='investor').count()
    investor_connections = Connection.objects.filter(initiator=user_obj, target__user_type='innovator').count()

    projects       = Project.objects.filter(owner=user_obj).order_by('-created_at')
    patents        = Patent.objects.filter(owner=user_obj).order_by('-filed_date')
    posts          = Post.objects.filter(user=user_obj, is_hidden=False).order_by('-created_at')
    groups         = Group.objects.filter(members=user_obj).order_by('-created_at')
    owned_pages    = Page.objects.filter(owner=user_obj, is_hidden=False).order_by('-created_at')
    followed_pages = Page.objects.filter(followers=user_obj, is_hidden=False).exclude(owner=user_obj).order_by('-created_at')
    companies      = Company.objects.filter(owner=user_obj).order_by('-created_at')
    proposals_sent = Proposal.objects.filter(from_investor=user_obj).select_related('post').order_by('-created_at')[:6]
    proposals_recv = Proposal.objects.filter(post__user=user_obj).select_related('from_investor', 'post').order_by('-created_at')[:6]

    likes_count     = Like.objects.filter(user=user_obj).count()
    interests_count = Interest.objects.filter(user=user_obj).count()
    profile_view_count = PV.objects.filter(profile_user=user_obj).count()

    connection_status = None
    if request.user.is_authenticated and request.user != user_obj:
        conn = Connection.objects.filter(
            Q(initiator=request.user, target=user_obj) | Q(initiator=user_obj, target=request.user)
        ).first()
        connection_status = conn.status if conn else None

    context = {
        'profile_user': user_obj,
        'profile': profile,
        'inventor_connections': inventor_connections,
        'investor_connections': investor_connections,
        'projects': projects,
        'projects_count': projects.count(),
        'patents': patents,
        'patents_count': patents.count(),
        'posts': posts,
        'groups': groups,
        'owned_pages': owned_pages,
        'followed_pages': followed_pages,
        'companies': companies,
        'proposals_sent': proposals_sent,
        'proposals_recv': proposals_recv,
        'likes_count': likes_count,
        'interests_count': interests_count,
        'profile_view_count': profile_view_count,
        'connection_status': connection_status,
    }
    return render(request, 'profile.html', context)


################

def home_view(request):
    user = request.user

    # Fetch Companies
    companies = Company.objects.all()[:6]

    # Fetch Nodes in Community
    community_nodes = CustomUser.objects.filter(connections_received__user=user).exclude(id=user.id)[:6]

    # Fetch Profile-Based Companies
    profile_based_companies = Company.objects.filter(industry=user.userprofile.industry)[:6]

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
    from .models import Project, CustomUser, UserProfile, SubscriptionPlan
    featured = Project.objects.filter(
        is_hidden=False, review_status__in=['approved', 'featured']
    ).select_related('owner', 'owner__userprofile').prefetch_related('images').order_by('-created_at')[:6]
    innovator_count = CustomUser.objects.filter(user_type='innovator').count()
    investor_count  = CustomUser.objects.filter(user_type='investor').count()
    project_count   = Project.objects.filter(is_hidden=False).exclude(status='draft').count()
    sub_plans       = list(SubscriptionPlan.objects.filter(is_active=True).order_by('order'))
    return render(request, 'index.html', {
        "hide_navbar": True,
        "featured_projects": featured,
        "innovator_count": innovator_count,
        "investor_count": investor_count,
        "project_count": project_count,
        "sub_plans": sub_plans,
    })
##about.html
def about(request):
    context = {"page_title": "About" , "page_name": "About"}
    return render(request, 'about.html', context)
##services.html
def services(request):
    context = {"page_title": "Services", "page_name": "Services"}
    return render(request, 'services.html', context)

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

    from .models import (
        Post, Connection, ProfileView, GroupMembership, Group, Page,
        Notification, ProjectView, Company, Event, Job, JobApplication,
        Meeting, Proposal
    )
    from django.db.models import Sum, Count

    user = request.user
    projects = Project.objects.filter(owner=user).order_by('-created_at')
    for project in projects:
        project.main_image = project.get_main_image_url()

    # Stats
    posts_count = Post.objects.filter(user=user).count()
    accepted = Connection.objects.filter(
        Q(initiator=user, status='accepted') | Q(target=user, status='accepted')
    )
    connections_count = accepted.count()
    profile_views_count = ProfileView.objects.filter(profile_user=user).count()
    project_views_count = ProjectView.objects.filter(project__owner=user).count()
    groups_count = GroupMembership.objects.filter(user=user, status='accepted').count()
    pages_owned = Page.objects.filter(owner=user).count()
    companies_owned = Company.objects.filter(owner=user).count()
    notifications_unread = Notification.objects.filter(user=user, is_read=False).count()

    # Recent posts (latest 5 for sidebar)
    recent_posts = Post.objects.filter(user=user).order_by('-created_at')[:5]

    # All posts for Posts tab
    my_posts = Post.objects.filter(user=user).order_by('-created_at')

    # Communities
    my_groups_created = Group.objects.filter(creator=user).order_by('-created_at')
    my_groups_joined = GroupMembership.objects.filter(
        user=user, status='accepted'
    ).exclude(group__creator=user).select_related('group').order_by('-created_at')
    my_pages = Page.objects.filter(owner=user).order_by('-created_at')
    my_companies = Company.objects.filter(owner=user).order_by('-created_at')

    # Work & Activity
    my_events = Event.objects.filter(created_by=user).order_by('-date')
    my_jobs = Job.objects.filter(created_by=user).order_by('-created_at')
    my_meetings = Meeting.objects.filter(
        Q(creator=user) | Q(participants=user)
    ).distinct().order_by('-scheduled_at', '-created_at')
    my_applications = JobApplication.objects.filter(applicant=user).select_related('job').order_by('-applied_at')

    # Deals / Proposals
    my_proposals_sent = Proposal.objects.filter(from_investor=user).select_related('post').order_by('-created_at')
    my_proposals_received = Proposal.objects.filter(post__user=user).select_related('from_investor').order_by('-created_at')

    # Profile completion (based on UserProfile fields that exist)
    up = getattr(user, 'userprofile', None)
    _pc_checks = [
        bool(up and up.bio),
        bool(up and up.industry),
        bool(up and up.company),
        bool(up and up.phone_number),
        bool(up and up.profile_pics),
        bool(user.first_name),
        bool(user.last_name),
        bool(up and (up.investment_thesis or up.preferred_sectors)),
    ]
    pc_filled = sum(_pc_checks)
    profile_completion = int((pc_filled / len(_pc_checks)) * 100)

    # Investor interest alerts: projects that have new interested investors
    investor_interest_alerts = []
    for p in projects:
        cnt = p.interested.count()
        if cnt:
            investor_interest_alerts.append({'project': p, 'count': cnt})
    investor_interest_alerts.sort(key=lambda x: x['count'], reverse=True)

    # Suggested next actions (use absolute paths as href)
    from django.urls import reverse
    from django.utils.safestring import mark_safe

    _IC = {
        'user':    mark_safe('<svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24"><circle cx="12" cy="8" r="4"/><path d="M20 21a8 8 0 1 0-16 0"/></svg>'),
        'rocket':  mark_safe('<svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24"><path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09z"/><path d="m12 15-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z"/><path d="M9 12H4s.55-3.03 2-4c1.62-1.08 5 0 5 0"/><path d="M12 15v5s3.03-.55 4-2c1.08-1.62 0-5 0-5"/></svg>'),
        'chart':   mark_safe('<svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/><path d="M21 20H3"/></svg>'),
        'network': mark_safe('<svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>'),
        'target':  mark_safe('<svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>'),
        'bell':    mark_safe('<svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>'),
    }

    suggested_actions = []
    if profile_completion < 80:
        suggested_actions.append({'icon': _IC['user'], 'text': 'Complete your profile to attract investors', 'href': reverse('update_profile'), 'priority': 'high'})
    if not projects.exists():
        suggested_actions.append({'icon': _IC['rocket'], 'text': 'Post your first project and start raising capital', 'href': reverse('create_project'), 'priority': 'high'})
    else:
        incomplete = [p for p in projects if p.completeness_score() < 80]
        if incomplete:
            suggested_actions.append({'icon': _IC['chart'], 'text': f'Complete pitch deck — "{incomplete[0].title[:28]}"', 'href': reverse('edit_project', args=[incomplete[0].pk]), 'priority': 'medium'})
    if connections_count == 0:
        suggested_actions.append({'icon': _IC['network'], 'text': 'Build your network — connect with investors', 'href': reverse('networks'), 'priority': 'medium'})
    if not investor_interest_alerts:
        if projects.exists():
            suggested_actions.append({'icon': _IC['target'], 'text': 'Submit a project for review to attract investors', 'href': reverse('project_list'), 'priority': 'low'})
    else:
        total_interested = sum(a['count'] for a in investor_interest_alerts)
        suggested_actions.append({'icon': _IC['bell'], 'text': f'{total_interested} investor(s) expressed interest in your projects', 'href': reverse('notifications'), 'priority': 'high'})

    return render(request, 'dashboard.html', {
        'project_form': project_form,
        'attachment_form': attachment_form,
        'projects': projects,
        'industry_choices': Project._meta.get_field('industry').choices,
        'posts_count': posts_count,
        'connections_count': connections_count,
        'profile_views_count': profile_views_count,
        'project_views_count': project_views_count,
        'groups_count': groups_count,
        'pages_owned': pages_owned,
        'companies_owned': companies_owned,
        'notifications_unread': notifications_unread,
        'recent_posts': recent_posts,
        'profile_completion': profile_completion,
        'investor_interest_alerts': investor_interest_alerts,
        'suggested_actions': suggested_actions[:4],
        # Extended dashboard data
        'my_posts': my_posts,
        'my_groups_created': my_groups_created,
        'my_groups_joined': my_groups_joined,
        'my_pages': my_pages,
        'my_companies': my_companies,
        'my_events': my_events,
        'my_jobs': my_jobs,
        'my_meetings': my_meetings,
        'my_applications': my_applications,
        'my_proposals_sent': my_proposals_sent,
        'my_proposals_received': my_proposals_received,
    })






@login_required
def download_attachment(request, attachment_id):
    """Track download and redirect to the file."""
    from .models import Attachment, AttachmentDownload, Notification
    att = get_object_or_404(Attachment, pk=attachment_id)
    # Record download
    AttachmentDownload.objects.create(
        attachment=att,
        downloaded_by=request.user if request.user.is_authenticated else None,
        ip_address=request.META.get('REMOTE_ADDR'),
    )
    # Notify project owner
    if request.user.is_authenticated and request.user != att.project.owner:
        Notification.objects.create(
            user=att.project.owner,
            message=f"{request.user.get_full_name() or request.user.username} downloaded \"{att.title or att.file.name}\" from your project \"{att.project.title}\".",
            notification_type='other',
            link=f'/projects/{att.project.pk}/',
        )
    from django.http import HttpResponseRedirect
    return HttpResponseRedirect(att.file.url)


@login_required
def download_message_attachment(request, attachment_id):
    """Serve a chat attachment as a download and notify the sender."""
    from .models import MessageAttachment, Notification
    from django.http import FileResponse, HttpResponseRedirect
    att = get_object_or_404(MessageAttachment, pk=attachment_id)
    msg = att.message
    conversation = msg.conversation

    # Only allow participants of this conversation to download
    if not conversation.participants.filter(pk=request.user.pk).exists():
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden()

    # Notify the sender (if the downloader is someone else)
    if request.user != msg.sender:
        downloader_name = request.user.get_full_name() or request.user.username
        file_label = att.filename or att.file.name.split('/')[-1]
        Notification.objects.create(
            user=msg.sender,
            message=f"{downloader_name} downloaded your attachment \"{file_label}\".",
            notification_type='other',
            link=f'/chat/{conversation.pk}/',
        )

    # Files are stored on Cloudinary — redirect to their URL with fl_attachment
    # so the browser triggers a Save-As dialog instead of opening inline.
    import os
    from django.http import HttpResponseRedirect
    filename = att.filename or os.path.basename(att.file.name)
    cloudinary_url = att.file.url
    # Insert fl_attachment transformation so Cloudinary serves it as a download
    if '/upload/' in cloudinary_url:
        cloudinary_url = cloudinary_url.replace(
            '/upload/',
            f'/upload/fl_attachment:{filename.replace(" ", "_")}/',
            1,
        )
    return HttpResponseRedirect(cloudinary_url)


@login_required
@login_required
def view_message_attachment(request, attachment_id):
    """Render a chat attachment in a styled viewer page."""
    from .models import MessageAttachment
    att = get_object_or_404(MessageAttachment, pk=attachment_id)
    conversation = att.message.conversation
    if not conversation.participants.filter(pk=request.user.pk).exists():
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden()
    return render(request, 'attachment_viewer.html', {
        'att': att,
        'conversation': conversation,
        'hide_navbar': True,
    })


@login_required
def media_chat_attachment_viewer(request, file_path):
    """Intercept direct /media/chat_attachments/... browser navigations → styled viewer.
    Non-HTML requests (img src, video src) are redirected straight to the Cloudinary URL."""
    from .models import MessageAttachment
    from django.http import HttpResponseRedirect

    accept = request.META.get('HTTP_ACCEPT', '')
    lookup = 'chat_attachments/' + file_path.lstrip('/')
    att = MessageAttachment.objects.filter(file=lookup).first()

    if att and att.message.conversation.participants.filter(pk=request.user.pk).exists():
        if 'text/html' in accept:
            # Full browser navigation → styled viewer page
            return HttpResponseRedirect(f'/chat/attachments/{att.pk}/view/')
        else:
            # Asset load (img/video src) → raw Cloudinary URL
            return HttpResponseRedirect(att.file.url)

    # No matching attachment — redirect to Cloudinary URL directly if possible
    if att:
        return HttpResponseRedirect(att.file.url)
    from django.http import Http404
    raise Http404


@login_required
def add_project_comment(request, project_id):
    """Add a comment or reply to a project."""
    from .models import ProjectComment, Notification
    project = get_object_or_404(Project, pk=project_id)
    if request.method == 'POST':
        content   = request.POST.get('content', '').strip()
        parent_id = request.POST.get('parent_id')
        if content:
            parent = None
            if parent_id:
                try:
                    parent = ProjectComment.objects.get(pk=parent_id, project=project)
                except ProjectComment.DoesNotExist:
                    pass
            ProjectComment.objects.create(
                project=project, user=request.user, content=content, parent=parent
            )
            if request.user != project.owner:
                Notification.objects.create(
                    user=project.owner,
                    message=f"{request.user.get_full_name() or request.user.username} commented on your project \"{project.title}\".",
                    notification_type='other',
                    link=f'/projects/{project.pk}/',
                )
    return redirect(request.META.get('HTTP_REFERER', 'project_detail'), pk=project_id)


# View to handle attachment creation
@login_required
def add_attachment(request, project_id):
    project = get_object_or_404(Project, id=project_id, owner=request.user)
    if request.method == 'POST':
        files = request.FILES.getlist('attachments') or (
            [request.FILES['file']] if 'file' in request.FILES else []
        )
        for f in files:
            Attachment.objects.create(
                project     = project,
                file        = f,
                title       = request.POST.get('title', ''),
                description = request.POST.get('description', ''),
                doc_type    = request.POST.get('doc_type', 'general'),
                visibility  = request.POST.get('visibility', 'connections'),
            )
        messages.success(request, f'{len(files)} file(s) uploaded.')
        return redirect(request.META.get('HTTP_REFERER', 'dashboard'))
    return render(request, 'add_attachment.html', {'project': project})


def user_project_attachments(request, user_id, project_id):
    project = get_object_or_404(Project, id=project_id, owner_id=user_id)
    attachments = Attachment.objects.filter(project=project)
    return render(request, 'user_attachments.html', {'attachments': attachments, 'project': project})

##image uploads
from django.shortcuts import render, redirect
from .models import Project, ProjectImage
from .forms import ProjectImageForm

@login_required
def upload_image(request, project_id):
    project = get_object_or_404(Project, id=project_id, owner=request.user)
    if request.method == 'POST':
        if 'image' in request.FILES:
            img = ProjectImage(
                project     = project,
                image       = request.FILES['image'],
                name        = request.POST.get('name', ''),
                description = request.POST.get('description', ''),
                is_main     = request.POST.get('is_main') == 'on',
            )
            img.save()
            messages.success(request, 'Image uploaded.')
            return redirect('project_images', project_id=project.id)
        form = ProjectImageForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.save(commit=False)
            image.project = project
            image.save()
            return redirect('project_images', project_id=project.id)
    else:
        form = ProjectImageForm()
    return render(request, 'upload_image.html', {'form': form, 'project': project})


@login_required
def project_images(request, project_id):
    project = get_object_or_404(Project, id=project_id, owner=request.user)

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
    from .models import Job, Company
    jobs_qs = Job.objects.filter(is_active=True, is_hidden=False).order_by('-created_at')
    user_has_company = (
        request.user.is_authenticated and
        Company.objects.filter(owner=request.user).exists()
    )
    context = {"page_title": "Jobs", "page_name": "Jobs", "jobs": jobs_qs, "user_has_company": user_has_company}
    return render(request, 'jobs.html', context)
##messages.html
def user_messages(request):
    context = {"page_title": "Messages", "page_name": "Messages"}
    return render(request, 'messages.html', context)
##networks.html
@login_required
def networks(request):
    from .models import Company, Group, Page, GroupMembership, CustomUser, Event, EventRegistration
    from datetime import date as _date

    user = request.user

    # ── Accepted connections ──────────────────────────────────────────────
    accepted = Connection.objects.filter(
        Q(initiator=user, status='accepted') | Q(target=user, status='accepted')
    ).select_related('initiator', 'target', 'initiator__userprofile', 'target__userprofile')
    connections = [
        c.target if c.initiator == user else c.initiator
        for c in accepted
    ]
    connected_ids = {u.id for u in connections}

    # ── Pending: incoming requests ─────────────────────────────────────
    pending_incoming = Connection.objects.filter(
        target=user, status='pending'
    ).select_related('initiator', 'initiator__userprofile').order_by('-created_at')

    # ── Pending: sent by user ─────────────────────────────────────────
    pending_sent_ids = set(
        Connection.objects.filter(initiator=user, status='pending').values_list('target_id', flat=True)
    )

    # ── Suggested people ──────────────────────────────────────────────
    exclude_people = connected_ids | pending_sent_ids | {user.id}
    suggested_innovators = CustomUser.objects.filter(
        is_active=True, user_type='innovator'
    ).exclude(id__in=exclude_people).select_related('userprofile').order_by('?')[:8]

    suggested_investors = CustomUser.objects.filter(
        is_active=True, user_type='investor'
    ).exclude(id__in=exclude_people).select_related('userprofile').order_by('?')[:8]

    # ── Your groups (joined) ──────────────────────────────────────────
    your_memberships = GroupMembership.objects.filter(
        user=user, status='accepted'
    ).select_related('group').order_by('-created_at')[:8]
    your_groups = [m.group for m in your_memberships]
    joined_group_ids = list(GroupMembership.objects.filter(user=user).values_list('group_id', flat=True))
    suggested_groups = Group.objects.filter(
        is_hidden=False
    ).exclude(id__in=joined_group_ids).order_by('?')[:8]

    # ── Your companies (followed + owned) ─────────────────────────────
    followed_companies = Company.objects.filter(followers=user).order_by('-created_at')[:8]
    owned_companies    = Company.objects.filter(owner=user).order_by('-created_at')[:4]
    followed_company_ids = list(followed_companies.values_list('id', flat=True))
    owned_company_ids    = list(owned_companies.values_list('id', flat=True))
    exclude_company_ids  = followed_company_ids + owned_company_ids
    suggested_companies  = Company.objects.exclude(id__in=exclude_company_ids).order_by('?')[:8]

    # ── Your pages (followed + owned) ────────────────────────────────
    followed_pages = Page.objects.filter(followers=user, is_hidden=False).order_by('-created_at')[:8]
    owned_pages    = Page.objects.filter(owner=user, is_hidden=False).order_by('-created_at')[:4]
    followed_page_ids = list(followed_pages.values_list('id', flat=True))
    owned_page_ids    = list(owned_pages.values_list('id', flat=True))
    exclude_page_ids  = followed_page_ids + owned_page_ids
    suggested_pages   = Page.objects.filter(is_hidden=False).exclude(id__in=exclude_page_ids).order_by('?')[:8]

    # ── Upcoming events ────────────────────────────────────────────────
    upcoming_events = Event.objects.filter(
        is_hidden=False, date__gte=_date.today()
    ).order_by('date')[:4]
    registered_event_ids = set(
        EventRegistration.objects.filter(user=user).values_list('event_id', flat=True)
    )

    context = {
        "page_title": "My Network", "page_name": "Networks",
        # Connections
        "connections":          connections,
        "connections_count":    len(connections),
        "connected_ids":        connected_ids,
        # Pending
        "pending_incoming":     pending_incoming,
        "pending_incoming_count": pending_incoming.count(),
        "pending_sent_ids":     pending_sent_ids,
        # Suggested people
        "suggested_innovators": suggested_innovators,
        "suggested_investors":  suggested_investors,
        # Groups
        "your_groups":          your_groups,
        "suggested_groups":     suggested_groups,
        # Companies
        "followed_companies":   followed_companies,
        "owned_companies":      owned_companies,
        "suggested_companies":  suggested_companies,
        # Pages
        "followed_pages":       followed_pages,
        "owned_pages":          owned_pages,
        "suggested_pages":      suggested_pages,
        # Events
        "upcoming_events":      upcoming_events,
        "registered_event_ids": registered_event_ids,
    }
    return render(request, 'networks.html', context)
##notifications.html
@login_required
def notifications(request):
    from .models import Notification, Conversation
    notifs = Notification.objects.filter(user=request.user).order_by('-created_at')
    unread_count = notifs.filter(is_read=False).count()
    notifs.filter(is_read=False).update(is_read=True)

    # Build inbox items — same logic as the inbox view
    conversations = Conversation.objects.filter(
        participants=request.user
    ).select_related('project', 'post').prefetch_related('participants', 'messages').order_by('-created_at')

    inbox_items = []
    msg_unread_total = 0
    for convo in conversations:
        other = convo.participants.exclude(id=request.user.id).first()
        last_msg = convo.messages.order_by('-timestamp').first()
        unread = convo.messages.filter(recipient=request.user, is_read=False).count()
        msg_unread_total += unread
        inbox_items.append({
            'conversation': convo,
            'other_user':   other,
            'last_msg':     last_msg,
            'unread':       unread,
        })
    inbox_items.sort(
        key=lambda x: x['last_msg'].timestamp if x['last_msg'] else x['conversation'].created_at,
        reverse=True
    )

    context = {
        "page_title": "Notifications", "page_name": "Notifications",
        'all_notifications':       notifs,
        'connected_notifications': notifs.filter(notification_type='connected'),
        'message_notifications':   notifs.filter(notification_type='message_sent'),
        'other_notifications':     notifs.filter(notification_type='other'),
        'unread_count':            unread_count,
        'inbox_items':             inbox_items,
        'msg_unread_total':        msg_unread_total,
    }
    return render(request, 'notifications.html', context)


from .models import Notification
@login_required
def notifications_view(request):
    # Fetch the logged-in user's notifications
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')

    # Mark all unread notifications as read
    notifications.filter(is_read=False).update(is_read=True)

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
    from django.db.models import Count
    industry_filter = request.GET.get('industry')
    base_qs = CustomUser.objects.filter(user_type='innovator', is_active=True).select_related('userprofile')
    innovators = base_qs.filter(userprofile__industry=industry_filter) if industry_filter else base_qs

    for innovator in innovators:
        innovator.first_project = innovator.projects.order_by('-created_at').first()

    # Count per industry for category cards
    counts_qs = base_qs.values('userprofile__industry').annotate(cnt=Count('id'))
    industry_counts = {r['userprofile__industry']: r['cnt'] for r in counts_qs}

    return render(request, 'innovators.html', {
        'innovators': innovators,
        'industry_counts': industry_counts,
        'selected_industry': industry_filter,
    })



@login_required
@login_required
@login_required
def user_search_api(request):
    """AJAX endpoint: search users by name/username for new-chat compose."""
    from .models import CustomUser, UserProfile
    q = request.GET.get('q', '').strip()
    results = []
    if q:
        qs = CustomUser.objects.filter(is_active=True).exclude(pk=request.user.pk).filter(
            Q(first_name__icontains=q) | Q(last_name__icontains=q) | Q(username__icontains=q) |
            Q(email__icontains=q)
        ).select_related('userprofile')[:20]
    else:
        # Show recent conversation partners first
        recent_ids = (
            Conversation.objects.filter(participants=request.user)
            .values_list('participants', flat=True)
            .distinct()
        )
        qs = CustomUser.objects.filter(pk__in=recent_ids, is_active=True).exclude(
            pk=request.user.pk
        ).select_related('userprofile')[:12]

    for u in qs:
        prof = getattr(u, 'userprofile', None)
        avatar = prof.profile_pics.url if prof and prof.profile_pics else None
        results.append({
            'id':       u.pk,
            'name':     u.get_full_name() or u.username,
            'username': u.username,
            'role':     u.user_type or 'member',
            'avatar':   avatar,
            'company':  getattr(prof, 'company', '') or '',
        })
    return JsonResponse({'users': results})


def inbox(request):
    from .models import Conversation
    # Get all conversations this user is part of, newest message first
    conversations = Conversation.objects.filter(
        participants=request.user
    ).select_related('project', 'post').prefetch_related('participants', 'messages').order_by('-created_at')

    inbox_items = []
    total_unread = 0
    for convo in conversations:
        other = convo.participants.exclude(id=request.user.id).first()
        last_msg = convo.messages.order_by('-timestamp').first()
        unread = convo.messages.filter(recipient=request.user, is_read=False).count()
        total_unread += unread
        inbox_items.append({
            'conversation': convo,
            'other_user':   other,
            'last_msg':     last_msg,
            'unread':       unread,
        })

    # Sort by last message timestamp descending
    inbox_items.sort(key=lambda x: x['last_msg'].timestamp if x['last_msg'] else x['conversation'].created_at, reverse=True)

    # Recent contacts for the compose modal
    recent_contact_ids = [item['other_user'].pk for item in inbox_items if item['other_user']][:8]

    # Pinned conversations
    from .models import Pin
    pinned_chat_ids = set(
        Pin.objects.filter(user=request.user, pin_type='chat')
        .values_list('conversation_id', flat=True)
    )

    return render(request, 'inbox.html', {
        'inbox_items':         inbox_items,
        'unread_count':        total_unread,
        'page_name':           'Inbox',
        'recent_contact_ids':  recent_contact_ids,
        'pinned_chat_ids':     pinned_chat_ids,
    })

@login_required
def sent_items(request):
    sent = Message.objects.filter(sender=request.user).order_by('-timestamp')
    return render(request, 'sent_items.html', {'messages': sent, 'page_name': 'Sent'})

@login_required
def share_to_chat(request):
    """
    POST: share a post or project as a rich card into a direct conversation.
    Params: content_type ('post'|'project'), content_id, recipient_id, caption (optional)
    Returns JSON: {ok, conversation_id}
    """
    from .models import Post, Project, Conversation, Message, CustomUser

    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    content_type = request.POST.get('content_type', '').strip()
    content_id   = request.POST.get('content_id', '').strip()
    recipient_id = request.POST.get('recipient_id', '').strip()
    caption      = request.POST.get('caption', '').strip()

    if not content_type or not content_id or not recipient_id:
        return JsonResponse({'error': 'Missing parameters'}, status=400)

    recipient = get_object_or_404(CustomUser, pk=recipient_id)

    # Find or create a direct conversation between the two users
    conv = (
        Conversation.objects
        .filter(participants=request.user, context_type='direct')
        .filter(participants=recipient)
        .first()
    )
    if not conv:
        conv = Conversation.objects.create(context_type='direct')
        conv.participants.add(request.user, recipient)

    if content_type == 'post':
        obj = get_object_or_404(Post, pk=content_id)
        msg_text = caption or f'Shared a post: {obj.content[:100]}'
        Message.objects.create(
            sender=request.user, recipient=recipient,
            conversation=conv, content=msg_text,
            message_type='post_share', shared_post=obj,
        )
    elif content_type == 'project':
        obj = get_object_or_404(Project, pk=content_id)
        msg_text = caption or f'Check out this project: {obj.title}'
        Message.objects.create(
            sender=request.user, recipient=recipient,
            conversation=conv, content=msg_text,
            message_type='project_share', shared_project=obj,
        )
    else:
        return JsonResponse({'error': 'Invalid content_type'}, status=400)

    return JsonResponse({'ok': True, 'conversation_id': conv.id})


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
        from .models import Connection, Notification
        target = get_object_or_404(CustomUser, id=user_id)
        if target == request.user:
            return redirect(request.META.get('HTTP_REFERER', 'app'))

        existing = Connection.objects.filter(
            Q(initiator=request.user, target=target) | Q(initiator=target, target=request.user)
        ).first()

        if not existing:
            Connection.objects.create(initiator=request.user, target=target, status='pending')
            Notification.objects.create(
                user=target,
                message=f"{request.user.get_full_name() or request.user.username} wants to connect with you.",
                notification_type='connected',
                action_type='connection_request',
            )
            messages.success(request, f"Connection request sent to {target.get_full_name()}.")
        else:
            messages.info(request, "A connection request already exists.")
        return redirect(request.META.get('HTTP_REFERER', 'app'))
    return redirect('app')




from django.core.mail import send_mail  # For email messaging, or use your preferred method.

@login_required
def message_innovator(request, user_id):
    """
    Legacy entry point: /message_innovator/<userprofile_id>/
    Finds or creates a Conversation and redirects to the proper chat page.
    """
    recipient_profile = get_object_or_404(UserProfile, id=user_id)
    other_user = recipient_profile.user

    conversation = (
        Conversation.objects.filter(participants=request.user)
        .filter(participants=other_user)
        .first()
    )
    if not conversation:
        conversation = Conversation.objects.create(context_type='direct')
        conversation.participants.add(request.user, other_user)

    return redirect('chat_page', conversation_id=conversation.id)


# #  
from django.http import JsonResponse
@login_required
def like_project(request, pk):
    from .models import Notification
    project = get_object_or_404(Project, pk=pk)

    if request.user in project.liked_by.all():
        project.liked_by.remove(request.user)
        liked = False
    else:
        project.liked_by.add(request.user)
        liked = True
        if request.user != project.owner:
            actor = request.user.get_full_name() or request.user.username
            Notification.objects.create(
                user=project.owner,
                notification_type='other',
                message=f"{actor} liked your project \"{project.title[:60]}\"",
                link=f"/projects/{project.pk}/",
            )

    project.save()
    return JsonResponse({'liked': liked, 'project_id': project.pk})


from django.views.decorators.csrf import csrf_exempt
import json
from .models import Project, Rating
@login_required
@csrf_exempt
def rate_project(request, pk):
    if request.method == 'POST':
        try:
            content_type = request.content_type or ''
            if 'application/json' in content_type:
                data = json.loads(request.body)
                rating_value = int(data.get('rating'))
            else:
                rating_value = int(request.POST.get('score', 0))

            project = Project.objects.get(pk=pk)

            _, created = Rating.objects.update_or_create(
                user=request.user,
                project=project,
                defaults={'value': rating_value}
            )

            avg = project.average_rating()

            # Notify project owner
            from .models import Notification
            Notification.objects.create(
                user=project.owner,
                message=f"{request.user.get_full_name() or request.user.username} rated your project \"{project.title}\" {rating_value}/5.",
                notification_type='other',
                link=f'/projects/{project.pk}/',
            )

            if request.headers.get('Accept') == 'application/json' or 'application/json' in content_type:
                return JsonResponse({'success': True, 'rating': avg})
            from django.contrib import messages as dj_messages
            dj_messages.success(request, "Rating submitted!")
            return redirect('project_detail', pk=pk)
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
    
    
    return redirect('investors')

####
from .forms import MessageForm
from .models import Conversation, Message

@login_required
def start_conversation(request, user_id):
    other_user = get_object_or_404(CustomUser, pk=user_id)

    # Try to find existing direct conversation
    conversation = (
        Conversation.objects.filter(participants=request.user)
        .filter(participants=other_user)
        .filter(context_type='direct')
        .first()
    )

    if not conversation:
        conversation = Conversation.objects.create(context_type='direct')
        conversation.participants.add(request.user, other_user)

    return redirect('chat_page', conversation_id=conversation.id)


@login_required
def start_project_conversation(request, project_id):
    """Start or resume a project-linked conversation with the project owner."""
    from .models import Project as _Proj
    project = get_object_or_404(_Proj, pk=project_id)
    owner = project.owner

    if owner == request.user:
        # Can't start a conversation with yourself — just redirect to project
        return redirect('project_detail', pk=project_id)

    # Find existing project conversation between these two users about this project
    conversation = (
        Conversation.objects.filter(participants=request.user)
        .filter(participants=owner)
        .filter(context_type='project', project=project)
        .first()
    )

    if not conversation:
        conversation = Conversation.objects.create(context_type='project', project=project)
        conversation.participants.add(request.user, owner)

    return redirect('chat_page', conversation_id=conversation.id)


@login_required
def quick_message(request):
    """AJAX: find/create a direct conversation and send a quick message from listing pages."""
    import json
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    try:
        data = json.loads(request.body)
    except Exception:
        data = request.POST

    recipient_id = data.get('recipient_id')
    content = str(data.get('content', '')).strip()

    if not recipient_id or not content:
        return JsonResponse({'error': 'Missing fields'}, status=400)

    recipient = get_object_or_404(CustomUser, pk=recipient_id)
    if recipient == request.user:
        return JsonResponse({'error': 'Cannot message yourself'}, status=400)

    conversation = (
        Conversation.objects.filter(participants=request.user)
        .filter(participants=recipient)
        .filter(context_type='direct')
        .first()
    )
    if not conversation:
        conversation = Conversation.objects.create(context_type='direct')
        conversation.participants.add(request.user, recipient)

    Message.objects.create(
        sender=request.user,
        recipient=recipient,
        conversation=conversation,
        content=content,
    )

    return JsonResponse({'ok': True, 'conversation_id': conversation.id})

@login_required
def chat_page(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id)

    # Security: only participants can view
    if request.user not in conversation.participants.all():
        return redirect('inbox')

    participant = conversation.participants.exclude(id=request.user.id).first()

    # Detect if current user is admin / if participant is admin
    def _is_admin_user(u):
        return u and (u.is_superuser or u.is_staff or getattr(u, 'user_type', '') == 'admin')

    i_am_admin = _is_admin_user(request.user)
    is_admin_chat = _is_admin_user(participant)

    def _detect_attachment_type(f):
        ext = f.name.rsplit('.', 1)[-1].lower() if '.' in f.name else ''

        image_ext = {'jpg','jpeg','png','gif','webp','bmp','svg'}
        video_ext = {'mp4','webm','mov','avi','mkv','m4v'}

        if ext in image_ext:
            return 'image'
        if ext in video_ext:
            return 'video'
        return 'document'

    # Handle POST send
    if request.method == 'POST' and participant:
        content = request.POST.get('content', '').strip()
        sticker  = request.POST.get('sticker', '').strip()
        reply_to_id = request.POST.get('reply_to_id', '').strip()
        files = request.FILES.getlist('attachments')

        reply_to_msg = None
        if reply_to_id:
            try:
                reply_to_msg = Message.objects.get(pk=reply_to_id, conversation=conversation)
            except Message.DoesNotExist:
                pass

        if sticker:
            # Sticker message
            Message.objects.create(
                sender=request.user, recipient=participant,
                conversation=conversation,
                content=sticker, message_type='sticker',
                reply_to=reply_to_msg,
            )
        elif files:
            # File attachment message (content = optional caption)
            from .models import MessageAttachment
            msg = Message.objects.create(
                sender=request.user, recipient=participant,
                conversation=conversation,
                content=content, message_type='file',
                reply_to=reply_to_msg,
            )
            for f in files[:10]:
                try:
                    MessageAttachment.objects.create(
                        message=msg,
                        file=f,
                        attachment_type=_detect_attachment_type(f),
                        filename=f.name,
                        file_size=f.size,
                    )
                except Exception as upload_err:
                    import logging
                    logging.getLogger(__name__).error(
                        "Chat attachment upload failed for %s: %s", f.name, upload_err
                    )
        elif content:
            # Plain text
            Message.objects.create(
                sender=request.user, recipient=participant,
                conversation=conversation,
                content=content, message_type='text',
                reply_to=reply_to_msg,
            )

        # Auto-reply: send once when a non-admin user first messages an admin
        if is_admin_chat and not i_am_admin and not conversation.auto_replied and (content or sticker or files):
            auto_text = _admin_auto_reply(content or (sticker and 'Hi, I need help.') or files[0].name)
            Message.objects.create(
                sender=participant, recipient=request.user,
                conversation=conversation,
                content=auto_text,
            )
            conversation.auto_replied = True
            conversation.save(update_fields=['auto_replied'])

        return redirect('chat_page', conversation_id=conversation.id)

    form = MessageForm()

    chat_messages = Message.objects.filter(
        conversation=conversation
    ).select_related(
        'sender', 'sender__userprofile',
        'reply_to', 'reply_to__sender',
        'shared_post', 'shared_project',
    ).prefetch_related('reactions', 'reactions__user', 'attachments').order_by('timestamp')

    # Mark incoming messages as read
    chat_messages.filter(recipient=request.user, is_read=False).update(is_read=True)

    participant_profile = getattr(participant, 'userprofile', None) if participant else None

    # Profile panel extras
    participant_projects = []
    if participant and participant.user_type == 'innovator':
        from .models import Project as _Proj
        participant_projects = list(
            _Proj.objects.filter(owner=participant, review_status__in=['approved', 'featured'])
            .order_by('-created_at')[:3]
        )

    is_connected = Connection.objects.filter(
        Q(initiator=request.user, target=participant, status='accepted') |
        Q(initiator=participant, target=request.user, status='accepted')
    ).exists() if participant else False

    connection_pending_sent = Connection.objects.filter(
        initiator=request.user, target=participant, status='pending'
    ).exists() if participant else False

    # Attach reaction summary directly to each message object
    from collections import defaultdict
    messages_list = list(chat_messages)
    RESOLVED_PREFIX = "✅ Your support request has been marked"
    for msg in messages_list:
        groups = defaultdict(list)
        for r in msg.reactions.all():
            groups[r.emoji].append(r.user_id)
        msg.reaction_summary = [
            {'emoji': e, 'count': len(uids), 'mine': request.user.id in uids}
            for e, uids in groups.items()
        ]
        msg.is_system = msg.content.startswith(RESOLVED_PREFIX)

    context = {
        'conversation':            conversation,
        'participant':             participant,
        'participant_name':        participant.get_full_name() if participant else 'Unknown',
        'participant_profile':     participant_profile,
        'chat_messages':           messages_list,
        'form':                    form,
        'room_name':               str(conversation_id),
        'participant_projects':    participant_projects,
        'is_connected':            is_connected,
        'connection_pending_sent': connection_pending_sent,
        'project_context':         conversation.project if conversation.context_type == 'project' else None,
        'is_project_chat':         conversation.context_type == 'project',
        'is_admin_chat':           is_admin_chat,
        'i_am_admin':              i_am_admin,
        'is_resolved':             conversation.is_resolved,
        'resolved_at':             conversation.resolved_at,
    }
    return render(request, 'chat_page.html', context)




def _admin_auto_reply(content):
    """Return a contextual auto-reply text based on the user's message keywords."""
    t = content.lower()
    if any(w in t for w in ['password', 'reset', 'forgot']):
        return (
            "Thanks for reaching out about your password. We've received your request "
            "and our team will process it shortly. For security, password resets are handled "
            "manually — we'll send you instructions via email within a few hours."
        )
    if any(w in t for w in ['locked', 'lock', "can't log", "cant log", 'cannot log', 'login', 'sign in', 'access', 'locked out']):
        return (
            "We've received your account access request. Our team will investigate and "
            "get your account restored as soon as possible. Please check your email for any "
            "security alerts in the meantime."
        )
    if any(w in t for w in ['verify', 'verification', 'verified', 'badge']):
        return (
            "Thank you for reaching out about account verification. We'll review your "
            "profile and documents shortly. Verification typically takes 1–3 business days."
        )
    if any(w in t for w in ['bug', 'technical', 'error', 'broken', 'not working', "doesn't work", 'crash', 'glitch']):
        return (
            "Thanks for reporting this technical issue. Our engineering team has been "
            "notified and will investigate. If you can share any screenshots or steps to "
            "reproduce the problem, that would be very helpful!"
        )
    if any(w in t for w in ['delete', 'close account', 'remove account', 'deactivate']):
        return (
            "We've received your account deletion/deactivation request. Please note this "
            "action is irreversible. A member of our team will contact you to confirm before "
            "proceeding — usually within 24 hours."
        )
    if any(w in t for w in ['upgrade', 'premium', 'plan', 'subscription', 'tier']):
        return (
            "Thanks for your interest in upgrading your account! Our team will reach out "
            "with available options and pricing details. We'll be in touch shortly."
        )
    if any(w in t for w in ['report', 'inappropriate', 'spam', 'abuse', 'harassment', 'scam']):
        return (
            "We take reports of inappropriate content very seriously. Your report has been "
            "logged and will be reviewed within 24 hours. Thank you for helping keep "
            "Oduma Corp safe."
        )
    if any(w in t for w in ['profile', 'company', 'update info', 'edit my', 'change my']):
        return (
            "We've received your request to update your profile or company information. "
            "Please describe exactly what you'd like changed and our team will assist you."
        )
    return (
        "Thanks for reaching out to Oduma Corp Support! We've received your message "
        "and a member of our team will respond as soon as possible. "
        "Support hours are Monday–Friday, 9am–6pm WAT."
    )


@login_required
def resolve_conversation(request, conversation_id):
    from django.utils import timezone
    if request.method != 'POST':
        return redirect('chat_page', conversation_id=conversation_id)
    conversation = get_object_or_404(Conversation, id=conversation_id)
    # Only admin can resolve
    if not (request.user.is_superuser or request.user.is_staff or getattr(request.user, 'user_type', '') == 'admin'):
        return redirect('chat_page', conversation_id=conversation_id)
    if request.user not in conversation.participants.all():
        return redirect('inbox')

    if not conversation.is_resolved:
        conversation.is_resolved = True
        conversation.resolved_at = timezone.now()
        conversation.save(update_fields=['is_resolved', 'resolved_at'])

        # Find the non-admin participant
        user = conversation.participants.exclude(
            id=request.user.id
        ).exclude(
            is_superuser=True
        ).exclude(
            is_staff=True
        ).first()

        if user:
            from .models import Notification
            # Post a system message in the conversation
            Message.objects.create(
                sender=request.user,
                recipient=user,
                conversation=conversation,
                content=(
                    "✅ Your support request has been marked as resolved by our team. "
                    "If your issue is still ongoing, please reply to this message and we will "
                    "reopen the case for you."
                ),
            )
            # In-app notification
            Notification.objects.create(
                user=user,
                notification_type='other',
                message="Your support request has been resolved by Oduma Corp Admin.",
                link=f"/chat/{conversation.id}/",
            )

    return redirect('chat_page', conversation_id=conversation_id)


@login_required
def toggle_message_reaction(request, message_id):
    import json
    from .models import MessageReaction
    from collections import defaultdict
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    try:
        data  = json.loads(request.body)
        emoji = data.get('emoji', '').strip()
    except Exception:
        emoji = request.POST.get('emoji', '').strip()
    if not emoji:
        return JsonResponse({'error': 'No emoji'}, status=400)
    msg = get_object_or_404(Message, pk=message_id)

    # One reaction per user per message
    existing = MessageReaction.objects.filter(message=msg, user=request.user).first()

    if existing and existing.emoji == emoji:
        # Same emoji clicked — toggle off
        existing.delete()
    elif existing:
        # Different emoji — update in place
        existing.emoji = emoji
        existing.save(update_fields=['emoji'])
    else:
        # No previous reaction — create
        MessageReaction.objects.create(message=msg, user=request.user, emoji=emoji)

    # Return updated counts
    groups = defaultdict(list)
    for r in msg.reactions.all():
        groups[r.emoji].append(r.user_id)
    summary = [
        {'emoji': e, 'count': len(uids), 'mine': request.user.id in uids}
        for e, uids in groups.items()
    ]
    return JsonResponse({'reactions': summary, 'message_id': message_id})


##app.html
@login_required
def app_view(request):
    from .models import (
        Post, Project, ProjectProposal, Connection, ProfileView,
        Invention, Patent, Group, Page, Event, GroupMembership, ReadLater,
        ProjectView, GroupDiscussion
    )
    from django.db.models import Avg, Count

    user = request.user

    # Handle new post submission
    if request.method == 'POST' and 'post_content' in request.POST:
        title    = request.POST.get('post_title', '').strip()
        content  = request.POST.get('post_content', '').strip()
        post_type = request.POST.get('post_type', 'idea')
        industry  = request.POST.get('post_industry', '')
        image     = request.FILES.get('post_image')
        if content:
            post = Post.objects.create(
                user=user,
                title=title,
                content=content,
                post_type=post_type,
                industry=industry,
            )
            if image:
                post.image = image
                post.save()
        return redirect('app')

    # Accepted connection IDs
    accepted = Connection.objects.filter(
        Q(initiator=user, status='accepted') | Q(target=user, status='accepted')
    )
    connected_user_ids = set()
    for c in accepted:
        connected_user_ids.add(c.target_id if c.initiator_id == user.pk else c.initiator_id)

    # Pending connections (sent by others to this user)
    pending_connections = Connection.objects.filter(target=user, status='pending').select_related('initiator')

    # Industry filter
    industry_filter = request.GET.get('industry', '')
    date_filter     = request.GET.get('date', '')

    # Feed posts — prioritize by user's industry/interests
    posts_qs = Post.objects.filter(is_hidden=False).select_related('user', 'user__userprofile').prefetch_related('comments').order_by('-created_at')
    if industry_filter:
        posts_qs = posts_qs.filter(industry=industry_filter)
    if date_filter:
        posts_qs = posts_qs.filter(created_at__date=date_filter)
    # Boost posts from same industry as user
    user_industry = getattr(user.userprofile, 'industry', '') if hasattr(user, 'userprofile') else ''
    if user_industry:
        same_industry  = posts_qs.filter(industry=user_industry)[:15]
        other_posts    = posts_qs.exclude(industry=user_industry)[:10]
        posts = list(same_industry) + [p for p in other_posts if p not in same_industry]
    else:
        posts = list(posts_qs[:25])

    # Projects feed — exclude drafts, group by innovator
    projects_qs = Project.objects.filter(is_hidden=False).exclude(status='draft').select_related('owner', 'owner__userprofile').prefetch_related('images').order_by('-created_at')
    if industry_filter:
        projects_qs = projects_qs.filter(industry=industry_filter)

    innovator_map = {}
    for proj in projects_qs[:40]:
        oid = proj.owner_id
        if oid not in innovator_map:
            innovator_map[oid] = {'innovator': proj.owner, 'projects': []}
        if len(innovator_map[oid]['projects']) < 3:
            proj.project_image = proj.get_main_image_url()
            proj.view_count  = ProjectView.objects.filter(project=proj).count()
            proj.like_count  = proj.liked_by.count()
            proj.collab_count = proj.collaborations_on_project.count()
            proj.proposal_count = proj.project_proposals.count()
            innovator_map[oid]['projects'].append(proj)
    all_innovators_with_projects = list(innovator_map.values())

    # Profile stats for left sidebar
    try:
        profile = user.userprofile
    except Exception:
        profile = None
    profile_views    = ProfileView.objects.filter(profile_user=user).count()
    inventions_count = Invention.objects.filter(owner=user).count()
    patents_count    = Patent.objects.filter(owner=user).count()
    groups_count     = GroupMembership.objects.filter(user=user, status='accepted').count()
    events_count     = Event.objects.filter(date__gte=now().date()).count()
    pages_count      = Page.objects.filter(owner=user).count()

    # Proposals for innovators right sidebar
    incoming_proposals = ProjectProposal.objects.filter(
        project__owner=user, status='pending'
    ).select_related('from_user', 'project').order_by('-created_at')[:5] if user.user_type != 'investor' else []

    # Investor: saved/liked projects
    investor_saved = ReadLater.objects.filter(user=user).select_related('project').exclude(project=None)[:8] if user.user_type == 'investor' else []

    # Recent profile viewers
    from .models import ProfileView as PV
    recent_viewers = PV.objects.filter(profile_user=user, viewer__isnull=False).exclude(viewer=user).select_related('viewer').order_by('-viewed_at')[:4]

    # Industry choices for filter
    industry_choices = [c[0] for c in Post._meta.get_field('industry').choices]

    # Subscription plans for pricing tab
    from .models import SubscriptionPlan, UserSubscription
    sub_plans = SubscriptionPlan.objects.filter(is_active=True).order_by('order')
    try:
        user_sub = user.subscription
    except UserSubscription.DoesNotExist:
        user_sub = None

    # Featured companies — top by follower count
    from .models import Company as _Company
    featured_companies = _Company.objects.annotate(
        fc=Count('followers')
    ).order_by('-fc', '-created_at')[:6]

    # Trending discussions — top by comment count in last 30 days
    from django.utils.timezone import now as _now
    from datetime import timedelta as _td
    _thirty_ago = _now() - _td(days=30)
    trending_discussions = GroupDiscussion.objects.filter(
        created_at__gte=_thirty_ago
    ).annotate(
        cmt_count=Count('comments')
    ).order_by('-cmt_count', '-created_at').select_related('group', 'author')[:6]

    # Connections list for share-to-chat modal
    share_connections = [
        c.target if c.initiator == user else c.initiator
        for c in Connection.objects.filter(
            Q(initiator=user, status='accepted') | Q(target=user, status='accepted')
        ).select_related('initiator', 'initiator__userprofile', 'target', 'target__userprofile')
    ]

    # Pinned IDs
    from .models import Pin
    pinned_post_ids = set(
        Pin.objects.filter(user=user, pin_type='post').values_list('post_id', flat=True)
    )
    pinned_project_ids = set(
        Pin.objects.filter(user=user, pin_type='project').values_list('project_id', flat=True)
    )

    # User's reactions on feed posts (post_id → reaction type)
    from .models import PostReaction
    post_ids = [p.id for p in posts]
    user_post_reactions = {
        r.post_id: r.reaction
        for r in PostReaction.objects.filter(post_id__in=post_ids, user=user)
    }

    context = {
        'page_name': 'Home',
        'posts': posts,
        'all_innovators_with_projects': all_innovators_with_projects,
        'connected_user_ids': connected_user_ids,
        'pending_connections': pending_connections,
        'proposals': incoming_proposals,
        'investor_saved': investor_saved,
        'profile': profile,
        'profile_views': profile_views,
        'inventions_count': inventions_count,
        'patents_count': patents_count,
        'groups_count': groups_count,
        'events_count': events_count,
        'pages_count': pages_count,
        'recent_viewers': recent_viewers,
        'industry_choices': industry_choices,
        'industry_filter': industry_filter,
        'date_filter': date_filter,
        'sub_plans': sub_plans,
        'user_sub': user_sub,
        'share_connections': share_connections,
        'show_confetti': request.GET.get('welcome') == '1',
        'featured_companies': featured_companies,
        'trending_discussions': trending_discussions,
        'trending_hashtags': _get_trending_hashtags(limit=10),
        'pinned_post_ids':      pinned_post_ids,
        'pinned_project_ids':   pinned_project_ids,
        'user_post_reactions':  user_post_reactions,
    }
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

@login_required
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    images = ProjectImage.objects.filter(project=project)
    main_image = images.filter(is_main=True).first() or images.first()
    extra_images = images.exclude(pk=main_image.pk) if main_image else images.none()

    from .models import Rating, Attachment, ReadLater, Connection
    from django.db.models import Avg, Q as DQ
    ratings = Rating.objects.filter(project=project)
    avg_rating = ratings.aggregate(avg=Avg('value'))['avg'] or 0
    rating_count = ratings.count()
    user_rating = None
    user_liked = False
    is_saved = False
    is_connected = False
    user_type = ''

    if request.user.is_authenticated:
        ur = ratings.filter(user=request.user).first()
        user_rating = ur.value if ur else None
        user_liked = project.liked_by.filter(pk=request.user.pk).exists()
        is_saved = ReadLater.objects.filter(user=request.user, project=project).exists()
        user_type = getattr(request.user, 'user_type', '')
        # Admins bypass connection requirement
        if user_type == 'admin':
            is_connected = True
        else:
            is_connected = Connection.objects.filter(
                DQ(initiator=request.user, target=project.owner) |
                DQ(initiator=project.owner, target=request.user),
                status='accepted'
            ).exists()

    attachments = Attachment.objects.filter(project=project)

    # Track project view
    if request.user.is_authenticated:
        from .models import ProjectView as PjV
        PjV.objects.get_or_create(
            project=project, user=request.user,
            defaults={'session_key': request.session.session_key or ''}
        )

    # Collaborators
    from .models import ProjectCollaboration
    collaborators = ProjectCollaboration.objects.filter(
        project=project, status='accepted'
    ).select_related('from_user')

    is_interested = False
    if request.user.is_authenticated:
        is_interested = project.interested.filter(pk=request.user.pk).exists()
    interest_count = project.interested.count()

    return render(request, 'project_detail.html', {
        'project': project,
        'main_image': main_image,
        'extra_images': extra_images,
        'avg_rating': avg_rating,
        'rating_count': rating_count,
        'user_rating': user_rating,
        'user_liked': user_liked,
        'is_saved': is_saved,
        'is_connected': is_connected,
        'user_type': user_type,
        'attachments': attachments,
        'collaborators': collaborators,
        'is_interested': is_interested,
        'interest_count': interest_count,
    })

# def project_detail(request, pk):
#     # Get the project by its ID (pk)
#     post = get_object_or_404(Post, pk=pk)
    
#     # Pass the project data to the template
#     return render(request, 'project_detail.html', {'post': post})

###Attachment

def user_attachments(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    attachments = Attachment.objects.filter(project__owner=user)
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
@login_required
def update_profile(request):
    return redirect('edit_profile')

@login_required
def _update_profile_unused(request):
    user = request.user
    up, _ = UserProfile.objects.get_or_create(user=user)

    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            # Also save UserProfile-specific fields
            up.phone_number = request.POST.get('phone_number', up.phone_number or '')
            up.industry     = request.POST.get('industry', up.industry or '')
            up.company      = request.POST.get('company', up.company or '')
            if 'profile_pic_up' in request.FILES:
                up.profile_pics = request.FILES['profile_pic_up']
            up.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=user)

    # Profile completion for sidebar bar
    _pc_checks = [
        bool(up.bio), bool(up.industry), bool(up.company),
        bool(up.phone_number), bool(up.profile_pics),
        bool(user.first_name), bool(user.last_name),
        bool(up.investment_thesis or up.preferred_sectors),
    ]
    pc = int(sum(_pc_checks) / len(_pc_checks) * 100)

    return render(request, "update_profile.html", {
        "form": form,
        "up": up,
        "profile": up,
        "profile_completion": pc,
        "industry_choices": UserProfile._meta.get_field('industry').choices,
    })


@login_required
@require_POST
def remove_profile_photo(request):
    """Delete the user's uploaded profile picture and fall back to initials."""
    from .models import UserProfile
    import os
    up, _ = UserProfile.objects.get_or_create(user=request.user)
    if up.profile_pics:
        # Delete the file from disk too
        try:
            if os.path.isfile(up.profile_pics.path):
                os.remove(up.profile_pics.path)
        except Exception:
            pass
        up.profile_pics = None
        up.save()
        messages.success(request, "Profile photo removed.")
    return redirect('update_profile')


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
@login_required
def delete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.method == "POST":
        project.delete()
        return redirect('dashboard')
    return render(request, 'confirm_delete.html', {'project': project})

#####Edit from dashboard
@login_required
def edit_project(request, project_id):
    project = get_object_or_404(Project, id=project_id, owner=request.user)

    if request.method == "POST":
        form = ProjectForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, "Project updated successfully.")
            return redirect('project_detail', pk=project.pk)
    else:
        form = ProjectForm(instance=project)

    return render(request, 'edit_project.html', {
        'form': form,
        'project': project,
        'industry_choices': INDUSTRY_CHOICES,
    })


@login_required
def edit_attachment(request, attachment_id):
    from .models import Attachment
    att = get_object_or_404(Attachment, pk=attachment_id, project__owner=request.user)
    if request.method == 'POST':
        visibility = request.POST.get('visibility', att.visibility)
        if visibility in ('public', 'connections', 'private'):
            att.visibility = visibility
            att.save()
    return redirect('edit_project', project_id=att.project_id)


@login_required
def create_project(request):
    if getattr(request.user, 'user_type', '') == 'investor':
        messages.error(request, "Investors cannot create projects. Collaborate with an innovator instead.")
        return redirect(request.META.get('HTTP_REFERER', 'app'))
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()

            # Persist custom industry to DB so others can use it
            from .models import ProjectImage, Attachment, CustomIndustry
            preset_vals = [v for v, _ in project._meta.get_field('industry').choices]
            if project.industry and project.industry not in preset_vals:
                CustomIndustry.objects.get_or_create(name=project.industry)
            image_files = request.FILES.getlist('images')
            for i, img_file in enumerate(image_files[:10]):
                img_name = request.POST.get(f'image_name_{i}', '')
                ProjectImage.objects.create(
                    project=project,
                    image=img_file,
                    name=img_name,
                    is_main=(i == 0),
                )

            # Handle up to 4 documents
            for n in range(1, 5):
                doc_file = request.FILES.get(f'doc_file_{n}')
                if doc_file:
                    Attachment.objects.create(
                        project=project,
                        file=doc_file,
                        title=request.POST.get(f'doc_title_{n}', ''),
                        doc_type=request.POST.get(f'doc_type_{n}', 'general'),
                        visibility=request.POST.get(f'doc_visibility_{n}', 'connections'),
                    )

            messages.success(request, "Project created successfully!")
            return redirect('project_detail', pk=project.pk)
    else:
        form = ProjectForm()
    from .models import Project as _Proj, CustomIndustry
    preset = list(_Proj._meta.get_field('industry').choices)
    custom = list(CustomIndustry.objects.values_list('name', flat=True))
    preset_vals = {v for v, _ in preset}
    all_choices = preset + [(n, n) for n in custom if n not in preset_vals]
    return render(request, 'create_project.html', {
        'form': form,
        'industry_choices': all_choices,
    })


# ── Pipeline Stage Progression ─────────────────────────────────────────────

@login_required
def request_stage_progression(request, pk):
    """Innovator requests to advance their project to the next pipeline stage."""
    from .models import StageProgressionRequest
    project = get_object_or_404(Project, pk=pk)
    if request.user != project.owner:
        messages.error(request, "Only the project owner can request stage progression.")
        return redirect('project_detail', pk=pk)
    if project.stage_status == 'pending_approval':
        messages.warning(request, "A progression request is already pending review.")
        return redirect('project_detail', pk=pk)

    stage_order = ['idea', 'validation', 'investment', 'growth']
    current_idx = stage_order.index(project.pipeline_stage)
    if current_idx >= len(stage_order) - 1:
        messages.info(request, "Your project is already in the final stage.")
        return redirect('project_detail', pk=pk)

    next_stage = stage_order[current_idx + 1]
    StageProgressionRequest.objects.create(
        project=project,
        from_stage=project.pipeline_stage,
        to_stage=next_stage,
        requested_by=request.user,
    )
    project.stage_status = 'pending_approval'
    project.save(update_fields=['stage_status'])
    messages.success(request, f"Progression request to '{next_stage.title()} Stage' submitted. Awaiting admin review.")
    return redirect('project_detail', pk=pk)


@login_required
def admin_stage_approvals(request):
    """Admin view listing all pending stage progression requests."""
    if request.user.user_type != 'admin':
        return redirect('app')
    from .models import StageProgressionRequest
    pending = StageProgressionRequest.objects.filter(status='pending').select_related('project', 'requested_by')
    recent  = StageProgressionRequest.objects.exclude(status='pending').select_related('project', 'requested_by', 'reviewed_by')[:20]
    return render(request, 'admin_stage_approvals.html', {'pending': pending, 'recent': recent})


@login_required
def admin_approve_stage(request, req_id):
    """Admin approves a stage progression request."""
    if request.user.user_type != 'admin':
        return redirect('app')
    from .models import StageProgressionRequest
    from django.utils import timezone as tz
    spr = get_object_or_404(StageProgressionRequest, pk=req_id, status='pending')
    admin_note = request.POST.get('admin_note', '')
    spr.status      = 'approved'
    spr.reviewed_by = request.user
    spr.reviewed_at = tz.now()
    spr.admin_note  = admin_note
    spr.save()
    # Advance the project stage
    project = spr.project
    project.pipeline_stage = spr.to_stage
    project.stage_status   = 'approved'
    project.save(update_fields=['pipeline_stage', 'stage_status'])
    messages.success(request, f"Project '{project.title}' advanced to {spr.to_stage.title()} Stage.")
    return redirect('admin_stage_approvals')


@login_required
def admin_reject_stage(request, req_id):
    """Admin rejects a stage progression request."""
    if request.user.user_type != 'admin':
        return redirect('app')
    from .models import StageProgressionRequest
    from django.utils import timezone as tz
    spr = get_object_or_404(StageProgressionRequest, pk=req_id, status='pending')
    admin_note = request.POST.get('admin_note', '')
    spr.status      = 'rejected'
    spr.reviewed_by = request.user
    spr.reviewed_at = tz.now()
    spr.admin_note  = admin_note
    spr.save()
    project = spr.project
    project.stage_status = 'rejected'
    project.save(update_fields=['stage_status'])
    messages.warning(request, f"Progression request for '{project.title}' rejected.")
    return redirect('admin_stage_approvals')


# ── Credibility & Verification ─────────────────────────────────────────────

@login_required
def submit_verification_request(request):
    """User submits a request to be verified."""
    from .models import VerificationRequest
    profile = getattr(request.user, 'userprofile', None)
    if not profile:
        return redirect('app')
    # Only allow re-submission if not already pending/verified
    if profile.verification_status in ('pending', 'verified'):
        messages.info(request, f"Your verification status is already: {profile.get_verification_status_display()}.")
        return redirect('my_profile')
    if request.method == 'POST':
        VerificationRequest.objects.filter(user=request.user, status='rejected').delete()
        vr = VerificationRequest(
            user          = request.user,
            bio_statement = request.POST.get('bio_statement', ''),
            linkedin_url  = request.POST.get('linkedin_url', ''),
            website_url   = request.POST.get('website_url', ''),
            notes         = request.POST.get('notes', ''),
        )
        if 'id_document' in request.FILES:
            vr.id_document = request.FILES['id_document']
        vr.save()
        profile.verification_status = 'pending'
        profile.save(update_fields=['verification_status'])
        messages.success(request, "Verification request submitted. We'll review it shortly.")
    return redirect('my_profile')


@login_required
def admin_verification_queue(request):
    """Admin: list all verification requests."""
    if request.user.user_type != 'admin':
        return redirect('app')
    from .models import VerificationRequest
    pending = VerificationRequest.objects.filter(status='pending').select_related('user', 'user__userprofile')
    recent  = VerificationRequest.objects.exclude(status='pending').select_related('user', 'user__userprofile', 'reviewed_by').order_by('-reviewed_at')[:30]
    return render(request, 'admin_verification_queue.html', {
        'pending': pending, 'recent': recent,
    })


@login_required
def admin_approve_verification(request, req_id):
    """Admin: approve a verification request."""
    if request.user.user_type != 'admin':
        return redirect('app')
    from .models import VerificationRequest
    from django.utils import timezone as tz
    vr = get_object_or_404(VerificationRequest, pk=req_id, status='pending')
    vr.status      = 'approved'
    vr.reviewed_by = request.user
    vr.reviewed_at = tz.now()
    vr.admin_note  = request.POST.get('admin_note', '')
    vr.save()
    profile = vr.user.userprofile
    profile.verification_status = 'verified'
    profile.verified_at = tz.now()
    profile.verified_by = request.user
    profile.save(update_fields=['verification_status', 'verified_at', 'verified_by'])
    messages.success(request, f"{vr.user.get_full_name()} is now Verified.")
    return redirect('admin_verification_queue')


@login_required
def admin_reject_verification(request, req_id):
    """Admin: reject a verification request."""
    if request.user.user_type != 'admin':
        return redirect('app')
    from .models import VerificationRequest
    from django.utils import timezone as tz
    vr = get_object_or_404(VerificationRequest, pk=req_id, status='pending')
    vr.status      = 'rejected'
    vr.reviewed_by = request.user
    vr.reviewed_at = tz.now()
    vr.admin_note  = request.POST.get('admin_note', '')
    vr.save()
    profile = vr.user.userprofile
    profile.verification_status = 'rejected'
    profile.save(update_fields=['verification_status'])
    messages.warning(request, f"Verification for {vr.user.get_full_name()} rejected.")
    return redirect('admin_verification_queue')


@login_required
def submit_project_for_review(request, pk):
    """Innovator submits a project for admin review/approval."""
    project = get_object_or_404(Project, pk=pk, owner=request.user)
    if project.review_status == 'under_review':
        messages.info(request, "This project is already under review.")
        return redirect('project_detail', pk=pk)
    if project.review_status in ('approved', 'featured'):
        messages.info(request, "This project is already approved.")
        return redirect('project_detail', pk=pk)
    project.review_status = 'under_review'
    project.save(update_fields=['review_status'])
    messages.success(request, "Project submitted for review. Our team will assess it shortly.")
    return redirect('project_detail', pk=pk)


@login_required
def admin_project_review_queue(request):
    """Admin: list projects filterable by review status."""
    if request.user.user_type != 'admin':
        return redirect('app')
    current_status = request.GET.get('status', '')
    qs = Project.objects.select_related('owner', 'owner__userprofile', 'reviewed_by').order_by('-created_at')
    if current_status:
        qs = qs.filter(review_status=current_status)
    return render(request, 'admin_project_reviews.html', {
        'projects':        qs,
        'status_choices':  Project.REVIEW_STATUS,
        'current_status':  current_status,
    })


@login_required
def admin_set_project_review_status(request, pk):
    """Admin: set a project's review status (approve / reject / feature)."""
    if request.user.user_type != 'admin':
        return redirect('app')
    from django.utils import timezone as tz
    project = get_object_or_404(Project, pk=pk)
    new_status = request.POST.get('review_status', '')
    valid = [s for s, _ in Project.REVIEW_STATUS]
    if new_status not in valid:
        messages.error(request, "Invalid status.")
        return redirect('admin_project_review_queue')
    project.review_status = new_status
    project.review_note   = request.POST.get('review_note', '')
    project.reviewed_by   = request.user
    project.reviewed_at   = tz.now()
    project.save(update_fields=['review_status', 'review_note', 'reviewed_by', 'reviewed_at'])
    messages.success(request, f"'{project.title}' set to {project.get_review_status_display()}.")
    return redirect('admin_project_review_queue')


# User Registration
###########
from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CustomUserCreationForm
from .models import UserProfile

def register(request):
    if request.user.is_authenticated:
        return render(request, 'register.html', {'already_logged_in': True})
    context = {"page_title": "App Center"}
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Save the CustomUser form and create the user
            user = form.save()

            # Create the UserProfile for the new user
            if not hasattr(user, 'userprofile'):
                UserProfile.objects.create(user=user)

            # ── Welcome notification ──
            from .models import Notification, Conversation, Message as Msg
            from django.contrib.auth import get_user_model
            User = get_user_model()
            first_name = user.first_name or user.username

            Notification.objects.create(
                user=user,
                notification_type='other',
                message=(
                    f"Welcome to Oduma Corp, {first_name}! 🎉 "
                    "Your account is ready. Complete your profile to start connecting with innovators and investors across Africa."
                ),
                link='/app/',
            )

            # ── Welcome DM from the first superuser (team account) ──
            try:
                admin = User.objects.filter(is_superuser=True).order_by('pk').first()

                if admin and admin.pk != user.pk:

                    conv = Conversation.objects.create(context_type='direct')

                    conv.participants.add(admin.pk)
                    conv.participants.add(user.pk)

                    Msg.objects.create(
                        conversation_id=conv.pk,
                        sender_id=admin.pk,
                        recipient_id=user.pk,
            
                        content=(
                            f"Hi {first_name}, welcome to Oduma Corp! 👋\n\n""<img />"
                            "Here are your login details — keep them safe:\n\n<br>"
                            f"📧 Email: {user.email}\n <br>"
                            f"👤 Username: {user.username}\n\n <br>"
                            "You can log in using either your email or username.\n\n"
                            "Here's how to get started:\n"
                            "1️⃣ Complete your profile — add a photo, bio, and your industry.\n"
                            "2️⃣ Post your first project (innovators) or browse opportunities (investors).\n"
                            "3️⃣ Connect with people in your industry and start collaborating.\n\n"
                            "If you have any questions, just reply here. We're happy to help! 🚀"
                        ),
                    )

            except Exception as e:
                print("Conversation creation failed:", e)

            # Log the user in
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')

            # Success message
            messages.success(request, "Registration successful!")
            return redirect('/app/?welcome=1')
        else:
            # Error message for invalid form
            messages.error(request, "Registration failed. Please check your details.")
    else:
        # Empty form for GET request
        form = CustomUserCreationForm()

    return render(request, "register.html", {"form": form})

# User login
def login_view(request):
    if request.user.is_authenticated:
        return redirect('app')
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
    from .models import Group, Page, Job, Event
    query = request.GET.get('q', '').strip()
    search_type = request.GET.get('type', 'all')

    post_results    = []
    project_results = []
    group_results   = []
    page_results    = []
    job_results     = []
    event_results   = []

    if query:
        if search_type in ('all', 'posts'):
            post_results = list(Post.objects.filter(
                Q(title__icontains=query) | Q(content__icontains=query), is_hidden=False
            )[:10])
        if search_type in ('all', 'projects'):
            project_results = list(Project.objects.filter(
                Q(title__icontains=query) | Q(description__icontains=query) | Q(keywords__icontains=query),
                is_hidden=False
            ).exclude(status='draft')[:10])
        if search_type in ('all', 'groups'):
            group_results = list(Group.objects.filter(
                Q(name__icontains=query) | Q(description__icontains=query), is_hidden=False
            )[:10])
        if search_type in ('all', 'pages'):
            page_results = list(Page.objects.filter(
                Q(title__icontains=query) | Q(description__icontains=query), is_hidden=False
            )[:10])
        if search_type in ('all', 'jobs'):
            job_results = list(Job.objects.filter(
                Q(title__icontains=query) | Q(description__icontains=query)
            )[:10])
        if search_type in ('all', 'events'):
            event_results = list(Event.objects.filter(
                Q(name__icontains=query) | Q(description__icontains=query)
            )[:10])

    return render(request, 'search_results.html', {
        'query': query,
        'search_type': search_type,
        'post_results': post_results,
        'project_results': project_results,
        'group_results': group_results,
        'page_results': page_results,
        'job_results': job_results,
        'event_results': event_results,
        'total_count': len(post_results) + len(project_results) + len(group_results) + len(page_results) + len(job_results) + len(event_results),
    })

##feedback form

###
import logging

from django.core.mail import send_mail

logger = logging.getLogger(__name__)
def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            name    = form.cleaned_data['name']
            email   = form.cleaned_data['email']
            message = form.cleaned_data['message']
            topic   = request.POST.get('topic', 'General Inquiry')
            subject = request.POST.get('subject', '')

            logger.info(f"Received contact form: Name={name}, Email={email}, Topic={topic}")

            # Save submission to DB
            from .models import ContactSubmission, Notification
            submission = ContactSubmission.objects.create(
                name=name, email=email, message=message,
                topic=topic, subject=subject,
            )

            # Notify all admin users
            admin_users = CustomUser.objects.filter(user_type='admin')
            submissions_url = '/admin/contact-submissions/'
            for admin in admin_users:
                Notification.objects.create(
                    user=admin,
                    message=f"New contact message from {name} ({email}) — Topic: {topic}",
                    notification_type='other',
                    link=submissions_url,
                )

            # Email admins
            try:
                send_mail(
                    subject=f"[Contact] {topic}: {subject or message[:60]}",
                    message=f"Name: {name}\nEmail: {email}\nTopic: {topic}\nSubject: {subject}\n\n{message}",
                    from_email=email,
                    recipient_list=["info@odumacorp.com", "odumacorp@gmail.com"],
                )
                messages.success(request, "Your message has been sent successfully!")
            except Exception as e:
                logger.error(f"Email sending failed: {e}")
                messages.success(request, "Your message has been received! We'll get back to you soon.")

            form = ContactForm()
        else:
            messages.error(request, "There was an error with your submission.")
    else:
        form = ContactForm()

    return render(request, "contact.html", {"form": form})

###all users





def view_innovator(request, user_id):
    innovator = get_object_or_404(CustomUser, pk=user_id)
    projects = Project.objects.filter(owner=innovator)
    my_connections = request.user.userprofile.connected_users.values_list('user_id', flat=True) if request.user.is_authenticated else []

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

# ============================================================
# STUB / WIRED VIEWS  — routes that templates reference
# ============================================================

# --- profile alias ---
def profile_alias(request):
    return my_profile_view(request)

# --- meetings ---
@login_required
def meetings_list(request):
    from .models import Meeting, Connection
    user = request.user
    qs = Meeting.objects.filter(
        Q(creator=user) | Q(participants=user)
    ).distinct().order_by('-created_at')
    upcoming = qs.exclude(status='ended')
    past     = qs.filter(status='ended')[:20]
    accepted = Connection.objects.filter(
        Q(initiator=user, status='accepted') | Q(target=user, status='accepted')
    ).select_related('initiator', 'target')
    connections = [c.target if c.initiator == user else c.initiator for c in accepted if (c.target if c.initiator == user else c.initiator).is_active]
    return render(request, 'meetings.html', {'upcoming': upcoming, 'past': past, 'connections': connections})

@login_required
def join_meeting(request, meeting_id):
    from .models import Meeting, Connection
    meeting = get_object_or_404(Meeting, pk=meeting_id)
    is_host = meeting.creator == request.user
    # Build connected users list for the share-meeting dropdown
    accepted = Connection.objects.filter(
        Q(initiator=request.user, status='accepted') | Q(target=request.user, status='accepted')
    ).select_related('initiator', 'target')
    connections = [
        c.target if c.initiator == request.user else c.initiator
        for c in accepted
        if (c.target if c.initiator == request.user else c.initiator).is_active
    ]
    return render(request, 'meeting_room.html', {
        'meeting': meeting,
        'is_host': is_host,
        'connections': connections,
    })

@login_required
def share_meeting(request, meeting_id):
    """Send the meeting details as a DM to a selected connection."""
    from .models import Meeting, CustomUser, Conversation, Message, Notification
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'error': 'POST required'}, status=405)
    meeting = get_object_or_404(Meeting, pk=meeting_id)
    # Only participants (or creator) can share
    if not meeting.participants.filter(pk=request.user.pk).exists() and meeting.creator != request.user:
        return JsonResponse({'ok': False, 'error': 'Forbidden'}, status=403)
    recipient_id = request.POST.get('recipient_id', '').strip()
    if not recipient_id:
        return JsonResponse({'ok': False, 'error': 'Please choose a recipient.'})
    try:
        recipient = CustomUser.objects.get(pk=recipient_id)
    except CustomUser.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'User not found.'})

    # Build a clean invite message
    page_url = request.build_absolute_uri(f'/meetings/{meeting.pk}/join/')
    lines = [f"📹 You're invited to join a meeting!",
             f"",
             f"📌 {meeting.title}"]
    if meeting.scheduled_at:
        lines.append(f"📅 {meeting.scheduled_at.strftime('%b %d, %Y at %H:%M UTC')}")
    if meeting.zoom_join_url:
        lines.append(f"🔗 {meeting.zoom_join_url}")
    if meeting.zoom_meeting_id:
        lines.append(f"🆔 Meeting ID: {meeting.zoom_meeting_id}")
    if meeting.zoom_password:
        lines.append(f"🔑 Passcode: {meeting.zoom_password}")
    lines += [f"", f"Or open on Oduma Corp: {page_url}"]
    text = "\n".join(lines)

    # Get or create conversation
    conv = Conversation.objects.filter(participants=request.user).filter(participants=recipient).first()
    if not conv:
        conv = Conversation.objects.create()
        conv.participants.add(request.user, recipient)

    msg = Message.objects.create(
        conversation=conv,
        sender=request.user,
        recipient=recipient,
        content=text,
        message_type='text',
    )
    Notification.objects.create(
        user=recipient,
        message=f"{request.user.get_full_name() or request.user.username} shared a meeting with you: \"{meeting.title}\"",
        notification_type='message_sent',
        link=f'/chat/{conv.pk}/',
    )
    return JsonResponse({'ok': True, 'conversation_id': conv.pk})


@login_required
def end_meeting(request, meeting_id):
    from .models import Meeting
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'error': 'POST required'}, status=405)
    meeting = get_object_or_404(Meeting, pk=meeting_id)
    if meeting.creator != request.user:
        meeting.participants.remove(request.user)
    else:
        meeting.status = 'ended'
        meeting.save()
    return JsonResponse({'ok': True})

@login_required
def meeting_recordings(request, meeting_id):
    from .models import Meeting
    from .zoom_api import get_recordings, ZoomConfigError, ZoomAPIError
    meeting = get_object_or_404(Meeting, pk=meeting_id)
    if not meeting.zoom_meeting_id:
        return JsonResponse({'ok': False, 'error': 'No Zoom meeting linked to this session.'})
    try:
        files = get_recordings(meeting.zoom_meeting_id)
        if files:
            status = files[0].get('status', 'completed') if isinstance(files[0], dict) else 'completed'
            return JsonResponse({'ok': True, 'status': status, 'files': files})
        return JsonResponse({'ok': True, 'status': 'none', 'files': []})
    except (ZoomConfigError, ZoomAPIError) as e:
        return JsonResponse({'ok': False, 'error': str(e)})

@login_required
def create_meeting(request):
    import json
    from .models import Meeting, CustomUser
    from .zoom_api import create_meeting as zoom_create, ZoomConfigError, ZoomAPIError
    if request.method != 'POST':
        # Browser navigated here directly — redirect to meetings page and auto-open the modal
        from django.shortcuts import redirect
        return redirect('/meetings/?new=1')
    import secrets
    try:
        title        = request.POST.get('title', '').strip() or 'Oduma Corp Meeting'
        invitee_ids  = request.POST.getlist('invitee_ids')
        duration     = int(request.POST.get('duration', 60) or 60)
        agenda       = request.POST.get('agenda', '').strip()
        scheduled_at_str = request.POST.get('scheduled_at', '').strip()
        scheduled_at = None
        if scheduled_at_str:
            try:
                from django.utils.dateparse import parse_datetime
                scheduled_at = parse_datetime(scheduled_at_str)
            except Exception:
                pass
        # Resolve Odu's email for Zoom alternative-host slot
        from .models import CustomUser as _CU
        odu_email = (
            _CU.objects.filter(username__iexact='odu')
            .values_list('email', flat=True)
            .first()
        ) or 'odu@odumacorp.com'

        # Create in Zoom — creator is host, Odu is always co-host/alternative host
        zoom_data = {}
        try:
            zoom_data = zoom_create(
                title,
                scheduled_at=scheduled_at,
                duration_minutes=duration,
                host_email=request.user.email,
                alternative_host_emails=[odu_email],
            )
        except Exception:
            pass  # Zoom not configured; meeting created locally only
        # Generate unique room_id to satisfy the unique constraint
        room_id = secrets.token_hex(16)
        meeting = Meeting.objects.create(
            creator      = request.user,
            title        = title,
            room_id      = room_id,
            scheduled_at = scheduled_at,
            status       = 'scheduled',
            zoom_meeting_id = str(zoom_data.get('id', '')),
            zoom_join_url   = zoom_data.get('join_url', ''),
            zoom_start_url  = zoom_data.get('start_url', ''),
            zoom_password   = zoom_data.get('password', ''),
        )
        meeting.participants.add(request.user)
        for uid in invitee_ids:
            try:
                meeting.participants.add(CustomUser.objects.get(pk=uid))
            except CustomUser.DoesNotExist:
                pass

        from django.urls import reverse
        url = reverse('join_meeting', args=[meeting.id])
        join_link = url

        # Notify admins + Odu so they can join if they want
        creator_name = request.user.get_full_name() or request.user.username
        scheduled_str = (
            f" scheduled for {scheduled_at.strftime('%b %d, %H:%M')}" if scheduled_at else ''
        )
        notif_msg = (
            f"{creator_name} started a meeting: \"{title}\"{scheduled_str}. "
            "You can join if you'd like."
        )
        observers = set(
            CustomUser.objects.filter(user_type='admin').exclude(pk=request.user.pk)
        ) | set(
            CustomUser.objects.filter(username__iexact='odu')
        )
        from .models import Notification
        for observer in observers:
            # Add as participant so they can join via the meeting page
            meeting.participants.add(observer)
            Notification.objects.create(
                user=observer,
                message=notif_msg,
                notification_type='other',
                link=join_link,
            )

        return JsonResponse({'ok': True, 'url': url})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=500)

# --- investor dashboard ---
@login_required
def investor_dashboard(request):
    from .models import (
        Connection, ProjectProposal, ProjectCollaboration,
        ReadLater, Interest, Like, Project,
        Proposal, Collaboration, PatentRequest, Post, PitchRequest,
    )
    from django.db.models import Q as _Q
    user = request.user

    # Connections
    accepted = Connection.objects.filter(
        Q(initiator=user, status='accepted') | Q(target=user, status='accepted')
    ).select_related('initiator', 'target', 'initiator__userprofile', 'target__userprofile')
    connected_users = [c.target if c.initiator == user else c.initiator for c in accepted if (c.target if c.initiator == user else c.initiator).is_active]
    innovators_connected = [u for u in connected_users if getattr(u, 'user_type', '') == 'innovator']
    investors_connected  = [u for u in connected_users if getattr(u, 'user_type', '') == 'investor']

    # Project proposals sent by this investor
    sent_proposals     = ProjectProposal.objects.filter(from_user=user).select_related('project', 'project__owner').order_by('-created_at')
    pending_proposals  = sent_proposals.filter(status='pending')
    accepted_proposals = sent_proposals.filter(status='accepted')

    # Post-based proposals (old Proposal model)
    post_proposals = Proposal.objects.filter(from_investor=user).select_related('post', 'post__user').order_by('-created_at')

    # Project collaborations
    sent_collabs = ProjectCollaboration.objects.filter(from_user=user).select_related('project', 'project__owner').order_by('-created_at')

    # Post-based collaborations
    post_collabs = Collaboration.objects.filter(from_user=user).select_related('post', 'post__user').order_by('-created_at')

    # Patent requests
    patent_requests = PatentRequest.objects.filter(from_investor=user).select_related('post', 'post__user').order_by('-created_at')

    # Saved projects
    saved = ReadLater.objects.filter(user=user).select_related('project').exclude(project=None)

    # Liked posts and projects
    liked_posts      = user.liked_posts.select_related('user', 'user__userprofile').order_by('-created_at')[:20]
    interested_posts = user.interested_posts.select_related('user', 'user__userprofile').order_by('-created_at')[:20]
    liked_projects   = Project.objects.filter(liked_by=user)

    # Pending connections incoming
    pending_connections = Connection.objects.filter(target=user, status='pending').select_related('initiator', 'initiator__userprofile')

    # Pitch requests sent by this investor
    my_pitch_requests = PitchRequest.objects.filter(investor=user).select_related('project', 'project__owner')

    # ── Deal Flow: filtered recommended projects ──────────────────────────
    profile = getattr(user, 'userprofile', None)
    f_industry = request.GET.get('industry', '').strip()
    f_stage    = request.GET.get('stage', '').strip()
    f_funding  = request.GET.get('funding_stage', '').strip()
    f_search   = request.GET.get('q', '').strip()

    deal_flow_qs = Project.objects.filter(
        is_hidden=False
    ).exclude(owner=user).exclude(status='draft').select_related('owner', 'owner__userprofile')

    if f_industry:
        deal_flow_qs = deal_flow_qs.filter(industry=f_industry)
    if f_stage:
        deal_flow_qs = deal_flow_qs.filter(pipeline_stage=f_stage)
    if f_funding:
        deal_flow_qs = deal_flow_qs.filter(funding_stage=f_funding)
    if f_search:
        deal_flow_qs = deal_flow_qs.filter(
            _Q(title__icontains=f_search) |
            _Q(problem_statement__icontains=f_search) |
            _Q(keywords__icontains=f_search)
        )

    # Personalise: if investor has preferred sectors, sort matches first
    if profile and profile.preferred_sectors:
        sectors = [s.strip().lower() for s in profile.preferred_sectors.split(',') if s.strip()]
        matched, rest = [], []
        for p in deal_flow_qs.order_by('-created_at')[:60]:
            if p.industry.lower() in sectors:
                matched.append(p)
            else:
                rest.append(p)
        deal_flow_projects = matched + rest
    else:
        deal_flow_projects = list(deal_flow_qs.order_by('-created_at')[:40])

    # Projects this investor has expressed interest in
    interested_project_ids = set(Project.objects.filter(interested=user).values_list('id', flat=True))

    # Saved project ids
    saved_project_ids = set(saved.values_list('project_id', flat=True))

    # Pitch-requested project ids
    pitched_project_ids = set(my_pitch_requests.values_list('project_id', flat=True))

    # ── Intelligent Matching: top matches for this investor ─────────────────
    from .matching import get_top_matches_with_breakdown, compute_match_score, score_label as _score_label
    match_pool = Project.objects.filter(
        is_hidden=False
    ).exclude(owner=user).exclude(status='draft').select_related('owner', 'owner__userprofile')[:80]
    top_matches = get_top_matches_with_breakdown(profile, match_pool, n=6)
    # Also score deal_flow_projects in-place
    for p in deal_flow_projects:
        p.match_score = compute_match_score(profile, p)
        p.match_label, p.match_css = _score_label(p.match_score)

    # Upcoming events
    from .models import Event as _Event, EventRegistration as _ER
    from datetime import date as _date
    upcoming_events = _Event.objects.filter(
        is_hidden=False, date__gte=_date.today()
    ).order_by('date')[:3]
    registered_event_ids = set(
        _ER.objects.filter(user=user).values_list('event_id', flat=True)
    )

    context = {
        'connected_users': connected_users,
        'connections_count': len(connected_users),
        'innovators_connected': innovators_connected,
        'investors_connected': investors_connected,
        'connected_innovators': innovators_connected,
        'connected_investors': investors_connected,
        # Project proposals
        'sent_proposals': sent_proposals,
        'pending_proposals': pending_proposals,
        'accepted_proposals': accepted_proposals,
        'proposals': post_proposals,
        # Collaborations
        'sent_collabs': sent_collabs,
        'project_collabs': sent_collabs,
        'collaborations': post_collabs,
        'patent_requests': patent_requests,
        # Pending
        'pending_connections': pending_connections,
        'pending_collabs': post_collabs.filter(status='pending'),
        'pending_proj_collabs': sent_collabs.filter(status='pending'),
        # Content
        'saved': saved,
        'liked_projects': liked_projects,
        'liked_posts': liked_posts,
        'interested_posts': interested_posts,
        'recommended_projects': deal_flow_projects[:6],
        'dash_meetings': [],
        # Deal Flow
        'deal_flow_projects': deal_flow_projects,
        'deal_flow_count': len(deal_flow_projects),
        'interested_project_ids': interested_project_ids,
        'saved_project_ids': saved_project_ids,
        'pitched_project_ids': pitched_project_ids,
        'my_pitch_requests': my_pitch_requests,
        # Filters (echo back for active state)
        'f_industry': f_industry,
        'f_stage':    f_stage,
        'f_funding':  f_funding,
        'f_search':   f_search,
        # Investor profile
        'investor_profile': profile,
        # Choices for filter dropdowns
        'industry_choices': INDUSTRY_CHOICES,
        'pipeline_stage_choices': [
            ('idea','Idea Stage'),('validation','Validation Stage'),
            ('investment','Investment Stage'),('growth','Growth Stage'),
        ],
        'funding_stage_choices': [
            ('pre_seed','Pre-Seed'),('seed','Seed'),('pre_series_a','Pre-Series A'),
            ('series_a','Series A'),('series_b','Series B+'),('grant','Grant / Non-dilutive'),
        ],
        'page_name': 'Investor Dashboard',
        # Matching
        'top_matches':          top_matches,
        'pitched_ids':          pitched_project_ids,
        # Events
        'upcoming_events':      upcoming_events,
        'registered_event_ids': registered_event_ids,
    }

    # Pins
    from .models import Pin
    user_pins = Pin.objects.filter(user=user).select_related(
        'conversation', 'post', 'project',
    ).prefetch_related('conversation__participants')
    context['pinned_chats']       = [p for p in user_pins if p.pin_type == 'chat']
    context['pinned_posts']       = [p for p in user_pins if p.pin_type == 'post']
    context['pinned_projects']    = [p for p in user_pins if p.pin_type == 'project']
    context['pinned_chat_ids']    = set(p.conversation_id for p in user_pins if p.pin_type == 'chat' and p.conversation_id)
    context['pinned_post_ids']    = set(p.post_id for p in user_pins if p.pin_type == 'post' and p.post_id)
    context['pinned_project_ids'] = set(p.project_id for p in user_pins if p.pin_type == 'project' and p.project_id)

    return render(request, 'investor_dashboard.html', context)


@login_required
def request_pitch(request, pk):
    """Investor requests a pitch/meeting from an innovator for their project."""
    from .models import PitchRequest
    if getattr(request.user, 'user_type', '') != 'investor':
        messages.error(request, "Only investors can request pitches.")
        return redirect('project_detail', pk=pk)
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        msg = request.POST.get('message', '').strip()
        pr, created = PitchRequest.objects.get_or_create(
            project=project, investor=request.user,
            defaults={'message': msg}
        )
        if not created:
            messages.info(request, "You already requested a pitch for this project.")
        else:
            messages.success(request, f"Pitch request sent to {project.owner.get_full_name() or project.owner.username}.")
    return redirect(request.META.get('HTTP_REFERER', 'project_detail'))


@login_required
def toggle_project_interest(request, pk):
    """Investor toggles interest in a project (adds/removes from project.interested)."""
    project = get_object_or_404(Project, pk=pk)
    if project.interested.filter(pk=request.user.pk).exists():
        project.interested.remove(request.user)
        interested = False
    else:
        project.interested.add(request.user)
        interested = True
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        from django.http import JsonResponse as _JR
        return _JR({'interested': interested, 'count': project.interested.count()})
    return redirect(request.META.get('HTTP_REFERER', 'project_detail'))


@login_required
def update_investor_profile(request):
    """Save investor profile preferences: ticket size, sectors, geography, thesis."""
    if getattr(request.user, 'user_type', '') != 'investor':
        return redirect('app')
    profile = getattr(request.user, 'userprofile', None)
    if not profile:
        return redirect('app')
    if request.method == 'POST':
        profile.ticket_size_min   = request.POST.get('ticket_size_min') or None
        profile.ticket_size_max   = request.POST.get('ticket_size_max') or None
        profile.preferred_sectors = request.POST.get('preferred_sectors', '')
        profile.geography_focus   = request.POST.get('geography_focus', '')
        profile.investment_thesis = request.POST.get('investment_thesis', '')
        profile.save(update_fields=[
            'ticket_size_min', 'ticket_size_max',
            'preferred_sectors', 'geography_focus', 'investment_thesis',
        ])
        messages.success(request, "Investor profile updated.")
    return redirect('investor_dashboard')

# --- proposals ---
@login_required
def proposals_list(request):
    from .models import ProjectProposal, ProjectCollaboration
    # Proposals sent TO this user's projects
    incoming_proposals = ProjectProposal.objects.filter(
        project__owner=request.user
    ).select_related('from_user', 'project').order_by('-created_at')

    incoming_collabs = ProjectCollaboration.objects.filter(
        project__owner=request.user
    ).select_related('from_user', 'project').order_by('-created_at')

    # Proposals/collabs sent BY this user
    sent_proposals = ProjectProposal.objects.filter(
        from_user=request.user
    ).select_related('project__owner', 'project').order_by('-created_at')

    sent_collabs = ProjectCollaboration.objects.filter(
        from_user=request.user
    ).select_related('project__owner', 'project').order_by('-created_at')

    return render(request, 'proposals.html', {
        'incoming_proposals': incoming_proposals,
        'incoming_collabs':   incoming_collabs,
        'sent_proposals':     sent_proposals,
        'sent_collabs':       sent_collabs,
        'pending_proposals':  incoming_proposals.filter(status='pending').count(),
        'pending_collabs':    incoming_collabs.filter(status='pending').count(),
    })

# --- connections ---
@login_required
def accept_connection(request, conn_id):
    from .models import Connection
    conn = get_object_or_404(Connection, pk=conn_id)
    if request.method == 'POST' and conn.target == request.user:
        conn.status = 'accepted'
        conn.save()
        conn.initiator.connected_users.add(request.user)
        request.user.connected_users.add(conn.initiator)
        messages.success(request, 'Connection accepted.')
    return redirect('notifications')

@login_required
def reject_connection(request, conn_id):
    from .models import Connection
    conn = get_object_or_404(Connection, pk=conn_id)
    if request.method == 'POST' and conn.target == request.user:
        conn.delete()
        messages.info(request, 'Connection declined.')
    return redirect('notifications')

# --- comments ---
@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if request.method == 'POST' and (comment.user == request.user or request.user.user_type == 'admin'):
        comment.delete()
        messages.success(request, 'Comment deleted.')
    return redirect(request.META.get('HTTP_REFERER', 'app'))

@login_required
def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if request.method == 'POST' and comment.user == request.user:
        comment.content = request.POST.get('content', comment.content)
        comment.save()
        messages.success(request, 'Comment updated.')
    return redirect(request.META.get('HTTP_REFERER', 'app'))

# --- chat message edit / delete (AJAX, soft operations) ---
@login_required
def chat_share_to_feed(request):
    """Share a chat message text as a new feed post."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    import json as _json
    body = _json.loads(request.body)
    content = body.get('content', '').strip()
    post_type = body.get('post_type', 'update')
    if not content:
        return JsonResponse({'error': 'Content required'}, status=400)
    from .models import Post
    title = content.split('\n')[0][:120] or 'Shared'
    post = Post.objects.create(
        user=request.user,
        title=title,
        content=content,
        post_type=post_type,
        industry=getattr(getattr(request.user, 'userprofile', None), 'industry', None) or 'tech',
    )
    return JsonResponse({'ok': True, 'post_id': post.id})


@login_required
def chat_delete_message(request, message_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    msg = get_object_or_404(Message, pk=message_id)
    if msg.sender != request.user:
        return JsonResponse({'error': 'Not allowed'}, status=403)
    msg.is_deleted = True
    msg.content = ''
    msg.save(update_fields=['is_deleted', 'content'])
    return JsonResponse({'ok': True, 'message_id': msg.id})


@login_required
def chat_edit_message(request, message_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    msg = get_object_or_404(Message, pk=message_id)
    if msg.sender != request.user:
        return JsonResponse({'error': 'Not allowed'}, status=403)
    if msg.is_deleted:
        return JsonResponse({'error': 'Cannot edit deleted message'}, status=400)
    import json as _json
    body = _json.loads(request.body)
    new_content = body.get('content', '').strip()
    if not new_content:
        return JsonResponse({'error': 'Content required'}, status=400)
    from django.utils import timezone
    msg.content = new_content
    msg.is_edited = True
    msg.edited_at = timezone.now()
    msg.save(update_fields=['content', 'is_edited', 'edited_at'])
    return JsonResponse({'ok': True, 'message_id': msg.id, 'content': msg.content})


# --- messages ---
@login_required
def delete_message(request, message_id):
    msg = get_object_or_404(Message, pk=message_id)
    if request.method == 'POST' and (msg.sender == request.user or msg.recipient == request.user):
        msg.delete()
        messages.success(request, 'Message deleted.')
    return redirect('inbox')

@login_required
def message_detail(request, message_id):
    msg = get_object_or_404(Message, pk=message_id)
    return render(request, 'messages/message_detail.html', {'message': msg})

# --- contact submissions ---
@login_required
@login_required
def contact_submissions(request):
    if request.user.user_type != 'admin':
        return redirect('app')
    from .models import ContactSubmission
    submissions = ContactSubmission.objects.all()
    return render(request, 'contact_submissions.html', {'submissions': submissions})


@login_required
def reply_contact_submission(request, sub_id):
    if request.user.user_type != 'admin':
        return redirect('app')
    if request.method != 'POST':
        return redirect('contact_submissions')

    from django.utils import timezone
    from .models import ContactSubmission
    submission = get_object_or_404(ContactSubmission, pk=sub_id)
    reply_text = request.POST.get('reply_text', '').strip()

    if reply_text:
        SENDER_EMAILS = ["info@odumacorp.com", "odumacorp@gmail.com"]
        sent = False
        for sender in SENDER_EMAILS:
            try:
                send_mail(
                    subject=f"Re: {submission.subject or submission.topic} — Oduma Corp",
                    message=reply_text,
                    from_email=sender,
                    recipient_list=[submission.email],
                )
                sent = True
                break
            except Exception as e:
                logger.warning(f"Reply email failed from {sender}: {e}")
        if sent:
            submission.is_replied  = True
            submission.replied_at  = timezone.now()
            submission.admin_reply = reply_text
            submission.save()
            messages.success(request, f"Reply sent to {submission.email}.")
        else:
            messages.error(request, "Failed to send the reply email. Please try again.")
    else:
        messages.error(request, "Reply message cannot be empty.")

    return redirect('contact_submissions')

# --- admin view mode toggle ---
@login_required
def toggle_admin_view(request):
    """Lets admin switch between 'admin' and 'user' view modes."""
    if request.user.user_type != 'admin':
        return redirect('app')
    current = request.session.get('admin_view_mode', 'admin')
    request.session['admin_view_mode'] = 'user' if current == 'admin' else 'admin'
    return redirect(request.META.get('HTTP_REFERER', 'app'))

# --- admin panel ---
@login_required
def admin_panel(request):
    if not request.user.is_authenticated or request.user.user_type != 'admin':
        return redirect('app')

    import json as _json
    from django.utils import timezone as _tz
    from django.db.models import Count, Avg, OuterRef, Subquery
    from .models import (
        CustomUser, Project, Post, Company, ShareEvent, SurveyResponse,
        Notification, Message, Connection, Event, EventRegistration,
        NewsItem, Job, JobApplication, ContactSubmission, AttachmentDownload,
        Group, Page, ProjectComment, Comment, ProjectCollaboration, Rating,
        AdminPermissions, StageProgressionRequest, VerificationRequest,
        UserProfile,
    )

    now = _tz.now()
    today_start     = now.replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday_start = today_start - _tz.timedelta(days=1)
    week_start      = today_start - _tz.timedelta(days=7)
    month_start     = today_start - _tz.timedelta(days=30)
    quarter_start   = today_start - _tz.timedelta(days=90)
    half_start      = today_start - _tz.timedelta(days=180)
    year_start      = today_start - _tz.timedelta(days=365)

    # ── Users (annotated) ────────────────────────────────────────────
    users = (
        CustomUser.objects
        .annotate(
            project_count=Count('projects', distinct=True),
            conn_initiated=Count('initiated_connections', distinct=True),
            conn_received=Count('received_connections', distinct=True),
        )
        .order_by('-date_joined')
    )

    # ── Top connected users ──────────────────────────────────────────
    top_connected = list(
        CustomUser.objects
        .annotate(
            initiated=Count('initiated_connections', distinct=True),
            received=Count('received_connections', distinct=True),
        )
        .order_by('-initiated')[:10]
    )
    for u in top_connected:
        u.total = u.initiated + u.received
    top_connected.sort(key=lambda u: u.total, reverse=True)

    # ── Projects ─────────────────────────────────────────────────────
    projects = Project.objects.select_related('owner').order_by('-created_at')

    # ── Posts ────────────────────────────────────────────────────────
    posts = Post.objects.select_related('user').order_by('-created_at')

    # ── Messages ─────────────────────────────────────────────────────
    messages_list    = Message.objects.select_related('sender', 'recipient').order_by('-timestamp')[:200]
    flagged_messages = Message.objects.filter(is_flagged=True).select_related('sender', 'recipient', 'flagged_by').order_by('-timestamp')

    # ── Events (annotate attendee_count) ─────────────────────────────
    events = (
        Event.objects
        .annotate(attendee_count=Count('registrations', distinct=True))
        .order_by('-date')
    )

    # ── News ─────────────────────────────────────────────────────────
    news_items = NewsItem.objects.order_by('-created_at')

    # ── Jobs + Applications ──────────────────────────────────────────
    jobs             = Job.objects.order_by('-created_at')
    job_applications = JobApplication.objects.select_related('applicant', 'job').order_by('-applied_at')

    # ── Connections ──────────────────────────────────────────────────
    connections = Connection.objects.select_related('initiator', 'target').order_by('-created_at')[:200]

    # ── Comments ─────────────────────────────────────────────────────
    project_comments = ProjectComment.objects.select_related('user', 'project').order_by('-created_at')[:200]
    post_comments    = Comment.objects.select_related('user', 'post').order_by('-created_at')[:200]

    # ── Collaborations ───────────────────────────────────────────────
    collaborations = ProjectCollaboration.objects.select_related('from_user', 'project').order_by('-created_at')[:200]

    # ── Ratings ──────────────────────────────────────────────────────
    ratings = Rating.objects.select_related('user', 'project').order_by('-id')[:200]

    # ── Contact submissions ──────────────────────────────────────────
    contact_submissions = ContactSubmission.objects.order_by('-submitted_at')

    # ── Attachment downloads ─────────────────────────────────────────
    attachment_downloads = AttachmentDownload.objects.select_related(
        'downloaded_by', 'attachment', 'attachment__project', 'attachment__project__owner'
    ).order_by('-downloaded_at')[:200]

    # ── Groups ───────────────────────────────────────────────────────
    groups = Group.objects.select_related('creator').order_by('-created_at')

    # ── Pages ────────────────────────────────────────────────────────
    pages = Page.objects.select_related('owner').order_by('-created_at')

    # ── Sub-admins ───────────────────────────────────────────────────
    admin_users = CustomUser.objects.filter(user_type='admin').exclude(id=request.user.id)
    sub_admins = []
    for sa in admin_users:
        try:
            perms = sa.admin_permissions
        except AdminPermissions.DoesNotExist:
            perms = None
        sub_admins.append((sa, perms))

    # ── Notifications ────────────────────────────────────────────────
    recent_notifications = Notification.objects.select_related('user').order_by('-created_at')[:100]

    # ── Survey ───────────────────────────────────────────────────────
    survey_qs = SurveyResponse.objects.all()
    survey_total = survey_qs.count()
    survey_avg = survey_qs.aggregate(
        avg_ui=Avg('ui_design'),
        avg_ux=Avg('ux_navigation'),
        avg_usability=Avg('usability_tasks'),
        avg_satisfaction=Avg('exp_satisfaction'),
    )
    survey = {
        'total': survey_total,
        'avg_ui': round(survey_avg['avg_ui'] or 0, 1),
        'avg_ux': round(survey_avg['avg_ux'] or 0, 1),
        'avg_usability': round(survey_avg['avg_usability'] or 0, 1),
        'avg_satisfaction': round(survey_avg['avg_satisfaction'] or 0, 1),
        'recent': survey_qs.order_by('-submitted_at')[:50],
    }

    # ── Share stats ──────────────────────────────────────────────────
    by_platform_qs = ShareEvent.objects.values('platform').annotate(total=Count('id'))
    by_platform    = {row['platform']: row['total'] for row in by_platform_qs}
    by_type_qs     = ShareEvent.objects.values('share_type').annotate(total=Count('id'))
    by_type        = {row['share_type']: row['total'] for row in by_type_qs}

    PLATFORM_ORDER  = ['whatsapp', 'telegram', 'twitter', 'facebook', 'linkedin', 'copy_link', 'instagram', 'other']
    PLATFORM_LABELS = {'whatsapp':'WhatsApp','telegram':'Telegram','twitter':'X / Twitter',
                       'facebook':'Facebook','linkedin':'LinkedIn','copy_link':'Copy Link',
                       'instagram':'Instagram','other':'Other'}
    platform_labels = [PLATFORM_LABELS.get(p, p.title()) for p in PLATFORM_ORDER if by_platform.get(p, 0) > 0]
    platform_data   = [by_platform.get(p, 0) for p in PLATFORM_ORDER if by_platform.get(p, 0) > 0]
    for k, v in by_platform.items():
        if k not in PLATFORM_ORDER:
            platform_labels.append(k.title())
            platform_data.append(v)

    type_labels, type_data = [], []
    for key, label in [('individual','Individual / DM'), ('group','Group'), ('general','General')]:
        if by_type.get(key, 0) > 0:
            type_labels.append(label)
            type_data.append(by_type[key])

    shares = {
        'total':           ShareEvent.objects.count(),
        'by_platform':     by_platform,
        'groups':          by_type.get('group', 0),
        'individuals':     by_type.get('individual', 0),
        'recent':          ShareEvent.objects.select_related('shared_by').order_by('-shared_at')[:50],
        'by_type':         by_type,
        'platform_labels': _json.dumps(platform_labels),
        'platform_data':   _json.dumps(platform_data),
        'type_labels':     _json.dumps(type_labels),
        'type_data':       _json.dumps(type_data),
    }

    # ── Totals ───────────────────────────────────────────────────────
    total_users               = CustomUser.objects.count()
    total_projects            = Project.objects.count()
    total_posts               = Post.objects.count()
    total_messages            = Message.objects.count()
    total_unread              = Message.objects.filter(is_read=False).count()
    total_connections         = Connection.objects.filter(status='accepted').count()
    total_pending_connections = Connection.objects.filter(status='pending').count()
    total_comments            = (ProjectComment.objects.count() + Comment.objects.count())
    total_collaborations      = ProjectCollaboration.objects.count()
    total_ratings             = Rating.objects.count()
    total_job_applications    = JobApplication.objects.count()
    total_contact_submissions = ContactSubmission.objects.count()
    total_downloads           = AttachmentDownload.objects.count()
    total_groups              = Group.objects.count()
    total_pages               = Page.objects.count()
    total_events              = Event.objects.count()
    total_news                = NewsItem.objects.count()
    total_jobs                = Job.objects.count()
    total_notifications       = Notification.objects.count()
    total_admins              = CustomUser.objects.filter(user_type='admin').count()

    # ── Growth stats JSON (for dashboard period filter) ───────────────
    def _growth(qs, field='date_joined'):
        return {
            'today': qs.filter(**{f'{field}__gte': today_start}).count(),
            'week':  qs.filter(**{f'{field}__gte': week_start}).count(),
            'month': qs.filter(**{f'{field}__gte': month_start}).count(),
            'all':   qs.count(),
        }

    def _gs(cutoff):
        kw = lambda f, **extra: {f + '__gte': cutoff, **extra}
        return {
            'users':       CustomUser.objects.filter(**kw('date_joined')).count(),
            'innovators':  CustomUser.objects.filter(**kw('date_joined', user_type='innovator')).count(),
            'investors':   CustomUser.objects.filter(**kw('date_joined', user_type='investor')).count(),
            'projects':    Project.objects.filter(**kw('created_at')).count(),
            'posts':       Post.objects.filter(**kw('created_at')).count(),
            'groups':      Group.objects.filter(**kw('created_at')).count(),
            'pages':       Page.objects.filter(**kw('created_at')).count(),
            'connections': Connection.objects.filter(**kw('created_at', status='accepted')).count(),
            'messages':    Message.objects.filter(**kw('timestamp')).count(),
        }

    growth_stats = {
        'today':     _gs(today_start),
        'yesterday': _gs(yesterday_start),
        'week':      _gs(week_start),
        'month':     _gs(month_start),
        'quarter':   _gs(quarter_start),
        'half':      _gs(half_start),
        'year':      _gs(year_start),
        'all': {
            'users':       total_users,
            'innovators':  CustomUser.objects.filter(user_type='innovator').count(),
            'investors':   CustomUser.objects.filter(user_type='investor').count(),
            'projects':    total_projects,
            'posts':       total_posts,
            'groups':      total_groups,
            'pages':       total_pages,
            'connections': total_connections,
            'messages':    total_messages,
        },
    }

    pending_stage_count        = StageProgressionRequest.objects.filter(status='pending').count()
    pending_verification_count = VerificationRequest.objects.filter(status='pending').count()
    pending_review_count       = Project.objects.filter(review_status='under_review').count()

    # ── User locations for map ─────────────────────────────────────────
    location_qs = (
        UserProfile.objects
        .exclude(location='')
        .values('location', 'user_type')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    location_summary = {}
    for row in location_qs:
        loc = row['location'].strip()
        if not loc:
            continue
        if loc not in location_summary:
            location_summary[loc] = {'total': 0, 'innovators': 0, 'investors': 0}
        location_summary[loc]['total'] += row['count']
        if row['user_type'] == 'innovator':
            location_summary[loc]['innovators'] += row['count']
        elif row['user_type'] == 'investor':
            location_summary[loc]['investors'] += row['count']
    location_list = sorted(location_summary.items(), key=lambda x: -x[1]['total'])
    locations_json = _json.dumps([
        {'location': loc, **data} for loc, data in location_list
    ])
    total_with_location = sum(d['total'] for _, d in location_list)

    return render(request, 'admin_panel.html', {
        # core data
        'users':               users,
        'projects':            projects,
        'posts':               posts,
        'messages_list':       messages_list,
        'flagged_messages':    flagged_messages,
        'events':              events,
        'news_items':          news_items,
        'jobs':                jobs,
        'job_applications':    job_applications,
        'connections':         connections,
        'project_comments':    project_comments,
        'post_comments':       post_comments,
        'collaborations':      collaborations,
        'ratings':             ratings,
        'contact_submissions': contact_submissions,
        'attachment_downloads':attachment_downloads,
        'groups':              groups,
        'pages':               pages,
        'sub_admins':          sub_admins,
        'recent_notifications':recent_notifications,
        'survey':              survey,
        'shares':              shares,
        'top_connected':       top_connected,
        'growth_stats_json':   _json.dumps(growth_stats),
        # totals
        'total_users':               total_users,
        'total_projects':            total_projects,
        'total_posts':               total_posts,
        'total_messages':            total_messages,
        'total_unread':              total_unread,
        'total_connections':         total_connections,
        'total_pending_connections': total_pending_connections,
        'total_comments':            total_comments,
        'total_collaborations':      total_collaborations,
        'total_ratings':             total_ratings,
        'total_job_applications':    total_job_applications,
        'total_contact_submissions': total_contact_submissions,
        'total_downloads':           total_downloads,
        'total_groups':              total_groups,
        'total_pages':               total_pages,
        'total_events':              total_events,
        'total_news':                total_news,
        'total_jobs':                total_jobs,
        'total_notifications':       total_notifications,
        'total_admins':              total_admins,
        # pending queues
        'pending_stage_count':        pending_stage_count,
        'pending_verification_count': pending_verification_count,
        'pending_review_count':       pending_review_count,
        # location map
        'locations_json':        locations_json,
        'location_list':         location_list,
        'total_with_location':   total_with_location,
        'page_name': 'Admin Panel',
    })

def _admin_post_redirect(request):
    return redirect(request.META.get('HTTP_REFERER', 'admin_panel'))


@login_required
def admin_stats_range(request):
    """AJAX endpoint: returns growth stats for a custom date range."""
    if request.user.user_type != 'admin':
        return JsonResponse({'error': 'Forbidden'}, status=403)
    from django.utils import timezone as _tz
    from .models import (
        CustomUser, Project, Post, Group, Page, Connection, Message,
    )
    import json as _json
    from datetime import datetime
    from_str = request.GET.get('from', '')
    to_str   = request.GET.get('to', '')
    try:
        from_dt = datetime.strptime(from_str, '%Y-%m-%d')
        to_dt   = datetime.strptime(to_str,   '%Y-%m-%d').replace(hour=23, minute=59, second=59)
        from_dt = _tz.make_aware(from_dt)
        to_dt   = _tz.make_aware(to_dt)
    except (ValueError, TypeError):
        return JsonResponse({'error': 'Invalid dates. Use YYYY-MM-DD.'}, status=400)

    def _r(f, **extra):
        return {f + '__range': (from_dt, to_dt), **extra}

    data = {
        'users':       CustomUser.objects.filter(**_r('date_joined')).count(),
        'innovators':  CustomUser.objects.filter(**_r('date_joined', user_type='innovator')).count(),
        'investors':   CustomUser.objects.filter(**_r('date_joined', user_type='investor')).count(),
        'projects':    Project.objects.filter(**_r('created_at')).count(),
        'posts':       Post.objects.filter(**_r('created_at')).count(),
        'groups':      Group.objects.filter(**_r('created_at')).count(),
        'pages':       Page.objects.filter(**_r('created_at')).count(),
        'connections': Connection.objects.filter(**_r('created_at', status='accepted')).count(),
        'messages':    Message.objects.filter(**_r('timestamp')).count(),
    }
    return JsonResponse(data)

@login_required
def admin_add_event(request):
    return _admin_post_redirect(request)

@login_required
def admin_add_job(request):
    return _admin_post_redirect(request)

@login_required
def admin_add_news(request):
    return _admin_post_redirect(request)

@login_required
def admin_add_sub_admin(request):
    return _admin_post_redirect(request)

@login_required
def admin_broadcast_notification(request):
    return _admin_post_redirect(request)

@login_required
def admin_change_project_status(request, project_id):
    return _admin_post_redirect(request)

@login_required
def admin_change_role(request, user_id):
    from django.http import JsonResponse
    if request.user.user_type != 'admin':
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'ok': False, 'error': 'Forbidden'}, status=403)
        return redirect('app')
    user_obj = get_object_or_404(CustomUser, pk=user_id)
    new_role = request.POST.get('role', '')
    if new_role in ('innovator', 'investor', 'admin') and user_obj != request.user:
        user_obj.user_type = new_role
        user_obj.save(update_fields=['user_type'])
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'ok': True, 'role': user_obj.user_type})
    return _admin_post_redirect(request)

@login_required
def admin_edit_comment(request, comment_id):
    return _admin_post_redirect(request)

@login_required
def admin_edit_event(request, event_id):
    return _admin_post_redirect(request)

@login_required
def admin_edit_group(request, group_id):
    return _admin_post_redirect(request)

@login_required
def admin_edit_job(request, job_id):
    return _admin_post_redirect(request)

@login_required
def admin_edit_message(request, message_id):
    return _admin_post_redirect(request)

@login_required
def admin_edit_news(request, news_id):
    return _admin_post_redirect(request)

@login_required
def admin_edit_page(request, page_id):
    return _admin_post_redirect(request)

@login_required
def admin_edit_post(request, post_id):
    return _admin_post_redirect(request)

@login_required
def admin_edit_project(request, project_id):
    return _admin_post_redirect(request)

@login_required
def admin_event_attendees(request, event_id):
    return _admin_post_redirect(request)

@login_required
def admin_flag_message(request, message_id):
    return _admin_post_redirect(request)

@login_required
def admin_manage_sub_admin(request, user_id):
    return _admin_post_redirect(request)

@login_required
def admin_reset_user_password(request, user_id):
    return _admin_post_redirect(request)

@login_required
def admin_set_user_password(request, user_id):
    return _admin_post_redirect(request)

@login_required
def admin_toggle_hide_comment(request, comment_id):
    return _admin_post_redirect(request)

@login_required
def admin_toggle_hide_event(request, event_id):
    return _admin_post_redirect(request)

@login_required
def admin_toggle_hide_group(request, group_id):
    return _admin_post_redirect(request)

@login_required
def admin_toggle_hide_job(request, job_id):
    return _admin_post_redirect(request)

@login_required
def admin_toggle_hide_message(request, message_id):
    return _admin_post_redirect(request)

@login_required
def admin_toggle_hide_news(request, news_id):
    return _admin_post_redirect(request)

@login_required
def admin_toggle_hide_page(request, page_id):
    return _admin_post_redirect(request)

@login_required
def admin_toggle_hide_post(request, post_id):
    return _admin_post_redirect(request)

@login_required
def admin_toggle_hide_post_comment(request, comment_id):
    return _admin_post_redirect(request)

@login_required
def admin_toggle_hide_project(request, project_id):
    return _admin_post_redirect(request)

@login_required
def admin_toggle_hide_user(request, user_id):
    from django.http import JsonResponse
    if request.user.user_type != 'admin':
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'ok': False, 'error': 'Forbidden'}, status=403)
        return redirect('app')
    user_obj = get_object_or_404(CustomUser, pk=user_id)
    if user_obj != request.user:
        user_obj.is_hidden = not user_obj.is_hidden
        user_obj.save(update_fields=['is_hidden'])
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'ok': True, 'is_hidden': user_obj.is_hidden})
    return _admin_post_redirect(request)

@login_required
def admin_toggle_user(request, user_id):
    from django.http import JsonResponse
    if request.user.user_type != 'admin':
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'ok': False, 'error': 'Forbidden'}, status=403)
        return redirect('app')
    user_obj = get_object_or_404(CustomUser, pk=user_id)
    if user_obj != request.user:
        user_obj.is_active = not user_obj.is_active
        user_obj.save(update_fields=['is_active'])
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'ok': True, 'is_active': user_obj.is_active})
    return _admin_post_redirect(request)

@login_required
def admin_unflag_message(request, message_id):
    return _admin_post_redirect(request)

# ── Admin delete views ─────────────────────────────────────────────────────────
@login_required
def admin_delete_user(request, user_id):
    if request.method == 'POST':
        from .models import CustomUser
        user_obj = get_object_or_404(CustomUser, pk=user_id)
        if user_obj != request.user:
            user_obj.delete()
    return redirect('admin_panel')

@login_required
def admin_delete_project(request, project_id):
    if request.method == 'POST':
        from .models import Project
        get_object_or_404(Project, pk=project_id).delete()
    return redirect('admin_panel')

@login_required
def admin_delete_post(request, post_id):
    if request.method == 'POST':
        from .models import Post
        get_object_or_404(Post, pk=post_id).delete()
    return redirect('admin_panel')

@login_required
def admin_delete_event(request, event_id):
    if request.method == 'POST':
        from .models import Event
        get_object_or_404(Event, pk=event_id).delete()
    return redirect('admin_panel')

@login_required
def admin_delete_news(request, news_id):
    if request.method == 'POST':
        from .models import NewsItem
        get_object_or_404(NewsItem, pk=news_id).delete()
    return redirect('admin_panel')

@login_required
def admin_delete_job(request, job_id):
    if request.method == 'POST':
        from .models import Job
        get_object_or_404(Job, pk=job_id).delete()
    return redirect('admin_panel')

@login_required
def admin_accept_connection(request, connection_id):
    if not (request.user.is_superuser or request.user.is_staff or getattr(request.user, 'user_type', '') == 'admin'):
        messages.error(request, 'Permission denied.')
        return redirect('admin_panel')
    if request.method == 'POST':
        from .models import Connection
        conn = get_object_or_404(Connection, pk=connection_id, status='pending')
        conn.status = 'accepted'
        conn.save()
        conn.initiator.connected_users.add(conn.target)
        conn.target.connected_users.add(conn.initiator)
        messages.success(request, f'Connection between {conn.initiator.get_full_name() or conn.initiator.username} and {conn.target.get_full_name() or conn.target.username} accepted.')
    return redirect('admin_panel')

@login_required
def admin_delete_connection(request, connection_id):
    if request.method == 'POST':
        from .models import Connection
        get_object_or_404(Connection, pk=connection_id).delete()
    return redirect('admin_panel')

@login_required
def admin_delete_comment(request, comment_id):
    if request.method == 'POST':
        from .models import Comment
        get_object_or_404(Comment, pk=comment_id).delete()
    return redirect('admin_panel')

@login_required
def admin_delete_group(request, group_id):
    if request.method == 'POST':
        from .models import Group
        get_object_or_404(Group, pk=group_id).delete()
    return redirect('admin_panel')

@login_required
def admin_delete_page(request, page_id):
    if request.method == 'POST':
        from .models import Page
        get_object_or_404(Page, pk=page_id).delete()
    return redirect('admin_panel')

@login_required
def admin_remove_sub_admin(request, user_id):
    if request.method == 'POST':
        from .models import CustomUser
        user_obj = get_object_or_404(CustomUser, pk=user_id)
        user_obj.user_type = 'innovator'
        user_obj.save(update_fields=['user_type'])
    return redirect('admin_panel')


# ── Site Content Management ────────────────────────────────────────

_MANAGED_PAGES = [
    ('jobs',              'Jobs Board'),
    ('events_hub',        'Events Hub'),
    ('events',            'Events (Legacy)'),
    ('training_hub',      'Training & Courses'),
    ('mentorship_hub',    'Mentorship Hub'),
    ('companies_list',    'Businesses / Companies'),
    ('groups_list',       'Community Groups'),
    ('proposals_list',    'Proposals'),
    ('search',            'Search'),
    ('about',             'About Us'),
    ('faq',               'FAQ'),
    ('contact',           'Contact'),
    ('services',          'Consulting Services'),
    ('subscription_plans','Pricing & Plans'),
    ('innovators',        'Browse Innovators'),
    ('investors',         'Find Investors'),
    ('blog_list',         'Blog'),
]


def _ensure_site_pages():
    from .models import SitePage
    for key, label in _MANAGED_PAGES:
        SitePage.objects.get_or_create(key=key, defaults={'label': label, 'is_active': True})


@login_required
def admin_content(request):
    if request.user.user_type != 'admin':
        return redirect('app')
    from .models import SiteSettings, Announcement, BlogPost, SitePage
    _ensure_site_pages()
    site_settings  = SiteSettings.get()
    announcements  = Announcement.objects.order_by('-created_at')
    blogs          = BlogPost.objects.order_by('-created_at')
    site_pages     = SitePage.objects.order_by('label')
    return render(request, 'admin_content.html', {
        'site_settings': site_settings,
        'announcements': announcements,
        'blogs':         blogs,
        'site_pages':    site_pages,
        'page_name':     'Content Management',
    })


@login_required
def admin_save_site_settings(request):
    if request.user.user_type != 'admin':
        return redirect('app')
    if request.method == 'POST':
        from .models import SiteSettings
        s = SiteSettings.get()
        s.twitter_url    = request.POST.get('twitter_url', '').strip()
        s.linkedin_url   = request.POST.get('linkedin_url', '').strip()
        s.instagram_url  = request.POST.get('instagram_url', '').strip()
        s.facebook_url   = request.POST.get('facebook_url', '').strip()
        s.youtube_url    = request.POST.get('youtube_url', '').strip()
        s.contact_email  = request.POST.get('contact_email', '').strip()
        s.contact_phone  = request.POST.get('contact_phone', '').strip()
        s.footer_tagline = request.POST.get('footer_tagline', '').strip()
        s.updated_by     = request.user
        s.save()
        messages.success(request, 'Site settings saved.')
    return redirect('admin_content')


@login_required
def admin_save_announcement(request):
    if request.user.user_type != 'admin':
        return redirect('app')
    if request.method == 'POST':
        from .models import Announcement
        ann_id = request.POST.get('id', '').strip()
        title      = request.POST.get('title', '').strip()
        body       = request.POST.get('body', '').strip()
        ann_type   = request.POST.get('type', 'info')
        show_from  = request.POST.get('show_from', '') or None
        show_until = request.POST.get('show_until', '') or None
        is_active  = request.POST.get('is_active') == '1'
        if title:
            if ann_id:
                ann = get_object_or_404(Announcement, pk=ann_id)
            else:
                ann = Announcement(created_by=request.user)
            ann.title = title
            ann.body  = body
            ann.type  = ann_type
            ann.show_from  = show_from
            ann.show_until = show_until
            ann.is_active  = is_active
            ann.save()
            messages.success(request, 'Announcement saved.')
    return redirect('admin_content')


@login_required
def admin_delete_announcement(request, pk):
    if request.user.user_type != 'admin':
        return redirect('app')
    if request.method == 'POST':
        from .models import Announcement
        get_object_or_404(Announcement, pk=pk).delete()
    return redirect('admin_content')


@login_required
def admin_toggle_announcement(request, pk):
    if request.user.user_type != 'admin':
        return redirect('app')
    if request.method == 'POST':
        from .models import Announcement
        ann = get_object_or_404(Announcement, pk=pk)
        ann.is_active = not ann.is_active
        ann.save(update_fields=['is_active'])
    return redirect('admin_content')


@login_required
def admin_save_blog(request):
    if request.user.user_type != 'admin':
        return redirect('app')
    if request.method == 'POST':
        from .models import BlogPost
        from django.utils.text import slugify
        from django.utils import timezone as _tz
        blog_id    = request.POST.get('id', '').strip()
        title      = request.POST.get('title', '').strip()
        excerpt    = request.POST.get('excerpt', '').strip()
        body       = request.POST.get('body', '').strip()
        is_pub     = request.POST.get('is_published') == '1'
        cover      = request.FILES.get('cover_image')
        if title:
            if blog_id:
                blog = get_object_or_404(BlogPost, pk=blog_id)
            else:
                blog = BlogPost(author=request.user)
                blog.slug = slugify(title)[:320]
                # ensure unique slug
                base_slug = blog.slug
                n = 1
                while BlogPost.objects.filter(slug=blog.slug).exists():
                    blog.slug = f'{base_slug}-{n}'
                    n += 1
            blog.title   = title
            blog.excerpt = excerpt
            blog.body    = body
            if cover:
                blog.cover_image = cover
            if is_pub and not blog.published_at:
                blog.published_at = _tz.now()
            blog.is_published = is_pub
            blog.save()
            messages.success(request, 'Blog post saved.')
    return redirect('admin_content')


@login_required
def admin_delete_blog(request, pk):
    if request.user.user_type != 'admin':
        return redirect('app')
    if request.method == 'POST':
        from .models import BlogPost
        get_object_or_404(BlogPost, pk=pk).delete()
    return redirect('admin_content')


@login_required
def admin_toggle_blog(request, pk):
    if request.user.user_type != 'admin':
        return redirect('app')
    if request.method == 'POST':
        from .models import BlogPost
        from django.utils import timezone as _tz
        blog = get_object_or_404(BlogPost, pk=pk)
        blog.is_published = not blog.is_published
        if blog.is_published and not blog.published_at:
            blog.published_at = _tz.now()
        blog.save(update_fields=['is_published', 'published_at'])
    return redirect('admin_content')


@login_required
def admin_toggle_site_page(request, pk):
    if request.user.user_type != 'admin':
        return redirect('app')
    if request.method == 'POST':
        from .models import SitePage
        page = get_object_or_404(SitePage, pk=pk)
        page.is_active  = not page.is_active
        page.updated_by = request.user
        page.save(update_fields=['is_active', 'updated_by', 'updated_at'])
    return redirect('admin_content')


@login_required
def admin_save_site_page(request, pk):
    if request.user.user_type != 'admin':
        return redirect('app')
    if request.method == 'POST':
        from .models import SitePage
        page = get_object_or_404(SitePage, pk=pk)
        page.disabled_message = request.POST.get('disabled_message', '').strip()
        page.updated_by = request.user
        page.save(update_fields=['disabled_message', 'updated_by', 'updated_at'])
    return redirect('admin_content')


def blog_list(request):
    from .models import BlogPost
    blogs = BlogPost.objects.filter(is_published=True).order_by('-published_at')
    return render(request, 'blog_list.html', {'blogs': blogs})


def blog_detail(request, slug):
    from .models import BlogPost
    blog = get_object_or_404(BlogPost, slug=slug, is_published=True)
    return render(request, 'blog_detail.html', {'blog': blog})


# --- companies / businesses ---
def companies_list(request):
    from .models import Company
    from django.db.models import Count, Q
    q             = request.GET.get('q', '').strip()
    industry_filter = request.GET.get('industry', '')
    date_sort     = request.GET.get('date_sort', 'newest')
    owner_filter  = request.GET.get('owner_id', '')

    base_qs = Company.objects.all()
    qs = base_qs
    if industry_filter:
        qs = qs.filter(industry=industry_filter)
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(tagline__icontains=q) | Q(description__icontains=q))
    if owner_filter:
        qs = qs.filter(owner_id=owner_filter)

    order = 'created_at' if date_sort == 'oldest' else '-created_at'
    companies = qs.order_by(order)

    counts_qs = base_qs.values('industry').annotate(cnt=Count('id'))
    industry_counts = {r['industry']: r['cnt'] for r in counts_qs}

    user_company = None
    my_companies = []
    rl_company_ids = set()
    company_owners = []
    if request.user.is_authenticated:
        user_company = Company.objects.filter(owner=request.user).first()
        my_companies = list(Company.objects.filter(owner=request.user).order_by('-created_at'))
        # Exclude user's own companies from the all-companies list
        companies = companies.exclude(owner=request.user)
        from .models import ReadLater
        rl_company_ids = set(
            ReadLater.objects.filter(user=request.user, company__isnull=False)
            .values_list('company_id', flat=True)
        )
        # Owners for the filter dropdown (exclude current user since they have their own tab)
        owner_ids = Company.objects.exclude(owner=request.user).values_list('owner_id', flat=True).distinct()
    else:
        owner_ids = Company.objects.values_list('owner_id', flat=True).distinct()

    from django.contrib.auth import get_user_model
    _User = get_user_model()
    company_owners = list(
        _User.objects.filter(pk__in=owner_ids)
             .order_by('first_name', 'last_name')
             .values('pk', 'first_name', 'last_name', 'username')
    )

    return render(request, 'companies.html', {
        'companies': companies,
        'my_companies': my_companies,
        'industry_counts': industry_counts,
        'selected_industry': industry_filter,
        'industry': industry_filter,
        'industry_choices': Company.INDUSTRY_CHOICES,
        'q': q,
        'date_sort': date_sort,
        'owner_filter': owner_filter,
        'company_owners': company_owners,
        'user_company': user_company,
        'rl_company_ids': rl_company_ids,
    })


@login_required
def company_profile(request, company_id):
    from .models import Company, CompanyMedia, CompanyUpdate
    company     = get_object_or_404(Company, pk=company_id)
    media_items = CompanyMedia.objects.filter(company=company).order_by('-uploaded_at')
    updates     = CompanyUpdate.objects.filter(company=company).order_by('-created_at')
    is_following = company.followers.filter(id=request.user.id).exists()
    is_owner     = company.owner == request.user
    # Read Later status
    is_saved = False
    if request.user.is_authenticated:
        from .models import ReadLater
        is_saved = ReadLater.objects.filter(user=request.user, company=company).exists()
    return render(request, 'company_profile.html', {
        'company': company, 'media_items': media_items, 'updates': updates,
        'is_following': is_following, 'is_owner': is_owner, 'is_saved': is_saved,
    })


@login_required
def company_edit(request, company_id):
    from .models import Company
    company = get_object_or_404(Company, pk=company_id)
    if company.owner != request.user:
        messages.error(request, 'Permission denied.')
        return redirect('company_profile', company_id=company_id)
    if request.method == 'POST':
        for field in ('name','description','tagline','industry','company_type','size','location','website','email','phone'):
            val = request.POST.get(field)
            if val is not None:
                setattr(company, field, val)
        if 'logo' in request.FILES:
            company.logo = request.FILES['logo']
        if 'cover_image' in request.FILES:
            company.cover_image = request.FILES['cover_image']
        company.save()
        messages.success(request, 'Business updated.')
        return redirect('company_profile', company_id=company_id)
    return render(request, 'company_edit.html', {
        'company': company,
        'industry_choices': INDUSTRY_CHOICES,
    })


@login_required
def create_company(request):
    from .models import Company, CustomIndustry

    preset = list(Company.INDUSTRY_CHOICES)
    custom = list(CustomIndustry.objects.values_list('name', flat=True))
    preset_vals_set = {v for v, _ in preset}
    ctx = {
        'industry_choices': preset + [(n, n) for n in custom if n not in preset_vals_set],
        'type_choices': Company.COMPANY_TYPE_CHOICES,
        'size_choices': Company.SIZE_CHOICES,
    }

    if request.method == 'POST':
        from django.core.validators import URLValidator
        from django.core.validators import validate_email as _ve
        from django.core.exceptions import ValidationError as DjVE
        import re as _re

        name        = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        tagline     = request.POST.get('tagline', '').strip()
        location    = request.POST.get('location', '').strip()
        website     = request.POST.get('website', '').strip()
        email       = request.POST.get('email', '').strip()
        phone       = request.POST.get('phone', '').strip()

        field_errors = {}

        if not name:
            field_errors['name'] = 'Company name is required.'
        elif len(name) > 255:
            field_errors['name'] = 'Company name must be under 255 characters.'

        if not description:
            field_errors['description'] = 'Description is required.'

        if website:
            try:
                URLValidator()(website)
            except DjVE:
                field_errors['website'] = 'Enter a valid URL (e.g. https://yourcompany.com).'

        if email:
            try:
                _ve(email)
            except DjVE:
                field_errors['email'] = 'Enter a valid email address.'

        if phone and not _re.match(r'^\+?[\d\s\-\(\)\.]{7,20}$', phone):
            field_errors['phone'] = 'Enter a valid phone number.'

        if field_errors:
            ctx['field_errors'] = field_errors
            return render(request, 'create_company.html', ctx)

        industry_val = (request.POST.get('industry') or 'other').strip()

        if industry_val and industry_val not in preset_vals_set:
            CustomIndustry.objects.get_or_create(name=industry_val)

        company = Company(
            owner=request.user,
            name=name,
            description=description,
            tagline=tagline,
            industry=industry_val,
            company_type=request.POST.get('company_type', 'startup') or 'startup',
            size=request.POST.get('size', ''),
            location=location,
            website=website,
            email=email,
            phone=phone,
        )

        if request.FILES.get('logo'):
            company.logo = request.FILES['logo']

        if request.FILES.get('cover_image'):
            company.cover_image = request.FILES['cover_image']

        try:
            company.save()
        except Exception as e:
            messages.error(request, f'Could not create business page: {e}')
            return render(request, 'create_company.html', ctx)

        messages.success(request, 'Business page created!')
        return redirect('company_profile', company_id=company.id)

    return render(request, 'create_company.html', ctx)

@login_required
def company_follow(request, company_id):
    from .models import Company
    from django.http import JsonResponse
    company = get_object_or_404(Company, pk=company_id)
    if company.followers.filter(pk=request.user.pk).exists():
        company.followers.remove(request.user)
        following = False
    else:
        company.followers.add(request.user)
        following = True
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'following': following, 'count': company.followers.count()})
    return redirect('company_profile', company_id=company_id)


@login_required
def company_post_update(request, company_id):
    from .models import Company, CompanyUpdate
    company = get_object_or_404(Company, pk=company_id)
    if request.method == 'POST':
        upd = CompanyUpdate(company=company, author=request.user,
                            content=request.POST.get('content', ''))
        if 'image' in request.FILES:
            upd.image = request.FILES['image']
        upd.save()
        messages.success(request, 'Update posted.')
    return redirect('company_profile', company_id=company_id)


@login_required
def company_upload_media(request, company_id):
    from .models import Company, CompanyMedia
    company = get_object_or_404(Company, pk=company_id)
    if company.owner != request.user:
        messages.error(request, 'Permission denied.')
        return redirect('company_profile', company_id=company_id)
    if request.method == 'POST' and request.FILES.get('file'):
        CompanyMedia.objects.create(
            company=company, uploaded_by=request.user,
            file=request.FILES['file'],
            media_type=request.POST.get('media_type', 'image'),
            title=request.POST.get('title', ''),
            caption=request.POST.get('caption', ''),
        )
        messages.success(request, 'Media uploaded.')
    return redirect('company_profile', company_id=company_id)


@login_required
def company_delete_media(request, company_id, media_id):
    from .models import CompanyMedia, Company
    media = get_object_or_404(CompanyMedia, pk=media_id, company_id=company_id)
    company = get_object_or_404(Company, pk=company_id)
    if media.uploaded_by == request.user or company.owner == request.user:
        media.delete()
    return redirect('company_profile', company_id=company_id)


@login_required
def company_delete_update(request, company_id, update_id):
    from .models import CompanyUpdate
    update = get_object_or_404(CompanyUpdate, pk=update_id, company_id=company_id)
    if update.author == request.user:
        update.delete()
    return redirect('company_profile', company_id=company_id)

# --- groups ---
@login_required
def groups_list(request):
    from .models import Group, GroupMembership, CustomIndustry
    my_groups    = []
    other_groups = []
    pending_invites = []
    if request.user.is_authenticated:
        my_groups = Group.objects.filter(members=request.user, is_hidden=False).order_by('-created_at')
        other_groups = Group.objects.exclude(members=request.user).filter(is_hidden=False).order_by('-created_at')
        pending_invites = GroupMembership.objects.filter(
            user=request.user, status='invited'
        ).select_related('group', 'invited_by') if hasattr(GroupMembership, 'status') else []
    else:
        other_groups = Group.objects.filter(is_hidden=False).order_by('-created_at')

    preset = list(Group.INDUSTRY_CHOICES)
    custom = list(CustomIndustry.objects.values_list('name', flat=True))
    preset_vals = {v for v, _ in preset}
    return render(request, 'groups.html', {
        'my_groups':       my_groups,
        'other_groups':    other_groups,
        'pending_invites': pending_invites,
        'industry_choices': preset + [(n, n) for n in custom if n not in preset_vals],
    })

@login_required
def group_create(request):
    from .models import Group, CustomIndustry
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if name:
            industry = request.POST.get('industry', 'other').strip()[:50]
            preset_vals = {v for v, _ in Group.INDUSTRY_CHOICES}
            if industry and industry not in preset_vals:
                CustomIndustry.objects.get_or_create(name=industry)
            group = Group.objects.create(
                name=name,
                creator=request.user,
                description=request.POST.get('description', '').strip(),
                industry=industry or 'other',
                is_private=bool(request.POST.get('is_private')),
            )
            group.members.add(request.user)
            if 'cover_image' in request.FILES:
                group.cover_image = request.FILES['cover_image']
                group.save()
            messages.success(request, f'Group "{name}" created!')
        else:
            messages.error(request, 'Group name is required.')
    return redirect('groups_list')

@login_required
def group_detail(request, group_id):
    from .models import GroupMembership, GroupDiscussion, GroupDiscussionComment
    from django.db.models import Count
    group = get_object_or_404(Group, pk=group_id)
    is_creator = group.creator == request.user

    membership = GroupMembership.objects.filter(group=group, user=request.user).first()
    is_member = membership and membership.status == 'accepted'

    # Discussions with annotated counts
    discussions = (
        GroupDiscussion.objects
        .filter(group=group)
        .annotate(
            comment_count=Count('comments', distinct=True),
            like_count=Count('likes', distinct=True),
        )
        .prefetch_related('images')
        .select_related('author')
        .order_by('-created_at')
    )

    # Trending (last 30 days)
    from django.utils import timezone
    import datetime
    cutoff = timezone.now() - datetime.timedelta(days=30)
    trending = (
        GroupDiscussion.objects
        .filter(group=group, created_at__gte=cutoff)
        .annotate(
            comment_count=Count('comments', distinct=True),
            like_count=Count('likes', distinct=True),
        )
        .order_by('-like_count', '-comment_count')[:5]
    )

    # Members list (accepted)
    members = (
        GroupMembership.objects
        .filter(group=group, status='accepted')
        .select_related('user', 'user__userprofile')
    )

    # Creator-only data
    pending_requests = []
    invitable_users = []
    if is_creator:
        pending_requests = (
            GroupMembership.objects
            .filter(group=group, status='pending')
            .select_related('user')
        )
        from .models import CustomUser
        member_ids = group.members.values_list('id', flat=True)
        invitable_users = CustomUser.objects.exclude(id__in=member_ids).order_by('first_name')

    # Stats
    stats = {
        'member_count': group.members.count(),
        'total_discussions': GroupDiscussion.objects.filter(group=group).count(),
        'total_comments': GroupDiscussionComment.objects.filter(discussion__group=group).count(),
        'invites_sent': GroupMembership.objects.filter(group=group, status='invited').count(),
        'invites_accepted': GroupMembership.objects.filter(group=group, status='accepted').count(),
        'join_requests_pending': GroupMembership.objects.filter(group=group, status='pending').count(),
    }

    return render(request, 'group_detail.html', {
        'group': group,
        'is_creator': is_creator,
        'is_member': is_member,
        'membership': membership,
        'discussions': discussions,
        'trending': trending,
        'members': members,
        'pending_requests': pending_requests,
        'invitable_users': invitable_users,
        'stats': stats,
    })

@login_required
def group_discussion_detail(request, group_id, discussion_id):
    group = get_object_or_404(Group, pk=group_id)
    return render(request, 'group_discussion.html', {'group': group, 'discussion_id': discussion_id})

@login_required
def group_discussion_media(request, group_id, discussion_id):
    group = get_object_or_404(Group, pk=group_id)
    return render(request, 'group_discussion_media.html', {'group': group, 'discussion_id': discussion_id})

@login_required
def group_discussion_react(request, group_id, discussion_id):
    return redirect(request.META.get('HTTP_REFERER', 'groups_list'))

@login_required
def group_invite(request, group_id):
    return redirect(request.META.get('HTTP_REFERER', 'groups_list'))

@login_required
def group_join_request(request, group_id):
    return redirect(request.META.get('HTTP_REFERER', 'groups_list'))

@login_required
def group_leave(request, group_id):
    return redirect('groups_list')

@login_required
def group_post_discussion(request, group_id):
    return redirect(request.META.get('HTTP_REFERER', 'groups_list'))

@login_required
def group_respond(request, group_id, member_id):
    return redirect(request.META.get('HTTP_REFERER', 'groups_list'))

@login_required
def group_accept_invite(request, group_id):
    return redirect(request.META.get('HTTP_REFERER', 'groups_list'))

@login_required
def group_comment_react(request, group_id, discussion_id, comment_id):
    return redirect(request.META.get('HTTP_REFERER', 'groups_list'))

@login_required
def group_edit(request, group_id):
    from .models import Group, CustomIndustry
    group = get_object_or_404(Group, pk=group_id)
    if group.creator != request.user:
        messages.error(request, "Only the group creator can edit this group.")
        return redirect('group_detail', group_id=group_id)
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if not name:
            messages.error(request, 'Group name is required.')
            return redirect('group_detail', group_id=group_id)
        group.name = name
        group.description = request.POST.get('description', '').strip()
        industry = request.POST.get('industry', group.industry).strip()[:50]
        preset_vals = {v for v, _ in Group.INDUSTRY_CHOICES}
        if industry and industry not in preset_vals:
            CustomIndustry.objects.get_or_create(name=industry)
        group.industry = industry or 'other'
        group.is_private = bool(request.POST.get('is_private'))
        if request.FILES.get('cover_image'):
            group.cover_image = request.FILES['cover_image']
        group.save()
        messages.success(request, 'Group updated.')
    return redirect('group_detail', group_id=group_id)


@login_required
def group_delete(request, group_id):
    from .models import Group
    group = get_object_or_404(Group, pk=group_id)
    if group.creator != request.user:
        messages.error(request, "Only the group creator can delete this group.")
        return redirect('group_detail', group_id=group_id)
    if request.method == 'POST':
        group.delete()
        messages.success(request, 'Group deleted.')
        return redirect('groups_list')
    return redirect('group_detail', group_id=group_id)


@login_required
def page_edit(request, page_id):
    from .models import Page, CustomIndustry
    pg = get_object_or_404(Page, pk=page_id)
    if pg.owner != request.user:
        messages.error(request, "Only the page owner can edit this page.")
        return redirect('page_detail', page_id=page_id)
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        if not title:
            messages.error(request, 'Page title is required.')
            return redirect('page_detail', page_id=page_id)
        pg.title = title
        pg.description = request.POST.get('description', '').strip()
        industry = request.POST.get('industry', pg.industry).strip()[:50]
        preset_vals = {v for v, _ in Page.INDUSTRY_CHOICES}
        if industry and industry not in preset_vals:
            CustomIndustry.objects.get_or_create(name=industry)
        pg.industry = industry or 'other'
        pg.website = request.POST.get('website', '').strip()
        if request.FILES.get('cover_image'):
            pg.cover_image = request.FILES['cover_image']
        if request.FILES.get('logo'):
            pg.logo = request.FILES['logo']
        pg.save()
        messages.success(request, 'Page updated.')
    return redirect('page_detail', page_id=page_id)


@login_required
def page_delete(request, page_id):
    from .models import Page
    pg = get_object_or_404(Page, pk=page_id)
    if pg.owner != request.user:
        messages.error(request, "Only the page owner can delete this page.")
        return redirect('page_detail', page_id=page_id)
    if request.method == 'POST':
        pg.delete()
        messages.success(request, 'Page deleted.')
        return redirect('pages_list')
    return redirect('page_detail', page_id=page_id)


# --- innovator page / profile ---
@login_required
def innovator_page(request):
    return redirect('innovators')

def innovator_profile(request, user_id):
    user = get_object_or_404(CustomUser, pk=user_id)
    return render(request, 'innovator_profile.html', {'viewed_user': user})

# --- businesses ---
@login_required
def my_businesses(request):
    from .models import Company
    businesses = Company.objects.filter(owner=request.user).order_by('-created_at')
    return render(request, 'my_businesses.html', {'businesses': businesses})

# --- pages ---
@login_required
def pages_list(request):
    from .models import Page, CustomIndustry
    my_pages = followed_pages = discover_pages = []
    if request.user.is_authenticated:
        my_pages       = Page.objects.filter(owner=request.user, is_hidden=False).order_by('-created_at')
        followed_pages = Page.objects.filter(followers=request.user, is_hidden=False).exclude(owner=request.user).order_by('-created_at')
        discover_pages = Page.objects.filter(is_hidden=False).exclude(owner=request.user).exclude(followers=request.user).order_by('-created_at')
    else:
        discover_pages = Page.objects.filter(is_hidden=False).order_by('-created_at')

    preset = list(Page.INDUSTRY_CHOICES)
    custom = list(CustomIndustry.objects.values_list('name', flat=True))
    preset_vals = {v for v, _ in preset}
    return render(request, 'pages.html', {
        'my_pages':       my_pages,
        'followed_pages': followed_pages,
        'discover_pages': discover_pages,
        'industry_choices': preset + [(n, n) for n in custom if n not in preset_vals],
    })

@login_required
def page_create(request):
    from .models import Page, CustomIndustry
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        if title:
            industry = request.POST.get('industry', 'other').strip()[:50]
            preset_vals = {v for v, _ in Page.INDUSTRY_CHOICES}
            if industry and industry not in preset_vals:
                CustomIndustry.objects.get_or_create(name=industry)
            page = Page.objects.create(
                owner=request.user,
                title=title,
                description=request.POST.get('description', '').strip(),
                industry=industry or 'other',
                website=request.POST.get('website', '').strip(),
            )
            if 'logo' in request.FILES:
                page.logo = request.FILES['logo']
            if 'cover_image' in request.FILES:
                page.cover_image = request.FILES['cover_image']
            page.save()
            messages.success(request, f'Page "{title}" created!')
        else:
            messages.error(request, 'Page title is required.')
    return redirect('pages_list')

@login_required
def page_detail(request, page_id):
    from .models import Page, PagePost, PagePostReaction, PagePostImage
    pg = get_object_or_404(Page, pk=page_id)
    posts = PagePost.objects.filter(page=pg).prefetch_related('post_images', 'reactions', 'shares')
    is_owner = request.user.is_authenticated and pg.owner == request.user
    is_follower = request.user.is_authenticated and pg.followers.filter(pk=request.user.pk).exists()
    user_reactions = {}
    if request.user.is_authenticated:
        for r in PagePostReaction.objects.filter(post__page=pg, user=request.user):
            user_reactions[r.post_id] = r.reaction
    # annotate counts
    for post in posts:
        post.reaction_count = post.reactions.count()
        post.share_count = post.shares.count()
    # Handle POST (owner posting)
    if request.method == 'POST' and is_owner:
        content = request.POST.get('content', '').strip()
        if content:
            new_post = PagePost.objects.create(page=pg, content=content)
            images = request.FILES.getlist('images')
            cover_index = int(request.POST.get('cover_index', 0))
            for i, img in enumerate(images[:5]):
                PagePostImage.objects.create(
                    post=new_post, image=img, is_cover=(i == cover_index), order=i
                )
        return redirect('page_detail', page_id=page_id)
    return render(request, 'page_detail.html', {
        'pg': pg,
        'posts': posts,
        'is_owner': is_owner,
        'is_follower': is_follower,
        'user_reactions': user_reactions,
    })


@login_required
def page_follow_toggle(request, page_id):
    from .models import Page
    import json
    pg = get_object_or_404(Page, pk=page_id)
    if pg.owner == request.user:
        return JsonResponse({'error': 'owner'}, status=400)
    if pg.followers.filter(pk=request.user.pk).exists():
        pg.followers.remove(request.user)
        following = False
    else:
        pg.followers.add(request.user)
        following = True
    return JsonResponse({'following': following, 'count': pg.followers.count()})


@login_required
def page_post_react(request, page_id, post_id):
    from .models import PagePost, PagePostReaction
    post = get_object_or_404(PagePost, pk=post_id, page_id=page_id)
    reaction_type = request.POST.get('reaction', 'like')
    existing = PagePostReaction.objects.filter(post=post, user=request.user).first()
    if existing:
        if existing.reaction == reaction_type:
            existing.delete()
            reacted = False
            my_reaction = None
        else:
            existing.reaction = reaction_type
            existing.save()
            reacted = True
            my_reaction = reaction_type
    else:
        PagePostReaction.objects.create(post=post, user=request.user, reaction=reaction_type)
        reacted = True
        my_reaction = reaction_type
    return JsonResponse({'reacted': reacted, 'my_reaction': my_reaction, 'total': post.reactions.count()})


@login_required
def page_post_share(request, page_id, post_id):
    from .models import PagePost, PagePostShare
    post = get_object_or_404(PagePost, pk=post_id, page_id=page_id)
    _, created = PagePostShare.objects.get_or_create(post=post, user=request.user)
    return JsonResponse({'already_shared': not created})


@login_required
def page_post_media(request, page_id, post_id):
    from .models import Page, PagePost
    pg = get_object_or_404(Page, pk=page_id, owner=request.user)
    post = get_object_or_404(PagePost, pk=post_id, page=pg)
    return render(request, 'page_post_media.html', {'pg': pg, 'post': post})

# --- posts ---
def post_detail(request, post_id):
    from .models import ReadLater
    post = get_object_or_404(Post, pk=post_id)
    comments = post.comments.filter(parent=None).select_related('user').prefetch_related('replies__user', 'replies__likes')
    user_liked = False
    user_interested = False
    user_reposted = False
    liked_comment_ids = set()
    is_saved = False
    profile = None

    if request.user.is_authenticated:
        user_liked = post.likes.filter(pk=request.user.pk).exists()
        user_interested = post.interests.filter(pk=request.user.pk).exists()
        user_reposted = post.reposts.filter(pk=request.user.pk).exists()
        liked_comment_ids = set(
            post.comments.filter(likes=request.user).values_list('pk', flat=True)
        )
        is_saved = ReadLater.objects.filter(user=request.user, post=post).exists()
        try:
            profile = request.user.userprofile
        except Exception:
            profile = None

    return render(request, 'post_detail.html', {
        'post': post,
        'comments': comments,
        'is_saved': is_saved,
        'user_liked': user_liked,
        'user_interested': user_interested,
        'user_reposted': user_reposted,
        'liked_comment_ids': liked_comment_ids,
        'profile': profile,
    })


@login_required
def add_comment(request, post_id):
    from .models import Comment, Notification
    post = get_object_or_404(Post, pk=post_id)
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        parent_id = request.POST.get('parent_id')
        parent = None
        if parent_id:
            try:
                parent = Comment.objects.get(pk=parent_id, post=post)
            except Comment.DoesNotExist:
                pass
        if content:
            Comment.objects.create(post=post, user=request.user, content=content, parent=parent)
            if request.user != post.user:
                actor = request.user.get_full_name() or request.user.username
                Notification.objects.create(
                    user=post.user,
                    notification_type='other',
                    message=f"{actor} commented on your post \"{post.title[:60]}\": {content[:80]}",
                    link=f"/posts/{post.pk}/",
                )
    return redirect('post_detail', post_id=post_id)

@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id, user=request.user)
    POST_TYPE_CHOICES = [
        ('idea','💡 Idea'),('article','📝 Article'),('update','🚀 Update'),
        ('announcement','📢 Announcement'),('question','❓ Question'),
    ]
    if request.method == 'POST':
        post.title = request.POST.get('title', post.title).strip()
        post.content = request.POST.get('content', post.content).strip()
        post.post_type = request.POST.get('post_type', post.post_type)
        post.industry = request.POST.get('industry', post.industry)
        post.website_link = request.POST.get('website_link', '').strip() or None
        if 'image' in request.FILES:
            post.image = request.FILES['image']
        post.save()
        messages.success(request, "Post updated successfully.")
        return redirect('post_detail', post_id=post.pk)
    return render(request, 'edit_post.html', {
        'post': post,
        'industry_choices': INDUSTRY_CHOICES,
        'post_type_choices': POST_TYPE_CHOICES,
    })


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id, user=request.user)
    if request.method == 'POST':
        post.delete()
        messages.success(request, "Post deleted.")
        return redirect('app')
    return redirect('post_detail', post_id=post_id)


def post_media(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    return render(request, 'post_media.html', {'post': post})

@login_required
def toggle_post_interest(request, post_id):
    from django.http import JsonResponse
    from .models import Notification
    post = get_object_or_404(Post, pk=post_id)
    if post.interests.filter(pk=request.user.pk).exists():
        post.interests.remove(request.user)
        interested = False
    else:
        post.interests.add(request.user)
        interested = True
        if request.user != post.user:
            actor = request.user.get_full_name() or request.user.username
            Notification.objects.create(
                user=post.user,
                notification_type='other',
                message=f"{actor} is interested in your post \"{post.title[:60]}\"",
                link=f"/posts/{post.pk}/",
            )
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'interested': interested, 'count': post.interests.count()})
    return redirect(request.META.get('HTTP_REFERER', 'app'))

@login_required
def toggle_post_like(request, post_id):
    from django.http import JsonResponse
    from .models import Notification
    post = get_object_or_404(Post, pk=post_id)
    if post.likes.filter(pk=request.user.pk).exists():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True
        if request.user != post.user:
            actor = request.user.get_full_name() or request.user.username
            Notification.objects.create(
                user=post.user,
                notification_type='other',
                message=f"{actor} liked your post \"{post.title[:60]}\"",
                link=f"/posts/{post.pk}/",
            )
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'liked': liked, 'count': post.likes.count()})
    return redirect(request.META.get('HTTP_REFERER', 'app'))


@login_required
def toggle_post_reaction(request, post_id):
    import json
    from django.http import JsonResponse
    from .models import PostReaction, Notification
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    post = get_object_or_404(Post, pk=post_id)
    try:
        data = json.loads(request.body)
        reaction_type = data.get('reaction', 'like').strip()
    except Exception:
        reaction_type = request.POST.get('reaction', 'like').strip()
    valid = {c[0] for c in PostReaction.REACTION_CHOICES}
    if reaction_type not in valid:
        reaction_type = 'like'
    existing = PostReaction.objects.filter(post=post, user=request.user).first()
    if existing:
        if existing.reaction == reaction_type:
            existing.delete()
            reacted = False
            my_reaction = None
        else:
            existing.reaction = reaction_type
            existing.save(update_fields=['reaction'])
            reacted = True
            my_reaction = reaction_type
    else:
        PostReaction.objects.create(post=post, user=request.user, reaction=reaction_type)
        reacted = True
        my_reaction = reaction_type
        if request.user != post.user:
            actor = request.user.get_full_name() or request.user.username
            Notification.objects.create(
                user=post.user,
                notification_type='other',
                message=f"{actor} reacted to your post \"{post.title[:60]}\"",
                link=f"/posts/{post.pk}/",
            )
    total = post.reactions.count()
    top = list(post.reactions.values_list('reaction', flat=True).order_by('reaction').distinct()[:3])
    return JsonResponse({'reacted': reacted, 'my_reaction': my_reaction, 'total': total, 'top': top})

@login_required
def toggle_post_repost(request, post_id):
    from django.http import JsonResponse
    from .models import Notification
    post = get_object_or_404(Post, pk=post_id)
    if post.reposts.filter(pk=request.user.pk).exists():
        post.reposts.remove(request.user)
        reposted = False
    else:
        post.reposts.add(request.user)
        reposted = True
        if request.user != post.user:
            actor = request.user.get_full_name() or request.user.username
            Notification.objects.create(
                user=post.user,
                notification_type='other',
                message=f"{actor} reposted your post \"{post.title[:60]}\"",
                link=f"/posts/{post.pk}/",
            )
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'reposted': reposted, 'count': post.reposts.count()})
    return redirect(request.META.get('HTTP_REFERER', 'app'))

@login_required
def start_post_conversation(request, post_id):
    from .models import Conversation
    post = get_object_or_404(Post, pk=post_id)
    conv, _ = Conversation.objects.get_or_create(
        context_type='post',
        post=post,
        defaults={},
    )
    if not conv.participants.filter(pk=request.user.pk).exists():
        conv.participants.add(request.user)
    return redirect('chat_page', conversation_id=conv.id)

# --- projects ---
@login_required
def project_collaborate(request, project_id):
    from .models import ProjectCollaboration, Notification, Conversation, Message as Msg
    project = get_object_or_404(Project, pk=project_id)
    if request.method == 'POST':
        msg_text = (request.POST.get('message') or request.POST.get('message_text', '')).strip()
        role = request.POST.get('role', '')
        if msg_text:
            collab, _ = ProjectCollaboration.objects.get_or_create(
                project=project, from_user=request.user,
                defaults={'message': msg_text, 'status': 'pending'}
            )
            # Notify project owner
            Notification.objects.create(
                user=project.owner,
                notification_type='other',
                message=f"{request.user.get_full_name() or request.user.username} wants to collaborate on '{project.title}': {msg_text[:120]}",
                link=f"/projects/{project.pk}/",
            )
            # Send as a direct message too
            conv, _ = Conversation.objects.get_or_create(
                context_type='project', project=project,
                defaults={}
            )
            if not conv.participants.filter(pk=request.user.pk).exists():
                conv.participants.add(request.user)
            if not conv.participants.filter(pk=project.owner.pk).exists():
                conv.participants.add(project.owner)
            Msg.objects.create(conversation=conv, sender=request.user, content=msg_text)
            messages.success(request, "Collaboration request sent!")
    return redirect(request.META.get('HTTP_REFERER', '/app/'))


@login_required
def project_send_proposal(request, project_id):
    from .models import ProjectProposal, Notification, Conversation, Message as Msg
    project = get_object_or_404(Project, pk=project_id)
    if request.method == 'POST':
        msg_text = (request.POST.get('message') or request.POST.get('message_text', '')).strip()
        amount = request.POST.get('amount', '')
        equity = request.POST.get('equity_percentage', '')
        if msg_text:
            ProjectProposal.objects.get_or_create(
                project=project, from_user=request.user,
                defaults={'message': msg_text, 'amount': amount, 'status': 'pending'}
            )
            Notification.objects.create(
                user=project.owner,
                notification_type='other',
                message=f"{request.user.get_full_name() or request.user.username} sent an investment proposal for '{project.title}': {msg_text[:120]}",
                link=f"/projects/{project.pk}/",
            )
            conv, _ = Conversation.objects.get_or_create(
                context_type='project', project=project,
                defaults={}
            )
            for u in (request.user, project.owner):
                if not conv.participants.filter(pk=u.pk).exists():
                    conv.participants.add(u)
            Msg.objects.create(conversation=conv, sender=request.user, content=msg_text)
            messages.success(request, "Proposal sent!")
    return redirect(request.META.get('HTTP_REFERER', '/app/'))

# --- jobs ---
@login_required
def user_post_job(request):
    from .models import Job, Company
    user_company = Company.objects.filter(owner=request.user).first()
    if not user_company:
        messages.error(request, "You need to register a business before posting jobs.")
        return redirect('companies_list')
    if request.method == 'POST':
        title       = request.POST.get('title', '').strip()
        company     = request.POST.get('company', '').strip()
        location    = request.POST.get('location', '').strip()
        description = request.POST.get('description', '').strip()
        salary      = request.POST.get('salary_range', '').strip()
        job_type    = request.POST.get('job_type', 'full_time')
        apply_url   = request.POST.get('apply_url', '').strip()
        if title and description:
            Job.objects.create(
                title=title, company=company, location=location,
                description=description, salary_range=salary,
                job_type=job_type, apply_url=apply_url,
                created_by=request.user,
            )
            return redirect('jobs')
    return render(request, 'user_post_job.html', {})


@login_required
def job_detail(request, pk):
    from .models import Job, JobApplication
    job = get_object_or_404(Job, pk=pk, is_hidden=False)
    already_applied = False
    if request.user.is_authenticated:
        already_applied = JobApplication.objects.filter(job=job, applicant=request.user).exists()
    if request.method == 'POST' and not already_applied:
        letter     = request.POST.get('letter', '').strip()
        cv         = request.FILES.get('cv')
        attachment = request.FILES.get('attachment')
        JobApplication.objects.get_or_create(
            job=job, applicant=request.user,
            defaults={'letter': letter, 'cv': cv, 'attachment': attachment},
        )
        return redirect('job_detail', pk=pk)
    return render(request, 'job_detail.html', {'job': job, 'already_applied': already_applied})

# --- user profile aliases ---
def view_user(request, user_id):
    return redirect('profile_view', id=user_id)



# ─── Odu Chatbot (Claude API) ─────────────────────────────────────────────────

@login_required
def generate_project_description(request):
    """
    AJAX endpoint: POST questionnaire answers → AI-generated project description.
    Body (JSON): { q1: ..., q2: ..., ... }
    Response:    { description: "..." } or { error: "..." }
    """
    import json, anthropic
    from django.conf import settings as dj_settings

    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    # Extract questionnaire answers
    answers = {
        'problem':      data.get('q_problem', '').strip(),
        'target':       data.get('q_target', '').strip(),
        'solution':     data.get('q_solution', '').strip(),
        'stage':        data.get('q_stage', '').strip(),
        'unique':       data.get('q_unique', '').strip(),
        'revenue':      data.get('q_revenue', '').strip(),
        'team':         data.get('q_team', '').strip(),
        'milestones':   data.get('q_milestones', '').strip(),
        'funding_need': data.get('q_funding', '').strip(),
        'industry':     data.get('q_industry', '').strip(),
    }

    # Need at least problem and solution
    if not answers['problem'] or not answers['solution']:
        return JsonResponse({'error': 'Please answer at least the problem and solution questions.'}, status=400)

    api_key = getattr(dj_settings, 'ANTHROPIC_API_KEY', '')
    if not api_key:
        return JsonResponse({'error': 'AI service is not configured. Please enter your description manually.'}, status=503)

    # Build prompt from answers
    qa_lines = []
    labels = {
        'problem':      'Problem being solved',
        'target':       'Target users / customers',
        'solution':     'Proposed solution / technology',
        'stage':        'Current project stage',
        'unique':       'Unique differentiator',
        'revenue':      'Revenue / business model',
        'team':         'Team',
        'milestones':   'Milestones achieved',
        'funding_need': 'Funding needed',
        'industry':     'Industry / sector',
    }
    for key, label in labels.items():
        val = answers[key]
        if val:
            qa_lines.append(f"- {label}: {val}")

    qa_text = '\n'.join(qa_lines)

    prompt = f"""You are a professional startup pitch writer. Based on the following answers from an innovator, write a compelling, clear, and investor-ready project description (3–5 paragraphs, ~200–350 words).

The description should:
1. Open with the problem and why it matters
2. Explain the solution and how it works
3. Highlight what makes it unique
4. Mention the target market and business model
5. Close with current stage, team, and funding ask (if provided)

Use professional, engaging language suitable for investors. Do NOT use bullet points — write flowing paragraphs.

Innovator's answers:
{qa_text}

Write only the project description, nothing else."""

    try:
        client = anthropic.Anthropic(api_key=api_key)
        resp = client.messages.create(
            model='claude-haiku-4-5-20251001',
            max_tokens=600,
            messages=[{'role': 'user', 'content': prompt}],
        )
        description = resp.content[0].text.strip() if resp.content else ''
        if not description:
            return JsonResponse({'error': 'No description generated. Please try again.'}, status=500)
        return JsonResponse({'description': description})
    except Exception as e:
        return JsonResponse({'error': 'AI generation failed. Please write your description manually.'}, status=500)

import unicodedata
@login_required
def ai_assist(request):
    """
    General AI assist endpoint.
    POST JSON: { type: 'project_title' | 'company_tagline' | 'company_description', ...fields }
    Response: { suggestions: [...] } or { result: '...' } or { error: '...' }
    """
    import json, anthropic
    from django.conf import settings as dj_settings

    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    assist_type = data.get('type', '')
    api_key = getattr(dj_settings, 'ANTHROPIC_API_KEY', '')
    if not api_key:
        return JsonResponse({'error': 'AI service not configured.'}, status=503)

    if assist_type == 'project_title':
        problem  = data.get('problem', '').strip()
        solution = data.get('solution', '').strip()
        industry = data.get('industry', '').strip()
        if not problem and not solution:
            return JsonResponse({'error': 'Please describe your problem or solution first.'}, status=400)
        prompt = f"""You are a startup naming expert. Based on the details below, suggest exactly 5 short, memorable project/startup titles.

Industry: {industry or 'not specified'}
Problem: {problem or 'not specified'}
Solution: {solution or 'not specified'}

Rules:
- Each title should be 2–6 words
- Be creative, specific, and investor-friendly
- Do NOT use generic words like "solution", "platform", "system" unless truly fitting
- Output ONLY the 5 titles, one per line, no numbering, no extra text"""

    elif assist_type == 'company_tagline':
        name     = data.get('name', '').strip()
        industry = data.get('industry', '').strip()
        mission  = data.get('mission', '').strip()
        if not name:
            return JsonResponse({'error': 'Please enter a company name first.'}, status=400)
        prompt = f"""You are a brand copywriter. Write exactly 5 punchy, memorable taglines for this company.

Company name: {name}
Industry: {industry or 'not specified'}
Mission / what they do: {mission or 'not specified'}

Rules:
- Each tagline should be under 12 words
- Be compelling and memorable — think Nike "Just Do It" energy
- Vary the tone: one inspiring, one bold, one descriptive, one clever, one emotive
- Output ONLY the 5 taglines, one per line, no numbering, no extra text"""

    elif assist_type == 'company_description':
        name     = data.get('name', '').strip()
        industry = data.get('industry', '').strip()
        tagline  = data.get('tagline', '').strip()
        mission  = data.get('mission', '').strip()
        location = data.get('location', '').strip()
        size     = data.get('size', '').strip()
        ctype    = data.get('company_type', '').strip()
        if not name:
            return JsonResponse({'error': 'Please enter a company name first.'}, status=400)
        prompt = f"""You are a professional business writer. Write a compelling company description (2–3 paragraphs, ~120–200 words) for the company below. This will appear on their public profile for investors and innovators to read.

Company name: {name}
Industry: {industry or 'not specified'}
Type: {ctype or 'not specified'}
Team size: {size or 'not specified'}
Location: {location or 'not specified'}
Tagline: {tagline or 'not specified'}
Mission / what they do: {mission or 'not specified'}

The description should:
1. Open with who they are and what they do
2. Explain their mission and the problem they solve
3. Close with what makes them stand out and their vision for Africa

Write in third person. Professional but warm. No bullet points — flowing paragraphs only.
Output ONLY the description text, nothing else."""

    else:
        return JsonResponse({'error': 'Unknown assist type.'}, status=400)

    try:
        client = anthropic.Anthropic(api_key=api_key)
        resp = client.messages.create(
            model='claude-haiku-4-5-20251001',
            # model='claude-3-5-sonnet-20241022',
            
            max_tokens=500,
            messages=[{'role': 'user', 'content': prompt}],
        )
        # result = resp.content[0].text.strip() if resp.content else ''
        result = ""

        if hasattr(resp, "content") and resp.content:
            for block in resp.content:
                if hasattr(block, "text"):
                    result += block.text

        result = result.strip()

        # 🔥 sanitize
        result = unicodedata.normalize('NFKD', result)
        result = result.replace('•', '-')
        result = result.encode('ascii', 'ignore').decode('ascii')
        # if hasattr(resp, "content") and resp.content:
        #     for block in resp.content:
        #         if hasattr(block, "text"):
        #             result += block.text
        if not result:
            return JsonResponse({'error': 'No result generated. Please try again.'}, status=500)

        if assist_type in ('project_title', 'company_tagline'):
            suggestions = [line.strip() for line in result.split('\n') if line.strip()]
            return JsonResponse({'suggestions': suggestions})
        else:
            return JsonResponse({'result': result})

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return JsonResponse({'error': str(e)}, status=500)


def _odu_local_reply(message, user):
    """Return a quick local reply for common patterns, or None to fall through to AI."""
    import re
    m = message.lower().strip()

    # ── Greetings ──
    if re.match(r'^(hi|hello|hey|howdy|good\s*(morning|afternoon|evening)|sup|what\'?s up)\b', m):
        name = user.first_name or user.username
        return (
            f"Hey {name}! 👋 I'm Odu, your Oduma Corp assistant. "
            "I can help you navigate the platform, post projects, find investors, "
            "connect with people, and much more. What would you like to do today?"
        )

    # ── Who/what is Odu ──
    if re.search(r'\b(who are you|what are you|what is odu|tell me about yourself|introduce yourself)\b', m):
        return (
            "I'm **Odu** — the AI assistant built into Oduma Corp! \n\n"
            "I'm here to help you get the most out of the platform. I can:\n"
            "• Guide you to the right pages\n"
            "• Explain platform features\n"
            "• Help you connect with investors or innovators\n"
            "• Answer questions about projects, groups, pages, and more\n\n"
            "Just ask me anything!"
        )

    # ── What is Oduma Corp ──
    if re.search(r'\b(what is oduma|what is this platform|what does oduma do|about oduma)\b', m):
        return (
            "**Oduma Corp** is a platform that bridges African innovators and investors. \n\n"
            "Innovators can post projects, build pitch decks, collaborate, and get funded.\n"
            "Investors can discover projects, send proposals, schedule meetings, and connect with teams.\n\n"
            "The platform also has Groups, Pages, Companies, Jobs, Courses, Mentorship, and more!"
        )

    # ── Navigation: Dashboard ──
    if re.search(r'\b(dashboard|my stats|my activity|overview)\b', m):
        return (
            "Your **Dashboard** is at `/dashboard/` — it shows all your stats: "
            "posts, projects, connections, profile views, project views, groups, and pages. "
            "You can also create posts, projects, groups, pages, companies, and meetings from there. 📊"
        )

    # ── Navigation: Feed / App ──
    if re.search(r'\b(feed|home|app|main page|posts|news feed)\b', m):
        return (
            "The main **Feed** is at `/app/` — it has two tabs:\n"
            "• **Posts** — updates and ideas from your network\n"
            "• **Projects** — innovator projects you can explore, collaborate on, or invest in\n\n"
            "You can write a post or create a new project right from there!"
        )

    # ── Navigation: Profile ──
    if re.search(r'\b(my profile|view profile|edit profile|profile page)\b', m):
        return (
            f"Your profile is at `/profile/{user.id}/` — you can update your bio, "
            "industry, photo, company, skills, and social links. "
            "A complete profile gets more attention from investors! 👤"
        )

    # ── How to create a project ──
    if re.search(r'\b(create|add|post|submit|upload)\b.*\bproject\b|\bproject\b.*\b(create|add|post|submit|upload)\b', m):
        return (
            "To **create a project**, go to `/projects/create/` or click *New Project* on your dashboard. \n\n"
            "You'll fill in:\n"
            "• Title, industry, category, description\n"
            "• Problem statement, solution, market opportunity\n"
            "• Funding requirement and business model\n"
            "• Images, video, and pitch deck sections\n\n"
            "A detailed project attracts more investor proposals!"
        )

    # ── How to find investors ──
    if re.search(r'\b(find|browse|discover|connect with|meet)\b.*\binvestor\b|\binvestor\b.*\b(find|browse|discover)\b', m):
        return (
            "You can find investors at `/investors/` — browse profiles filtered by industry and location. "
            "Click **Connect** on any investor profile to send a connection request. "
            "Once connected, you can send a direct message or invite them to a meeting! 💼"
        )

    # ── How to find innovators ──
    if re.search(r'\b(find|browse|discover)\b.*\binnovator\b|\binnovator\b.*\b(find|browse|discover)\b', m):
        return (
            "Browse innovators at `/innovators/` — you'll see profiles with their projects, "
            "industry, bio, and ratings. Click **Connect** to send a request, "
            "or **View Profile** to explore their work. 💡"
        )

    # ── Messaging / Inbox ──
    if re.search(r'\b(message|inbox|chat|dm|direct message|send.*message|talk to)\b', m):
        return (
            "Your **Inbox** is at `/inbox/` — you can view all conversations and send messages "
            "to anyone you're connected with. "
            "You can also start a chat directly from someone's profile page. 💬"
        )

    # ── Meetings / Zoom ──
    if re.search(r'\b(meeting|zoom|schedule|video call|call)\b', m):
        return (
            "You can schedule **Zoom meetings** at `/meetings/create/`. 📅\n\n"
            "• Create a meeting with a title, time, and invite your connections\n"
            "• The platform generates a Zoom link automatically\n"
            "• You can view upcoming and past meetings at `/meetings/`"
        )

    # ── Groups ──
    if re.search(r'\b(group|community|join group|create group)\b', m):
        return (
            "**Groups** are at `/groups/` — communities of innovators and investors around shared interests. 👥\n\n"
            "• Browse and join groups in your industry\n"
            "• Start discussions, share updates, and collaborate\n"
            "• Create your own group at `/groups/create/`"
        )

    # ── Pages ──
    if re.search(r'\b(page|brand page|company page|create page)\b', m):
        return (
            "**Pages** at `/pages/` are public brand profiles for businesses, startups, and organizations. 📄\n\n"
            "• Create a page at `/pages/create/`\n"
            "• Share updates and grow your following\n"
            "• Followers see your posts in their feed"
        )

    # ── Companies ──
    if re.search(r'\b(compan|business|startup|firm)\b', m):
        return (
            "You can list and discover **Companies** at `/companies/`. 🏢\n\n"
            "• Browse companies by industry\n"
            "• Follow companies to stay updated\n"
            "• Add your own company at `/companies/create/`"
        )

    # ── Jobs ──
    if re.search(r'\b(job|career|hiring|vacancy|work|employment)\b', m):
        return (
            "Check out **Jobs** on the platform — innovators and companies post open positions. 💼\n\n"
            "You can browse available roles and apply directly through Oduma Corp."
        )

    # ── Courses / Training ──
    if re.search(r'\b(course|training|learn|education|module)\b', m):
        return (
            "The **Training Hub** at `/training/` has courses to help you build skills in entrepreneurship, "
            "fundraising, innovation, and more. 🎓\n\n"
            "Enroll in a course and track your progress through the course modules."
        )

    # ── Mentorship ──
    if re.search(r'\b(mentor|mentorship|coach|guidance)\b', m):
        return (
            "The **Mentorship** section connects you with experienced mentors. 🌟\n\n"
            "• Browse mentor profiles and their areas of expertise\n"
            "• Submit a mentorship request\n"
            "• Once matched, your mentor can guide your project and growth"
        )

    # ── Notifications ──
    if re.search(r'\b(notification|alert|updates|unread)\b', m):
        return (
            "Your **Notifications** are at `/notifications/` — you'll see alerts for "
            "new connections, messages, project proposals, group invites, and platform updates. 🔔"
        )

    # ── Network / Connections ──
    if re.search(r'\b(network|connection|connect|disconnect)\b', m):
        return (
            "Your **Network** is at `/networks/` — see all your connections and get suggestions for "
            "people, companies, groups, and pages to follow. 🌐\n\n"
            "To connect with someone, visit their profile and click **Connect**."
        )

    # ── How to get funding / investors ──
    if re.search(r'\b(funding|raise|investment|pitch|investor.*interest|attract)\b', m):
        return (
            "To attract investors on Oduma Corp: 💰\n\n"
            "1. **Post a detailed project** with a full pitch deck (problem, solution, market, financials)\n"
            "2. **Complete your profile** — investors check the founder before the idea\n"
            "3. **Browse investors** at `/investors/` and send connection requests\n"
            "4. **Be active** — post updates, join groups, and engage with the community\n"
            "5. **Schedule meetings** with interested investors via `/meetings/create/`"
        )

    # ── Password / account settings ──
    if re.search(r'\b(password|change password|account settings|security)\b', m):
        return (
            "You can change your password at `/update_password/`. 🔒\n\n"
            "For other account settings and profile updates, visit your profile at `/profile/{}/`.".format(user.id)
        )

    # ── Thank you ──
    if re.match(r'^(thanks|thank you|thx|ty|appreciate it|cheers)\b', m):
        return "You're welcome! 😊 Feel free to ask if you need anything else. I'm always here!"

    # ── Help ──
    if re.match(r'^(help|what can you do|commands|options)\b', m):
        return (
            "Here's what I can help you with: 🤖\n\n"
            "• **Navigation** — finding any page on the platform\n"
            "• **Projects** — creating, editing, pitching\n"
            "• **Connections** — finding investors, innovators, companies\n"
            "• **Meetings** — scheduling Zoom calls\n"
            "• **Groups & Pages** — joining communities, building a brand\n"
            "• **Training & Mentorship** — courses and guidance\n"
            "• **Jobs** — finding or posting opportunities\n\n"
            "Just type your question naturally!"
        )

    return None  # No local match — fall through to AI


@login_required
def odu_chat(request):
    """AJAX endpoint: POST {message} → {reply}"""
    from django.http import JsonResponse
    from django.conf import settings
    import anthropic

    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    user_message = request.POST.get('message', '').strip()
    if not user_message:
        return JsonResponse({'error': 'No message provided'}, status=400)

    # Try local auto-reply first (fast, no API cost)
    local_reply = _odu_local_reply(user_message, request.user)
    if local_reply:
        return JsonResponse({'reply': local_reply})

    api_key = getattr(settings, 'ANTHROPIC_API_KEY', '')
    if not api_key:
        return JsonResponse({'reply': (
            "I'm Odu! 👋 I can help you navigate Oduma Corp. "
            "Try asking me about projects, connections, meetings, groups, or any platform feature!"
        )})

    SYSTEM_PROMPT = """You are Odu, the friendly AI assistant for Oduma Corp — a platform connecting African innovators and investors.

Platform features:
- Projects: innovators post pitch-ready projects; investors browse, send proposals, and collaborate
- Posts: feed of ideas, updates, and discussions
- Inbox/Messaging: direct messages between connected users
- Network (/networks/): connections + suggestions for people, companies, groups, pages
- Groups (/groups/): industry communities with discussions
- Pages (/pages/): brand/company public pages with followers
- Companies (/companies/): business directory with follow feature
- Dashboard (/dashboard/): personal stats — posts, projects, connections, views
- Meetings (/meetings/): Zoom video calls, scheduled through the platform
- Training (/training/): courses and learning modules
- Mentorship: mentor profiles, mentorship requests, and assignments
- Jobs: job postings and applications
- Consulting: consulting service requests

Navigation paths:
/app/ | /projects/ | /projects/create/ | /innovators/ | /investors/
/inbox/ | /networks/ | /groups/ | /groups/create/ | /pages/ | /pages/create/
/companies/ | /companies/create/ | /dashboard/ | /meetings/ | /meetings/create/
/training/ | /mentor/ | /notifications/ | /profile/<id>/

Tone: warm, concise, helpful. Use bullet points and markdown for clarity. Keep replies under 200 words unless detail is needed."""

    try:
        client = anthropic.Anthropic(api_key=api_key)
        resp = client.messages.create(
            model='claude-haiku-4-5-20251001',
            max_tokens=400,
            system=SYSTEM_PROMPT,
            messages=[{'role': 'user', 'content': user_message}],
        )
        reply = resp.content[0].text if resp.content else "I'm not sure how to help with that. Try asking about a specific feature!"
    except Exception:
        reply = (
            "Sorry, I'm having a moment! 😅 In the meantime, you can:\n"
            "• Browse projects at `/projects/`\n"
            "• Find investors at `/investors/`\n"
            "• Check your dashboard at `/dashboard/`"
        )

    return JsonResponse({'reply': reply})


@login_required
def submit_feedback(request):
    """Save a quick feedback from the floating button."""
    from django.http import JsonResponse
    from .models import SurveyResponse
    if request.method == 'POST':
        SurveyResponse.objects.create(
            submitted_by=request.user,
            feedback_type=request.POST.get('feedback_type', 'other'),
            feedback_text=request.POST.get('feedback_text', ''),
            page=request.POST.get('page', ''),
            section=request.POST.get('section', ''),
        )
    return JsonResponse({'ok': True})


# ─── Subscription ──────────────────────────────────────────────────────────────

def subscription_plans(request):
    """Public pricing page — also shows current plan if logged in."""
    from .models import SubscriptionPlan, UserSubscription
    plans = SubscriptionPlan.objects.filter(is_active=True).order_by('order')
    current_plan = None
    current_sub = None
    if request.user.is_authenticated:
        try:
            current_sub = request.user.subscription
            current_plan = current_sub.plan
        except UserSubscription.DoesNotExist:
            pass
    return render(request, 'subscription_plans.html', {
        'plans': plans,
        'current_plan': current_plan,
        'current_sub': current_sub,
    })


@login_required
def my_subscription(request):
    """User's billing / subscription management page."""
    from .models import SubscriptionPlan, UserSubscription, SubscriptionOrder
    try:
        sub = request.user.subscription
    except UserSubscription.DoesNotExist:
        free_plan = SubscriptionPlan.objects.filter(slug='starter').first()
        sub = UserSubscription.objects.create(user=request.user, plan=free_plan)

    orders = SubscriptionOrder.objects.filter(user=request.user)[:10]
    plans = SubscriptionPlan.objects.filter(is_active=True).order_by('order')
    return render(request, 'my_subscription.html', {
        'sub': sub,
        'orders': orders,
        'plans': plans,
    })


@login_required
def upgrade_subscription(request):
    """POST: switch user to a new plan (creates SubscriptionOrder)."""
    from .models import SubscriptionPlan, UserSubscription, SubscriptionOrder
    from django.utils import timezone
    import datetime

    if request.method != 'POST':
        return redirect('subscription_plans')

    plan_slug     = request.POST.get('plan_slug', '').strip()
    billing_cycle = request.POST.get('billing_cycle', 'monthly')

    plan = SubscriptionPlan.objects.filter(slug=plan_slug, is_active=True).first()
    if not plan:
        messages.error(request, 'Invalid plan selected.')
        return redirect('subscription_plans')

    # Determine amount
    if plan.slug == 'starter':
        amount = 0
    elif billing_cycle == 'yearly':
        amount = plan.price_yearly
    else:
        amount = plan.price_monthly

    # Get or create subscription record
    try:
        sub = request.user.subscription
    except UserSubscription.DoesNotExist:
        sub = None

    # Downgrading to Starter is always free and immediate
    if plan.slug == 'starter' or amount == 0:
        if sub:
            sub.plan = plan
            sub.status = 'active'
            sub.billing_cycle = billing_cycle
            sub.expires_at = None
            sub.cancelled_at = None
            sub.save()
        else:
            UserSubscription.objects.create(user=request.user, plan=plan, billing_cycle=billing_cycle)
        SubscriptionOrder.objects.create(
            user=request.user, plan=plan, billing_cycle=billing_cycle,
            amount=0, status='paid', paid_at=timezone.now(),
        )
        messages.success(request, f'You are now on the {plan.name} plan.')
        return redirect('my_subscription')

    # Paid plan — create order and activate (payment gateway to be integrated)
    # For now: activate immediately; admin records payment externally
    expires_delta = datetime.timedelta(days=365 if billing_cycle == 'yearly' else 30)
    order = SubscriptionOrder.objects.create(
        user=request.user, plan=plan, billing_cycle=billing_cycle,
        amount=amount, status='paid',
        paid_at=timezone.now(),
    )

    if sub:
        sub.plan = plan
        sub.status = 'active'
        sub.billing_cycle = billing_cycle
        sub.expires_at = timezone.now() + expires_delta
        sub.cancelled_at = None
        sub.auto_renew = True
        sub.save()
    else:
        UserSubscription.objects.create(
            user=request.user, plan=plan,
            billing_cycle=billing_cycle,
            status='active',
            expires_at=timezone.now() + expires_delta,
        )

    messages.success(
        request,
        f'Welcome to {plan.name}! Your subscription is now active. '
        'Please complete your payment via the billing details sent to your email.'
    )
    return redirect('my_subscription')


@login_required
def cancel_subscription(request):
    """POST: cancel subscription and revert to Starter."""
    from .models import SubscriptionPlan, UserSubscription
    from django.utils import timezone
    if request.method != 'POST':
        return redirect('my_subscription')
    try:
        sub = request.user.subscription
        if sub.plan.slug == 'starter':
            messages.info(request, 'You are already on the free Starter plan.')
            return redirect('my_subscription')
        free_plan = SubscriptionPlan.objects.get(slug='starter')
        sub.plan = free_plan
        sub.status = 'cancelled'
        sub.cancelled_at = timezone.now()
        sub.expires_at = None
        sub.auto_renew = False
        sub.save()
        # Immediately set to active on free plan
        sub.status = 'active'
        sub.save(update_fields=['status'])
        messages.success(request, 'Your subscription has been cancelled. You are now on the Starter plan.')
    except UserSubscription.DoesNotExist:
        messages.error(request, 'No active subscription found.')
    return redirect('my_subscription')


# ─── Innovator Agreement Workflow ──────────────────────────────────────────────

@login_required
@login_required
def agree_to_proposal(request, proposal_id):
    from .models import ProjectProposal, Notification
    proposal = get_object_or_404(ProjectProposal, pk=proposal_id)
    if proposal.project.owner != request.user:
        messages.error(request, 'Not authorized.')
        return redirect('proposals_list')
    if request.method == 'POST':
        proposal.status = 'accepted'
        proposal.save()
        Notification.objects.create(
            user=proposal.from_user,
            notification_type='other',
            message=f"{request.user.get_full_name() or request.user.username} accepted your investment proposal for '{proposal.project.title}'.",
            link=f"/projects/{proposal.project.pk}/",
        )
        messages.success(request, 'Proposal accepted. The investor has been notified.')
    return redirect('proposals_list')


@login_required
def decline_proposal(request, proposal_id):
    from .models import ProjectProposal, Notification
    proposal = get_object_or_404(ProjectProposal, pk=proposal_id)
    if proposal.project.owner != request.user:
        messages.error(request, 'Not authorized.')
        return redirect('proposals_list')
    if request.method == 'POST':
        proposal.status = 'declined'
        proposal.save()
        Notification.objects.create(
            user=proposal.from_user,
            notification_type='other',
            message=f"Your investment proposal for '{proposal.project.title}' was not accepted at this time.",
            link=f"/projects/{proposal.project.pk}/",
        )
        messages.info(request, 'Proposal declined.')
    return redirect('proposals_list')


@login_required
def proposal_action(request, proposal_id):
    """Handle counter-offer, hold, review, reply actions on a proposal via AJAX."""
    import json
    from .models import ProjectProposal, Notification, Conversation, Message as Msg
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'})
    proposal = get_object_or_404(ProjectProposal, pk=proposal_id)
    if proposal.project.owner != request.user:
        return JsonResponse({'success': False, 'error': 'Not authorized'})
    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'})

    action  = data.get('action')
    message = data.get('message', '').strip()
    status  = data.get('status')

    if not message:
        return JsonResponse({'success': False, 'error': 'Message is required'})

    valid_statuses = [s[0] for s in ProjectProposal.STATUS_CHOICES]
    # Update proposal status if provided
    if status and status in valid_statuses:
        proposal.status = status
        proposal.save()
    elif action == 'counter':
        proposal.status = 'countered'
        proposal.counter_message = message
        proposal.save()
    elif action == 'hold':
        proposal.status = 'on_hold'
        proposal.save()
    elif action == 'review':
        proposal.status = 'reviewing'
        proposal.save()

    # Create/find conversation and send message
    conversation = Conversation.objects.filter(
        participants=request.user
    ).filter(participants=proposal.from_user).first()
    if not conversation:
        conversation = Conversation.objects.create()
        conversation.participants.add(request.user, proposal.from_user)
    Msg.objects.create(
        sender=request.user,
        recipient=proposal.from_user,
        content=f"[Re: {proposal.project.title}] {message}",
        conversation=conversation,
    )

    # Notify investor
    action_labels = {
        'counter': 'sent a counter offer',
        'hold': 'put your proposal on hold',
        'review': 'requested more information',
        'reply': 'replied to your proposal',
    }
    label = action_labels.get(action, 'responded to your proposal')
    Notification.objects.create(
        user=proposal.from_user,
        notification_type='other',
        message=f"{request.user.get_full_name() or request.user.username} {label} for '{proposal.project.title}'.",
        link=f"/proposals/",
    )
    return JsonResponse({'success': True})


@login_required
def agree_to_collaboration(request, collab_id):
    from .models import ProjectCollaboration, Notification
    collab = get_object_or_404(ProjectCollaboration, pk=collab_id)
    if collab.project.owner != request.user:
        messages.error(request, 'Not authorized.')
        return redirect('proposals_list')
    if request.method == 'POST':
        collab.status = 'accepted'
        collab.save()
        Notification.objects.create(
            user=collab.from_user,
            notification_type='other',
            message=f"{request.user.get_full_name() or request.user.username} accepted your collaboration request on '{collab.project.title}'.",
            link=f"/projects/{collab.project.pk}/",
        )
        messages.success(request, 'Collaboration accepted. The collaborator has been notified.')
    return redirect('proposals_list')


@login_required
def decline_collaboration(request, collab_id):
    from .models import ProjectCollaboration, Notification
    collab = get_object_or_404(ProjectCollaboration, pk=collab_id)
    if collab.project.owner != request.user:
        messages.error(request, 'Not authorized.')
        return redirect('proposals_list')
    if request.method == 'POST':
        collab.status = 'declined'
        collab.save()
        Notification.objects.create(
            user=collab.from_user,
            notification_type='other',
            message=f"Your collaboration request on '{collab.project.title}' was not accepted at this time.",
            link=f"/projects/{collab.project.pk}/",
        )
        messages.info(request, 'Collaboration declined.')
    return redirect('proposals_list')


@login_required
def agree_to_patent_request(request, pr_id):
    # Stub — PatentRequest model not yet implemented
    messages.info(request, 'Patent workflow coming soon.')
    return redirect('proposals_list')


# ─── Share Tracking ────────────────────────────────────────────────────────────

def track_share(request):
    """Record a social share event (called via JS fetch after user clicks share)."""
    from django.http import JsonResponse
    from .models import ShareEvent
    import json as _json
    if request.method != 'POST':
        return JsonResponse({'ok': False}, status=405)
    # Accept both FormData and JSON body
    ct = request.content_type or ''
    if 'application/json' in ct:
        try:
            data = _json.loads(request.body)
        except Exception:
            data = {}
        get = lambda k, d='': data.get(k, d)
    else:
        get = lambda k, d='': request.POST.get(k, d)

    platform   = get('platform', 'other')
    share_type = get('share_type', 'general')
    content_type = get('content_type', '')
    object_id  = get('object_id') or None
    shared_url = get('shared_url', '')

    ShareEvent.objects.create(
        shared_by    = request.user if request.user.is_authenticated else None,
        platform     = platform,
        share_type   = share_type,
        content_type = content_type,
        object_id    = object_id,
        shared_url   = shared_url,
        ip_address   = request.META.get('REMOTE_ADDR'),
    )
    return JsonResponse({'ok': True})


# ─── Read Later ────────────────────────────────────────────────────────────────

@login_required
def read_later_list(request):
    from .models import ReadLater
    items = ReadLater.objects.filter(user=request.user).select_related(
        'post', 'project', 'company'
    ).order_by('-saved_at')
    return render(request, 'read_later.html', {'items': items})


@login_required
def toggle_read_later(request):
    """POST: add/remove a post, project, or company from Read Later. Returns {saved: bool}."""
    from django.http import JsonResponse
    from .models import ReadLater, Post, Project, Company
    if request.method != 'POST':
        return JsonResponse({'ok': False}, status=405)
    # Accept both naming conventions (content_type/object_id and type/id)
    ctype    = request.POST.get('content_type') or request.POST.get('type', '')
    obj_id   = request.POST.get('object_id') or request.POST.get('id')
    if not ctype or not obj_id:
        return JsonResponse({'ok': False, 'error': 'Missing fields'}, status=400)

    kwargs = {'user': request.user}
    if ctype == 'post':
        kwargs['post_id'] = obj_id
    elif ctype == 'project':
        kwargs['project_id'] = obj_id
    elif ctype == 'company':
        kwargs['company_id'] = obj_id
    else:
        return JsonResponse({'ok': False, 'error': 'Invalid content_type'}, status=400)

    existing = ReadLater.objects.filter(**kwargs).first()
    if existing:
        existing.delete()
        return JsonResponse({'ok': True, 'saved': False})
    ReadLater.objects.create(**kwargs)
    return JsonResponse({'ok': True, 'saved': True})


@login_required
def remove_read_later(request, item_id):
    """DELETE a specific ReadLater entry."""
    from .models import ReadLater
    item = get_object_or_404(ReadLater, pk=item_id, user=request.user)
    item.delete()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        from django.http import JsonResponse
        return JsonResponse({'ok': True})
    return redirect('read_later_list')


def service_worker(request):
    """Serve service worker from root scope."""
    import os
    from django.http import HttpResponse
    from django.conf import settings
    sw_path = os.path.join(settings.STATICFILES_DIRS[0] if settings.STATICFILES_DIRS else settings.STATIC_ROOT, 'js', 'service-worker.js')
    if not os.path.exists(sw_path):
        # Try alternate locations
        for sd in getattr(settings, 'STATICFILES_DIRS', []):
            candidate = os.path.join(sd, 'js', 'service-worker.js')
            if os.path.exists(candidate):
                sw_path = candidate
                break
    try:
        with open(sw_path, 'r') as f:
            content = f.read()
        return HttpResponse(content, content_type='application/javascript')
    except FileNotFoundError:
        return HttpResponse('// Service worker not found', content_type='application/javascript', status=404)


# ══════════════════════════════════════════════════════════════════
#  Oduma Corp Service Views
# ══════════════════════════════════════════════════════════════════

# ── Training / Courses ────────────────────────────────────────────

@login_required
def training_hub(request):
    """Course catalog with enrolled courses and recommended courses."""
    from .models import Course, CourseEnrollment
    category = request.GET.get('category', '').strip()
    level    = request.GET.get('level', '').strip()

    courses_qs = Course.objects.filter(is_published=True)
    if category:
        courses_qs = courses_qs.filter(category=category)
    if level:
        courses_qs = courses_qs.filter(level=level)

    enrolled_ids = set(
        CourseEnrollment.objects.filter(user=request.user)
        .values_list('course_id', flat=True)
    )
    my_enrollments = CourseEnrollment.objects.filter(
        user=request.user
    ).select_related('course').exclude(status='dropped').order_by('-enrolled_at')

    return render(request, 'training_hub.html', {
        'courses':       courses_qs,
        'enrolled_ids':  enrolled_ids,
        'my_enrollments': my_enrollments,
        'category_choices': Course.CATEGORY_CHOICES,
        'level_choices':    Course.LEVEL_CHOICES,
        'active_category':  category,
        'active_level':     level,
    })


@login_required
def course_detail(request, slug):
    """Single course view with modules and enroll/progress actions."""
    from .models import Course, CourseEnrollment
    course = get_object_or_404(Course, slug=slug, is_published=True)
    enrollment = CourseEnrollment.objects.filter(user=request.user, course=course).first()
    modules = course.modules.all()
    return render(request, 'course_detail.html', {
        'course':     course,
        'enrollment': enrollment,
        'modules':    modules,
    })


@login_required
def enroll_course(request, slug):
    """Enroll in a course (POST)."""
    from .models import Course, CourseEnrollment
    course = get_object_or_404(Course, slug=slug, is_published=True)
    enrollment, created = CourseEnrollment.objects.get_or_create(
        user=request.user, course=course,
        defaults={'status': 'enrolled', 'progress': 0}
    )
    if created:
        messages.success(request, f'Enrolled in "{course.title}"!')
    else:
        messages.info(request, "You're already enrolled in this course.")
    return redirect('course_detail', slug=slug)


@login_required
def update_course_progress(request, slug):
    """AJAX/POST: update progress percentage for an enrollment."""
    from .models import Course, CourseEnrollment
    from django.utils import timezone as tz
    from django.http import JsonResponse
    course = get_object_or_404(Course, slug=slug)
    enrollment = get_object_or_404(CourseEnrollment, user=request.user, course=course)
    if request.method == 'POST':
        progress = min(100, max(0, int(request.POST.get('progress', enrollment.progress))))
        enrollment.progress = progress
        if progress >= 100:
            enrollment.status = 'completed'
            enrollment.completed_at = tz.now()
        elif progress > 0:
            enrollment.status = 'in_progress'
        enrollment.save(update_fields=['progress', 'status', 'completed_at'])
        return JsonResponse({'progress': progress, 'status': enrollment.status})
    return JsonResponse({'error': 'POST required'}, status=405)


# ── Mentorship ────────────────────────────────────────────────────

@login_required
def mentorship_hub(request):
    """Browse active mentors and your mentorship requests."""
    from .models import MentorProfile, MentorshipRequest
    expertise = request.GET.get('expertise', '').strip()
    mentors_qs = MentorProfile.objects.filter(is_active=True).select_related('user', 'user__userprofile')
    if expertise:
        mentors_qs = mentors_qs.filter(expertise=expertise)

    my_requests = MentorshipRequest.objects.filter(
        from_user=request.user
    ).select_related('mentor', 'mentor__user', 'project').order_by('-created_at')

    return render(request, 'mentorship_hub.html', {
        'mentors':           mentors_qs,
        'my_requests':       my_requests,
        'expertise_choices': MentorProfile.EXPERTISE_CHOICES,
        'active_expertise':  expertise,
    })


@login_required
def request_mentor(request, mentor_id):
    """Submit a mentorship request."""
    from .models import MentorProfile, MentorshipRequest, Project
    mentor = get_object_or_404(MentorProfile, pk=mentor_id, is_active=True)
    if request.method == 'POST':
        project_id = request.POST.get('project_id') or None
        project = None
        if project_id:
            project = Project.objects.filter(pk=project_id, owner=request.user).first()

        existing = MentorshipRequest.objects.filter(
            from_user=request.user, mentor=mentor, project=project
        ).first()
        if existing:
            messages.info(request, "You've already submitted a request to this mentor.")
        else:
            MentorshipRequest.objects.create(
                from_user = request.user,
                mentor    = mentor,
                project   = project,
                message   = request.POST.get('message', ''),
                goals     = request.POST.get('goals', ''),
            )
            messages.success(request, f"Mentorship request sent to {mentor.user.get_full_name() or mentor.user.username}!")
    return redirect('mentorship_hub')


# ── Innovation Consulting ─────────────────────────────────────────

@login_required
def request_consulting(request, project_id=None):
    """Submit an innovation consulting request, optionally tied to a project."""
    from .models import ConsultingRequest, Project
    project = None
    if project_id:
        project = get_object_or_404(Project, pk=project_id, owner=request.user)

    if request.method == 'POST':
        ConsultingRequest.objects.create(
            user        = request.user,
            project     = project,
            category    = request.POST.get('category', 'strategy'),
            description = request.POST.get('description', ''),
            urgency     = request.POST.get('urgency', 'medium'),
        )
        messages.success(request, "Support request submitted! Our team will reach out shortly.")
        if project:
            return redirect('project_detail', pk=project.pk)
        return redirect('services')

    return render(request, 'consulting_request.html', {
        'project':            project,
        'category_choices':   ConsultingRequest.CATEGORY_CHOICES,
        'urgency_choices':    ConsultingRequest.STATUS_CHOICES,
    })


@login_required
def my_consulting_requests(request):
    """User's consulting request history."""
    from .models import ConsultingRequest
    requests_qs = ConsultingRequest.objects.filter(user=request.user).select_related('project')
    return render(request, 'my_consulting_requests.html', {'requests': requests_qs})


# ── Events Hub ────────────────────────────────────────────────────

def events_hub(request):
    """Public events listing: demo days, investor meetups, workshops, etc."""
    from .models import Event, EventRegistration, Company
    event_type = request.GET.get('type', '').strip()
    events_qs  = Event.objects.filter(is_hidden=False).order_by('date')
    if event_type:
        events_qs = events_qs.filter(event_type=event_type)

    registered_ids = set()
    user_has_company = False
    if request.user.is_authenticated:
        registered_ids = set(
            EventRegistration.objects.filter(user=request.user)
            .values_list('event_id', flat=True)
        )
        user_has_company = Company.objects.filter(owner=request.user).exists()

    from datetime import date
    today = date.today()
    upcoming = [e for e in events_qs if e.date >= today]
    past     = [e for e in events_qs if e.date < today]

    return render(request, 'events_hub.html', {
        'upcoming':           upcoming,
        'past':               past,
        'registered_ids':     registered_ids,
        'event_type_choices': Event.EVENT_TYPES,
        'active_type':        event_type,
        'user_has_company':   user_has_company,
    })


@login_required
def register_for_event(request, event_id):
    """Register the current user for an event."""
    from .models import Event, EventRegistration
    event = get_object_or_404(Event, pk=event_id, is_hidden=False)
    reg, created = EventRegistration.objects.get_or_create(
        user=request.user, event=event,
        defaults={
            'full_name': request.user.get_full_name(),
            'email':     request.user.email,
        }
    )
    if created:
        messages.success(request, f'You\'re registered for "{event.name}"!')
    else:
        messages.info(request, "You're already registered for this event.")
    return redirect('events_hub')


@login_required
def user_post_event(request):
    from .models import Event, Company
    user_company = Company.objects.filter(owner=request.user).first()
    if not user_company:
        messages.error(request, "You need to register a business before posting events.")
        return redirect('companies_list')
    if request.method == 'POST':
        name          = request.POST.get('name', '').strip()
        date_str      = request.POST.get('date', '').strip()
        location      = request.POST.get('location', '').strip()
        description   = request.POST.get('description', '').strip()
        organizer     = request.POST.get('organizer', '').strip()
        event_type    = request.POST.get('event_type', 'general')
        max_attendees = request.POST.get('max_attendees', '').strip()
        image         = request.FILES.get('image')
        if name and date_str and location:
            from datetime import datetime
            try:
                date_val = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                messages.error(request, "Invalid date format.")
                return render(request, 'user_post_event.html', {
                    'company': user_company,
                    'event_type_choices': Event.EVENT_TYPES,
                })
            Event.objects.create(
                name=name, date=date_val, location=location,
                description=description, organizer=organizer or user_company.name,
                event_type=event_type,
                max_attendees=int(max_attendees) if max_attendees else None,
                image=image, created_by=request.user,
            )
            messages.success(request, "Event posted successfully!")
            return redirect('events_hub')
    return render(request, 'user_post_event.html', {
        'company': user_company,
        'event_type_choices': Event.EVENT_TYPES,
    })


# ── Intelligent Matching ──────────────────────────────────────────

@login_required
def top_matches_for_investor(request):
    """AJAX or full page: top matched projects for the current investor."""
    from .models import Project
    from .matching import get_top_matches_with_breakdown
    from django.http import JsonResponse
    profile = getattr(request.user, 'userprofile', None)
    projects_qs = Project.objects.filter(
        is_hidden=False, review_status__in=['approved', 'featured']
    ).exclude(owner=request.user).select_related('owner', 'owner__userprofile')[:80]

    matches = get_top_matches_with_breakdown(profile, projects_qs, n=12)
    # Collect pitched project IDs for the template
    from .models import ProjectProposal
    pitched_ids = set(
        ProjectProposal.objects.filter(from_user=request.user)
        .values_list('project_id', flat=True)
    ) if request.user.is_authenticated else set()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = [{'id': m['project'].pk, 'title': m['project'].title,
                 'score': m['score'], 'label': m['label']} for m in matches]
        return JsonResponse({'matches': data})
    return render(request, 'top_matches.html', {'matches': matches, 'pitched_ids': pitched_ids})


@login_required
def project_investor_matches(request, pk):
    """Show matching investors for an innovator's project."""
    from .models import Project
    from .matching import get_innovator_investor_matches
    project = get_object_or_404(Project, pk=pk, owner=request.user)
    investors_qs = CustomUser.objects.filter(
        user_type='investor', is_hidden=False
    ).select_related('userprofile')
    matches = get_innovator_investor_matches(project, investors_qs, n=8)
    return render(request, 'project_investor_matches.html', {
        'project': project,
        'matches': matches,
    })


# ── Innovator Command-Center Dashboard ───────────────────────────

@login_required
def innovator_dashboard(request):
    """Redesigned command-center dashboard for innovators."""
    from .models import (
        Project, Interest, PitchRequest, Notification,
        Connection, MentorshipRequest, ConsultingRequest,
        CourseEnrollment, Event, EventRegistration,
    )
    from .matching import get_innovator_investor_matches
    from django.db.models import Sum

    user = request.user
    profile = getattr(user, 'userprofile', None)

    # Projects
    projects = Project.objects.filter(
        owner=user
    ).order_by('-created_at').prefetch_related('pitch_requests')

    total_projects    = projects.count()
    published_projects = projects.exclude(status='draft').count()

    # Interest / pitch metrics
    project_ids = projects.values_list('id', flat=True)
    total_interest   = Interest.objects.filter(target_user=user).count()
    pitch_count      = PitchRequest.objects.filter(project__owner=user).count()
    pending_pitches  = PitchRequest.objects.filter(project__owner=user, status='pending').count()

    # Per-project interest counts (M2M)
    projects_with_interest = []
    for p in projects:
        interest_count = p.interested.count() if hasattr(p, 'interested') else 0
        suggestions = []
        score = p.completeness_score()
        if score < 100:
            for field in p.PITCH_FIELDS:
                if not getattr(p, field, '').strip():
                    label_map = {
                        'problem_statement':  'Problem Statement',
                        'solution_overview':  'Solution Overview',
                        'market_opportunity': 'Market Opportunity',
                        'business_model':     'Business Model',
                        'traction':           'Traction / Validation',
                        'funding_requirement':'Funding Requirement',
                        'use_of_funds':       'Use of Funds',
                        'team_overview':      'Team Overview',
                    }
                    suggestions.append(f"Add {label_map.get(field, field)}")
                    if len(suggestions) >= 3:
                        break
        projects_with_interest.append({
            'project':        p,
            'interest_count': interest_count,
            'score':          score,
            'suggestions':    suggestions,
        })

    # Connections
    connections = Connection.objects.filter(
        Q(initiator=user, status='accepted') | Q(target=user, status='accepted')
    ).count()
    pending_connections = Connection.objects.filter(target=user, status='pending').count()

    # Top matching investors for user's best project
    top_investor_matches = []
    if projects.exists():
        best_project = projects.filter(review_status__in=['approved','featured','under_review']).first() or projects.first()
        investors_qs = CustomUser.objects.filter(
            user_type='investor', is_hidden=False
        ).select_related('userprofile')[:40]
        top_investor_matches = get_innovator_investor_matches(best_project, investors_qs, n=4)

    # Notifications (recent)
    recent_notifications = Notification.objects.filter(user=user).order_by('-created_at')[:8]

    # Mentorship
    my_mentorship = MentorshipRequest.objects.filter(from_user=user, status='accepted').select_related('mentor', 'mentor__user').first()

    # Consulting
    open_consulting = ConsultingRequest.objects.filter(user=user).exclude(status__in=['completed','declined']).count()

    # Courses
    my_courses = CourseEnrollment.objects.filter(user=user).exclude(status__in=['dropped','completed']).select_related('course')[:3]

    # Upcoming events
    from datetime import date
    upcoming_events = Event.objects.filter(
        is_hidden=False, date__gte=date.today()
    ).order_by('date')[:3]
    registered_event_ids = set(
        EventRegistration.objects.filter(user=user).values_list('event_id', flat=True)
    )

    # Pins
    from .models import Pin
    user_pins = Pin.objects.filter(user=user).select_related(
        'conversation', 'post', 'project',
        'conversation__participants',
    ).prefetch_related('conversation__participants')
    pinned_chat_ids    = set(p.conversation_id for p in user_pins if p.pin_type == 'chat' and p.conversation_id)
    pinned_post_ids    = set(p.post_id for p in user_pins if p.pin_type == 'post' and p.post_id)
    pinned_project_ids = set(p.project_id for p in user_pins if p.pin_type == 'project' and p.project_id)
    pinned_chats    = [p for p in user_pins if p.pin_type == 'chat']
    pinned_posts    = [p for p in user_pins if p.pin_type == 'post']
    pinned_projects = [p for p in user_pins if p.pin_type == 'project']

    return render(request, 'innovator_dashboard.html', {
        'profile':                profile,
        'projects_with_interest': projects_with_interest,
        'total_projects':         total_projects,
        'published_projects':     published_projects,
        'pitch_count':            pitch_count,
        'pending_pitches':        pending_pitches,
        'connections':            connections,
        'pending_connections':    pending_connections,
        'top_investor_matches':   top_investor_matches,
        'recent_notifications':   recent_notifications,
        'my_mentorship':          my_mentorship,
        'open_consulting':        open_consulting,
        'my_courses':             my_courses,
        'upcoming_events':        upcoming_events,
        'registered_event_ids':   registered_event_ids,
        # Pins
        'pinned_chats':           pinned_chats,
        'pinned_posts':           pinned_posts,
        'pinned_projects':        pinned_projects,
        'pinned_chat_ids':        pinned_chat_ids,
        'pinned_post_ids':        pinned_post_ids,
        'pinned_project_ids':     pinned_project_ids,
    })


@login_required
def get_counts(request):
    """Lightweight JSON endpoint — returns unread notification + message counts for the current user."""
    from .models import Notification, Message
    notif_count = Notification.objects.filter(user=request.user, is_read=False).count()
    msg_count   = Message.objects.filter(recipient=request.user, is_read=False).count()
    return JsonResponse({'notifications': notif_count, 'messages': msg_count})


@login_required
@require_POST
def toggle_pin(request):
    """Toggle pin on a chat, post, or project. Returns JSON {pinned: bool}."""
    from .models import Pin, Conversation, Post, Project
    pin_type = request.POST.get('type')
    obj_id   = request.POST.get('id')
    if pin_type not in ('chat', 'post', 'project') or not obj_id:
        return JsonResponse({'error': 'Invalid request'}, status=400)
    try:
        obj_id = int(obj_id)
    except (ValueError, TypeError):
        return JsonResponse({'error': 'Invalid id'}, status=400)

    if pin_type == 'chat':
        obj = get_object_or_404(Conversation, pk=obj_id, participants=request.user)
        existing = Pin.objects.filter(user=request.user, pin_type='chat', conversation=obj).first()
        if existing:
            existing.delete()
            return JsonResponse({'pinned': False})
        Pin.objects.create(user=request.user, pin_type='chat', conversation=obj)

    elif pin_type == 'post':
        obj = get_object_or_404(Post, pk=obj_id)
        existing = Pin.objects.filter(user=request.user, pin_type='post', post=obj).first()
        if existing:
            existing.delete()
            return JsonResponse({'pinned': False})
        Pin.objects.create(user=request.user, pin_type='post', post=obj)

    elif pin_type == 'project':
        obj = get_object_or_404(Project, pk=obj_id)
        existing = Pin.objects.filter(user=request.user, pin_type='project', project=obj).first()
        if existing:
            existing.delete()
            return JsonResponse({'pinned': False})
        Pin.objects.create(user=request.user, pin_type='project', project=obj)

    return JsonResponse({'pinned': True})


# ─── Hashtag helpers & views ──────────────────────────────────────────────────

import re as _hashtag_re

def _get_trending_hashtags(limit=10):
    """Return [(tag, count), ...] from recent post content."""
    from .models import Post
    contents = Post.objects.filter(is_hidden=False).order_by('-created_at').values_list('content', flat=True)[:400]
    counts = {}
    for text in contents:
        for tag in _hashtag_re.findall(r'#(\w+)', (text or '').lower()):
            counts[tag] = counts.get(tag, 0) + 1
    return sorted(counts.items(), key=lambda x: -x[1])[:limit]


def hashtag_feed(request, tag):
    from .models import Post, Project, GroupDiscussion
    tag = tag.lower().strip()
    pattern = f'#{tag}'

    posts = (
        Post.objects.filter(content__icontains=pattern, is_hidden=False)
        .select_related('user', 'user__userprofile')
        .order_by('-created_at')[:20]
    )
    projects = (
        Project.objects.filter(
            Q(description__icontains=pattern) | Q(keywords__icontains=pattern),
            is_hidden=False
        )
        .select_related('owner', 'owner__userprofile')
        .prefetch_related('images')
        .order_by('-created_at')[:12]
    )
    discussions = (
        GroupDiscussion.objects.filter(content__icontains=pattern)
        .select_related('group', 'author')
        .order_by('-created_at')[:10]
    )
    related = _get_trending_hashtags(limit=15)

    return render(request, 'hashtag_feed.html', {
        'tag': tag,
        'posts': posts,
        'projects': projects,
        'discussions': discussions,
        'related_hashtags': [t for t, _ in related if t != tag][:12],
        'total': posts.count() + projects.count() + discussions.count(),
    })


def popular_hashtags(request):
    tags = _get_trending_hashtags(limit=20)
    return JsonResponse({'hashtags': [{'name': t, 'count': c} for t, c in tags]})

