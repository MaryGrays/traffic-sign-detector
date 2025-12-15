#!/bin/bash
echo "=== НАЧАЛО НАСТРОЙКИ ПРОЕКТА ==="

echo "ДОБАВЛЕНИЕ ТЕСТОВ"

# Создаем структуру для тестов
mkdir -p web/tests
mkdir -p api/tests

# 1. Тесты для Django
cat > web/tests/test_views.py << 'PYTEST'
"""
Тесты для Django views
"""
import pytest
from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from traffic_signs.models import DetectionHistory

class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        
    def test_home_page(self):
        """Тест главной страницы"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Traffic Sign Detector')
    
    def test_upload_page_get(self):
        """Тест страницы загрузки (GET запрос)"""
        response = self.client.get(reverse('upload'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Upload')
    
    def test_upload_page_post_no_file(self):
        """Тест загрузки без файла"""
        response = self.client.post(reverse('upload'), {})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'error', status_code=200)
    
    def test_api_docs_page(self):
        """Тест страницы документации API"""
        response = self.client.get(reverse('api_docs'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'API Documentation')

class ModelTests(TestCase):
    def test_detection_history_creation(self):
        """Тест создания модели DetectionHistory"""
        detection = DetectionHistory.objects.create(
            image_name="test.jpg",
            image_size=1024,
            image_type="image/jpeg",
            success=True,
            results=[{"sign_id": 1, "sign_name": "Стоп", "confidence": 0.95}],
            processing_time=0.1
        )
        self.assertEqual(detection.image_name, "test.jpg")
        self.assertTrue(detection.success)
        self.assertEqual(detection.get_signs_count(), 1)
PYTEST

# 2. Тесты для FastAPI
cat > api/tests/test_api.py << 'FASTAPITEST'
"""
Тесты для FastAPI
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_endpoint():
    """Тест корневого эндпоинта"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
    assert response.json()["message"] == "Traffic Sign Detection API"

def test_health_check():
    """Тест проверки здоровья"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_detect_endpoint_invalid_image():
    """Тест эндпоинта детекции с невалидным изображением"""
    response = client.post("/detection/detect", 
                          json={"image_base64": "invalid", "user_id": None})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == False
    assert "error" in data

def test_list_signs():
    """Тест получения списка знаков"""
    response = client.get("/signs/list")
    assert response.status_code == 200
    data = response.json()
    assert "signs" in data
    assert "total" in data
    assert isinstance(data["signs"], list)
FASTAPITEST

# 3. Если pytest.ini не создан, создаем его
if [ ! -f "web/pytest.ini" ]; then
    cat > web/pytest.ini << 'PYTESTINI'
[pytest]
DJANGO_SETTINGS_MODULE = traffic_sign_app.settings
python_files = tests.py test_*.py *_tests.py
PYTESTINI
fi

# 4. Создаем requirements для тестов
mkdir -p requirements
cat > requirements/test.txt << 'REQUIREMENTS'
-r web.txt
-r api.txt
pytest==7.4.0
pytest-django==4.7.0
pytest-asyncio==0.21.1
httpx==0.25.0
factory-boy==3.3.0
Faker==20.1.0
coverage==7.3.2
REQUIREMENTS

echo "✅ Тесты добавлены"

echo "ДОБАВЛЕНИЕ АСИНХРОННОСТИ"

# 1. Создаем async_views.py
cat > web/traffic_signs/async_views.py << 'ASYNCVIEWS'
"""
Асинхронные view для Django
"""
from django.http import JsonResponse
from django.views import View
import httpx
import asyncio
import base64

class AsyncAPIView(View):
    """Асинхронный view для работы с API"""
    async def get(self, request):
        """Асинхронный GET запрос"""
        async with httpx.AsyncClient() as client:
            try:
                # Асинхронный запрос к ML API
                response = await client.get('http://api:8001/health', timeout=10.0)
                data = response.json()
                return JsonResponse({
                    'api_status': data.get('status', 'unknown'),
                    'message': 'Асинхронный запрос выполнен'
                })
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)
    
    async def post(self, request):
        """Асинхронная обработка изображения"""
        if request.FILES.get('image'):
            image = request.FILES['image']
            image_data = await image.read()
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            async with httpx.AsyncClient() as client:
                try:
                    payload = {
                        'image_base64': image_base64,
                        'user_id': request.user.id if request.user.is_authenticated else None
                    }
                    
                    # Асинхронный запрос к ML API
                    response = await client.post(
                        'http://api:8001/detection/detect',
                        json=payload,
                        timeout=30.0
                    )
                    
                    return JsonResponse(response.json())
                    
                except httpx.RequestError as e:
                    return JsonResponse({
                        'success': False,
                        'error': f'API request failed: {str(e)}'
                    }, status=500)
        
        return JsonResponse({'error': 'No image provided'}, status=400)
ASYNCVIEWS

# 2. Если async_views.py не добавлен в urls.py, добавляем
if ! grep -q "async" web/traffic_signs/urls.py; then
    cat >> web/traffic_signs/urls.py << 'URLS'
from .async_views import AsyncAPIView

urlpatterns += [
    path('api/async/', AsyncAPIView.as_view(), name='async_api'),
]
URLS
fi

echo "✅ Асинхронность добавлена"

echo "ДОБАВЛЕНИЕ CELERY И REDIS"

# 1. Создаем celery.py в корне проекта
cat > web/traffic_sign_detector/celery.py << 'CELERYPY'
"""
Конфигурация Celery
"""
import os
from celery import Celery

# Устанавливаем переменную окружения для настроек Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'traffic_sign_detector.settings')

app = Celery('traffic_sign_detector')

# Используем строку конфигурации для настроек
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматическое обнаружение задач в приложениях Django
app.autodiscover_tasks()

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
CELERYPY

# 2. Создаем __init__.py для celery
cat > web/traffic_sign_detector/__init__.py << 'INITPY'
from .celery import app as celery_app

__all__ = ('celery_app',)
INITPY

# 3. Добавляем настройки Celery в settings.py если их нет
if ! grep -q "CELERY" web/traffic_sign_detector/settings.py; then
    cat >> web/traffic_sign_detector/settings.py << 'SETTINGS'

# Celery settings
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://redis:6379/0')
CELERY_RESULT_BACKEND = 'redis://redis:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
SETTINGS
fi

# 4. Создаем tasks.py
cat > web/traffic_signs/tasks.py << 'TASKSPY'
"""
Задачи Celery
"""
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
import time
import requests
import base64

@shared_task
def process_image_async(image_base64, user_id=None):
    """
    Асинхронная обработка изображения через Celery
    """
    try:
        # Имитация долгой обработки
        time.sleep(2)
        
        # Отправка в ML API
        api_url = 'http://api:8001/detection/detect'
        payload = {
            'image_base64': image_base64,
            'user_id': user_id
        }
        
        response = requests.post(api_url, json=payload, timeout=30)
        result = response.json()
        
        # Возвращаем результат
        return {
            'task_id': process_image_async.request.id,
            'success': result.get('success', False),
            'results': result.get('results', []),
            'processing_time': result.get('processing_time', 0)
        }
        
    except Exception as e:
        return {
            'task_id': process_image_async.request.id,
            'success': False,
            'error': str(e)
        }

@shared_task
def send_detection_email(user_email, detection_results):
    """
    Отправка email с результатами детекции
    """
    subject = 'Результаты распознавания дорожных знаков'
    message = f'''
    Результаты обработки вашего изображения:
    
    Успешно: {detection_results.get('success', False)}
    Время обработки: {detection_results.get('processing_time', 0)} сек
    
    Найденные знаки:
    '''
    
    for i, result in enumerate(detection_results.get('results', []), 1):
        message += f'{i}. {result.get("sign_name")} - уверенность: {result.get("confidence")}\n'
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user_email],
        fail_silently=False,
    )
    
    return f'Email sent to {user_email}'

@shared_task
def cleanup_old_detections(days_old=30):
    """
    Очистка старых записей детекции
    """
    from django.utils import timezone
    from datetime import timedelta
    from .models import DetectionHistory
    
    cutoff_date = timezone.now() - timedelta(days=days_old)
    deleted_count = DetectionHistory.objects.filter(
        upload_time__lt=cutoff_date
    ).delete()[0]
    
    return f'Deleted {deleted_count} old detections'
TASKSPY

# 5. Создаем celery_views.py
cat > web/traffic_signs/celery_views.py << 'CELERYVIEWS'
"""
Views для работы с Celery
"""
from django.shortcuts import render
from django.http import JsonResponse
from .tasks import process_image_async
import base64
from celery.result import AsyncResult

def celery_upload_view(request):
    """Загрузка изображения для обработки через Celery"""
    if request.method == 'POST' and request.FILES.get('image'):
        image = request.FILES['image']
        
        try:
            # Кодируем изображение
            image_data = image.read()
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # Запускаем асинхронную задачу
            task = process_image_async.delay(
                image_base64=image_base64,
                user_id=request.user.id if request.user.is_authenticated else None
            )
            
            return JsonResponse({
                'task_id': task.id,
                'status': 'PENDING',
                'message': 'Изображение отправлено на обработку',
                'check_url': f'/check-task/{task.id}/'
            })
            
        except Exception as e:
            return JsonResponse({
                'error': str(e),
                'status': 'ERROR'
            }, status=400)
    
    return render(request, 'traffic_signs/celery_upload.html')

def check_task_status(request, task_id):
    """Проверка статуса задачи Celery"""
    task_result = AsyncResult(task_id)
    
    response_data = {
        'task_id': task_id,
        'status': task_result.status,
        'ready': task_result.ready()
    }
    
    if task_result.ready():
        if task_result.successful():
            response_data['result'] = task_result.result
            response_data['status'] = 'SUCCESS'
        else:
            response_data['error'] = str(task_result.result)
            response_data['status'] = 'FAILURE'
    
    return JsonResponse(response_data)
CELERYVIEWS

# 6. Добавляем URL для Celery
cat >> web/traffic_signs/urls.py << 'CELERYURLS'

from .celery_views import celery_upload_view, check_task_status

urlpatterns += [
    path('celery-upload/', celery_upload_view, name='celery_upload'),
    path('check-task/<str:task_id>/', check_task_status, name='check_task_status'),
]
CELERYURLS

# 7. Создаем шаблон для Celery
mkdir -p web/traffic_signs/templates/traffic_signs

cat > web/traffic_signs/templates/traffic_signs/celery_upload.html << 'CELERYTEMPLATE'
{% extends "base.html" %}

{% block content %}
<div class="container">
    <h1>Фоновая обработка изображений с Celery</h1>
    
    <form id="celeryUploadForm" enctype="multipart/form-data">
        {% csrf_token %}
        <div class="mb-3">
            <label for="image" class="form-label">Выберите изображение:</label>
            <input type="file" class="form-control" id="image" name="image" accept="image/*" required>
        </div>
        <button type="submit" class="btn btn-primary">Отправить на обработку</button>
    </form>
    
    <div id="result" class="mt-4"></div>
    <div id="progress" class="mt-3" style="display: none;">
        <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Загрузка...</span>
        </div>
        <span class="ms-2">Обработка изображения...</span>
    </div>
</div>

<script>
document.getElementById('celeryUploadForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const formData = new FormData(this);
    const resultDiv = document.getElementById('result');
    const progressDiv = document.getElementById('progress');
    
    resultDiv.innerHTML = '';
    progressDiv.style.display = 'block';
    
    try {
        const response = await fetch('/celery-upload/', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.task_id) {
            // Начинаем проверку статуса задачи
            checkTaskStatus(data.task_id);
        } else {
            throw new Error('No task ID received');
        }
    } catch (error) {
        progressDiv.style.display = 'none';
        resultDiv.innerHTML = `
            <div class="alert alert-danger">
                Ошибка: ${error.message}
            </div>
        `;
    }
});

function checkTaskStatus(taskId) {
    const checkInterval = 2000; // 2 секунды
    
    function check() {
        fetch(\`/check-task/\${taskId}/\`)
            .then(response => response.json())
            .then(data => {
                const resultDiv = document.getElementById('result');
                const progressDiv = document.getElementById('progress');
                
                if (data.status === 'SUCCESS') {
                    progressDiv.style.display = 'none';
                    resultDiv.innerHTML = `
                        <div class="alert alert-success">
                            <h4>Обработка завершена!</h4>
                            <pre>\${JSON.stringify(data.result, null, 2)}</pre>
                        </div>
                    `;
                } else if (data.status === 'FAILURE') {
                    progressDiv.style.display = 'none';
                    resultDiv.innerHTML = `
                        <div class="alert alert-danger">
                            <h4>Ошибка обработки</h4>
                            <p>\${data.error}</p>
                        </div>
                    `;
                } else if (data.status === 'PENDING') {
                    // Задача еще выполняется, проверяем снова
                    setTimeout(check, checkInterval);
                }
            })
            .catch(error => {
                console.error('Error checking task status:', error);
                setTimeout(check, checkInterval);
            });
    }
    
    // Начинаем проверку
    setTimeout(check, checkInterval);
}
</script>
{% endblock %}
CELERYTEMPLATE

echo "✅ Celery добавлен"

echo "ДОБАВЛЕНИЕ CI/CD"

# 1. Создаем GitHub Actions
mkdir -p .github/workflows

cat > .github/workflows/ci.yml << 'GITHUBACTIONS'
name: CI/CD Pipeline

on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      
      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements/web.txt
        pip install -r requirements/test.txt
        pip install pytest pytest-django
    
    - name: Run Django tests
      env:
        DATABASE_URL: postgres://postgres:postgres@localhost:5432/test_db
        SECRET_KEY: test-secret-key
      run: |
        cd web
        python manage.py test --noinput
    
    - name: Run FastAPI tests
      run: |
        cd api
        pip install -r requirements.txt
        pip install pytest httpx
        python -m pytest tests/ -v
    
    - name: Lint with flake8
      run: |
        pip install flake8
        flake8 web/ api/ --count --select=E9,F63,F7,F82 --show-source --statistics
        flake8 web/ api/ --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
    
  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
    
    - name: Login to DockerHub
      uses: docker/login-action@v2
      with:
        username: \${{ secrets.DOCKER_USERNAME }}
        password: \${{ secrets.DOCKER_PASSWORD }}
    
    - name: Build and push Docker images
      uses: docker/build-push-action@v4
      with:
        context: .
        file: ./web/Dockerfile
        push: true
        tags: |
          \${{ secrets.DOCKER_USERNAME }}/traffic-sign-web:latest
          \${{ secrets.DOCKER_USERNAME }}/traffic-sign-web:\${{ github.sha }}
    
    - name: Deploy notification
      run: |
        echo "Deployment completed successfully!"
GITHUBACTIONS

# 2. Создаем GitLab CI
cat > .gitlab-ci.yml << 'GITLABCI'
stages:
  - test
  - build
  - deploy

variables:
  DOCKER_DRIVER: overlay2
  POSTGRES_DB: test_db
  POSTGRES_USER: postgres
  POSTGRES_PASSWORD: postgres

services:
  - postgres:15
  - redis:7-alpine

test:django:
  stage: test
  image: python:3.12-slim
  before_script:
    - apt-get update && apt-get install -y gcc libpq-dev
    - pip install --upgrade pip
    - cd web
    - pip install -r requirements.txt
    - pip install pytest pytest-django
  script:
    - python manage.py test --noinput
    - python -m pytest tests/ -v
  artifacts:
    when: always
    paths:
      - web/test-reports/
    reports:
      junit: web/test-reports/junit.xml

test:fastapi:
  stage: test
  image: python:3.12-slim
  before_script:
    - cd api
    - pip install -r requirements.txt
    - pip install pytest httpx
  script:
    - python -m pytest tests/ -v

build:web:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  before_script:
    - docker login -u "\$CI_REGISTRY_USER" -p "\$CI_REGISTRY_PASSWORD" \$CI_REGISTRY
  script:
    - docker build -t \$CI_REGISTRY_IMAGE/web:latest ./web
    - docker push \$CI_REGISTRY_IMAGE/web:latest

build:api:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  before_script:
    - docker login -u "\$CI_REGISTRY_USER" -p "\$CI_REGISTRY_PASSWORD" \$CI_REGISTRY
  script:
    - docker build -t \$CI_REGISTRY_IMAGE/api:latest ./api
    - docker push \$CI_REGISTRY_IMAGE/api:latest

deploy:staging:
  stage: deploy
  image: alpine:latest
  script:
    - apk add --no-cache curl
    - echo "Deploying to staging environment..."
    # Здесь будет скрипт деплоя
    - echo "Deployment completed"
  environment:
    name: staging
    url: https://staging.traffic-sign.example.com
  only:
    - main

deploy:production:
  stage: deploy
  image: alpine:latest
  script:
    - apk add --no-cache curl
    - echo "Deploying to production environment..."
    # Здесь будет скрипт деплоя
    - echo "Deployment completed"
  environment:
    name: production
    url: https://traffic-sign.example.com
  when: manual
  only:
    - tags
GITLABCI

echo "✅ CI/CD добавлен"

echo "=== ПРОЕКТ УСПЕШНО НАСТРОЕН ==="
echo "Для применения изменений выполните:"
echo "1. ./setup_project.sh"
echo "2. docker-compose up -d"
echo "3. docker-compose exec web python manage.py migrate"
