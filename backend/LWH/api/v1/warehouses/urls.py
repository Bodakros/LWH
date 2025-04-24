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

    path('<int:warehouse_id>/images/', views.warehouse_images, name='warehouse-images'),
    path('<int:warehouse_id>/images/<int:pk>/', views.warehouse_image_detail, name='warehouse-image-detail'),

    # Warehouse and stocks image endpoints
    path('<int:warehouse_id>/stocks/<int:stock_id>/images/', views.stock_images, name='stock-images'),
    path('<int:warehouse_id>/stocks/<int:stock_id>/images/<int:pk>/', views.stock_image_detail, name='stock-image-detail'),

    # Add these new URL paths to the existing urlpatterns list
    path('<int:warehouse_id>/images/reorder/', views.reorder_warehouse_images, name='reorder-warehouse-images'),
    path('<int:warehouse_id>/stocks/<int:stock_id>/images/reorder/', views.reorder_stock_images, name='reorder-stock-images'),
]