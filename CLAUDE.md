# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Oduma Connect** is a Django 5.1 web platform connecting innovators and investors across Africa. Users register with one of three roles (`innovator`, `investor`, `admin`) and can post projects, send messages, connect with each other, rate/like projects, collaborate on proposals, join groups, follow company pages, and schedule meetings.

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
- `core/urls.py` — all URL patterns (~291 lines; auth, profiles, projects, messaging, groups, companies, pages, meetings, admin panel, PWA, Odu chatbot)
- `core/models.py` — all models in one file (~53 models)
- `core/views.py` — all view functions in one file (~2,464 lines, 166+ views)
- `core/forms.py` — all forms (12 form classes)
- `core/consumers.py` — Django Channels WebSocket consumer for real-time chat
- `core/routing.py` — WebSocket URL routing (`ws/chat/<room_name>/`)
- `core/asgi.py` — ASGI entry point; wraps HTTP and WebSocket via `ProtocolTypeRouter`
- `core/context_processors.py` — injects `user_profile` and `unread_message_count` into every template
- `core/signals.py` — auto-creates `UserProfile` on `CustomUser` save; sends Welcome notification and Odu greeting message to new users
- `core/middleware.py` — `AnalyticsMiddleware` tracks page views (path, user, IP, browser, OS, referrer) for authenticated GET requests; stores in `PageView` model
- `core/zoom_api.py` — Zoom Server-to-Server OAuth; functions: `create_meeting`, `get_recordings`, `delete_meeting`
- `core/connections/` — stub sub-app (only `admin.py` present, no models/views yet)
- `core/widgets.py` — `MultiFileInput` widget (multi-file upload support for forms)
- `core/management/commands/seed_data.py` — creates dev seed data (users, projects, companies, groups, pages)
- `core/static/css/design-system.css` — centralized CSS design tokens (colors, typography, spacing, shadows); primary brand color `#004AAD`
- `core/static/js/service-worker.js` — PWA service worker for offline support
- `core/static/manifest.json` — PWA manifest (`start_url: /app/`, standalone display)
- `docs/` — primary HTML templates directory (Django `TEMPLATES DIRS` points here); 85+ templates
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

### Templates

Templates are split across two directories:
- `docs/` — main templates (85+ files); partials in `docs/_partials/` (`navbar.html`, `footer.html`, `base.html`, `breadcrumbs.html`, `project_cards.html`, `suggestions.html`); allauth overrides in `docs/allauth/`
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
