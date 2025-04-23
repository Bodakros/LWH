from rest_framework import serializers
from ..products.models import Product, ProductCategory
from ..warehouses.models import Warehouse, Stock, Address


class SearchProductCategorySerializer(serializers.ModelSerializer):
    """Серіалізатор для категорій продуктів у результатах пошуку"""
    class Meta:
        model = ProductCategory
        fields = ['id', 'name', 'slug']


class SearchProductSerializer(serializers.ModelSerializer):
    """Серіалізатор для продуктів у результатах пошуку"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    seller_name = serializers.CharField(source='seller.username', read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'sku', 'seller_id', 'seller_name',
            'category_id', 'category_name', 'base_price', 'product_type',
            'main_image', 'is_active', 'created_at'
        ]


class SearchAddressSerializer(serializers.ModelSerializer):
    """Серіалізатор для адреси в результатах пошуку складів"""
    class Meta:
        model = Address
        fields = [
            'id', 'country', 'oblast', 'locality_type', 'locality',
            'street_address', 'postal_code'
        ]


class SearchWarehouseSerializer(serializers.ModelSerializer):
    """Серіалізатор для складів у результатах пошуку"""
    owner_name = serializers.CharField(source='owner.username', read_only=True)
    address_details = SearchAddressSerializer(source='address', read_only=True)

    class Meta:
        model = Warehouse
        fields = [
            'id', 'name', 'owner_id', 'owner_name', 'address_id', 'address_details',
            'total_capacity', 'available_capacity', 'rating', 'operating_hours',
            'is_active', 'created_at'
        ]


class SearchStockSerializer(serializers.ModelSerializer):
    """Серіалізатор для секцій складу в результатах пошуку"""
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    volume = serializers.ReadOnlyField()

    class Meta:
        model = Stock
        fields = [
            'id', 'name', 'warehouse_id', 'warehouse_name', 'capacity',
            'length', 'width', 'height', 'volume', 'is_occupied',
            'location_code', 'created_at'
        ]