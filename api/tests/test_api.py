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
