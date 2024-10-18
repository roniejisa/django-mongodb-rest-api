# customers/decorators.py

from django.http import JsonResponse
from functools import wraps
from rs_rest_api.response import SendJson
from .utils import verifyHashRefreshToken, verifyHash
from rs_jwt.models import JWTBlacklist
import logging
import json
logger = logging.getLogger(__name__)

def check_jwt(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        jwt_token = request.headers.get('Authorization')
        if not jwt_token:
            return SendJson({}, 401, 'Unauthorized')
        # Kiểm tra có từ Beazer hay không
        if not jwt_token.startswith('Bearer '):
            return SendJson({}, 401, 'Unauthorized')

        token = jwt_token[7:]
        try:
            # Vẫn nên có kiểu kiểm tra blacklish kể cả accessToken
            try:
                inBlackList = JWTBlacklist.objects.get(token=token)
                if inBlackList:
                    return SendJson({}, 401, 'Unauthorized')
            except Exception:
                pass
            payload = verifyHash(token)
            if not payload:
                return SendJson({}, 401, 'Unauthorized')

            request.user = payload
        except Exception:
            logger.warning('Invalid JWT token')
            return SendJson({}, 401, 'Unauthorized')

        return view_func(request, *args, **kwargs)
    return _wrapped_view

def check_jwt_refresh(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        data = json.loads(request.body)
        try:
            jwt_token = data.get('refreshToken')
            # Kiểm tra có nằm trong blacklish hay không đã
            try:
                inBlackList = JWTBlacklist.objects.get(token=jwt_token)
                if inBlackList:
                    return SendJson({}, 401, 'Unauthorized')
            except Exception:
                pass
            # Kiểm tra có từ Beazer hay không
            if not jwt_token:
                return SendJson({}, 401, 'Unauthorized')
        
            payload = verifyHashRefreshToken(jwt_token)
            if not payload:
                return SendJson({}, 401, 'Unauthorized')

            request.user = payload
            request.refreshToken = jwt_token
        except Exception:
            logger.warning('Invalid JWT token or Timeout')
            return SendJson({}, 401, 'Unauthorized')

        return view_func(request, *args, **kwargs)
    return _wrapped_view