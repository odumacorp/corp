# Local quickstart (dev)

1. Create venv & install deps
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt

2. Copy env
   cp .env.example .env
   # edit .env: set SECRET_KEY, DEBUG=True for local

3. Run migrations and start
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py runservert

# Using Docker
docker build -t oduma-connect .
docker run -p 8000:8000 --env-file .env oduma-connect


from django.contrib.auth.models import User
user = User.objects.get(username="admin")
user.set_password("L@ndM1ne")
user.save()
exit()
