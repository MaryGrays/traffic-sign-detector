from django.urls import path
from django.shortcuts import render
from . import views
from .celery_views import celery_upload_view, check_task_status
from .async_views import AsyncAPIView

app_name = 'traffic_signs'

urlpatterns = [
    path('test-celery/', views.test_celery_upload, name='test_celery'),
    path('test-celery/', lambda request: render(request, 'traffic_signs/test_celery.html'), name='test_celery'),
    path('', views.home, name='home'),
    path('upload/', views.upload_image, name='upload'),
    path('results/', views.results, name='results'),
    path('api/docs/', views.api_docs, name='api_docs'),
    path('api/detect/', views.api_detect, name='api_detect'),

    # Celery
    path('celery-upload/', celery_upload_view, name='celery_upload'),
    path('check-task/<str:task_id>/', check_task_status, name='check_task'),

    # Async API
    path('api/async/', AsyncAPIView.as_view(), name='async_api'),
]

urlpatterns += [
    path('test-upload/', lambda request: render(request, 'traffic_signs/test_upload.html'), name='test_upload'),
]