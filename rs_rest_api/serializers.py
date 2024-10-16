# customers/serializers.py
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import Customer

class CustomerSerializer(serializers.ModelSerializer):
    def validate_username(self, value):
        if Customer.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username đã tồn tại. Vui lòng chọn một username khác.")
        return value

    def validate_email(self, value):
        if Customer.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email đã được sử dụng. Vui lòng sử dụng email khác.")
        return value
    class Meta:
        model = Customer
        fields = ['_id', 'email', 'username', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }