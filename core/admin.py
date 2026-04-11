from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    CustomUser, UserProfile, Invention,
    Event, EventRegistration,
    Project, ProjectImage, ProjectCollaboration, ProjectComment, ProjectView, ProjectProposal,
    Attachment, AttachmentDownload,
    Rating, Post, PostImage, Comment,
    Notification, Connection,
    Patent, Like, Interest,
    Group, GroupMembership, GroupDiscussion, GroupDiscussionComment, GroupDiscussionImage,
    Page, PagePost, PagePostReaction, PagePostShare, PagePostImage,
    Company, CompanyMedia, CompanyUpdate,
    Conversation, Message, MessageReaction,
    Job, JobApplication,
    ProfileView, PageView, ClickEvent,
    NewsItem, ContactSubmission,
    Collaboration, PatentRequest, Proposal,
    SurveyResponse, ShareEvent, ReadLater,
    AdminPermissions, Meeting,
    StageProgressionRequest, VerificationRequest, PitchRequest,
    Course, CourseModule, CourseEnrollment,
    MentorProfile, MentorshipRequest, MentorshipAssignment,
    ConsultingRequest,
    MyModel,
    SubscriptionPlan, UserSubscription, SubscriptionOrder,
)


# ── Users ──────────────────────────────────────────────────────────────────────

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display  = ('username', 'email', 'first_name', 'last_name', 'user_type', 'is_active', 'date_joined')
    list_filter   = ('user_type', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering      = ('-date_joined',)
    fieldsets     = UserAdmin.fieldsets + (
        ('Oduma Corp', {'fields': ('user_type', 'bio', 'phone_number', 'profile_pics')}),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display  = ('user', 'industry', 'company', 'verification_status')
    list_filter   = ('verification_status', 'industry')
    search_fields = ('user__username', 'user__email', 'company', 'industry')
    raw_id_fields = ('user',)


@admin.register(AdminPermissions)
class AdminPermissionsAdmin(admin.ModelAdmin):
    list_display  = ('admin_user', 'is_superadmin', 'can_manage_users', 'can_manage_projects')
    search_fields = ('admin_user__username',)
    raw_id_fields = ('admin_user',)


# ── Projects ───────────────────────────────────────────────────────────────────

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display  = ('title', 'owner', 'industry', 'pipeline_stage', 'review_status', 'funding_stage', 'created_at')
    list_filter   = ('review_status', 'pipeline_stage', 'industry', 'funding_stage')
    search_fields = ('title', 'description', 'owner__username', 'owner__email')
    raw_id_fields = ('owner',)
    ordering      = ('-created_at',)
    date_hierarchy = 'created_at'


@admin.register(ProjectImage)
class ProjectImageAdmin(admin.ModelAdmin):
    list_display  = ('project', 'name', 'is_main')
    list_filter   = ('is_main',)
    raw_id_fields = ('project',)


@admin.register(ProjectCollaboration)
class ProjectCollaborationAdmin(admin.ModelAdmin):
    list_display  = ('project', 'from_user', 'status', 'created_at')
    list_filter   = ('status',)
    raw_id_fields = ('project', 'from_user')


@admin.register(ProjectComment)
class ProjectCommentAdmin(admin.ModelAdmin):
    list_display  = ('project', 'user', 'created_at')
    raw_id_fields = ('project', 'user')


@admin.register(ProjectView)
class ProjectViewAdmin(admin.ModelAdmin):
    list_display  = ('project', 'user', 'viewed_at')
    raw_id_fields = ('project', 'user')


@admin.register(ProjectProposal)
class ProjectProposalAdmin(admin.ModelAdmin):
    list_display  = ('project', 'from_user', 'status', 'amount', 'created_at')
    list_filter   = ('status',)
    raw_id_fields = ('project', 'from_user')


@admin.register(StageProgressionRequest)
class StageProgressionRequestAdmin(admin.ModelAdmin):
    list_display  = ('project', 'requested_by', 'to_stage', 'status', 'requested_at')
    list_filter   = ('status',)
    raw_id_fields = ('project', 'requested_by')


@admin.register(VerificationRequest)
class VerificationRequestAdmin(admin.ModelAdmin):
    list_display  = ('user', 'status', 'submitted_at')
    list_filter   = ('status',)
    raw_id_fields = ('user',)


@admin.register(PitchRequest)
class PitchRequestAdmin(admin.ModelAdmin):
    list_display  = ('project', 'investor', 'status', 'requested_at')
    list_filter   = ('status',)
    raw_id_fields = ('project', 'investor')


# ── Posts & Feed ───────────────────────────────────────────────────────────────

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display  = ('user', 'post_type', 'industry', 'created_at')
    list_filter   = ('post_type', 'industry')
    search_fields = ('content', 'user__username')
    raw_id_fields = ('user',)
    ordering      = ('-created_at',)


@admin.register(PostImage)
class PostImageAdmin(admin.ModelAdmin):
    list_display  = ('post', 'name')
    raw_id_fields = ('post',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display  = ('post', 'user', 'created_at')
    raw_id_fields = ('post', 'user')


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display  = ('project', 'user', 'value')
    list_filter   = ('value',)
    raw_id_fields = ('project', 'user')


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display  = ('user', 'target_user', 'created_at')
    raw_id_fields = ('user', 'target_user')


@admin.register(Interest)
class InterestAdmin(admin.ModelAdmin):
    list_display  = ('user', 'target_user', 'created_at')
    raw_id_fields = ('user', 'target_user')


# ── Messaging ──────────────────────────────────────────────────────────────────

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display  = ('id', 'context_type', 'project', 'created_at')
    list_filter   = ('context_type',)
    ordering      = ('-created_at',)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display  = ('sender', 'conversation', 'message_type', 'timestamp', 'is_read')
    list_filter   = ('message_type', 'is_read')
    search_fields = ('content', 'sender__username')
    raw_id_fields = ('sender', 'conversation')
    ordering      = ('-timestamp',)


@admin.register(MessageReaction)
class MessageReactionAdmin(admin.ModelAdmin):
    list_display  = ('message', 'user', 'emoji', 'created_at')
    raw_id_fields = ('message', 'user')


# ── Notifications & Connections ────────────────────────────────────────────────

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display  = ('user', 'notification_type', 'is_read', 'created_at')
    list_filter   = ('notification_type', 'is_read')
    search_fields = ('user__username', 'message')
    raw_id_fields = ('user',)
    ordering      = ('-created_at',)


@admin.register(Connection)
class ConnectionAdmin(admin.ModelAdmin):
    list_display  = ('initiator', 'target', 'status', 'created_at')
    list_filter   = ('status',)
    search_fields = ('initiator__username', 'target__username')
    raw_id_fields = ('initiator', 'target')


# ── Companies, Groups & Pages ──────────────────────────────────────────────────

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display  = ('name', 'industry', 'owner', 'created_at')
    list_filter   = ('industry',)
    search_fields = ('name', 'owner__username')
    raw_id_fields = ('owner',)


@admin.register(CompanyMedia)
class CompanyMediaAdmin(admin.ModelAdmin):
    list_display  = ('company', 'media_type', 'uploaded_at')
    raw_id_fields = ('company',)


@admin.register(CompanyUpdate)
class CompanyUpdateAdmin(admin.ModelAdmin):
    list_display  = ('company', 'created_at')
    raw_id_fields = ('company',)


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display  = ('name', 'creator', 'industry', 'created_at')
    list_filter   = ('industry',)
    search_fields = ('name', 'creator__username')
    raw_id_fields = ('creator',)


@admin.register(GroupMembership)
class GroupMembershipAdmin(admin.ModelAdmin):
    list_display  = ('group', 'user', 'status', 'created_at')
    list_filter   = ('status',)
    raw_id_fields = ('group', 'user')


@admin.register(GroupDiscussion)
class GroupDiscussionAdmin(admin.ModelAdmin):
    list_display  = ('group', 'author', 'title', 'created_at')
    raw_id_fields = ('group', 'author')


admin.site.register(GroupDiscussionComment)
admin.site.register(GroupDiscussionImage)


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display  = ('title', 'owner', 'industry', 'created_at')
    list_filter   = ('industry',)
    search_fields = ('title', 'owner__username')
    raw_id_fields = ('owner',)


admin.site.register(PagePost)
admin.site.register(PagePostReaction)
admin.site.register(PagePostShare)
admin.site.register(PagePostImage)


# ── Jobs & Events ──────────────────────────────────────────────────────────────

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display  = ('title', 'company', 'location', 'job_type', 'is_active', 'created_at')
    list_filter   = ('job_type', 'is_active')
    search_fields = ('title', 'company')
    ordering      = ('-created_at',)


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display  = ('job', 'applicant', 'applied_at')
    raw_id_fields = ('job', 'applicant')


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display  = ('name', 'event_type', 'date', 'location', 'organizer')
    list_filter   = ('event_type',)
    search_fields = ('name', 'location')
    ordering      = ('date',)
    date_hierarchy = 'date'


@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display  = ('event', 'user', 'registered_at')
    raw_id_fields = ('event', 'user')


# ── Proposals & Collaborations ─────────────────────────────────────────────────

@admin.register(Proposal)
class ProposalAdmin(admin.ModelAdmin):
    list_display  = ('from_investor', 'post', 'status', 'amount', 'created_at')
    list_filter   = ('status',)
    raw_id_fields = ('from_investor', 'post')
    ordering      = ('-created_at',)


@admin.register(Collaboration)
class CollaborationAdmin(admin.ModelAdmin):
    list_display  = ('from_user', 'post', 'status', 'created_at')
    list_filter   = ('status',)
    raw_id_fields = ('from_user', 'post')


# ── Attachments ────────────────────────────────────────────────────────────────

@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display  = ('project', 'title', 'doc_type', 'uploaded_at')
    list_filter   = ('doc_type',)
    raw_id_fields = ('project',)


@admin.register(AttachmentDownload)
class AttachmentDownloadAdmin(admin.ModelAdmin):
    list_display  = ('attachment', 'downloaded_by', 'downloaded_at')
    raw_id_fields = ('attachment', 'downloaded_by')


# ── Mentorship & Consulting ────────────────────────────────────────────────────

@admin.register(MentorProfile)
class MentorProfileAdmin(admin.ModelAdmin):
    list_display  = ('user', 'is_active', 'expertise', 'created_at')
    list_filter   = ('is_active', 'expertise')
    search_fields = ('user__username', 'bio')
    raw_id_fields = ('user',)


@admin.register(MentorshipRequest)
class MentorshipRequestAdmin(admin.ModelAdmin):
    list_display  = ('from_user', 'mentor', 'status', 'created_at')
    list_filter   = ('status',)
    raw_id_fields = ('from_user', 'mentor')


@admin.register(MentorshipAssignment)
class MentorshipAssignmentAdmin(admin.ModelAdmin):
    list_display  = ('mentor', 'mentee', 'status', 'assigned_at')
    list_filter   = ('status',)
    raw_id_fields = ('mentor', 'mentee')


@admin.register(ConsultingRequest)
class ConsultingRequestAdmin(admin.ModelAdmin):
    list_display  = ('user', 'status', 'submitted_at')
    list_filter   = ('status',)
    search_fields = ('user__username', 'description')
    raw_id_fields = ('user',)
    ordering      = ('-submitted_at',)


# ── Courses ────────────────────────────────────────────────────────────────────

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display  = ('title', 'category', 'level', 'is_published', 'created_at')
    list_filter   = ('category', 'level', 'is_published')
    search_fields = ('title', 'description')


@admin.register(CourseModule)
class CourseModuleAdmin(admin.ModelAdmin):
    list_display  = ('course', 'title', 'order')
    raw_id_fields = ('course',)


@admin.register(CourseEnrollment)
class CourseEnrollmentAdmin(admin.ModelAdmin):
    list_display  = ('user', 'course', 'status', 'progress', 'enrolled_at')
    list_filter   = ('status',)
    raw_id_fields = ('user', 'course')


# ── Meetings ───────────────────────────────────────────────────────────────────

@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display  = ('title', 'creator', 'status', 'scheduled_at', 'created_at')
    list_filter   = ('status',)
    search_fields = ('title', 'creator__username')
    raw_id_fields = ('creator',)
    ordering      = ('-scheduled_at',)


# ── Analytics & Tracking ───────────────────────────────────────────────────────

@admin.register(ProfileView)
class ProfileViewAdmin(admin.ModelAdmin):
    list_display  = ('profile_user', 'viewer', 'viewed_at')
    raw_id_fields = ('profile_user', 'viewer')


@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):
    list_display  = ('user', 'path', 'browser', 'timestamp')
    list_filter   = ('browser',)
    search_fields = ('path', 'user__username')
    ordering      = ('-timestamp',)


@admin.register(ClickEvent)
class ClickEventAdmin(admin.ModelAdmin):
    list_display  = ('user', 'element_id', 'path', 'timestamp')
    ordering      = ('-timestamp',)


# ── Misc ───────────────────────────────────────────────────────────────────────

@admin.register(NewsItem)
class NewsItemAdmin(admin.ModelAdmin):
    list_display  = ('title', 'created_at', 'is_published')
    list_filter   = ('is_published',)
    search_fields = ('title', 'body')


@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display  = ('name', 'email', 'subject', 'submitted_at')
    search_fields = ('name', 'email', 'subject')
    ordering      = ('-submitted_at',)
    readonly_fields = ('submitted_at',)


@admin.register(Patent)
class PatentAdmin(admin.ModelAdmin):
    list_display  = ('title', 'owner', 'filed_date')
    raw_id_fields = ('owner',)


@admin.register(PatentRequest)
class PatentRequestAdmin(admin.ModelAdmin):
    list_display  = ('from_investor', 'post', 'status', 'created_at')
    list_filter   = ('status',)
    raw_id_fields = ('from_investor', 'post')


@admin.register(Invention)
class InventionAdmin(admin.ModelAdmin):
    list_display  = ('name', 'owner')
    raw_id_fields = ('owner',)


@admin.register(SurveyResponse)
class SurveyResponseAdmin(admin.ModelAdmin):
    list_display  = ('submitted_by', 'submitted_at')
    raw_id_fields = ('submitted_by',)


@admin.register(ShareEvent)
class ShareEventAdmin(admin.ModelAdmin):
    list_display  = ('shared_by', 'content_type', 'shared_at')
    raw_id_fields = ('shared_by',)


@admin.register(ReadLater)
class ReadLaterAdmin(admin.ModelAdmin):
    list_display  = ('user', 'project', 'post', 'saved_at')
    raw_id_fields = ('user', 'project', 'post')


# ── Subscriptions ──────────────────────────────────────────────────────────────

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display  = ('name', 'slug', 'price_monthly', 'price_yearly', 'is_active')
    list_filter   = ('is_active',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display  = ('user', 'plan', 'status', 'billing_cycle', 'expires_at')
    list_filter   = ('status', 'billing_cycle')
    search_fields = ('user__username', 'user__email')
    raw_id_fields = ('user',)
    ordering      = ('-started_at',)


@admin.register(SubscriptionOrder)
class SubscriptionOrderAdmin(admin.ModelAdmin):
    list_display  = ('user', 'plan', 'amount', 'status', 'created_at')
    list_filter   = ('status',)
    raw_id_fields = ('user',)
    ordering      = ('-created_at',)


# ── Misc (bare registrations for simple models) ───────────────────────────────

admin.site.register(MyModel)
