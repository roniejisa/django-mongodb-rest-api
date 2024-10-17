# customers/urls.py
from django.urls import path, include
from .views import CustomerRestAPI
from .auth.views import Auth
customer_api = CustomerRestAPI.as_view()

urlpatterns = [
    path('customers/', customer_api, name='customers_list'),          # GET: List all customers, POST: Create new customer
    path('customers/<str:_id>/', customer_api, name='customer_detail'),  # GET: Retrieve, PUT: Update, DELETE: Delete
    path('auth/login', Auth.as_view(action='login'), name = 'login'),
    path('auth/profile', Auth.as_view(action='profile'), name = 'profile'),
    path('auth/refresh-token', Auth.as_view(action='refresh-token'), name = 'refresh-token'),
]