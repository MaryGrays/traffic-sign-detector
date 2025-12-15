import requests
import re

print("Тестирование загрузки изображения")

# URL для тестирования
upload_url = "http://localhost:8000/upload/"
api_url = "http://localhost:8000/api/upload/"

print("\n1. Тестирование веб-интерфейса (/upload/):")

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
        print(f"   ✅ CSRF токен найден")
        
        # Теперь отправляем POST запрос с CSRF токеном
        test_image_content = b"FAKE_IMAGE_CONTENT_FOR_TESTING" * 100
        
        # Подготавливаем данные для отправки
        files = {'image': ('test_image.jpg', test_image_content, 'image/jpeg')}
        data = {'csrfmiddlewaretoken': csrf_token}
        
        headers = {
            'Referer': upload_url
        }
        
        post_response = session.post(upload_url, 
                                    data=data,
                                    files=files,
                                    headers=headers)
        
        print(f"   POST статус: {post_response.status_code}")
        
        if post_response.status_code == 200:
            print("   ✅ Страница загружена успешно")
            if "Results" in post_response.text or "Detected Traffic Signs" in post_response.text:
                print("   ✅ Обнаружена страница результатов")
            elif "Upload Traffic Sign Image" in post_response.text:
                print("   ⚠️  Вернулась страница загрузки")
        else:
            print(f"   ❌ Ошибка POST: {post_response.status_code}")
            
    else:
        print("   ❌ CSRF токен не найден на странице")
        
except Exception as e:
    print(f"   ❌ Ошибка: {e}")

print("\n2. Тестирование API эндпоинта (/api/upload/):")

try:
    # API endpoint не должен требовать CSRF (благодаря @csrf_exempt)
    test_image_content = b"API_TEST_IMAGE_CONTENT" * 100
    files = {'image': ('test_api_image.jpg', test_image_content, 'image/jpeg')}
    
    response = requests.post(api_url, files=files)
    print(f"   Статус: {response.status_code}")
    
    if response.status_code == 200:
        print("   ✅ API endpoint работает!")
        try:
            result = response.json()
            print(f"   📊 JSON ответ получен")
            if result.get('success'):
                print(f"   🎉 API детекция успешна!")
                if 'results' in result:
                    print(f"   Найдено знаков: {len(result['results'])}")
                    for i, res in enumerate(result['results']):
                        sign_name = res.get('sign_name', 'Unknown')
                        print(f"   {i+1}. {sign_name} - {res.get('confidence', 0):.2f}")
            else:
                print(f"   ⚠️  API ошибка: {result.get('error', 'Unknown')}")
        except:
            print(f"   📝 Ответ: {response.text[:200]}")
    else:
        print(f"   ❌ Ошибка: {response.status_code}")
        print(f"   Ответ: {response.text[:200]}")
        
except Exception as e:
    print(f"   ❌ Ошибка: {e}")

print("\n" + "="*60)
print("Тестирование завершено")
