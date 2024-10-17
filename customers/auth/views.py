# customers/views.py

import json
from ..models import Customer
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from rs_rest_api.response import SendJson
import logging
from rs_jwt.utils import signToken, signRefreshToken
from rs_rest_api.utils import verifyHash, hashSign
from rs_jwt.jwt import check_jwt, check_jwt_refresh
from bson.objectid import ObjectId
from rs_rest_api.validator import ValidatorRestAPI
from rs_rest_api.decorators import require_api_key
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
                token = signToken({
                    '_id': str(obj._id)
                })
                refreshToken = signRefreshToken({
                    '_id': str(obj._id )
                })
                return SendJson({
                    'accessToken': token,
                    'refreshToken': refreshToken
                }, 200 , 'Đăng nhập thành công')
            return SendJson({}, 433, 'Not Found')
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
            try:
                obj = Customer.objects.get(_id=ObjectId(user['_id']))
                token = signToken({
                    '_id': str(obj._id)
                })
                refreshToken = signRefreshToken({
                    '_id': str(obj._id)
                })
                return SendJson({
                    'accessToken': token,
                    'refreshToken': refreshToken
                }, 200 , 'Refresh token thành công')
            except Exception as e:
                return SendJson({'error': 'Not Found'}, 404, 'Not Found')