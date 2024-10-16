# customers/decorators.py

from django.http import JsonResponse
from functools import wraps
from .response import SendJson
import logging

logger = logging.getLogger(__name__)

def check_jwt(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        jwtToken = request.headers.get('Authorization')
        if not jwtToken:
            return SendJson({}, 401, 'Unauthorized')
        # Kiểm tra có từ Beazer hay không
        if 'Bearer' not in jwtToken:
            return SendJson({}, 401, 'Unauthorized')
        if not jwtToken:
            return SendJson({}, 401, 'Unauthorized')
        if not verifyHash(jwtToken):
            return SendJson({}, 401, 'Unauthorized')
        return view_func(request, *args, **kwargs)
    return _wrapped_view