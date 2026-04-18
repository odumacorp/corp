# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Oduma Corp** is a Django 5.1 web platform connecting innovators and investors across Africa. Users register with one of three roles (`innovator`, `investor`, `admin`) and can post projects, send messages, connect with each other, rate/like projects, collaborate on proposals, join groups, follow company pages, schedule meetings, take courses, and access mentorship and consulting services.

The platform includes an **Odu** system bot (auto-created user) that sends welcome messages to new users and powers a built-in chatbot.

## Development Setup

```bash
python -m venv env
source env/bin/activate
pip install -r requirements.txt
cp settings.ini.example settings.ini   # fill in required values
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

`python-decouple` reads config from `settings.ini` locally (not `.env`). Required variables: `DEBUG`, `SECRET_KEY`, `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS`. Optional: `DATABASE_URL` (defaults to SQLite), `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` (for Google OAuth), `ANTHROPIC_API_KEY`, `ZOOM_ACCOUNT_ID`, `ZOOM_CLIENT_ID`, `ZOOM_CLIENT_SECRET`.

> Note: `requirements.txt` lists core packages (Django, gunicorn, whitenoise, psycopg, anthropic, etc.) but does not include `django-allauth`, `channels`, `python-decouple`, or `python-dotenv`, which are used by the app. These may be installed separately or pinned elsewhere.

Docker is also supported:
```bash
docker build -t oduma-connect .
docker run -p 8000:8000 --env-file .env oduma-connect
```

Seed development data:
```bash
python manage.py seed_data   # creates sample users, projects, companies, groups, pages
```

## Common Commands

```bash
python manage.py runserver          # start dev server
python manage.py makemigrations     # after model changes
python manage.py migrate
python manage.py test core          # run tests (currently minimal)
python manage.py collectstatic      # gather static files (whitenoise)
python manage.py seed_data          # populate dev database with sample data
```

## Architecture

Everything lives in a single Django app: **`core/`**. There is no separate app per feature — all models, views, forms, URLs, and templates are in `core/`.

- `core/settings.py` — project settings; uses `python-decouple` (reads from `settings.ini`)
- `core/urls.py` — all URL patterns (~356 lines; auth, profiles, projects, messaging, groups, companies, pages, meetings, admin panel, PWA, Odu chatbot, mentorship, courses, consulting, services)
- `core/models.py` — all models in one file (~1,374 lines)
- `core/views.py` — all view functions in one file (~4,468 lines, 214+ views, 1 class-based view `UserProfileView`)
- `core/forms.py` — all forms (12 form classes)
- `core/consumers.py` — Django Channels WebSocket consumer for real-time chat
- `core/routing.py` — WebSocket URL routing (`ws/chat/<room_name>/`)
- `core/asgi.py` — ASGI entry point; wraps HTTP and WebSocket via `ProtocolTypeRouter`
- `core/context_processors.py` — injects `user_profile` and `unread_message_count` into every template
- `core/signals.py` — auto-creates `UserProfile` on `CustomUser` save; sends Welcome notification and Odu greeting message to new users
- `core/middleware.py` — `AnalyticsMiddleware` tracks page views (path, user, IP, browser, OS, referrer) for authenticated GET requests; stores in `PageView` model
- `core/matching.py` — intelligent investor-project matching service; scores compatibility 0–100 based on industry, funding stage, and geography factors
- `core/zoom_api.py` — Zoom Server-to-Server OAuth; functions: `create_meeting`, `get_recordings`, `delete_meeting`
- `core/connections/` — stub sub-app (only `admin.py` present, no models/views yet)
- `core/widgets.py` — `MultiFileInput` widget (multi-file upload support for forms)
- `core/templatetags/dict_extras.py` — custom Django template tags
- `core/management/commands/seed_data.py` — creates dev seed data (users, projects, companies, groups, pages)
- `core/static/css/design-system.css` — centralized CSS design tokens (colors, typography, spacing, shadows); primary brand color `#004AAD`
- `core/static/js/service-worker.js` — PWA service worker for offline support
- `core/static/manifest.json` — PWA manifest (`start_url: /app/`, standalone display)
- `docs/` — primary HTML templates directory (Django `TEMPLATES DIRS` points here); 119+ templates
- `core/templates/` — secondary templates directory for `events/` and `ideas/` feature templates
- `staticfiles/` — collected static files (whitenoise-served)

### Key Models  

| Model | Purpose |
|-------|---------|
| `CustomUser` | Extends `AbstractUser`; adds `user_type`, `bio`, `profile_pics`, `friends`, `connected_users`, `phone_number` |
| `UserProfile` | One-to-one with `CustomUser`; stores `company`, `industry`, richer profile fields |
| `Project` | Innovator-owned projects with status, industry, images, ratings, likes |
| `ProjectImage` | Multiple images per project; `is_main` flag for primary image |
| `Post` | Feed posts with industry tagging; supports `PostImage` attachments |
| `Message` / `Conversation` | Direct messaging between users |
| `MessageReaction` | Emoji reactions on messages |
| `Connection` | Explicit connection record between two users (initiator + target) |
| `Notification` | In-app notifications (types: `connected`, `message_sent`, `other`) |
| `Patent`, `Invention` | Patent/invention tracking for innovators |
| `PatentRequest` | Investor requests to license/acquire patents |
| `Rating` | User ratings for projects (unique per project-user pair) |
| `Like` / `Interest` | User likes and interests on other users |
| `Company` | Companies with industry, logo, `CompanyMedia`, `CompanyUpdate` |
| `Group` / `Page` | User groups and company-style pages |
| `GroupMembership` | User membership in groups |
| `GroupDiscussion` / `GroupDiscussionComment` / `GroupDiscussionImage` | Group discussion threads |
| `PagePost` / `PagePostReaction` / `PagePostShare` / `PagePostImage` | Content on pages |
| `Attachment` | File uploads associated with projects |
| `AttachmentDownload` | Tracks attachment download events |
| `Event` / `EventRegistration` | Events with registration |
| `Comment` | Comments on posts |
| `ProjectComment` | Comments on projects |
| `Proposal` | Formal collaboration proposals between users |
| `ProjectProposal` | Project-level proposals |
| `Collaboration` | Active collaboration records |
| `ProjectCollaboration` | Project-level collaboration |
| `Meeting` | Scheduled video meetings (Zoom integration) |
| `Job` / `JobApplication` | Job postings and applications |
| `ContactSubmission` | Contact form submissions |
| `ProfileView` / `ProjectView` | View tracking for profiles and projects |
| `PageView` / `ClickEvent` | Analytics: page view and click tracking |
| `NewsItem` | Platform news/announcements |
| `AdminPermissions` | Granular admin permission flags per user |
| `SurveyResponse` | User survey responses |
| `ShareEvent` | Tracks content share events |
| `ReadLater` | Saved/bookmarked content for users |
| `Course` / `CourseModule` | Learning courses and their modules |
| `CourseEnrollment` | User enrollment tracking for courses |
| `MentorProfile` | Mentor profiles and expertise information |
| `MentorshipRequest` | Requests for mentorship from users |
| `MentorshipAssignment` | Active mentor-mentee assignments |
| `ConsultingRequest` | Consulting service requests |

> Note: `CustomUser` and `UserProfile` both store some overlapping fields (`bio`, `profile_pics`, `friends`). The canonical profile data lives on `UserProfile`; `CustomUser` fields are legacy.

### Authentication

Uses **django-allauth** alongside a custom registration/login flow. Both are active simultaneously:
- Custom views: `/register/`, `/login/`, `/logout/`
- Allauth routes: `/accounts/` (includes Google OAuth)
- `AUTH_USER_MODEL = 'core.CustomUser'`
- Username is auto-generated as `first_name.last_name` (lowercased) during registration

### Real-time Chat

Django Channels provides WebSocket support via `core/asgi.py` (`ASGI_APPLICATION = 'core.asgi.application'`). The `ChatConsumer` in `core/consumers.py` handles room-based group broadcast. WebSocket URL: `ws/chat/<room_name>/`.

### Odu Chatbot

`/odu/chat/` and `/odu/feedback/` provide an AI-powered assistant. New users automatically receive a welcome message from the Odu system bot (created via `seed_data` or signals).

### Mentorship & Consulting

The platform includes a mentorship system (`/mentor/`, `/mentorship/`) and consulting requests (`/consulting_request/`). `MentorProfile` stores mentor expertise; `MentorshipRequest` and `MentorshipAssignment` track the lifecycle of mentor-mentee relationships.

### Course Management

A learning management system is available at `/course/` and `/enrollment/`. `Course` and `CourseModule` define content; `CourseEnrollment` tracks user progress.

### Matching Algorithm

`core/matching.py` provides an investor-project compatibility scoring service (0–100) based on industry alignment, funding stage, geography, and other factors. Used to surface relevant projects to investors.

### Templates

Templates are split across two directories:
- `docs/` — main templates (119+ files); partials in `docs/_partials/` (`base.html`, `base1.html`, `navbar.html`, `footer.html`, `breadcrumbs.html`, `project_cards.html`, `suggestions.html`, `notif_empty.html`, `notif_item.html`); allauth overrides in `docs/allauth/`; additional subdirectories: `docs/auth/`, `docs/messages/`, `docs/project_images/`
- `core/templates/` — feature-specific templates for `events/` and `ideas/`

Both directories are listed in Django's `TEMPLATES DIRS`.

### Static & Media Files

- Static files served by **whitenoise** in both dev and production
- `STATICFILES_DIRS` includes `docs/` so CSS/JS inside `docs/` is collected
- `core/static/css/design-system.css` defines the brand design system (import before feature CSS)
- Media uploads go to `MEDIA_ROOT` (local `media/` directory, subdivided by type)

### PWA

The app is configured as a Progressive Web App:
- `core/static/manifest.json` — app name, icons, `start_url: /app/`, standalone display, theme `#004AAD`
- `core/static/js/service-worker.js` — offline caching
- `docs/offline.html` — offline fallback page

### Deployment

Deployed on **Render** (`connect-ihni.onrender.com`). Production uses PostgreSQL via `DATABASE_URL`; local dev defaults to SQLite.

## UI / Design System

### Brand tokens (defined in `core/static/css/design-system.css`)
- Primary blue: `#1B5EC7` (CSS var `--oc-blue`)
- Ink/dark: `#0A1628`
- Light blue bg: `#e0e8f4` (`--oc-blue-lt`)
- Border: `#e4eaf2`
- Font: `Space Grotesk` (headings/UI), system sans-serif (body)
- Navbar height token: `--oc-navbar-h: 62px` — controls both the navbar height and `body padding-top`. Must be updated if navbar height changes.

### Navbar (`docs/_partials/navbar.html`)
- Fixed position, `z-index: 100`
- Search bar collapses to icon at `<1280px`; hidden entirely at `<640px`
- Profile name/caret hidden at `<640px`
- Hamburger always visible; uses `e.stopPropagation()` to prevent document listener closing it
- Document click listener: only skips `.oc-mobile-menu` — do NOT add `.oc-navbar` to the guard
- Bottom nav (frosted glass, 6 icons) replaces footer on all screen sizes

### Mobile drawer (authenticated)
- Explore sub-links (Innovators, Investors, Businesses) are **always visible** — not behind an accordion
- Guest users have an accordion for the explore section

### Custom dropdowns
- Replace all native `<select>` in filter bars with `pm-dd` (dashboards) or `cl-dd` (companies) components
- Each option uses `data-val=""` attribute; match with `o.dataset.val === val` (never `includes()`)

### File inputs
- Native `<input type="file">` wrapped in `.pf-file-wrap` pattern: hidden real input + styled visible overlay
- JS updates the filename label on change

### Spacing conventions
- Page wrapper: `padding: 16px 20px 44px`
- Hero sections: `padding: 22px`
- Empty states: `padding: 28px 22px`
- Stats/card cells: `padding: 10–12px`

### After editing `core/static/css/design-system.css`
Always run `python manage.py collectstatic` — whitenoise serves from `staticfiles/` not the source directory.
