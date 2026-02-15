from django.urls import path , include
from . import views
from django.contrib.auth import views as auth_views
from .views import edit_profile
from django.conf.urls.static import static
from django.contrib import admin
from django.conf import settings


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


urlpatterns = [
    path('edit-profile/', views.edit_profile, name='edit_profile'),
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
    path('edit_profile/', edit_profile, name='edit_profile'),

    # Authentication
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/<int:user_id>/', views.dashboard, name='dashboard'),


    # path('profile/', profile_view, name='profile'),
    # path('profile/<str:username>/', profile_view, name='profile_with_username'),  # With username

    path('profile/<int:id>/', views.profile_view, name='profile_view'),
    path('profile/', views.my_profile_view, name='my_profile'),

    path('project/<int:project_id>/edit/', views.edit_project, name='edit_project'),

    # path('edit_project/<int:project_id>/', views.edit_project, name='edit_project'),
    # path('delete_project/<int:project_id>/', views.delete_project, name='delete_project'),
    path('project/<int:project_id>/delete/', views.delete_project, name='delete_project'),

    path('update-profile/', update_profile, name='update_profile'),

    path('investors/', views.investors_view, name='investors'),
    path('investors/industry/<str:industry_name>/', views.investors_by_industry_view, name='investors_by_industry'),
    path('investors/by-industry/', views.investors_by_industry, name='investors_by_industry'),

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


    path('filter/industry/<str:industry>/', views.filter_by_industry, name='filter_by_industry'),
    path('filter/user/<int:user_id>/', views.filter_by_user, name='filter_by_user'),
    path('filter/date/<str:date>/', views.filter_by_date, name='filter_by_date'),

    ###investors
    path('investors/', investors_view, name='investors'),
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

    path('connect_investor/<int:investor_id>/', views.connect_investor, name='connect_investor'),
    path('message_investor/<int:investor_id>/', views.message_investor, name='message_investor'),

    path('start_conversation/<int:user_id>/', views.start_conversation, name='start_conversation'),
    path('chat/<int:conversation_id>/', views.chat_page, name='chat_page'),



    path('inbox/', views.inbox, name='inbox'),
    path('sent/', views.sent_items, name='sent_items'),
    path('send_message/<int:recipient_id>/', views.send_message, name='send_message'),

    path('project/<int:project_id>/add_attachment/', views.add_attachment, name='add_attachment'),
    path('user/<int:user_id>/attachments/', views.user_attachments, name='user_attachments'),
    path('user/<int:user_id>/project/<int:project_id>/attachments/', views.user_project_attachments, name='user_project_attachments'),

    ##image uploads
    path('project/<int:project_id>/upload/', views.upload_image, name='upload_image'),
    path('project/<int:project_id>/images/', views.project_images, name='project_images'),



    path('api/projects/', views.get_projects_data, name='get_projects_data'),

]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)