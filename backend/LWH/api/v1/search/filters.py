from django_filters import rest_framework as filters
from django.db.models import Q
from ..products.models import Product, ProductCategory
from ..warehouses.models import Warehouse, Stock


class ProductFilter(filters.FilterSet):
    """Фільтр для пошуку продуктів"""
    # Текстовий пошук (назва, опис, артикул)
    search = filters.CharFilter(method='filter_search')

    # Фільтрація за категорією (включаючи підкатегорії)
    category = filters.NumberFilter(method='filter_category')

    # Фільтрація за ціною
    min_price = filters.NumberFilter(field_name='base_price', lookup_expr='gte')
    max_price = filters.NumberFilter(field_name='base_price', lookup_expr='lte')

    # Фільтрація за продавцем
    seller = filters.NumberFilter(field_name='seller__id')

    # Додаткові фільтри
    product_type = filters.CharFilter(field_name='product_type')
    is_active = filters.BooleanFilter(field_name='is_active')

    class Meta:
        model = Product
        fields = ['search', 'category', 'min_price', 'max_price', 'seller', 'product_type', 'is_active']

    def filter_search(self, queryset, name, value):
        """Метод для текстового пошуку по кількох полях"""
        if not value:
            return queryset

        # Пошук по назві, опису, артикулу
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value) |
            Q(sku__icontains=value)
        )

    def filter_category(self, queryset, name, value):
        """Метод для фільтрації за категорією з врахуванням підкатегорій"""
        if not value:
            return queryset

        try:
            category = ProductCategory.objects.get(id=value)

            # Отримання ID категорії та всіх її підкатегорій
            category_ids = [category.id]

            # Рекурсивно знаходимо всі підкатегорії
            def get_subcategories(parent_id):
                subcategories = ProductCategory.objects.filter(parent=parent_id)
                for subcategory in subcategories:
                    category_ids.append(subcategory.id)
                    get_subcategories(subcategory.id)

            get_subcategories(category.id)

            # Фільтруємо продукти за категоріями
            return queryset.filter(category__id__in=category_ids)
        except ProductCategory.DoesNotExist:
            return queryset.none()


class WarehouseFilter(filters.FilterSet):
    """Фільтр для пошуку складів"""
    # Пошук за текстом (назва складу)
    search = filters.CharFilter(method='filter_search')

    # Фільтрація за місцем розташування
    country = filters.CharFilter(field_name='address__country')
    oblast = filters.CharFilter(field_name='address__oblast')
    locality = filters.CharFilter(field_name='address__locality')
    locality_type = filters.CharFilter(field_name='address__locality_type')

    # Фільтрація за власником
    owner = filters.NumberFilter(field_name='owner__id')

    # Фільтрація за ємністю (для продавців та власників)
    min_capacity = filters.NumberFilter(method='filter_min_capacity')
    max_capacity = filters.NumberFilter(method='filter_max_capacity')
    min_available = filters.NumberFilter(method='filter_min_available')

    # Фільтрація за активністю
    is_active = filters.BooleanFilter(field_name='is_active')

    class Meta:
        model = Warehouse
        fields = ['search', 'country', 'oblast', 'locality', 'locality_type',
                  'owner', 'min_capacity', 'max_capacity', 'min_available', 'is_active']

    def filter_search(self, queryset, name, value):
        """Метод для текстового пошуку по назві складу"""
        if not value:
            return queryset

        return queryset.filter(name__icontains=value)

    def filter_min_capacity(self, queryset, name, value):
        """Фільтрація за мінімальною загальною ємністю"""
        if value is not None:
            queryset = queryset.filter(total_capacity__gte=value)
        return queryset

    def filter_max_capacity(self, queryset, name, value):
        """Фільтрація за максимальною загальною ємністю"""
        if value is not None:
            queryset = queryset.filter(total_capacity__lte=value)
        return queryset

    def filter_min_available(self, queryset, name, value):
        """Фільтрація за мінімальною доступною ємністю"""
        if value is not None:
            queryset = queryset.filter(available_capacity__gte=value)
        return queryset


class StockFilter(filters.FilterSet):
    """Фільтр для пошуку секцій складу"""
    # Пошук за текстом (назва секції)
    search = filters.CharFilter(method='filter_search')

    # Фільтрація за складом
    warehouse = filters.NumberFilter(field_name='warehouse__id')

    # Фільтрація за ємністю
    min_capacity = filters.NumberFilter(field_name='capacity', lookup_expr='gte')
    max_capacity = filters.NumberFilter(field_name='capacity', lookup_expr='lte')

    # Фільтрація за зайнятістю
    is_occupied = filters.BooleanFilter(field_name='is_occupied')

    class Meta:
        model = Stock
        fields = ['search', 'warehouse', 'min_capacity', 'max_capacity', 'is_occupied']

    def filter_search(self, queryset, name, value):
        """Метод для текстового пошуку по назві та коду локації"""
        if not value:
            return queryset

        return queryset.filter(
            Q(name__icontains=value) |
            Q(location_code__icontains=value)
        )