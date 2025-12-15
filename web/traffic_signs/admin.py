from django.contrib import admin
from .models import TrafficSign, DetectionResult

@admin.register(TrafficSign)
class TrafficSignAdmin(admin.ModelAdmin):
    list_display = ['name', 'sign_type', 'created_at']
    list_filter = ['sign_type']
    search_fields = ['name', 'description']
    ordering = ['name']

@admin.register(DetectionResult)
class DetectionResultAdmin(admin.ModelAdmin):
    list_display = ['sign', 'confidence', 'detected_at', 'user']
    list_filter = ['sign', 'detected_at']
    search_fields = ['sign__name']
    date_hierarchy = 'detected_at'
    readonly_fields = ['detected_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('sign', 'user')
