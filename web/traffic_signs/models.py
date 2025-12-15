from django.db import models
from django.contrib.auth.models import User

class TrafficSign(models.Model):
    """Модель для хранения информации о дорожных знаках"""
    SIGN_TYPES = [
        ('stop', 'Стоп'),
        ('speed_limit', 'Ограничение скорости'),
        ('no_entry', 'Въезд запрещен'),
        ('parking', 'Парковка'),
        ('pedestrian', 'Пешеходный переход'),
        ('other', 'Другой'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='Название знака')
    sign_type = models.CharField(max_length=50, choices=SIGN_TYPES, verbose_name='Тип знака')
    description = models.TextField(blank=True, verbose_name='Описание')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    class Meta:
        verbose_name = 'Дорожный знак'
        verbose_name_plural = 'Дорожные знаки'
    
    def __str__(self):
        return self.name


class DetectionResult(models.Model):
    """Результаты детекции знаков на изображениях"""
    image = models.ImageField(upload_to='detections/%Y/%m/%d/', verbose_name='Изображение')
    sign = models.ForeignKey(TrafficSign, on_delete=models.CASCADE, verbose_name='Распознанный знак')
    confidence = models.FloatField(verbose_name='Уверенность', help_text='Значение от 0 до 1')
    detected_at = models.DateTimeField(auto_now_add=True, verbose_name='Время детекции')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Пользователь')
    
    class Meta:
        verbose_name = 'Результат детекции'
        verbose_name_plural = 'Результаты детекции'
        ordering = ['-detected_at']
    
    def __str__(self):
        return f'{self.sign.name} ({self.confidence:.2f})'
