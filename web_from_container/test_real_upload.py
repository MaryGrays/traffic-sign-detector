import requests
import base64

print("Тестирование загрузки реального изображения через веб-интерфейс")

# URL для тестирования
upload_url = "http://localhost:8000/upload/"
api_url = "http://localhost:8000/api/upload/"

# Создаем тестовое изображение (симулируем файл)
test_image_content = b"FAKE_IMAGE_CONTENT_FOR_TESTING" * 100

# Тест 1: Веб-интерфейс
print("\n1. Тестирование веб-интерфейса (/upload/):")
files = {'image': ('test_image.jpg', test_image_content, 'image/jpeg')}
try:
    response = requests.post(upload_url, files=files)
    print(f"   Статус: {response.status_code}")
    if response.status_code == 200:
        print("   ✅ Страница загружена успешно")
        if "Results" in response.text:
            print("   ✅ Обнаружена страница результатов")
        elif "Upload Traffic Sign Image" in response.text:
            print("   ⚠️  Вернулась страница загрузки (возможно ошибка API)")
    else:
        print(f"   ❌ Ошибка: {response.status_code}")
except Exception as e:
    print(f"   ❌ Ошибка запроса: {e}")

# Тест 2: API эндпоинт
print("\n2. Тестирование API эндпоинта (/api/upload/):")
try:
    files = {'image': ('test_image.jpg', test_image_content, 'image/jpeg')}
    response = requests.post(api_url, files=files)
    print(f"   Статус: {response.status_code}")
    
    try:
        result = response.json()
        print(f"   📊 JSON ответ:")
        import json
        print(json.dumps(result, indent=2))
        
        if result.get('success'):
            print("   🎉 API детекция успешна!")
            if 'results' in result:
                print(f"   Найдено знаков: {len(result['results'])}")
                for i, res in enumerate(result['results']):
                    sign_name = res.get('sign_name', res.get('class_name', 'Unknown'))
                    print(f"   {i+1}. {sign_name} - {res.get('confidence', 0):.2f}")
        else:
            print(f"   ⚠️  Детекция не удалась: {result.get('error', 'Unknown error')}")
            
    except ValueError:
        print(f"   ❌ Ответ не JSON: {response.text[:200]}")
        
except Exception as e:
    print(f"   ❌ Ошибка API запроса: {e}")

print("\n" + "="*60)
print("Тестирование завершено")
