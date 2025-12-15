#!/usr/bin/env python
"""
Демонстрационный скрипт для проверки проекта
"""
import os
import sys
import requests
import json

def check_django():
    """Проверка Django"""
    print("🔍 Проверка Django...")
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            print("   ✅ Django доступен")
            return True
        else:
            print(f"   ❌ Django ответил с кодом {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Django не доступен: {e}")
        return False

def check_fastapi():
    """Проверка FastAPI"""
    print("🔍 Проверка FastAPI...")
    try:
        response = requests.get("http://localhost:8001/", timeout=5)
        if response.status_code == 200:
            print("   ✅ FastAPI доступен")
            
            # Проверяем документацию
            docs_response = requests.get("http://localhost:8001/docs", timeout=5)
            if docs_response.status_code == 200:
                print("   ✅ FastAPI документация доступна")
            else:
                print("   ⚠️ FastAPI документация не доступна")
            
            return True
        else:
            print(f"   ❌ FastAPI ответил с кодом {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ FastAPI не доступен: {e}")
        return False

def check_celery_page():
    """Проверка страницы Celery"""
    print("🔍 Проверка страницы Celery...")
    try:
        response = requests.get("http://localhost:8000/celery-upload/", timeout=5)
        if response.status_code == 200:
            print("   ✅ Страница Celery доступна")
            return True
        else:
            print(f"   ❌ Страница Celery не доступна: код {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Ошибка при проверке страницы Celery: {e}")
        return False

def check_redis():
    """Проверка Redis"""
    print("🔍 Проверка Redis...")
    try:
        import subprocess
        result = subprocess.run(
            ["docker", "exec", "traffic_sign_detector-redis-1", "redis-cli", "ping"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if "PONG" in result.stdout:
            print("   ✅ Redis работает")
            return True
        else:
            print(f"   ❌ Redis не отвечает: {result.stdout}")
            return False
    except Exception as e:
        print(f"   ❌ Ошибка при проверке Redis: {e}")
        return False

def check_postgres():
    """Проверка PostgreSQL"""
    print("🔍 Проверка PostgreSQL...")
    try:
        import subprocess
        result = subprocess.run(
            ["docker", "exec", "traffic_sign_detector-db-1", "pg_isready", "-U", "traffic_sign_user"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print("   ✅ PostgreSQL работает")
            return True
        else:
            print(f"   ❌ PostgreSQL не отвечает: {result.stdout}")
            return False
    except Exception as e:
        print(f"   ❌ Ошибка при проверке PostgreSQL: {e}")
        return False

def main():
    """Основная функция"""
    print("=" * 60)
    print("ДЕМОНСТРАЦИОННАЯ ПРОВЕРКА ПРОЕКТА")
    print("=" * 60)
    
    checks = [
        check_django,
        check_fastapi,
        check_celery_page,
        check_redis,
        check_postgres,
    ]
    
    results = []
    for check in checks:
        results.append(check())
    
    print("\n" + "=" * 60)
    print("ИТОГИ ПРОВЕРКИ:")
    print("=" * 60)
    
    successful = sum(results)
    total = len(results)
    
    print(f"✅ Успешно: {successful}/{total}")
    
    if successful == total:
        print("\n🎉 ВСЕ СИСТЕМЫ РАБОТАЮТ КОРРЕКТНО!")
        print("\nСсылки для демонстрации:")
        print("1. Django: http://localhost:8000/")
        print("2. Celery Upload: http://localhost:8000/celery-upload/")
        print("3. FastAPI: http://localhost:8001/")
        print("4. FastAPI Docs: http://localhost:8001/docs")
    else:
        print("\n⚠️  Некоторые системы требуют внимания")
        print("\nРекомендуемые действия:")
        print("1. Проверьте логи: docker-compose logs")
        print("2. Перезапустите контейнеры: docker-compose restart")
        print("3. Проверьте конфигурацию docker-compose.yml")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
