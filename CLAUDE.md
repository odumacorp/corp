# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Oduma Connect** is a Django 5.1 web platform connecting innovators and investors. Users register with one of three roles (`innovator`, `investor`, `admin`) and can post projects, send messages, connect with each other, and rate/like projects.

## Development Setup

```bash
python -m venv env
source env/bin/activate
pip install -r requirements.txt
cp .env.example .env   # set SECRET_KEY, DEBUG=True, and email config
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Required `.env` variables: `DEBUG`, `SECRET_KEY`, `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS`.

## Common Commands

```bash
python manage.py runserver          # start dev server
python manage.py makemigrations     # after model changes
python manage.py migrate
python manage.py test core          # run tests
python manage.py collectstatic      # gather static files (whitenoise)
```

## Architecture

Everything lives in a single Django app: **`core/`**. There is no separate app per feature — all models, views, forms, URLs, and templates are in `core/`.

- `core/settings.py` — project settings; uses `python-decouple` for env vars
- `core/urls.py` — all URL patterns (auth, profiles, projects, messaging, API)
- `core/models.py` — all models in one file
- `core/views.py` — all view functions in one file
- `core/forms.py` — all forms
- `core/consumers.py` — Django Channels WebSocket consumer for real-time chat
- `core/routing.py` — WebSocket URL routing (`ws/chat/<room_name>/`)
- `core/context_processors.py` — injects `user_profile` and `unread_message_count` into every template
- `core/signals.py` — auto-creates `UserProfile` on `CustomUser` save
- `core/connections/` — stub sub-app (only `admin.py` present, no models/views yet)
- `docs/` — HTML templates (configured as the Django `TEMPLATES DIRS`)
- `staticfiles/` — collected static files (whitenoise-served)

### Key Models

| Model | Purpose |
|-------|---------|
| `CustomUser` | Extends `AbstractUser`; adds `user_type`, `bio`, `profile_pics`, `friends`, `connected_users`, `phone_number` |
| `UserProfile` | One-to-one with `CustomUser`; stores `company`, `industry`, richer profile fields |
| `Project` | Innovator-owned projects with status, industry, images, ratings, likes |
| `Post` | Feed posts with industry tagging |
| `Message` / `Conversation` | Direct messaging between users |
| `Connection` | Explicit connection record between two users |
| `Notification` | In-app notifications |
| `Patent`, `Invention` | Patent/invention tracking for innovators |

> Note: `CustomUser` and `UserProfile` both store some overlapping fields (`bio`, `profile_pics`, `friends`). The canonical profile data lives on `UserProfile`; `CustomUser` fields are legacy.

### Authentication

Uses **django-allauth** alongside a custom registration/login flow. Both are active simultaneously:
- Custom views: `/register/`, `/login/`, `/logout/`
- Allauth routes: `/accounts/` (includes Google OAuth)
- `AUTH_USER_MODEL = 'core.CustomUser'`
- Username is auto-generated as `first_name.last_name` (lowercased) during registration

### Real-time Chat

Django Channels (`channels`) provides WebSocket support. The `ASGI_APPLICATION` in settings currently points to `core.wsgi.application` (likely a misconfiguration — should be an ASGI app referencing `routing.py`).

### Static & Media Files

- Static files served by **whitenoise** in both dev and production
- Media uploads go to `MEDIA_ROOT` (local `media/` directory)
- Templates are loaded from `docs/` (not the standard `templates/` directory)

### Deployment

Deployed on **Render** (`connect-ihni.onrender.com`). Production uses PostgreSQL; local dev defaults to SQLite.
