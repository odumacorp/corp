# Oduma Corp

**The innovation-investment platform for Africa.**

Oduma Corp connects innovators, investors, and businesses — enabling project discovery, direct messaging, collaboration, mentorship, and deal-making in a single platform.

---

## What it does

| Feature | Description |
|---------|-------------|
| **Project Hub** | Innovators post projects with images, funding stage, and industry tags. Investors browse, rate, and connect. |
| **Smart Matching** | Compatibility scoring (0–100) pairs investors with projects based on industry, funding stage, and geography. |
| **Direct Messaging** | Real-time chat via Django Channels WebSocket. Emoji reactions, file attachments, read receipts. |
| **Network** | Connect, follow, and collaborate. Send proposals, track connections, join groups and pages. |
| **Companies & Pages** | Create company profiles, post updates, build a following. |
| **Jobs Board** | Post and apply for positions across the ecosystem. |
| **Events** | Create and register for events. |
| **Courses** | Learning modules with enrollment tracking. |
| **Mentorship** | Request and assign mentors across industries. |
| **Consulting** | Submit consulting requests tied to specific projects. |
| **Odu AI Bot** | Built-in AI assistant powered by Anthropic Claude. Greets new users and answers platform questions. |
| **Meetings** | Schedule Zoom video meetings directly from the platform. |
| **Patents & Inventions** | Innovators track intellectual property; investors submit licensing requests. |
| **Admin Panel** | Custom admin dashboard with verification queue, analytics, broadcast messaging, and granular permissions. |
| **PWA** | Installable as a mobile app. Offline fallback page included. |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 5.1, Python |
| Real-time | Django Channels (WebSocket) |
| Database | PostgreSQL (production) / SQLite (local) |
| Auth | Custom + django-allauth (Google OAuth) |
| AI | Anthropic Claude API |
| Meetings | Zoom Server-to-Server OAuth |
| Static files | Whitenoise |
| Deployment | Render |
| Config | python-decouple (`settings.ini`) |

---

## Getting Started

### Prerequisites
- Python 3.10+
- pip

### Local setup

```bash
# 1. Clone and create virtual environment
git clone <repo-url>
cd Corp
python -m venv env
source env/bin/activate        # Windows: env\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp settings.ini.example settings.ini
# Edit settings.ini — fill in the required values (see below)

# 4. Run migrations
python manage.py migrate

# 5. Create an admin user
python manage.py createsuperuser

# 6. (Optional) Seed sample data
python manage.py seed_data

# 7. Start the server
python manage.py runserver
```

Visit `http://localhost:8000`

### settings.ini required values

```ini
DEBUG=True
SECRET_KEY=your-secret-key-here
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your@email.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True
```

### Optional integrations

```ini
DATABASE_URL=postgres://...          # defaults to SQLite if omitted
GOOGLE_CLIENT_ID=...                 # Google OAuth login
GOOGLE_CLIENT_SECRET=...
ANTHROPIC_API_KEY=...                # Odu AI chatbot
ZOOM_ACCOUNT_ID=...                  # Zoom meeting scheduling
ZOOM_CLIENT_ID=...
ZOOM_CLIENT_SECRET=...
```

### Docker

```bash
docker build -t oduma-connect .
docker run -p 8000:8000 --env-file .env oduma-connect
```

---

## Project Structure

```
Corp/
├── core/                      # Single Django app — all features live here
│   ├── models.py              # All models (~1,400 lines, 40+ models)
│   ├── views.py               # All views (~4,500 lines, 214+ view functions)
│   ├── urls.py                # All URL patterns (~356 lines)
│   ├── forms.py               # Form classes with SanitizeMixin validation
│   ├── consumers.py           # WebSocket chat consumer (Django Channels)
│   ├── signals.py             # Auto-creates UserProfile; sends Odu welcome message
│   ├── middleware.py          # AnalyticsMiddleware — page view tracking
│   ├── matching.py            # Investor-project compatibility scoring (0–100)
│   ├── zoom_api.py            # Zoom meeting integration
│   ├── context_processors.py  # Injects profile + unread count into every template
│   ├── settings.py            # Django settings (python-decouple)
│   ├── asgi.py                # ASGI entrypoint (HTTP + WebSocket routing)
│   ├── static/
│   │   ├── css/
│   │   │   └── design-system.css   # Brand tokens, components, layout
│   │   ├── js/
│   │   │   └── service-worker.js   # PWA offline caching
│   │   └── manifest.json           # PWA manifest
│   └── management/commands/
│       └── seed_data.py       # Dev data seeding
├── docs/                      # All HTML templates (Django TEMPLATES DIR)
│   ├── _partials/             # Shared partials: base.html, navbar.html, footer.html
│   ├── allauth/               # Google OAuth template overrides
│   ├── auth/                  # Login, register, password reset templates
│   ├── messages/              # Chat page templates
│   └── *.html                 # 119+ page templates
├── core/templates/            # Feature templates (events/, ideas/)
├── staticfiles/               # Collected static files (served by whitenoise)
├── media/                     # User-uploaded files
├── CLAUDE.md                  # AI assistant codebase guide
└── requirements.txt
```

---

## User Roles

| Role | Capabilities |
|------|-------------|
| `innovator` | Post projects, track patents, get matched with investors, request consulting and mentorship |
| `investor` | Browse projects, view smart matches, connect with innovators, submit patent requests |
| `admin` | Full platform access, verification queue, analytics dashboard, broadcast messages |

---

## Key URLs

| Path | Page |
|------|------|
| `/` | Landing page |
| `/app/` | Home feed (requires login) |
| `/register/` | User registration |
| `/login/` | Login |
| `/profile/<id>/` | User profile |
| `/innovators/` | Innovator directory |
| `/investors/` | Investor directory |
| `/projects/` | Project listings |
| `/project/<id>/` | Project detail |
| `/companies/` | Company directory |
| `/networks/` | Connections and network |
| `/chat/<room>/` | Real-time chat |
| `/odu/chat/` | Odu AI assistant |
| `/jobs/` | Jobs board |
| `/events/` | Events hub |
| `/mentorship/` | Mentorship hub |
| `/courses/` | Training hub |
| `/admin-panel/` | Custom admin dashboard |

---

## Development Commands

```bash
python manage.py runserver          # Start dev server
python manage.py makemigrations     # After any model changes
python manage.py migrate            # Apply migrations
python manage.py collectstatic      # Rebuild static files (required after CSS edits)
python manage.py seed_data          # Populate dev database with sample data
python manage.py test core          # Run tests
```

> **Important:** After editing `core/static/css/design-system.css`, always run `collectstatic`.
> Whitenoise serves from `staticfiles/` — changes to source files won't appear until collected.

---

## Design System

The UI follows a premium fintech/VC aesthetic:

- **Primary blue:** `#1B5EC7`
- **Dark ink:** `#0A1628`
- **Font:** Space Grotesk (headings and UI labels), system sans-serif (body text)
- **Navbar height:** controlled by `--oc-navbar-h: 62px` CSS token
- All design tokens defined in `core/static/css/design-system.css`
- Stroke SVG icons throughout — no emoji in UI chrome
- Mobile-first — fixed bottom navigation bar on all screen sizes

---

## Deployment

Hosted on **Render** at `connect-ihni.onrender.com`.

- **Database:** PostgreSQL via `DATABASE_URL` environment variable
- **Static files:** Whitenoise (no separate CDN required)
- **Process:** `gunicorn core.asgi:application` (ASGI for WebSocket support)

---

## License

Proprietary — Oduma Corp. All rights reserved.
