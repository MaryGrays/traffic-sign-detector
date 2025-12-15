import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
import re

print("Тестирование загрузки изображения с CSRF токеном")

# URL для тестирования
upload_url = "http://localhost:8000/upload/"
api_url = "http://localhost:8000/api/upload/"

# Тест 1: Получение CSRF токена и отправка через веб-интерфейс
print("\n1. Тестирование веб-интерфейса с CSRF токеном:")

# Сначала получаем страницу чтобы получить CSRF токен
session = requests.Session()
try:
    # GET запрос для получения CSRF токена
    get_response = session.get(upload_url)
    print(f"   GET статус: {get_response.status_code}")
    
    # Ищем CSRF токен в HTML
    csrf_pattern = r'name="csrfmiddlewaretoken" value="([^"]+)"'
    match = re.search(csrf_pattern, get_response.text)
    
    if match:
        csrf_token = match.group(1)
        print(f"   ✅ CSRF токен найден: {csrf_token[:20]}...")
        
        # Теперь отправляем POST запрос с CSRF токеном
        test_image_content = b"FAKE_IMAGE_CONTENT_FOR_TESTING" * 100
        
        # Создаем multipart форму с CSRF токеном
        multipart_data = MultipartEncoder(
            fields={
                'csrfmiddlewaretoken': csrf_token,
                'image': ('test_image.jpg', test_image_content, 'image/jpeg')
            }
        )
        
        headers = {
            'Content-Type': multipart_data.content_type,
            'Referer': upload_url
        }
        
        post_response = session.post(upload_url, 
                                    data=multipart_data, 
                                    headers=headers)
        
        print(f"   POST статус: {post_response.status_code}")
        
        if post_response.status_code == 200:
            print("   ✅ Страница загружена успешно")
            if "Results" in post_response.text or "Detected Traffic Signs" in post_response.text:
                print("   ✅ Обнаружена страница результатов")
            elif "Upload Traffic Sign Image" in post_response.text:
                print("   ⚠️  Вернулась страница загрузки")
                # Проверим есть ли ошибка
                if "error" in post_response.text.lower():
                    error_match = re.search(r'<div[^>]*class="[^"]*error[^"]*"[^>]*>([^<]+)', 
                                           post_response.text, re.IGNORECASE)
                    if error_match:
                        print(f"   Ошибка на странице: {error_match.group(1).strip()}")
        else:
            print(f"   ❌ Ошибка POST: {post_response.status_code}")
            print(f"   Ответ: {post_response.text[:200]}")
            
    else:
        print("   ❌ CSRF токен не найден на странице")
        
except Exception as e:
    print(f"   ❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()

# Тест 2: API эндпоинт (должен работать без CSRF)
print("\n2. Тестирование API эндпоинта (/api/upload/):")
print("   Note: API endpoints обычно не требуют CSRF токена")

try:
    # Создаем новый сессию для API теста
    test_image_content = b"API_TEST_IMAGE_CONTENT" * 100
    
    # API endpoint может не требовать CSRF, но давайте проверим
    files = {'image': ('test_api_image.jpg', test_image_content, 'image/jpeg')}
    
    # Пробуем без CSRF сначала
    response = requests.post(api_url, files=files)
    print(f"   Статус (без CSRF): {response.status_code}")
    
    if response.status_code == 403:
        print("   ⚠️  API также требует CSRF, получаем токен...")
        
        # Получаем CSRF токен
        get_response = requests.get(upload_url)
        match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', get_response.text)
        
        if match:
            csrf_token = match.group(1)
            cookies = {'csrftoken': csrf_token}
            headers = {'X-CSRFToken': csrf_token}
            
            # Отправляем с CSRF токеном
            multipart_data = MultipartEncoder(
                fields={
                    'csrfmiddlewaretoken': csrf_token,
                    'image': ('test_api_image.jpg', test_image_content, 'image/jpeg')
                }
            )
            
            headers['Content-Type'] = multipart_data.content_type
            response = requests.post(api_url, 
                                    data=multipart_data, 
                                    headers=headers,
                                    cookies=cookies)
            
            print(f"   Статус (с CSRF): {response.status_code}")
    
    # Пробуем прочитать ответ
    try:
        result = response.json()
        print(f"   📊 JSON ответ получен")
        if result.get('success'):
            print(f"   🎉 API детекция успешна!")
        else:
            print(f"   ⚠️  API ошибка: {result.get('error', 'Unknown')}")
    except:
        print(f"   📝 Ответ текст: {response.text[:200]}")
        
except Exception as e:
    print(f"   ❌ Ошибка API запроса: {e}")

print("\n" + "="*60)
print("Тестирование завершено")
