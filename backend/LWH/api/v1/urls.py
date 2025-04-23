from django.urls import path, include

urlpatterns = [
    path('users/', include('api.v1.users.urls')),
    path('products/', include('api.v1.products.urls')),
    path('warehouses/', include('api.v1.warehouses.urls')),
    path('inventory/', include('api.v1.inventory.urls')),
    path('search/', include('api.v1.search.urls')),
    path('automation/', include('api.v1.automation.urls')),
]