from django.forms.models import model_to_dict
from django.db.models.fields.files import ImageFieldFile
from bson.objectid import ObjectId
from hashlib import blake2b
from hmac import compare_digest

def serialize_customer(customer, exclude_fields=None, request=None):
    exclude_fields = exclude_fields or []
    
    # Convert model to dict while excluding specified fields
    customer_dict = model_to_dict(customer, exclude=exclude_fields)
    
    serialized_dict = {}
    
    for key, value in customer_dict.items():
        if isinstance(value, ImageFieldFile):
            if value:
                serialized_dict[key] = request.build_absolute_uri(value.url) if request else value.url
            else:
                serialized_dict[key] = None
        elif isinstance(value, ObjectId):
            serialized_dict[key] = str(value)
        else:
            serialized_dict[key] = value
    
    return serialized_dict


def validatorModel(model, value, type="same", message="Vui lòng nhập"): 
    if model.objects.filter(**{type: value}).exists():
        raise serializers.ValidationError(f'{type} bi trung. Vui long chon {type} khac')
    return value

AUTH_SIZE = 16  # Example digest size
SECRET_KEY = b'supersecretkey'  # Ensure the key is bytes

def hashSign(value):
    # Ensure value is bytes
    if isinstance(value, str):
        value = value.encode('utf-8')
    h = blake2b(digest_size=AUTH_SIZE, key=SECRET_KEY)
    h.update(value)
    return h.hexdigest()  # Return as string

def verifyHash(value, sig):
    # Ensure value is bytes
    if isinstance(value, str):
        value = value.encode('utf-8')
    good_sig = hashSign(value)  # This is a string
    # Ensure sig is a string
    if isinstance(sig, bytes):
        sig = sig.decode('utf-8')
    return compare_digest(good_sig, sig)