from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    # InventoryItem endpoints
    path('items/', views.inventory_item_list, name='inventory-item-list'),
    path('items/<int:pk>/', views.inventory_item_detail, name='inventory-item-detail'),

    # InventoryMovement endpoints
    path('movements/', views.inventory_movement_list, name='inventory-movement-list'),
    path('movements/<int:pk>/', views.inventory_movement_detail, name='inventory-movement-detail'),

    # InventoryAudit endpoints
    path('audits/', views.inventory_audit_list, name='inventory-audit-list'),
    path('audits/<int:pk>/', views.inventory_audit_detail, name='inventory-audit-detail'),

    # ReceivingRecord endpoints
    path('receiving/', views.receiving_record_list, name='receiving-record-list'),
    path('receiving/<int:pk>/', views.receiving_record_detail, name='receiving-record-detail'),

    # ReceivingItem endpoints
    path('receiving/<int:receiving_record_id>/items/', views.receiving_item_list, name='receiving-item-list'),
    path('receiving/<int:receiving_record_id>/items/<int:pk>/', views.receiving_item_detail, name='receiving-item-detail'),
    path('receiving/<int:receiving_record_id>/items/<int:pk>/receive/', views.receive_item, name='receive-item'),
]