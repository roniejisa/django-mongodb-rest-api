import jwt
from ai.settings import JWT_SECRET, JWT_SECRET_REFRESH, TIME_SECRET, TIME_REFRESH_SECRET
import datetime
def signToken(payload = {}):
    payload['exp'] = datetime.datetime.utcnow() + datetime.timedelta(minutes=TIME_SECRET)  # Expires in 30 minutes
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def signRefreshToken(payload = {}):
    payload['exp'] = datetime.datetime.utcnow() + datetime.timedelta(minutes=TIME_REFRESH_SECRET)  # Expires in 30 minutes
    return jwt.encode(payload, JWT_SECRET_REFRESH, algorithm="HS256")

def verifyHash(token):
    return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
def verifyHashRefreshToken(token):
    return jwt.decode(token, JWT_SECRET_REFRESH, algorithms=["HS256"])