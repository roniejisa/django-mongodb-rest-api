# rs_rest_api/views.py

import json
import logging
from django.http import JsonResponse, HttpResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.forms.models import model_to_dict
from django.db import IntegrityError
from .decorators import require_api_key
from .utils import serialize_customer, hashSign, verifyHash
from .response import SendJson
from .validator import ValidatorRestAPI
from .jwt import check_jwt
# from pymongo import MongoClient
from bson.objectid import ObjectId

@method_decorator(csrf_exempt, name='dispatch')
class RSRestAPI(View, ValidatorRestAPI):
    name = ""
    model = None
    exclude_fields = []
    filter_fields = []
    # Thêm trường hợp đặc biệt là khi xác định là tài khoản hay cái gì cần mã hóa thì để ở đây
    is_auth = False
    field_hash = ""
    request_name = ""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.logger = logging.getLogger(self.name)

    @method_decorator(require_api_key)
    def get(self, request, *args, **kwargs):
        if '_id' in kwargs:
            return self.view_detail(request, kwargs['_id'])
        else:
            return self.view_list(request)

    @method_decorator(require_api_key)
    @method_decorator(check_jwt)
    def post(self, request, *args, **kwargs):
        if '_id' in kwargs:
            return SendJson({'error': 'Not Found'}, 404, 'Not Found')
        return self.view_list(request)

    @method_decorator(require_api_key)
    @method_decorator(check_jwt)
    def put(self, request, *args, **kwargs):
        if '_id' not in kwargs:
            return SendJson({}, 404, 'Not Found')
        return self.view_detail(request, kwargs['_id'])@method_decorator(require_api_key)
    @method_decorator(require_api_key)
    @method_decorator(check_jwt)
    def patch(self, request, *args, **kwargs):
        if '_id' not in kwargs:
            return SendJson({}, 404, 'Not Found')
        return self.view_detail(request, kwargs['_id'])

    @method_decorator(require_api_key)
    @method_decorator(check_jwt)
    def delete(self, request, *args, **kwargs):
        if '_id' not in kwargs:
            return SendJson({}, 404, 'Not Found')
        return self.view_detail(request, kwargs['_id'])

    def view_list(self, request):
        if request.method == 'GET':
            try:
                page, limit, offset = self.paginate_query(request)
                # Lọc
                filters = self.filter_query(request)
                # Sắp xếp
                sort = request.GET.get('sort')  # Ví dụ: sort=username hoặc sort=-username

                items = self.model.objects.filter(**filters)
                if sort:
                    items = items.order_by(sort)
                items = items[offset:offset + limit]
                list_data = []
                for item in items:
                    item_dict = serialize_customer(item, self.exclude_fields)
                    list_data.append(item_dict)

                return SendJson({
                    'page': page,
                    'limit': limit,
                    'data': list_data
                }, 200, 'Lấy dữ liệu thành công!')
            except ValueError:
                self.logger.error("Invalid pagination parameters.")
                return JsonResponse({'error': 'Invalid pagination parameters.'}, status=400)
            except Exception as e:
                self.logger.error(f"Error fetching {self.name} with filters/sorting: {e}")
                return JsonResponse({'error': 'Internal Server Error.'}, status=500)

        elif request.method == 'POST':
            try:
                data = json.loads(request.body)
                # Kiểm tra dữ liệu bắt buộc
                notValid = self.check_not_valid(request, data)
                if notValid:
                    return SendJson({
                        "data": {},
                        "error": 400,
                        "message": notValid
                    })
                # Tạo mới đối tượng
                obj = self.model()
                for key in data:
                    if self.is_auth and key == self.field_hash:
                        data[key] = hashSign(data[key])
                    setattr(obj, key, data[key])
                obj.save()
                obj_data = serialize_customer(obj, self.exclude_fields)
                # Loại bỏ các trường không cần thiết
                return SendJson({
                    "data": obj_data
                }, 201, f'Tạo {self.name} liệu thành công!')
            except json.JSONDecodeError:
                self.logger.error(f"Invalid JSON: {request.body}")
                return SendJson({}, 400, 'Invalid JSON.')
            except Exception as e:
                self.logger.error(f"Unexpected error: {e}")
                return SendJson({}, 500, 'Internal Server Error.')
        else:
            self.logger.warning(f"Method not allowed: {request.method}")
            return SendJson({}, 405, 'Method not allowed.')

    def view_detail(self, request, _id):
        try:
            obj = self.model.objects.get(pk=ObjectId(_id))
        except Exception as e:
            return SendJson({}, 404, f'Not Found')
        if request.method == 'GET':
            obj_data = serialize_customer(obj, self.exclude_fields)
            return SendJson({
                'data': obj_data
            }, 200, 'Lấy dữ liệu thành công!')
            
        elif request.method == 'PUT' or request.method == 'PATCH':
            try:
                data = json.loads(request.body)

                # Kiểm tra dữ liệu bắt buộc
                notValid = self.check_not_valid(request, data, obj)
                if notValid:
                    return SendJson({
                        "data": {},
                        "error": 400,
                        "message": notValid
                    })
                # Cập nhật thông tin
                for key in data:
                    if self.is_auth and key == self.field_hash:
                        data[key] = hashSign(data[key])
                    setattr(obj, key, data[key])
                obj.save()
                
                return SendJson({
                    "data": serialize_customer(obj, self.exclude_fields)
                }, 200, f'Cập nhật {self.name} thành công!')
            except json.JSONDecodeError:
                self.logger.error(f"Invalid JSON: {request.body}")
                return SendJson({}, 400, 'Invalid JSON.')
            except Exception as e:
                self.logger.error(f"Unexpected error: {e}")
                return SendJson({}, 500, 'Internal Server Error.')

        elif request.method == 'DELETE':
            try:
                obj.delete()
                return SendJson({
                }, 204, f'Đã xóa {self.name} thành công!')
            except Exception as e:
                self.logger.error(f"Error deleting {self.name}: {e}")
                return SendJson({}, 500, f'Error deleting {self.name}: {e}')
        else:
            self.logger.warning(f"Method not allowed: {request.method}")
            return SendJson({}, 405, f'Method not allowed: {request.method}')

    def paginate_query(self, request):
        # Phân trang
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 2))
        offset = (page - 1) * limit
        return page, limit, offset
    
    def filter_query(self, request):
        # Tìm kiếm
        filters = {}
        for field in self.filter_fields:
            value = request.GET.get(field)
            if value:
                filters[f'{field}__icontains'] = value
        return filters