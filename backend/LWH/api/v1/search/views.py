from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q

from ..products.models import Product
from ..warehouses.models import Warehouse, Stock
from .serializers import (
    SearchProductSerializer,
    SearchWarehouseSerializer,
    SearchStockSerializer
)
from .filters import ProductFilter, WarehouseFilter, StockFilter


class StandardResultsSetPagination(PageNumberPagination):
    """Стандартна пагінація для результатів пошуку"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


@api_view(['GET'])
@permission_classes([AllowAny])
def product_search(request):
    """
    Пошук продуктів з можливістю фільтрації за різними параметрами.

    Параметри пошуку:
    - search: Текстовий пошук (назва, опис, артикул)
    - category: ID категорії (включає підкатегорії)
    - min_price, max_price: Діапазон цін
    - seller: ID продавця
    - product_type: Тип продукту
    - is_active: Чи активний продукт
    """
    queryset = Product.objects.all()

    # Застосовуємо фільтри
    filter_set = ProductFilter(request.GET, queryset=queryset)
    queryset = filter_set.qs

    # Сортування
    sort_by = request.GET.get('sort', 'name')
    if sort_by.startswith('-'):
        sort_field = sort_by[1:]
        if hasattr(Product, sort_field) or sort_field == 'price':
            if sort_field == 'price':
                queryset = queryset.order_by('-base_price')
            else:
                queryset = queryset.order_by(sort_by)
    else:
        if hasattr(Product, sort_by) or sort_by == 'price':
            if sort_by == 'price':
                queryset = queryset.order_by('base_price')
            else:
                queryset = queryset.order_by(sort_by)

    # Пагінація
    paginator = StandardResultsSetPagination()
    paginated_queryset = paginator.paginate_queryset(queryset, request)

    # Серіалізація
    serializer = SearchProductSerializer(paginated_queryset, many=True)

    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def warehouse_search(request):
    """
    Пошук складів з можливістю фільтрації за різними параметрами.

    Параметри пошуку:
    - search: Текстовий пошук за назвою
    - country, oblast, locality, locality_type: Фільтрація за адресою
    - owner: ID власника складу
    - min_capacity, max_capacity: Діапазон загальної ємності
    - min_available: Мінімальна доступна ємність
    - is_active: Чи активний склад
    """
    queryset = Warehouse.objects.all()

    # Застосовуємо фільтри
    filter_set = WarehouseFilter(request.GET, queryset=queryset)
    queryset = filter_set.qs

    # Сортування
    sort_by = request.GET.get('sort', 'name')
    if sort_by.startswith('-'):
        sort_field = sort_by[1:]
        if hasattr(Warehouse, sort_field):
            queryset = queryset.order_by(sort_by)
    else:
        if hasattr(Warehouse, sort_by):
            queryset = queryset.order_by(sort_by)

    # Пагінація
    paginator = StandardResultsSetPagination()
    paginated_queryset = paginator.paginate_queryset(queryset, request)

    # Серіалізація
    serializer = SearchWarehouseSerializer(paginated_queryset, many=True)

    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def stock_search(request):
    """
    Пошук секцій складу з можливістю фільтрації за різними параметрами.

    Параметри пошуку:
    - search: Текстовий пошук за назвою або кодом локації
    - warehouse: ID складу
    - min_capacity, max_capacity: Діапазон ємності
    - is_occupied: Чи зайнята секція
    """
    queryset = Stock.objects.all()

    # Застосовуємо фільтри
    filter_set = StockFilter(request.GET, queryset=queryset)
    queryset = filter_set.qs

    # Сортування
    sort_by = request.GET.get('sort', 'name')
    if sort_by.startswith('-'):
        sort_field = sort_by[1:]
        if hasattr(Stock, sort_field):
            queryset = queryset.order_by(sort_by)
    else:
        if hasattr(Stock, sort_by):
            queryset = queryset.order_by(sort_by)

    # Пагінація
    paginator = StandardResultsSetPagination()
    paginated_queryset = paginator.paginate_queryset(queryset, request)

    # Серіалізація
    serializer = SearchStockSerializer(paginated_queryset, many=True)

    return paginator.get_paginated_response(serializer.data)