from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
import base64
import random
import time

# Создаем FastAPI приложение
app = FastAPI(
    title="Traffic Sign Detection API",
    description="API для распознавания дорожных знаков",
    version="1.0.0"
)

# Модели данных (что принимаем и что возвращаем)
class DetectionRequest(BaseModel):
    image_base64: str  # Изображение в формате base64
    user_id: Optional[int] = None  # ID пользователя (если есть)

class DetectionResult(BaseModel):
    sign_id: int          # ID знака
    sign_name: str        # Название знака
    confidence: float     # Уверенность (от 0 до 1)
    bounding_box: List[float]  # Координаты [x, y, ширина, высота]

class DetectionResponse(BaseModel):
    success: bool                     # Успешно ли распознавание
    results: List[DetectionResult]    # Список найденных знаков
    processing_time: float            # Время обработки в секундах
    error: Optional[str] = None       # Сообщение об ошибке (если есть)

# Список дорожных знаков для демонстрации
TRAFFIC_SIGNS = [
    {"id": 1, "name": "Стоп", "confidence": 0.95},
    {"id": 2, "name": "Ограничение скорости 60", "confidence": 0.87},
    {"id": 3, "name": "Поворот направо", "confidence": 0.78},
    {"id": 4, "name": "Пешеходный переход", "confidence": 0.92},
    {"id": 5, "name": "Главная дорога", "confidence": 0.85},
]

@app.get("/")
async def root():
    """Главная страница API"""
    return {
        "message": "Traffic Sign Detection API",
        "version": "1.0.0",
        "endpoints": {
            "detect": "/detection/detect (POST)",
            "docs": "/docs",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """Проверка здоровья сервиса"""
    return {"status": "healthy", "service": "traffic_sign_detection"}

@app.post("/detection/detect", response_model=DetectionResponse)
async def detect_signs(request: DetectionRequest):
    """
    Основной endpoint для распознавания дорожных знаков
    
    Принимает:
    - image_base64: изображение в формате base64
    - user_id: ID пользователя (опционально)
    
    Возвращает:
    - success: True/False
    - results: список найденных знаков
    - processing_time: время обработки
    - error: сообщение об ошибке (если success=False)
    """
    start_time = time.time()
    
    try:
        # Декодируем изображение (в реальном проекте здесь была бы нейросеть)
        # Для демонстрации просто проверяем, что это валидный base64
        try:
            image_data = base64.b64decode(request.image_base64)
        except:
            return DetectionResponse(
                success=False,
                results=[],
                processing_time=0,
                error="Invalid base64 image data"
            )
        
        # Имитируем обработку (в реальном проекте здесь вызывается ML модель)
        time.sleep(0.1)  # Задержка для имитации обработки
        
        # Генерируем случайные результаты для демонстрации
        results = []
        num_signs = random.randint(1, 3)  # От 1 до 3 знаков
        
        for i in range(num_signs):
            sign = random.choice(TRAFFIC_SIGNS)
            confidence = sign["confidence"] + random.uniform(-0.1, 0.05)
            confidence = max(0.1, min(0.99, confidence))  # Ограничиваем от 0.1 до 0.99
            
            # Генерируем случайные координаты bounding box
            bbox = [
                random.uniform(100, 300),  # x
                random.uniform(100, 300),  # y
                random.uniform(50, 100),   # ширина
                random.uniform(50, 100)    # высота
            ]
            
            results.append(DetectionResult(
                sign_id=sign["id"],
                sign_name=sign["name"],
                confidence=round(confidence, 2),
                bounding_box=[round(x, 1) for x in bbox]
            ))
        
        processing_time = time.time() - start_time
        
        return DetectionResponse(
            success=True,
            results=results,
            processing_time=round(processing_time, 6),
            error=None
        )
        
    except Exception as e:
        return DetectionResponse(
            success=False,
            results=[],
            processing_time=0,
            error=f"Detection error: {str(e)}"
        )

@app.get("/signs/list")
async def list_available_signs():
    """Возвращает список знаков, которые может распознать система"""
    return {
        "signs": TRAFFIC_SIGNS,
        "total": len(TRAFFIC_SIGNS)
    }

# Асинхронные эндпоинты
@app.get("/async/health")
async def async_health_check():
    """Асинхронная проверка здоровья"""
    await asyncio.sleep(0.1)  # Имитация асинхронной операции
    return {"status": "healthy", "async": True}

@app.post("/async/detect")
async def async_detect_signs(request: DetectionRequest):
    """Асинхронный эндпоинт для детекции"""
    start_time = time.time()
    
    try:
        # Асинхронная обработка
        await asyncio.sleep(0.1)  # Имитация асинхронной обработки
        
        # Декодируем изображение
        try:
            image_data = base64.b64decode(request.image_base64)
        except:
            return DetectionResponse(
                success=False,
                results=[],
                processing_time=0,
                error="Invalid base64 image data"
            )
        
        # Генерируем результаты (в реальном проекте здесь асинхронный ML)
        results = []
        num_signs = random.randint(1, 3)
        
        for i in range(num_signs):
            sign = random.choice(TRAFFIC_SIGNS)
            confidence = sign["confidence"] + random.uniform(-0.1, 0.05)
            confidence = max(0.1, min(0.99, confidence))
            
            bbox = [
                random.uniform(100, 300),
                random.uniform(100, 300),
                random.uniform(50, 100),
                random.uniform(50, 100)
            ]
            
            results.append(DetectionResult(
                sign_id=sign["id"],
                sign_name=sign["name"],
                confidence=round(confidence, 2),
                bounding_box=[round(x, 1) for x in bbox]
            ))
        
        processing_time = time.time() - start_time
        
        return DetectionResponse(
            success=True,
            results=results,
            processing_time=round(processing_time, 6),
            error=None
        )
        
    except Exception as e:
        return DetectionResponse(
            success=False,
            results=[],
            processing_time=0,
            error=f"Async detection error: {str(e)}"
        )
