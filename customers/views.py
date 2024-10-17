# customers/views.py

import json
from rs_rest_api.views import RSRestAPI
from .models import Customer
class CustomerRestAPI(RSRestAPI):
    model = Customer
    name = "customers"
    exclude_fields = ['password']
    filter_fields = ['username', 'email']
    is_auth = True
    field_hash = "password"
    request_name = "password"

    VALIDATOR_POST = [
        {
            'name': 'username',
            'rules': [
                {
                    'type' : 'unique',
                    'message': 'Username đã tồn tại!'
                },
            ],
            'message' : 'Username là bắt buộc!'
        },
        {
            'name': 'email',
            'rules': [
                {
                    'type' : 'unique',
                    'message': 'Email đã tồn tại!'
                },
            ],
            'message' : 'Email là bắt buộc!'
        },
        {
            'name': 'password',
            'rules': [
                {
                    'type' : 'min_length',
                    'value' : 8,
                    'message' : 'Password phải nhiều hơn 8 ký tự!'
                },
                {
                    'type' : 'max_length',
                    'value' : 32,
                    'message' : 'Password phải nhỏ hơn 32 ký tự!'
                },
                {
                    'type' : 'same',
                    'value' : 'password_confirmation',
                    'message' : 'Password khác nhau!'
                },
            ],
            'message' : 'Password là bắt buộc!'
        }
    ]
    
    VALIDATOR_PATCH = [
        {
            'name': 'username',
            'rules': [
                {
                    'type' : 'unique',
                    'message': 'Username đã tồn tại!'
                },
            ],
            'message' : 'Username là bắt buộc!'
        },
        {
            'name': 'email',
            'rules': [
                {
                    'type' : 'unique',
                    'message': 'Email đã tồn tại!'
                },
            ],
            'message' : 'Email là bắt buộc!'
        },
        {
            'name': 'password',
            'rules': [
                {
                    'type' : 'min_length',
                    'value' : 8,
                    'message' : 'Password phải nhiều hơn 8 ký tự!'
                },
                {
                    'type' : 'max_length',
                    'value' : 32,
                    'message' : 'Password phải nhỏ hơn 32 ký tự!'
                },
                {
                    'type' : 'same',
                    'value' : 'password_confirmation',
                    'message' : 'Password khác nhau!'
                },
            ],
            'message' : 'Password là bắt buộc!'
        }
    ]

    # Mở ra để đăng ký
    # def post(self, request, *args, **kwargs):
    #     print('test')
    #     if '_id' in kwargs:
    #         return SendJson({'error': 'Not Found'}, 404, 'Not Found')
    #     return self.view_list(request)