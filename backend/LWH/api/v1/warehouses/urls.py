from django.urls import path
from . import views

app_name = 'warehouses'

urlpatterns = [
    # List all warehouses
    path('', views.warehouse_list, name='warehouse-list'),
    # Retrieve, update or delete a warehouse
    path('<int:pk>/', views.warehouse_detail, name='warehouse-detail'),
    # List stocks in a warehouse
    path('<int:warehouse_id>/stocks/', views.stock_list, name='stock-list'),
    # Retrieve, update or delete a stock
    path('<int:warehouse_id>/stocks/<int:pk>/', views.stock_detail, name='stock-detail'),
    # Address-related endpoints
    path('addresses/', views.address_list, name='address-list'),
    path('addresses/<int:pk>/', views.address_detail, name='address-detail'),
]