from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # Категорії продуктів
    path('categories/', views.product_category_list, name='category-list'),
    path('categories/<int:pk>/', views.product_category_detail, name='category-detail'),

    # Типи податків
    path('tax-types/', views.tax_type_list, name='tax-type-list'),
    path('tax-types/<int:pk>/', views.tax_type_detail, name='tax-type-detail'),

    # Податкові ставки
    path('tax-rates/', views.tax_rate_list, name='tax-rate-list'),
    path('tax-rates/<int:pk>/', views.tax_rate_detail, name='tax-rate-detail'),

    # Атрибути продуктів
    path('attributes/', views.attribute_list, name='attribute-list'),
    path('attributes/<int:pk>/', views.attribute_detail, name='attribute-detail'),
    path('attributes/<int:attribute_id>/options/', views.attribute_option_list, name='attribute-option-list'),
    path('attributes/<int:attribute_id>/options/<int:pk>/', views.attribute_option_detail, name='attribute-option-detail'),

    # Продукти
    path('', views.product_list, name='product-list'),
    path('<int:pk>/', views.product_detail, name='product-detail'),
    path('<int:pk>/taxes/', views.calculate_product_taxes, name='product-taxes'),

    # Зображення продуктів
    path('<int:product_id>/images/', views.product_image_list, name='product-image-list'),
    path('<int:product_id>/images/<int:pk>/', views.product_image_detail, name='product-image-detail'),

    # Атрибути продуктів
    path('<int:product_id>/attributes/', views.product_attribute_list, name='product-attribute-list'),
    path('<int:product_id>/attributes/<int:pk>/', views.product_attribute_detail, name='product-attribute-detail'),

    path('<int:product_id>/images/reorder/', views.reorder_product_images, name='reorder-product-images'),
]
