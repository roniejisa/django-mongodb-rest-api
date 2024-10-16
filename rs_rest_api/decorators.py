# customers/decorators.py

from django.http import JsonResponse
from functools import wraps
import logging

logger = logging.getLogger(__name__)

def require_api_key(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        api_key = request.headers.get('X-API-KEY')
        if not api_key:
            logger.warning("Missing X-API-KEY header.")
            return JsonResponse({'error': 'Missing X-API-KEY header.'}, status=403)
        if api_key != '123456':
            logger.warning(f"Invalid API Key: {api_key}")
            return JsonResponse({'error': 'Invalid API Key.'}, status=403)
        return view_func(request, *args, **kwargs)
    return _wrapped_view
