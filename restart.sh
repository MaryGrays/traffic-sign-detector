#!/bin/bash
echo "🔄 Перезагрузка Traffic Sign Detector..."
docker-compose down
docker-compose up -d
echo "✅ Проект перезагружен"
