from django.urls import path , include
from . import views
from django.contrib.auth import views as auth_views
from .views import edit_profile
from django.conf.urls.static import static
from django.contrib import admin
from django.conf import settings
from django.contrib.sitemaps.views import sitemap
from .sitemaps import StaticSitemap, AppPagesSitemap, ProjectSitemap, PostSitemap, ProfileSitemap, CompanySitemap

_sitemaps = {
    'static':   StaticSitemap(),
    'app':      AppPagesSitemap(),
    'projects': ProjectSitemap(),
    'posts':    PostSitemap(),
    'profiles': ProfileSitemap(),
    'companies':CompanySitemap(),
}


from .views import contact

from django.views.generic import TemplateView

from .views import profile_view, my_projects
from .views import update_profile
# from .views import networks_view
from .views import linkedin
# from .views import ProjectListView

from .views import register, login_view, logout_view

from .views import UserProfileView

from .views import investors_view
from .views import innovators_view


from django.views.generic.base import RedirectView

# Redirect raw .html static-file URLs → canonical Django URLs (permanent 301)
# These get served by whitenoise as unprocessed files and show as "not tagged" in GA.
_html_redirects = [
    path('about.html',         RedirectView.as_view(url='/about/',         permanent=True)),
    path('app.html',           RedirectView.as_view(url='/app/',           permanent=True)),
    path('dashboard.html',     RedirectView.as_view(url='/dashboard/',     permanent=True)),
    path('events.html',        RedirectView.as_view(url='/events/',        permanent=True)),
    path('jobs.html',          RedirectView.as_view(url='/jobs/',          permanent=True)),
    path('networks.html',      RedirectView.as_view(url='/networks/',      permanent=True)),
    path('notifications.html', RedirectView.as_view(url='/notifications/', permanent=True)),
    path('services.html',      RedirectView.as_view(url='/services/',      permanent=True)),
    # messages.html is handled by the inbox view
    path('messages.html',      RedirectView.as_view(url='/inbox/',         permanent=True)),
]

urlpatterns = _html_redirects + [
    path('sitemap.xml', sitemap, {'sitemaps': _sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', views.robots_txt, name='robots_txt'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('admin/contact-submissions/', views.contact_submissions, name='contact_submissions'),
    path('admin/contact-submissions/<int:sub_id>/reply/', views.reply_contact_submission, name='reply_contact_submission'),
    path('admin/login/', views.admin_login_2fa, name='django_admin_login'),  # intercept before admin.site.urls
    path('admin/login-as-odu/', views.login_as_odu, name='login_as_odu'),
    path('admin/return-from-odu/', views.return_from_odu, name='return_from_odu'),
    path('admin/trigger-odu-post/', views.trigger_odu_post, name='trigger_odu_post'),
    path('admin/publish-odu-post/', views.publish_odu_post, name='publish_odu_post'),
    path('admin/preview-odu-image/', views.preview_odu_image, name='preview_odu_image'),
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('app/', views.app_view, name='app'),
    path('about/', views.about, name='about'),
    path('networks/', views.networks, name='networks'),
    path('events/', views.events, name='events'),
    path('services/', views.services, name='services'),
    path('jobs/', views.jobs, name='jobs'),
    path('notifications/', views.notifications, name='notifications'),
    path('search/', views.search, name='search'),
    path('my_projects/', views.my_projects, name='my_projects'),

    ##auth
    path('accounts/', include('allauth.urls')),

    ##contact form
    path("contact/", contact, name="contact"),
    ##password
    path("update_password/", views.update_password, name="update_password"),

    #company suggestions
    # edit_profile already registered above as 'edit-profile/'

    # Authentication
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/<int:user_id>/', views.dashboard, name='dashboard'),


    # path('profile/', profile_view, name='profile'),
    # path('profile/<str:username>/', profile_view, name='profile_with_username'),  # With username

    path('profile/<int:id>/', views.profile_view_by_id, name='profile_view_by_id'),  # legacy redirect
    path('profile/<str:username>/', views.profile_view, name='profile_view'),
    path('profile/', views.my_profile_view, name='my_profile'),

    path('project/<int:project_id>/edit/', views.edit_project, name='edit_project'),
    path('attachment/<int:attachment_id>/edit/', views.edit_attachment, name='edit_attachment'),

    # path('edit_project/<int:project_id>/', views.edit_project, name='edit_project'),
    # path('delete_project/<int:project_id>/', views.delete_project, name='delete_project'),
    path('project/<int:project_id>/delete/', views.delete_project, name='delete_project'),

    path('update-profile/', update_profile, name='update_profile'),
    path('update-profile/remove-photo/', views.remove_profile_photo, name='remove_profile_photo'),

    path('investors/', views.investors_view, name='investors'),
    path('investors/industry/<str:industry_name>/', views.investors_by_industry_view, name='investors_by_industry'),
    path('investors/by-industry/', views.investors_by_industry, name='investors_by_industry_generic'),

    ##all users
    # path('networks/', views.networks_view, name='networks'),
    # path('networks/', networks_view, name='networks'),
    ##unfollow
    path('unfollow/<int:user_id>/', views.unfollow_user, name='unfollow_user'),

    ##linkedin
    path('linkedin/',views.linkedin, name='linkedin'),

    ##usernames

    path('user/<int:user_id>/', UserProfileView.as_view(), name='user_profile'),

    path('projects/<int:pk>/', views.project_detail, name='project_detail'),
    path('projects/<int:pk>/request-progression/', views.request_stage_progression, name='request_stage_progression'),


    path('filter/industry/<str:industry>/', views.filter_by_industry, name='filter_by_industry'),
    path('filter/user/<int:user_id>/', views.filter_by_user, name='filter_by_user'),
    path('filter/date/<str:date>/', views.filter_by_date, name='filter_by_date'),

    ##innovator
    path('innovators/', innovators_view, name='innovators'),
    path('innovator/<int:user_id>/', views.view_innovator, name='view_innovator'),

    path('connect/<int:user_id>/', views.connect_user, name='connect_user'),
    path('connect_innovator/<int:user_id>/', views.connect_innovator, name='connect_innovator'),
    path('disconnect/<int:user_id>/', views.disconnect_user, name='disconnect_user'),

    path('message_innovator/<int:user_id>/', views.message_innovator, name='message_innovator'),
    path('rate_project/<int:pk>/', views.rate_project, name='rate_project'),
    path('like_project/<int:pk>/', views.like_project, name='like_project'),


    ##connect with investor
    path('connect_investor/<int:investor_id>/', views.connect_investor, name='connect_investor'),
    path('message_investor/<int:investor_id>/', views.message_investor, name='message_investor'),

    path('start_conversation/<int:user_id>/', views.start_conversation, name='start_conversation'),
    path('chat/<int:conversation_id>/', views.chat_page_by_id, name='chat_page_by_id'),  # legacy redirect
    path('chat/<str:slug>/', views.chat_page, name='chat_page'),
    path('chat/<str:slug>/resolve/', views.resolve_conversation, name='resolve_conversation'),
    path('project-chat/<int:project_id>/', views.start_project_conversation, name='start_project_conversation'),
    path('quick-message/', views.quick_message, name='quick_message'),



    path('inbox/', views.inbox, name='inbox'),
    path('inbox/user-search/', views.user_search_api, name='user_search_api'),
    path('sent/', views.sent_items, name='sent_items'),
    path('send_message/<int:recipient_id>/', views.send_message, name='send_message'),

    path('project/<int:project_id>/add_attachment/', views.add_attachment, name='add_attachment'),
    path('user/<int:user_id>/attachments/', views.user_attachments, name='user_attachments'),
    path('user/<int:user_id>/project/<int:project_id>/attachments/', views.user_project_attachments, name='user_project_attachments'),

    ##image uploads
    path('project/<int:project_id>/upload/', views.upload_image, name='upload_image'),
    path('project/<int:project_id>/images/', views.project_images, name='project_images'),



    path('api/projects/', views.get_projects_data, name='get_projects_data'),
    path('api/hashtags/popular/', views.popular_hashtags, name='popular_hashtags'),
    path('api/counts/', views.get_counts, name='get_counts'),

    path('hashtags/<slug:tag>/', views.hashtag_feed, name='hashtag_feed'),

    path('faq/', TemplateView.as_view(template_name='faq.html'), name='faq'),
    path('test-404/', TemplateView.as_view(template_name='404.html'), name='test_404'),
    path('test-500/', TemplateView.as_view(template_name='500.html'), name='test_500'),
    path('privacy/', TemplateView.as_view(template_name='privacy_policy.html'), name='privacy_policy'),
    path('terms/', TemplateView.as_view(template_name='terms.html'), name='terms'),
    path('offline/', TemplateView.as_view(template_name='offline.html'), name='offline'),
    path('social-campaigns/', views.social_campaigns, name='social_campaigns'),
    path('service-worker.js', views.service_worker, name='service_worker'),

    # Profile alias
    path('profile/me/', views.profile_alias, name='profile'),

    # Project list
    path('projects/', views.project_list, name='project_list'),
    path('projects/create/', views.create_project, name='create_project'),

    # Meetings
    path('meetings/', views.meetings_list, name='meetings_list'),
    path('meetings/create/', views.create_meeting, name='create_meeting'),
    path('meetings/<int:meeting_id>/join/', views.join_meeting, name='join_meeting'),
    path('meetings/<int:meeting_id>/end/', views.end_meeting, name='end_meeting'),
    path('meetings/<int:meeting_id>/share/', views.share_meeting, name='share_meeting'),
    path('meetings/<int:meeting_id>/recordings/', views.meeting_recordings, name='meeting_recordings'),

    # Investor dashboard + investor actions
    path('investor/dashboard/', views.investor_dashboard, name='investor_dashboard'),
    path('investor/profile/update/', views.update_investor_profile, name='update_investor_profile'),
    path('projects/<int:pk>/request-pitch/', views.request_pitch, name='request_pitch'),
    path('projects/<int:pk>/interest/', views.toggle_project_interest, name='toggle_project_interest'),

    # Proposals
    path('proposals/', views.proposals_list, name='proposals_list'),

    # Connections
    path('connections/<int:conn_id>/accept/', views.accept_connection, name='accept_connection'),
    path('connections/<int:conn_id>/reject/', views.reject_connection, name='reject_connection'),
    path('notifications/<int:notif_id>/read/', views.mark_notif_read, name='mark_notif_read'),
    path('notifications/<int:notif_id>/dismiss/', views.dismiss_notif, name='dismiss_notif'),

    # Comments
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('comment/<int:comment_id>/edit/', views.edit_comment, name='edit_comment'),

    # Messages
    path('messages/<int:message_id>/', views.message_detail, name='message_detail'),
    path('messages/<int:message_id>/delete/', views.delete_message, name='delete_message'),
    path('messages/<int:message_id>/react/', views.toggle_message_reaction, name='toggle_message_reaction'),
    path('chat/message/<int:message_id>/delete/', views.chat_delete_message, name='chat_delete_message'),
    path('chat/message/<int:message_id>/edit/',   views.chat_edit_message,   name='chat_edit_message'),
    path('chat/share-to-feed/',                   views.chat_share_to_feed,  name='chat_share_to_feed'),

    # Contact submissions (also registered above admin/ to take priority)

    # Admin panel
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('admin-panel/login/', views.admin_login_2fa, name='admin_login_2fa'),
    path('admin-panel/login/setup-totp/', views.admin_setup_totp, name='admin_setup_totp'),
    path('admin-panel/login/verify-totp/', views.admin_verify_totp, name='admin_verify_totp'),
    path('admin-panel/2fa/disable/<int:user_id>/', views.admin_disable_2fa, name='admin_disable_2fa'),
    path('admin-panel/2fa/setup/<int:user_id>/', views.admin_setup_2fa_for, name='admin_setup_2fa_for'),
    path('admin-panel/stats/range/', views.admin_stats_range, name='admin_stats_range'),
    path('admin-panel/toggle-view/', views.toggle_admin_view, name='toggle_admin_view'),
    path('admin-panel/event/add/', views.admin_add_event, name='admin_add_event'),
    path('admin-panel/job/add/', views.admin_add_job, name='admin_add_job'),
    path('admin-panel/news/add/', views.admin_add_news, name='admin_add_news'),
    path('admin-panel/sub-admin/add/', views.admin_add_sub_admin, name='admin_add_sub_admin'),
    path('admin-panel/notification/broadcast/', views.admin_broadcast_notification, name='admin_broadcast_notification'),
    path('admin-panel/feature/toggle/', views.admin_toggle_feature, name='admin_toggle_feature'),
    path('admin-panel/project/<int:project_id>/status/', views.admin_change_project_status, name='admin_change_project_status'),
    path('admin-panel/user/<int:user_id>/role/', views.admin_change_role, name='admin_change_role'),
    path('admin-panel/comment/<int:comment_id>/edit/', views.admin_edit_comment, name='admin_edit_comment'),
    path('admin-panel/event/<int:event_id>/edit/', views.admin_edit_event, name='admin_edit_event'),
    path('admin-panel/group/<int:group_id>/edit/', views.admin_edit_group, name='admin_edit_group'),
    path('admin-panel/job/<int:job_id>/edit/', views.admin_edit_job, name='admin_edit_job'),
    path('admin-panel/message/<int:message_id>/edit/', views.admin_edit_message, name='admin_edit_message'),
    path('admin-panel/news/<int:news_id>/edit/', views.admin_edit_news, name='admin_edit_news'),
    path('admin-panel/page/<int:page_id>/edit/', views.admin_edit_page, name='admin_edit_page'),
    path('admin-panel/post/<int:post_id>/approve/', views.admin_approve_post, name='admin_approve_post'),
    path('admin-panel/post/<int:post_id>/reject/', views.admin_reject_post, name='admin_reject_post'),
    path('admin-panel/post/<int:post_id>/edit/', views.admin_edit_post, name='admin_edit_post'),
    path('admin-panel/project/<int:project_id>/edit/', views.admin_edit_project, name='admin_edit_project'),
    path('admin-panel/event/<int:event_id>/attendees/', views.admin_event_attendees, name='admin_event_attendees'),
    path('admin-panel/message/<int:message_id>/flag/', views.admin_flag_message, name='admin_flag_message'),
    path('admin-panel/sub-admin/<int:user_id>/manage/', views.admin_manage_sub_admin, name='admin_manage_sub_admin'),
    path('admin-panel/user/<int:user_id>/reset-password/', views.admin_reset_user_password, name='admin_reset_user_password'),
    path('admin-panel/user/<int:user_id>/set-password/', views.admin_set_user_password, name='admin_set_user_password'),
    path('admin-panel/comment/<int:comment_id>/hide/', views.admin_toggle_hide_comment, name='admin_toggle_hide_comment'),
    path('admin-panel/event/<int:event_id>/hide/', views.admin_toggle_hide_event, name='admin_toggle_hide_event'),
    path('admin-panel/group/<int:group_id>/hide/', views.admin_toggle_hide_group, name='admin_toggle_hide_group'),
    path('admin-panel/job/<int:job_id>/hide/', views.admin_toggle_hide_job, name='admin_toggle_hide_job'),
    path('admin-panel/message/<int:message_id>/hide/', views.admin_toggle_hide_message, name='admin_toggle_hide_message'),
    path('admin-panel/news/<int:news_id>/hide/', views.admin_toggle_hide_news, name='admin_toggle_hide_news'),
    path('admin-panel/page/<int:page_id>/hide/', views.admin_toggle_hide_page, name='admin_toggle_hide_page'),
    path('admin-panel/post/<int:post_id>/hide/', views.admin_toggle_hide_post, name='admin_toggle_hide_post'),
    path('admin-panel/post-comment/<int:comment_id>/hide/', views.admin_toggle_hide_post_comment, name='admin_toggle_hide_post_comment'),
    path('admin-panel/project/<int:project_id>/hide/', views.admin_toggle_hide_project, name='admin_toggle_hide_project'),
    path('admin-panel/user/<int:user_id>/hide/', views.admin_toggle_hide_user, name='admin_toggle_hide_user'),
    path('admin-panel/user/<int:user_id>/toggle/', views.admin_toggle_user, name='admin_toggle_user'),
    path('admin-panel/message/<int:message_id>/unflag/', views.admin_unflag_message, name='admin_unflag_message'),
    # Admin delete actions
    path('admin-panel/user/<int:user_id>/delete/',           views.admin_delete_user,       name='admin_delete_user'),
    path('admin-panel/project/<int:project_id>/delete/',     views.admin_delete_project,    name='admin_delete_project'),
    path('admin-panel/post/<int:post_id>/delete/',           views.admin_delete_post,       name='admin_delete_post'),
    path('admin-panel/event/<int:event_id>/delete/',         views.admin_delete_event,      name='admin_delete_event'),
    path('admin-panel/news/<int:news_id>/delete/',           views.admin_delete_news,       name='admin_delete_news'),
    path('admin-panel/job/<int:job_id>/delete/',             views.admin_delete_job,        name='admin_delete_job'),
    path('admin-panel/connection/<int:connection_id>/accept/', views.admin_accept_connection, name='admin_accept_connection'),
    path('admin-panel/connection/<int:connection_id>/delete/', views.admin_delete_connection, name='admin_delete_connection'),
    path('admin-panel/comment/<int:comment_id>/delete/',     views.admin_delete_comment,    name='admin_delete_comment'),
    path('admin-panel/group/<int:group_id>/delete/',         views.admin_delete_group,      name='admin_delete_group'),
    path('admin-panel/page/<int:page_id>/delete/',           views.admin_delete_page,       name='admin_delete_page'),
    path('admin-panel/sub-admin/<int:user_id>/remove/',      views.admin_remove_sub_admin,  name='admin_remove_sub_admin'),
    # Content management
    path('admin-panel/content/',                              views.admin_content,            name='admin_content'),
    path('admin-panel/content/settings/',                     views.admin_save_site_settings, name='admin_save_site_settings'),
    path('admin-panel/content/announcement/save/',            views.admin_save_announcement,  name='admin_save_announcement'),
    path('admin-panel/content/announcement/<int:pk>/delete/', views.admin_delete_announcement,name='admin_delete_announcement'),
    path('admin-panel/content/announcement/<int:pk>/toggle/', views.admin_toggle_announcement,name='admin_toggle_announcement'),
    path('admin-panel/content/blog/save/',                    views.admin_save_blog,          name='admin_save_blog'),
    path('admin-panel/content/blog/<int:pk>/delete/',         views.admin_delete_blog,        name='admin_delete_blog'),
    path('admin-panel/content/blog/<int:pk>/toggle/',         views.admin_toggle_blog,        name='admin_toggle_blog'),
    path('admin-panel/content/page/<int:pk>/toggle/',         views.admin_toggle_site_page,   name='admin_toggle_site_page'),
    path('admin-panel/content/page/<int:pk>/save/',           views.admin_save_site_page,     name='admin_save_site_page'),
    # Pipeline stage approvals
    path('admin-panel/stage-approvals/', views.admin_stage_approvals, name='admin_stage_approvals'),
    path('admin-panel/stage-approval/<int:req_id>/approve/', views.admin_approve_stage, name='admin_approve_stage'),
    path('admin-panel/stage-approval/<int:req_id>/reject/', views.admin_reject_stage, name='admin_reject_stage'),
    # Verification & project reviews
    path('verification/request/', views.submit_verification_request, name='submit_verification_request'),
    path('projects/<int:pk>/submit-review/', views.submit_project_for_review, name='submit_project_for_review'),
    path('admin-panel/verifications/', views.admin_verification_queue, name='admin_verification_queue'),
    path('admin-panel/verification/<int:req_id>/approve/', views.admin_approve_verification, name='admin_approve_verification'),
    path('admin-panel/verification/<int:req_id>/reject/', views.admin_reject_verification, name='admin_reject_verification'),
    path('admin-panel/user/<int:user_id>/verify/', views.admin_verify_user, name='admin_verify_user'),
    path('admin-panel/project-reviews/', views.admin_project_review_queue, name='admin_project_review_queue'),
    path('admin-panel/project/<int:pk>/review-status/', views.admin_set_project_review_status, name='admin_set_project_review_status'),
    # Analytics API
    path('admin-panel/analytics/data/',   views.admin_analytics_data,   name='admin_analytics_data'),
    path('admin-panel/analytics/export/', views.admin_analytics_export, name='admin_analytics_export'),

    # Companies
    path('companies/', views.companies_list, name='companies_list'),
    path('companies/create/', views.create_company, name='create_company'),
    path('company/<int:company_id>/', views.company_profile, name='company_profile'),
    path('company/<int:company_id>/edit/', views.company_edit, name='company_edit'),
    path('company/<int:company_id>/follow/', views.company_follow, name='company_follow'),
    path('company/<int:company_id>/post/', views.company_post_update, name='company_post_update'),
    path('company/<int:company_id>/media/upload/', views.company_upload_media, name='company_upload_media'),
    path('company/<int:company_id>/media/<int:media_id>/delete/', views.company_delete_media, name='company_delete_media'),
    path('company/<int:company_id>/update/<int:update_id>/delete/', views.company_delete_update, name='company_delete_update'),

    # Groups
    path('groups/', views.groups_list, name='groups_list'),
    path('groups/create/', views.group_create, name='group_create'),
    path('groups/<int:group_id>/', views.group_detail, name='group_detail'),
    path('groups/<int:group_id>/discussions/<int:discussion_id>/', views.group_discussion_detail, name='group_discussion_detail'),
    path('groups/<int:group_id>/discussions/<int:discussion_id>/media/', views.group_discussion_media, name='group_discussion_media'),
    path('groups/<int:group_id>/discussions/<int:discussion_id>/react/', views.group_discussion_react, name='group_discussion_react'),
    path('groups/<int:group_id>/invite/', views.group_invite, name='group_invite'),
    path('groups/<int:group_id>/join/', views.group_join_request, name='group_join_request'),
    path('groups/<int:group_id>/leave/', views.group_leave, name='group_leave'),
    path('groups/<int:group_id>/post/', views.group_post_discussion, name='group_post_discussion'),
    path('groups/<int:group_id>/respond/<int:member_id>/', views.group_respond, name='group_respond'),
    path('groups/<int:group_id>/accept/', views.group_accept_invite, name='group_accept_invite'),
    path('groups/<int:group_id>/discussions/<int:discussion_id>/comments/<int:comment_id>/react/', views.group_comment_react, name='group_comment_react'),
    path('groups/<int:group_id>/edit/', views.group_edit, name='group_edit'),
    path('groups/<int:group_id>/delete/', views.group_delete, name='group_delete'),

    # Innovator page / profile
    path('innovator/page/', views.innovator_page, name='innovator_page'),
    path('innovator/<int:user_id>/profile/', views.innovator_profile, name='innovator_profile'),

    # My businesses
    path('my-businesses/', views.my_businesses, name='my_businesses'),

    # Pages
    path('pages/', views.pages_list, name='pages_list'),
    path('pages/create/', views.page_create, name='page_create'),
    path('pages/<int:page_id>/', views.page_detail, name='page_detail'),
    path('pages/<int:page_id>/follow/', views.page_follow_toggle, name='page_follow_toggle'),
    path('pages/<int:page_id>/posts/<int:post_id>/react/', views.page_post_react, name='page_post_react'),
    path('pages/<int:page_id>/posts/<int:post_id>/share/', views.page_post_share, name='page_post_share'),
    path('pages/<int:page_id>/media/<int:post_id>/', views.page_post_media, name='page_post_media'),
    path('pages/<int:page_id>/edit/', views.page_edit, name='page_edit'),
    path('pages/<int:page_id>/delete/', views.page_delete, name='page_delete'),

    # Posts — canonical slug URL + legacy numeric redirects
    path('posts/<int:post_id>/', views.post_detail_by_id, name='post_detail_by_id'),
    path('posts/<slug:slug>/', views.post_detail, name='post_detail'),
    path('posts/<int:post_id>/edit/', views.edit_post, name='edit_post'),
    path('posts/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path('posts/<int:post_id>/media/', views.post_media, name='post_media'),
    path('posts/<int:post_id>/interest/', views.toggle_post_interest, name='toggle_post_interest'),
    path('posts/<int:post_id>/like/', views.toggle_post_like, name='toggle_post_like'),
    path('posts/<int:post_id>/react/', views.toggle_post_reaction, name='toggle_post_reaction'),
    path('posts/<int:post_id>/repost/', views.toggle_post_repost, name='toggle_post_repost'),
    path('posts/<int:post_id>/conversation/', views.start_post_conversation, name='start_post_conversation'),
    path('posts/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('polls/<int:poll_id>/vote/', views.poll_vote, name='poll_vote'),

    # Project actions
    path('projects/<int:project_id>/collaborate/', views.project_collaborate, name='project_collaborate'),
    path('projects/<int:project_id>/proposal/', views.project_send_proposal, name='project_send_proposal'),
    path('projects/<int:project_id>/comment/', views.add_project_comment, name='add_project_comment'),

    # Attachment download tracking
    path('attachments/<int:attachment_id>/download/', views.download_attachment, name='download_attachment'),
    path('chat/attachments/<int:attachment_id>/download/', views.download_message_attachment, name='download_message_attachment'),
    path('chat/attachments/<int:attachment_id>/view/', views.view_message_attachment, name='view_message_attachment'),

    # Jobs
    path('jobs/post/',              views.user_post_job, name='user_post_job'),
    path('jobs/create/',            views.user_post_job, name='create_job'),
    path('jobs/<int:pk>/',          views.job_detail,    name='job_detail'),

    # User view alias
    path('users/<int:user_id>/', views.view_user, name='view_user'),

    # Project AI description generator
    path('projects/generate-description/', views.generate_project_description, name='generate_project_description'),

    # General AI assist (titles, taglines, descriptions)
    path('ai/assist/', views.ai_assist, name='ai_assist'),
    path('ai/image-suggest/', views.ai_image_suggest, name='ai_image_suggest'),
    path('ai/fetch-image/', views.proxy_fetch_image, name='proxy_fetch_image'),

    # Odu chatbot + feedback
    path('odu/chat/', views.odu_chat, name='odu_chat'),
    path('odu/feedback/', views.submit_feedback, name='submit_feedback'),

    # Share tracking
    path('track/share/', views.track_share, name='track_share'),
    path('share/go/', views.share_redirect, name='share_redirect'),

    # Read Later
    path('read-later/', views.read_later_list, name='read_later_list'),
    path('read-later/toggle/', views.toggle_read_later, name='toggle_read_later'),
    path('read-later/<int:item_id>/remove/', views.remove_read_later, name='remove_read_later'),

    # Pin
    path('pin/toggle/', views.toggle_pin, name='toggle_pin'),

    # ── Oduma Corp Services ──────────────────────────────────────────────────
    # Training
    path('training/',                                     views.training_hub,            name='training_hub'),
    path('training/<slug:slug>/',                         views.course_detail,           name='course_detail'),
    path('training/<slug:slug>/enroll/',                  views.enroll_course,           name='enroll_course'),
    path('training/<slug:slug>/progress/',                views.update_course_progress,  name='update_course_progress'),
    # Mentorship
    path('mentorship/',                                   views.mentorship_hub,          name='mentorship_hub'),
    path('mentorship/request/<int:mentor_id>/',           views.request_mentor,          name='request_mentor'),
    # Consulting
    path('consulting/',                                   views.request_consulting,      name='request_consulting'),
    path('consulting/project/<int:project_id>/',          views.request_consulting,      name='request_consulting_for_project'),
    path('consulting/my/',                                views.my_consulting_requests,  name='my_consulting_requests'),
    # Events hub
    path('events-hub/',                                   views.events_hub,              name='events_hub'),
    path('events-hub/post/',                              views.user_post_event,         name='user_post_event'),
    path('events-hub/<int:event_id>/register/',           views.register_for_event,      name='register_for_event'),
    # Blog
    path('blog/',                                         views.blog_list,               name='blog_list'),
    path('blog/<slug:slug>/',                             views.blog_detail,             name='blog_detail'),
    # Matching
    path('matches/',                                      views.top_matches_for_investor, name='top_matches_for_investor'),
    path('projects/<int:pk>/investor-matches/',           views.project_investor_matches, name='project_investor_matches'),
    # Innovator dashboard
    path('innovator/dashboard/',                          views.innovator_dashboard,     name='innovator_dashboard'),

    # Innovator agreement workflow
    path('proposals/<int:proposal_id>/agree/',   views.agree_to_proposal,      name='agree_to_proposal'),
    path('proposals/<int:proposal_id>/decline/', views.decline_proposal,        name='decline_proposal'),
    path('proposals/<int:proposal_id>/action/', views.proposal_action,          name='proposal_action'),
    path('collaborations/<int:collab_id>/agree/',   views.agree_to_collaboration, name='agree_to_collaboration'),
    path('collaborations/<int:collab_id>/decline/', views.decline_collaboration,  name='decline_collaboration'),
    path('patent-requests/<int:pr_id>/agree/', views.agree_to_patent_request, name='agree_to_patent_request'),

    # Share to chat
    path('chat/share/', views.share_to_chat, name='share_to_chat'),

    # Subscription
    path('subscription/',          views.subscription_plans,    name='subscription_plans'),
    path('subscription/my-plan/',  views.my_subscription,       name='my_subscription'),
    path('subscription/upgrade/',  views.upgrade_subscription,  name='upgrade_subscription'),
    path('subscription/cancel/',   views.cancel_subscription,   name='cancel_subscription'),

    # Intercept raw chat attachment media URLs → styled viewer
    path('media/chat_attachments/<path:file_path>', views.media_chat_attachment_viewer, name='media_chat_attachment_viewer'),

    # Media viewer (collage click-through, gallery with thumbnail strip)
    path('view-media/', views.view_media, name='view_media'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)