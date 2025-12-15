"""
Views for traffic_signs application
"""
from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
import json
import os
from django.conf import settings
from django.core.files.storage import default_storage
from celery.result import AsyncResult
from .tasks import process_image_task
from django.contrib.auth.models import User
from traffic_signs.models import TrafficSign, DetectionResult

# Basic views
def home(request):
    return render(request, 'traffic_signs/home.html', {
        'title': 'Traffic Sign Detector - Home'
    })


def upload_image(request):
    """Обработчик загрузки изображения для детекции"""
    from traffic_signs.models import TrafficSign, DetectionResult
    import random

    # Получаем последние 5 детекций для показа (используем detected_at вместо uploaded_at)
    recent_detections = DetectionResult.objects.all().order_by('-detected_at')[:5]

    if request.method == 'POST' and request.FILES.get('image'):
        # 1. Получаем файл
        uploaded_file = request.FILES['image']

        # 2. Для теста: берём случайный знак из базы
        try:
            # Берем случайный знак или создаем тестовый
            test_signs = list(TrafficSign.objects.all())
            if test_signs:
                test_sign = random.choice(test_signs)
            else:
                # Если в базе нет знаков, создаём тестовый
                test_sign = TrafficSign.objects.create(
                    name='Stop Sign',
                    sign_type='regulatory',
                    description='Test stop sign'
                )
        except Exception as e:
            # Если что-то пошло не так, создаём знак
            test_sign = TrafficSign.objects.create(
                name=f'Traffic Sign ({e})',
                sign_type='other'
            )

        # 3. Создаём и сохраняем объект DetectionResult
        detection = DetectionResult(
            image=uploaded_file,
            sign=test_sign,
            confidence=random.uniform(0.7, 0.99),  # Случайное значение уверенности
            user=request.user if request.user.is_authenticated else None
        )
        detection.save()

        # 4. Показываем результат пользователю
        return render(request, 'traffic_signs/upload.html', {
            'detection': detection,
            'recent_detections': recent_detections,
            'message': 'Image successfully processed!'
        })

    # GET запрос - показываем пустую форму
    return render(request, 'traffic_signs/upload.html', {
        'recent_detections': recent_detections
    })

def results(request):
    return render(request, 'traffic_signs/results.html')

def api_docs(request):
    return render(request, 'traffic_signs/api_docs.html')

def api_detect(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            return JsonResponse({
                'success': True,
                'message': 'API processing (demo)',
                'results': [
                    {
                        'sign_id': 1,
                        'sign_name': 'Stop',
                        'confidence': 0.95,
                        'bounding_box': [100, 100, 200, 200]
                    }
                ]
            })
        except:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON'
            })
    return JsonResponse({'error': 'POST method required'})


# Celery views
def celery_upload_view(request):
    """Обработчик для страницы загрузки через Celery"""
    if request.method == 'POST':
        try:
            # Получаем файл из запроса
            image_file = request.FILES.get('image')
            if not image_file:
                return JsonResponse({'error': 'No image file provided'}, status=400)

            # Сохраняем файл
            file_path = default_storage.save(f'celery_uploads/{image_file.name}', image_file)

            # Запускаем Celery задачу
            task = process_image_task.delay(file_path)

            # Возвращаем JSON с ID задачи
            return JsonResponse({
                'success': True,
                'task_id': task.id,
                'message': 'Image uploaded for background processing',
                'file_name': image_file.name
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)

    # GET запрос - показываем страницу загрузки
    return render(request, 'traffic_signs/celery_upload.html')


def check_task_status(request, task_id):
    """Проверка статуса Celery задачи"""
    try:
        task_result = AsyncResult(task_id)

        response_data = {
            'task_id': task_id,
            'status': task_result.status,
        }

        if task_result.status == 'SUCCESS':
            response_data['result'] = task_result.result
            response_data['success'] = True
        elif task_result.status == 'FAILURE':
            response_data['error'] = str(task_result.result)
            response_data['success'] = False
        elif task_result.status in ['PENDING', 'STARTED']:
            response_data['info'] = 'Task is in progress'
            response_data['success'] = True
        elif task_result.status == 'PROGRESS':
            response_data['progress'] = task_result.info
            response_data['success'] = True

        return JsonResponse(response_data)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error checking task status: {str(e)}',
            'task_id': task_id
        }, status=500)


def celery_test(request):
    """Тестовая страница для проверки Celery"""
    return render(request, 'traffic_signs/celery_test.html')


def celery_upload_direct(request):
    """Простая загрузка через Celery (без AJAX)"""
    if request.method == 'POST' and request.FILES.get('image'):
        try:
            image_file = request.FILES['image']
            file_path = default_storage.save(f'direct_uploads/{image_file.name}', image_file)
            task = process_image_task.delay(file_path)

            return render(request, 'traffic_signs/celery_result.html', {
                'task_id': task.id,
                'file_name': image_file.name,
                'message': 'File uploaded successfully! Task is processing in background.'
            })
        except Exception as e:
            return render(request, 'traffic_signs/celery_result.html', {
                'error': str(e),
                'message': 'Error uploading file'
            })

    return render(request, 'traffic_signs/celery_direct_upload.html')


def test_celery_upload(request):
    """Простая тестовая страница для Celery"""
    return render(request, 'traffic_signs/test_celery.html')