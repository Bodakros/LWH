from django.urls import path
from . import views

app_name = 'automation'

urlpatterns = [
    # Base automation rules
    path('rules/', views.automation_rule_list, name='rule-list'),
    path('rules/<int:pk>/', views.automation_rule_detail, name='rule-detail'),

    # Warehouse selection rules
    path('warehouse-selection/', views.warehouse_selection_rule_list, name='warehouse-selection-list'),
    path('warehouse-selection/<int:pk>/', views.warehouse_selection_rule_detail, name='warehouse-selection-detail'),
    path('warehouse-selection/find-best/', views.find_best_warehouses, name='find-best-warehouses'),

    # Pricing rules
    path('pricing/', views.pricing_rule_list, name='pricing-list'),
    path('pricing/<int:pk>/', views.pricing_rule_detail, name='pricing-detail'),
    path('pricing/calculate/', views.calculate_price, name='calculate-price'),

    # Restock rules
    path('restock/', views.restock_rule_list, name='restock-list'),
    path('restock/<int:pk>/', views.restock_rule_detail, name='restock-detail'),
    path('restock/check-inventory/', views.check_inventory_levels, name='check-inventory'),

    # Product comparison settings
    path('comparison/', views.product_comparison_settings_list, name='comparison-list'),
    path('comparison/<int:pk>/', views.product_comparison_settings_detail, name='comparison-detail'),
    path('comparison/compare/', views.compare_products, name='compare-products'),

    # Comparison attribute weights
    path('comparison/<int:settings_id>/attributes/', views.comparison_attribute_weight_list, name='attribute-list'),
    path('comparison/<int:settings_id>/attributes/<int:pk>/', views.comparison_attribute_weight_detail, name='attribute-detail'),

    path('tasks/', views.manage_automation_tasks, name='manage-tasks'),
]