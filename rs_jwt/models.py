from djongo import models
from djongo.models import ObjectIdField

class JWTSession(models.Model):
    _id = ObjectIdField()  # Explicitly define the primary key
    refresh_token = models.TextField(null=False, blank=False, unique=True)
    user_id = models.CharField(max_length=150, null=False, blank=False, unique=True)
    device_info = models.CharField(max_length=150, null=False, blank=False, unique=True)
    ip_address = models.CharField(max_length=50)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'jwt_sessions'

class JWTBlacklist(models.Model):
    _id = ObjectIdField()  # Explicitly define the primary key
    token = models.CharField(max_length=150, null=False, blank=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'jwt_blacklists'