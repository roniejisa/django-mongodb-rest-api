from djongo import models
from djongo.models import ObjectIdField

class Customer(models.Model):
    _id = ObjectIdField()  # Explicitly define the primary key
    username = models.CharField(max_length=150, null=False, blank=False, unique=True)
    email = models.EmailField(max_length=200, null=False, blank=False, unique=True)
    password = models.CharField(max_length=200, null=False, blank=False)  # Stores hashed password
    is_active = models.BooleanField(default=False)
    avatar = models.ImageField(upload_to='images/customers/avatars', null=False, unique=True)
    class Meta:
        db_table = 'customers'
    
    def set_password(self, raw_password):
        self.password = make_password(raw_password)
    
    def check_password(self, raw_password):
        return check_password(raw_password, self.password)
    