import requests
import base64
import json

print('Тестирование эндпоинта /detection/detect...')

# Создаем простое тестовое изображение (base64 encoded)
# Это минимальное валидное JPEG изображение 1x1 пиксель
tiny_jpeg = '/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdAAH/2Q=='

try:
    # Подготовка payload
    payload = {
        'image_base64': tiny_jpeg,
        'user_id': None
    }
    
    print(f'Отправка запроса на http://api:8001/detection/detect')
    print(f'Размер изображения: {len(tiny_jpeg)} байт в base64')
    
    response = requests.post(
        'http://api:8001/detection/detect',
        json=payload,
        timeout=10
    )
    
    print(f'✅ Ответ получен: HTTP {response.status_code}')
    
    try:
        result = response.json()
        print(f'✅ JSON ответ:')
        print(json.dumps(result, indent=2))
        
        if result.get('success'):
            print('🎉 Детекция успешна!')
            if 'results' in result:
                print(f'   Найдено объектов: {len(result["results"])}')
                for i, res in enumerate(result['results']):
                    print(f'   {i+1}. {res.get("class_name", "Unknown")} - уверенность: {res.get("confidence", 0):.2f}')
        else:
            print(f'⚠️  Детекция не удалась: {result.get("error", "Unknown error")}')
            
    except ValueError:
        print(f'❌ Ответ не в JSON формате: {response.text[:200]}')
        
except requests.exceptions.ConnectionError:
    print('❌ Ошибка соединения: API недоступен')
except requests.exceptions.Timeout:
    print('❌ Таймаут: API не ответил вовремя')
except Exception as e:
    print(f'❌ Неожиданная ошибка: {e}')
    import traceback
    traceback.print_exc()

print('')
print('='*50)
print('Тестирование завершено')
