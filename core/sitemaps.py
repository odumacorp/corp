from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Project, Post, CustomUser, Company, Page, Group


class StaticSitemap(Sitemap):
    priority = 1.0
    changefreq = 'weekly'

    def items(self):
        return [
            'index', 'login', 'register', 'jobs', 'companies_list',
        ]

    def location(self, item):
        return reverse(item)


class AppPagesSitemap(Sitemap):
    priority = 0.9
    changefreq = 'daily'

    def items(self):
        return [
            'app', 'explore', 'courses_list', 'mentors_list',
        ]

    def location(self, item):
        try:
            return reverse(item)
        except Exception:
            return '/'


class ProjectSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return Project.objects.filter(is_hidden=False).order_by('-created_at')[:500]

    def lastmod(self, obj):
        return obj.created_at

    def location(self, obj):
        try:
            return reverse('project_detail', args=[obj.pk])
        except Exception:
            return '/'


class PostSitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.7

    def items(self):
        return Post.objects.filter(is_hidden=False).order_by('-created_at')[:500]

    def lastmod(self, obj):
        return obj.created_at

    def location(self, obj):
        if obj.slug:
            try:
                return reverse('post_detail', kwargs={'slug': obj.slug})
            except Exception:
                pass
        return '/'


class ProfileSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.6

    def items(self):
        return CustomUser.objects.filter(
            is_active=True, is_hidden=False
        ).exclude(user_type='admin').order_by('-date_joined')[:300]

    def location(self, obj):
        try:
            return reverse('profile_view', kwargs={'username': obj.username})
        except Exception:
            return '/'


class CompanySitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.6

    def items(self):
        return Company.objects.filter(is_hidden=False).order_by('-created_at')[:200]

    def location(self, obj):
        try:
            return reverse('company_profile', args=[obj.pk])
        except Exception:
            return '/'
