
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.contrib.admin import SimpleListFilter
from django.db.models import Q, Count, Sum
# Import necessary for dynamic filtering
from django.db.models import F

# Import models from other modules
from ..products.models import Product, ProductCategory
from ..warehouses.models import Warehouse, Stock
from ..inventory.models import InventoryItem


# Advanced search filters for Product admin
class StockLevelFilter(SimpleListFilter):
    title = _('Stock level')
    parameter_name = 'stock_level'

    def lookups(self, request, model_admin):
        return (
            ('out_of_stock', _('Out of stock')),
            ('low_stock', _('Low stock')),
            ('in_stock', _('In stock')),
            ('well_stocked', _('Well stocked')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'out_of_stock':
            # Products with zero inventory
            return queryset.filter(
                ~Q(inventory_items__status='available') |
                Q(inventory_items__quantity=0)
            ).distinct()

        if self.value() == 'low_stock':
            # Products with stock below threshold (example: less than 10)
            return queryset.filter(
                inventory_items__status='available',
                inventory_items__quantity__gt=0,
                inventory_items__quantity__lt=10
            ).distinct()

        if self.value() == 'in_stock':
            # Products with stock available
            return queryset.filter(
                inventory_items__status='available',
                inventory_items__quantity__gt=0
            ).distinct()

        if self.value() == 'well_stocked':
            # Products with ample stock (example: more than 50)
            return queryset.filter(
                inventory_items__status='available',
                inventory_items__quantity__gt=50
            ).distinct()


class PriceRangeFilter(SimpleListFilter):
    title = _('Price range')
    parameter_name = 'price_range'

    def lookups(self, request, model_admin):
        return (
            ('under_100', _('Under 100')),
            ('100_to_500', _('100 to 500')),
            ('500_to_1000', _('500 to 1000')),
            ('over_1000', _('Over 1000')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'under_100':
            return queryset.filter(base_price__lt=100)
        if self.value() == '100_to_500':
            return queryset.filter(base_price__gte=100, base_price__lt=500)
        if self.value() == '500_to_1000':
            return queryset.filter(base_price__gte=500, base_price__lt=1000)
        if self.value() == 'over_1000':
            return queryset.filter(base_price__gte=1000)


# Advanced search filters for Warehouse admin
class OccupancyRateFilter(SimpleListFilter):
    title = _('Occupancy rate')
    parameter_name = 'occupancy_rate'

    def lookups(self, request, model_admin):
        return (
            ('empty', _('Empty (0%)')),
            ('low', _('Low (1-33%)')),
            ('medium', _('Medium (34-66%)')),
            ('high', _('High (67-99%)')),
            ('full', _('Full (100%)')),
        )

    def queryset(self, request, queryset):
        # Custom calculation for warehouse occupancy
        warehouses = queryset.annotate(
            total_cap=Sum('stocks__capacity'),
            used_cap=Sum('stocks__capacity', filter=Q(stocks__is_occupied=True))
        )

        if self.value() == 'empty':
            return warehouses.filter(Q(used_cap=0) | Q(used_cap__isnull=True))

        if self.value() == 'low':
            return warehouses.filter(
                used_cap__gt=0,
                used_cap__lte=0.33 * F('total_cap')
            )

        if self.value() == 'medium':
            return warehouses.filter(
                used_cap__gt=0.33 * F('total_cap'),
                used_cap__lte=0.66 * F('total_cap')
            )

        if self.value() == 'high':
            return warehouses.filter(
                used_cap__gt=0.66 * F('total_cap'),
                used_cap__lt=F('total_cap')
            )

        if self.value() == 'full':
            return warehouses.filter(used_cap=F('total_cap'), total_cap__gt=0)


# Advanced search filters for InventoryItem admin
class ExpirationStatusFilter(SimpleListFilter):
    title = _('Expiration status')
    parameter_name = 'expiration_status'

    def lookups(self, request, model_admin):
        return (
            ('expired', _('Expired')),
            ('expires_soon', _('Expires soon (within 30 days)')),
            ('valid', _('Valid (more than 30 days)')),
            ('no_expiry', _('No expiry date')),
        )

    def queryset(self, request, queryset):
        from django.utils import timezone
        import datetime

        today = timezone.now().date()
        thirty_days_later = today + datetime.timedelta(days=30)

        if self.value() == 'expired':
            return queryset.filter(
                expiration_date__lt=today,
                expiration_date__isnull=False
            )

        if self.value() == 'expires_soon':
            return queryset.filter(
                expiration_date__gte=today,
                expiration_date__lte=thirty_days_later
            )

        if self.value() == 'valid':
            return queryset.filter(
                expiration_date__gt=thirty_days_later
            )

        if self.value() == 'no_expiry':
            return queryset.filter(expiration_date__isnull=True)


# Extend the Product admin class
class ProductAdminExtension:
    """
    Extension for Product admin with additional search functionality.
    This class should be used with multiple inheritance in the actual admin.py
    """
    search_fields = (
        'name', 'sku', 'description', 'seller__username',
        'seller__email', 'category__name', 'attributes_json'
    )

    list_filter = (
        'product_type', 'is_active', 'taxable',
        StockLevelFilter, PriceRangeFilter
    )

    def get_search_results(self, request, queryset, search_term):
        # Enhanced search for products
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)

        # Add additional search capabilities
        if search_term:
            # Search in attributes_json field
            attribute_q = Q(attributes_json__icontains=search_term)

            # Search for products that are in specific stock locations
            location_q = Q(inventory_items__stock__location_code__icontains=search_term)

            # Search by warehouse name
            warehouse_q = Q(inventory_items__warehouse__name__icontains=search_term)

            # Combine all searches
            queryset = queryset.filter(attribute_q | location_q | warehouse_q)
            use_distinct = True

        return queryset, use_distinct


# Extend the Warehouse admin class
class WarehouseAdminExtension:
    """Extension for Warehouse admin with additional search functionality"""
    search_fields = (
        'name', 'address__street_address', 'address__locality',
        'address__postal_code', 'address__country', 'owner__username'
    )

    list_filter = (
        'is_active', 'created_at', OccupancyRateFilter
    )

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)

        if search_term:
            # Search for warehouses that have specific products
            product_q = Q(stocks__inventory_items__product__name__icontains=search_term) | \
                        Q(stocks__inventory_items__product__sku__icontains=search_term)

            # Search by location code
            location_q = Q(stocks__location_code__icontains=search_term)

            # Combine all searches
            queryset = queryset.filter(product_q | location_q)
            use_distinct = True

        return queryset, use_distinct


# Extend the InventoryItem admin class
class InventoryItemAdminExtension:
    """Extension for InventoryItem admin with additional search functionality"""
    search_fields = (
        'product__name', 'product__sku', 'batch_number',
        'stock__location_code', 'warehouse__name'
    )

    list_filter = (
        'status', 'unit', 'received_date', ExpirationStatusFilter
    )

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)

        if search_term:
            # Search by product attributes
            attribute_q = Q(product__attributes_json__icontains=search_term)

            # Search by seller
            seller_q = Q(seller__username__icontains=search_term) | \
                       Q(seller__email__icontains=search_term)

            # Combine all searches
            queryset = queryset.filter(attribute_q | seller_q)
            use_distinct = True

        return queryset, use_distinct
