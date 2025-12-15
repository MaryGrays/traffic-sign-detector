"""
Views для работы с Celery
"""
from django.shortcuts import render
from django.http import JsonResponse
from .tasks import process_image_task  # ИЗМЕНИТЕ ИМПОРТ!
import base64
from celery.result import AsyncResult
import tempfile
import os


def celery_upload_view(request):
    """Загрузка изображения для обработки через Celery"""
    if request.method == 'POST' and request.FILES.get('image'):
        image = request.FILES['image']

        try:
            # Сохраняем файл
            from django.core.files.storage import default_storage
            file_path = default_storage.save(f'celery_uploads/{image.name}', image)

            # Запускаем асинхронную задачу
            from .tasks import process_image_task
            task = process_image_task.delay(file_path)

            # Возвращаем HTML с task_id (для простой формы)
            return render(request, 'traffic_signs/celery_upload.html', {
                'task_id': task.id,
                'message': 'Изображение отправлено на обработку'
            })

        except Exception as e:
            return render(request, 'traffic_signs/celery_upload.html', {
                'error': str(e)
            })

    # GET запрос - показываем страницу загрузки
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
