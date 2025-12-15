from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import TrafficSign, DetectionResult

@admin.register(TrafficSign)
class TrafficSignAdmin(admin.ModelAdmin):
    list_display = ['name', 'image', 'sign_type', 'created_at']
    list_filter = ['sign_type']
    readonly_fields = ['image_preview']
    search_fields = ['name', 'description']
    ordering = ['name']

    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="100" />')
        return "Нет изображения"

    image_preview.short_description = 'Предпросмотр'
admin.site.register(TrafficSign, TrafficSignAdmin)

@admin.register(DetectionResult)
class DetectionResultAdmin(admin.ModelAdmin):
    list_display = ['sign', 'confidence', 'detected_at', 'user']
    list_filter = ['sign', 'detected_at']
    search_fields = ['sign__name']
    date_hierarchy = 'detected_at'
    readonly_fields = ['detected_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('sign', 'user')
