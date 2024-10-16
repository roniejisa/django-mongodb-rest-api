
class ValidatorRestAPI():
    # Kiểm tra validator nên them request
    VALIDATOR_POST = None
    VALIDATOR_GET = None
    VALIDATOR_PUT = None
    VALIDATOR_PATCH = None
    VALIDATOR_DELETE = None
    def check_not_valid(self, request, body, obj = None):
        if self.VALIDATOR_POST is not None and request.method == 'POST':
            for validator in self.VALIDATOR_POST:
                message = self.check_validator(validator, body)
                if message:
                    return message
        if self.VALIDATOR_GET is not None and request.method == 'GET':
            for validator in self.VALIDATOR_GET:
                message = self.check_validator(validator, body)
                if message:
                    return message
        if self.VALIDATOR_PUT is not None and request.method == 'PUT':
            for validator in self.VALIDATOR_PUT:
                # Cần kiểm tra nếu body không có thì có thể bỏ qua luôn
                if validator['name'] not in body:
                    continue
                message = self.check_validator_edit(validator, body, obj)
                if message:
                    return message
        if self.VALIDATOR_PATCH is not None and request.method == 'PATCH':
            for validator in self.VALIDATOR_PATCH:
                # Cần kiểm tra nếu body không có thì có thể bỏ qua luôn
                if validator['name'] not in body:
                    continue
                message = self.check_validator_edit(validator, body, obj)
                if message:
                    return message
        if self.VALIDATOR_DELETE is not None and request.method == 'DELETE':
            for validator in self.VALIDATOR_DELETE:
                message = self.check_validator(validator, body)
                if message:
                    return message
        return False

    def check_validator(self, validator, body):
        if validator['name'] not in body:
            return validator['message']
        for check in validator['rules']:
            if check['type'] == 'unique':
                try:
                    self.model.objects.get(**{validator['name']: body[validator['name']]})
                    return check['message']
                except Exception:
                    pass
            elif check['type'] == 'min_length':
                if len(body[validator['name']]) < check['value']:
                    return check['message']
            elif check['type'] == 'max_length':
                if len(body[validator['name']]) > check['value']:
                    return check['message']
            elif check['type'] == 'regex':
                if not re.match(check['regex'], body[validator['name']]):
                    return check['message']
            elif check['type'] == 'same':
                if check['value'] not in body:
                    return check['message']
                if body[validator['name']] != body[check['value']]:
                    return check['message']
        return False
    
    def check_validator_edit(self, validator, body, obj):
        for check in validator['rules']:
            if check['type'] == 'unique':
                try:
                    result = self.model.objects.get(**{validator['name']: body[validator['name']]})
                    if str(result._id) != str(obj._id):
                        return check['message']
                except Exception:
                    pass
            elif check['type'] == 'min_length':
                if len(body[validator['name']]) < check['value']:
                    return check['message']
            elif check['type'] == 'max_length':
                if len(body[validator['name']]) > check['value']:
                    return check['message']
            elif check['type'] == 'regex':
                if not re.match(check['regex'], body[validator['name']]):
                    return check['message']
            elif check['type'] == 'same':
                if check['value'] not in body:
                    return check['message']
                if body[validator['name']] != body[check['value']]:
                    return check['message']
        return False