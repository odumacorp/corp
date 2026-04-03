from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0086_credibility_verification'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # ── Event: new fields ──────────────────────────────────────────────
        migrations.AddField(
            model_name='event',
            name='event_type',
            field=models.CharField(
                choices=[('general','General Event'),('demo_day','Demo Day'),
                         ('investor_meetup','Investor Meetup'),('workshop','Workshop'),
                         ('conference','Conference'),('networking','Networking'),('webinar','Webinar')],
                default='general', max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='event',
            name='is_featured',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='event',
            name='max_attendees',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),

        # ── Course ────────────────────────────────────────────────────────
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('slug', models.SlugField(max_length=270, unique=True)),
                ('description', models.TextField(blank=True, default='')),
                ('category', models.CharField(choices=[
                    ('entrepreneurship','Entrepreneurship'),('fundraising','Fundraising & Investment'),
                    ('innovation','Innovation & Design'),('tech','Technology & Product'),
                    ('finance','Finance & Accounting'),('leadership','Leadership & Management'),
                    ('marketing','Marketing & Growth'),('legal','Legal & Compliance'),
                ], default='entrepreneurship', max_length=50)),
                ('level', models.CharField(choices=[('beginner','Beginner'),('intermediate','Intermediate'),('advanced','Advanced')], default='beginner', max_length=20)),
                ('instructor_name', models.CharField(blank=True, default='Oduma Team', max_length=200)),
                ('cover_image', models.ImageField(blank=True, null=True, upload_to='course_covers/')),
                ('duration_hours', models.PositiveIntegerField(default=0)),
                ('is_published', models.BooleanField(default=False)),
                ('is_featured', models.BooleanField(default=False)),
                ('is_free', models.BooleanField(default=True)),
                ('price', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('instructor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='courses_taught', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-is_featured', '-created_at']},
        ),

        # ── CourseModule ──────────────────────────────────────────────────
        migrations.CreateModel(
            name='CourseModule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('content', models.TextField(blank=True, default='')),
                ('video_url', models.URLField(blank=True, default='')),
                ('order', models.PositiveIntegerField(default=0)),
                ('duration_minutes', models.PositiveIntegerField(default=0)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='modules', to='core.course')),
            ],
            options={'ordering': ['order']},
        ),

        # ── CourseEnrollment ──────────────────────────────────────────────
        migrations.CreateModel(
            name='CourseEnrollment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('enrolled','Enrolled'),('in_progress','In Progress'),('completed','Completed'),('dropped','Dropped')], default='enrolled', max_length=20)),
                ('progress', models.PositiveIntegerField(default=0)),
                ('enrolled_at', models.DateTimeField(auto_now_add=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='enrollments', to='core.course')),
                ('last_module', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='core.coursemodule')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='course_enrollments', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-enrolled_at'], 'unique_together': {('user', 'course')}},
        ),

        # ── MentorProfile ─────────────────────────────────────────────────
        migrations.CreateModel(
            name='MentorProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('expertise', models.CharField(choices=[
                    ('fundraising','Fundraising'),('product','Product Development'),
                    ('strategy','Business Strategy'),('tech','Technology'),
                    ('marketing','Marketing & Sales'),('legal','Legal & IP'),
                    ('finance','Finance & Accounting'),('operations','Operations & Scaling'),
                ], default='strategy', max_length=50)),
                ('bio', models.TextField(blank=True, default='')),
                ('industries', models.CharField(blank=True, default='', max_length=500)),
                ('availability', models.CharField(blank=True, default='', max_length=200)),
                ('max_mentees', models.PositiveIntegerField(default=3)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='mentor_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),

        # ── MentorshipRequest ─────────────────────────────────────────────
        migrations.CreateModel(
            name='MentorshipRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField(blank=True, default='')),
                ('goals', models.TextField(blank=True, default='')),
                ('status', models.CharField(choices=[('pending','Pending'),('accepted','Accepted'),('declined','Declined'),('completed','Completed')], default='pending', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('responded_at', models.DateTimeField(blank=True, null=True)),
                ('mentor_note', models.TextField(blank=True, default='')),
                ('from_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mentorship_requests_sent', to=settings.AUTH_USER_MODEL)),
                ('mentor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mentorship_requests', to='core.mentorprofile')),
                ('project', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='mentorship_requests', to='core.project')),
            ],
            options={'ordering': ['-created_at'], 'unique_together': {('from_user', 'mentor', 'project')}},
        ),

        # ── MentorshipAssignment ──────────────────────────────────────────
        migrations.CreateModel(
            name='MentorshipAssignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('active','Active'),('paused','Paused'),('completed','Completed')], default='active', max_length=20)),
                ('assigned_at', models.DateTimeField(auto_now_add=True)),
                ('notes', models.TextField(blank=True, default='')),
                ('mentor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mentorship_assignments', to='core.mentorprofile')),
                ('mentee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mentorship_assignments', to=settings.AUTH_USER_MODEL)),
                ('project', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='mentorship_assignments', to='core.project')),
            ],
            options={'ordering': ['-assigned_at']},
        ),

        # ── ConsultingRequest ─────────────────────────────────────────────
        migrations.CreateModel(
            name='ConsultingRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(choices=[
                    ('strategy','Business Strategy'),('fundraising','Fundraising Preparation'),
                    ('technical','Technical Advisory'),('market_research','Market Research'),
                    ('legal','Legal & IP'),('pitch_prep','Pitch Preparation'),
                    ('operations','Operations & Scaling'),('other','Other'),
                ], default='strategy', max_length=30)),
                ('description', models.TextField()),
                ('urgency', models.CharField(choices=[('low','Low'),('medium','Medium'),('high','High')], default='medium', max_length=20)),
                ('status', models.CharField(choices=[('submitted','Submitted'),('reviewing','Under Review'),('scheduled','Call Scheduled'),('completed','Completed'),('declined','Declined')], default='submitted', max_length=20)),
                ('submitted_at', models.DateTimeField(auto_now_add=True)),
                ('admin_note', models.TextField(blank=True, default='')),
                ('scheduled_at', models.DateTimeField(blank=True, null=True)),
                ('project', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='consulting_requests', to='core.project')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='consulting_requests', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-submitted_at']},
        ),
    ]
