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
