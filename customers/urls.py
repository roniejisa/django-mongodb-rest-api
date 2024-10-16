# customers/urls.py
from django.urls import path, include
from .views import CustomerRestAPI

customer_api = CustomerRestAPI.as_view()

urlpatterns = [
    path('customers/', customer_api, name='customers_list'),          # GET: List all customers, POST: Create new customer
    path('customers/<str:_id>/', customer_api, name='customer_detail'),  # GET: Retrieve, PUT: Update, DELETE: Delete
]