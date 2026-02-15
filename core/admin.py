
# Register your models here.
from django.contrib import admin
from .models import CustomUser

# Register your models
admin.site.register(CustomUser)

# from .models import Project
# @admin.register(Project)
# class ProjectAdmin(admin.ModelAdmin):
#     list_display = ('title', 'owner', 'sponsor', 'status', 'created_at')
#     search_fields = ('title', 'owner__username')
#     list_filter = ('status', 'created_at')

# from .models import Patent
# @admin.register(Patent)
# class PatentAdmin(admin.ModelAdmin):
#     list_display = ('title', 'owner', 'filed_date')
#     search_fields = ('title', 'owner__username')

# from .models import Like
# @admin.register(Like)
# class LikeAdmin(admin.ModelAdmin):
#     list_display = ('user', 'target_user', 'created_at')

# from .models import Interest
# @admin.register(Interest)
# class InterestAdmin(admin.ModelAdmin):
#     list_display = ('user', 'target_user', 'created_at')

