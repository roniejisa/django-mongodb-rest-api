# customers/decorators.py

from django.http import JsonResponse
from functools import wraps
import logging
from .response import SendJson
logger = logging.getLogger(__name__)

def require_api_key(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        api_key = request.headers.get('X-API-KEY')
        if not api_key:
            logger.warning("Missing X-API-KEY header.")
            return SendJson({}, 404, 'Not Found')
        if api_key != '123456':
            logger.warning(f"Invalid API Key: {api_key}")
            return SendJson({}, 404, 'Invalid Secret Key')
        return view_func(request, *args, **kwargs)
    return _wrapped_view
