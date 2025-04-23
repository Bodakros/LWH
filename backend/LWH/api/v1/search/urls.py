from django.urls import path
from . import views

app_name = 'search'

urlpatterns = [
    # Ендпоінти для пошуку будуть додані тут
    path('products/', views.product_search, name='product-search'),
    path('warehouses/', views.warehouse_search, name='warehouse-search'),
    path('stocks/', views.stock_search, name='stock-search'),
]