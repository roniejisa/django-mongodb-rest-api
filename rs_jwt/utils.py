import jwt
from ai.settings import JWT_SECRET, JWT_SECRET_REFRESH, TIME_SECRET, TIME_REFRESH_SECRET
import datetime
def signToken(payload = {}):
      # Expires in 30 minutes
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def signRefreshToken(payload = {}):
    payload['exp'] = datetime.datetime.utcnow() + datetime.timedelta(minutes=TIME_REFRESH_SECRET)  # Expires in 30 minutes
    return jwt.encode(payload, JWT_SECRET_REFRESH, algorithm="HS256")

def verifyHash(token):
    return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
def verifyHashRefreshToken(token):
    return jwt.decode(token, JWT_SECRET_REFRESH, algorithms=["HS256"])

def get_client_ip(request):
    ip_local_customer = request.headers.get('ip', '')
    if ip_local_customer != '': return ip_local_customer
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        # Header HTTP_X_FORWARDED_FOR có thể chứa nhiều IP, lấy IP đầu tiên
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def get_user_agent_string(request):
    return request.headers.get('User-Agent', '')