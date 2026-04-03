from django.contrib import admin
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
)

admin.site.register(CustomUser)
admin.site.register(UserProfile)
admin.site.register(Invention)
admin.site.register(Event)
admin.site.register(EventRegistration)
admin.site.register(Project)
admin.site.register(ProjectImage)
admin.site.register(ProjectCollaboration)
admin.site.register(ProjectComment)
admin.site.register(ProjectView)
admin.site.register(ProjectProposal)
admin.site.register(Attachment)
admin.site.register(AttachmentDownload)
admin.site.register(Rating)
admin.site.register(Post)
admin.site.register(PostImage)
admin.site.register(Comment)
admin.site.register(Notification)
admin.site.register(Connection)
admin.site.register(Patent)
admin.site.register(Like)
admin.site.register(Interest)
admin.site.register(Group)
admin.site.register(GroupMembership)
admin.site.register(GroupDiscussion)
admin.site.register(GroupDiscussionComment)
admin.site.register(GroupDiscussionImage)
admin.site.register(Page)
admin.site.register(PagePost)
admin.site.register(PagePostReaction)
admin.site.register(PagePostShare)
admin.site.register(PagePostImage)
admin.site.register(Company)
admin.site.register(CompanyMedia)
admin.site.register(CompanyUpdate)
admin.site.register(Conversation)
admin.site.register(Message)
admin.site.register(MessageReaction)
admin.site.register(Job)
admin.site.register(JobApplication)
admin.site.register(ProfileView)
admin.site.register(PageView)
admin.site.register(ClickEvent)
admin.site.register(NewsItem)
admin.site.register(ContactSubmission)
admin.site.register(Collaboration)
admin.site.register(PatentRequest)
admin.site.register(Proposal)
admin.site.register(SurveyResponse)
admin.site.register(ShareEvent)
admin.site.register(ReadLater)
admin.site.register(AdminPermissions)
admin.site.register(Meeting)
admin.site.register(StageProgressionRequest)
admin.site.register(VerificationRequest)
admin.site.register(PitchRequest)
admin.site.register(Course)
admin.site.register(CourseModule)
admin.site.register(CourseEnrollment)
admin.site.register(MentorProfile)
admin.site.register(MentorshipRequest)
admin.site.register(MentorshipAssignment)
admin.site.register(ConsultingRequest)
admin.site.register(MyModel)
