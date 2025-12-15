"""
Асинхронные view для Django
"""
from django.http import JsonResponse
from django.views import View
import httpx
import asyncio
import base64

class AsyncAPIView(View):
    """Асинхронный view для работы с API"""
    async def get(self, request):
        """Асинхронный GET запрос"""
        async with httpx.AsyncClient() as client:
            try:
                # Асинхронный запрос к ML API
                response = await client.get('http://api:8001/health', timeout=10.0)
                data = response.json()
                return JsonResponse({
                    'api_status': data.get('status', 'unknown'),
                    'message': 'Асинхронный запрос выполнен'
                })
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)
    
    async def post(self, request):
        """Асинхронная обработка изображения"""
        if request.FILES.get('image'):
            image = request.FILES['image']
            image_data = await image.read()
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            async with httpx.AsyncClient() as client:
                try:
                    payload = {
                        'image_base64': image_base64,
                        'user_id': request.user.id if request.user.is_authenticated else None
                    }
                    
                    # Асинхронный запрос к ML API
                    response = await client.post(
                        'http://api:8001/detection/detect',
                        json=payload,
                        timeout=30.0
                    )
                    
                    return JsonResponse(response.json())
                    
                except httpx.RequestError as e:
                    return JsonResponse({
                        'success': False,
                        'error': f'API request failed: {str(e)}'
                    }, status=500)
        
        return JsonResponse({'error': 'No image provided'}, status=400)
