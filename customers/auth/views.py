# customers/views.py

import json
from ..models import Customer
from rs_jwt.models import JWTSession, JWTBlacklist
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from rs_rest_api.response import SendJson
import logging
from rs_jwt.utils import signToken, signRefreshToken, get_client_ip, get_user_agent_string
from ai.settings import TIME_SECRET, TIME_REFRESH_SECRET
from rs_rest_api.utils import verifyHash, hashSign
from rs_jwt.jwt import check_jwt, check_jwt_refresh
from bson.objectid import ObjectId
from rs_rest_api.validator import ValidatorRestAPI
from rs_rest_api.decorators import require_api_key
import datetime
@method_decorator(csrf_exempt, name='dispatch')
class Auth(View, ValidatorRestAPI):
    name = 'auth'
    action = None
    VALIDATOR_POST = [
        {
            'name': 'username',
            'rules': [],
            'message' : 'Username là bắt buộc!'
        },
        {
            'name': 'password',
            'rules': [],
            'message' : 'Password là bắt buộc!'
        }
    ]
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.logger = logging.getLogger(self.name)

    
    @method_decorator(check_jwt)
    def get(self, request, *args, **kwargs):
        match self.action:
            case 'profile':
                return self.profile(request, *args, **kwargs)
        return SendJson({}, 404, 'Not Found')

    @method_decorator(require_api_key)
    def post(self, request, *args, **kwargs):
        match self.action:
            case 'login':
                return self.login(request, *args, **kwargs)
            case 'refresh-token':
                return self.refresh_token(request, *args, **kwargs)
        # handle POST request
        return SendJson({}, 404, 'Not Found')
    def login(self, request):
        if request.method == 'POST':
            
            # try:
            data = json.loads(request.body)
            notValid = self.check_not_valid(request, data)
            if notValid:
                return SendJson({},400,notValid)
            # try:
            obj = Customer.objects.get(username=data['username'])

            # Kiểm tra cả mật khẩu nữa
            if verifyHash(data['password'], obj.password):
                token, refreshToken, timeRefreshToken = self.createToken(obj)
                # Chỗ này cần lưu dữ liệu vào bảng jwt_sessions
                ip = get_client_ip(request)
                userAgent = get_user_agent_string(request)
                obj_session = {
                    'expires_at':timeRefreshToken,
                    'refresh_token':refreshToken,
                    'user_id':str(obj._id),
                    'device_info': userAgent,
                    'ip_address':ip,
                    'user_agent':userAgent
                }
                
                jwt_session = JWTSession()
                for key in obj_session:
                    setattr(jwt_session, key, obj_session[key])
                jwt_session.save()

                return SendJson({
                    'accessToken': token,
                    'refreshToken': refreshToken
                }, 200 , 'Đăng nhập thành công')
            return SendJson({}, 401, 'Tài khoản hoặc mật khẩu không đúng vui lòng thử lại!')
                # except Exception as e:
                #     return SendJson({'error': 'Not Found'}, 404, 'Not Found')
                # if obj.password != data['password']:
                #     return SendJson({'error': 'Not Found'}, 404, 'Not Found')
                # # Kiểm tra dữ liệu đăng nhập ở đây
                # return SendJson({
                #     'data': data
                # }, 404, 'Not Found')
            # except Exception as e:
                # return SendJson({'error': 'Not Found'}, 404, 'Not Found')
        # return SendJson({'error': 'Not Found'}, 404, 'Not Found')
    def profile(self, request):
        return SendJson({
            'data': request.user
        }, 200, 'Đăng nhập thành công')

    # Refresh TOKEN
    @method_decorator(check_jwt_refresh)
    def refresh_token(self, request):
        if request.method == 'POST':
            user = request.user
            oldToken = request.refreshToken
            try:
                obj = Customer.objects.get(_id=ObjectId(user['_id']))
                token, refreshToken, timeRefreshToken = self.createToken(obj)

                # Lấy lại thông tin của cái cũ ra đây để còn sửa và thay đổi thời gian
                jwt_session = JWTSession.objects.get(refresh_token=f'{str(oldToken)}')
                jwt_session.expires_at = timeRefreshToken
                jwt_session.refresh_token = refreshToken
                jwt_session.save()

                # Thêm lại vào blacklist tránh dùng lại
                jwt_blacklist = JWTBlacklist()
                jwt_blacklist.token = oldToken
                jwt_blacklist.created_at = datetime.datetime.now()
                jwt_blacklist.save()

                return SendJson({
                    'accessToken': token,
                    'refreshToken': refreshToken
                }, 200 , 'Refresh token thành công')
            except Exception as e:
                return SendJson({}, 401, 'Unauthorized')
    
    def createToken(self, obj):
        timeToken = datetime.datetime.utcnow() + datetime.timedelta(minutes=TIME_SECRET)
        token = signToken({
            '_id': str(obj._id),
            'exp': timeToken
        })

        timeRefreshToken = datetime.datetime.utcnow() + datetime.timedelta(minutes=TIME_REFRESH_SECRET)
        refreshToken = signRefreshToken({
            '_id': str(obj._id ),
            'exp': timeRefreshToken
        })

        return token, refreshToken, timeRefreshToken