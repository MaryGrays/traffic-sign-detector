import os
import sys

# Добавляем пути на случай если нужно
sys.path.insert(0, '/app')
sys.path.insert(0, '/app/app')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'traffic_sign_app.settings')

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
