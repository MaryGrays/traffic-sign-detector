from django.contrib import admin
from django.urls import path
from django.http import HttpResponse
from django.conf import settings
from django.conf.urls.static import static
from traffic_signs import views

def home(request):
    return HttpResponse('<h1>Traffic Sign Detector</h1><p>Django is working</p><p><a href="/upload/">Upload Image</a> | <a href="/admin/">Admin</a> | <a href="http://localhost:8001/docs">API Docs</a></p>')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home),
    path('upload/', views.upload_image),
    path('results/', views.detection_results),
    path('api/upload/', views.api_upload),
    path('api/docs/', views.api_documentation),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
