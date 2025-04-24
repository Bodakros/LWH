from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import mark_safe

from .models import Warehouse, Stock, Address, WarehouseImage, StockImage
from ..admin import LWHBaseAdmin, LWHImageAdmin
from ..search.admin import WarehouseAdminExtension

@admin.register(Address)
class AddressAdmin(LWHBaseAdmin):
    list_display = ('get_full_address', 'locality_type', 'locality', 'postal_code', 'country')
    list_filter = ('locality_type', 'country', 'oblast')
    search_fields = ('street_address', 'locality', 'postal_code')

    fieldsets = (
        (_('Country information'), {'fields': ('country',)}),
        (_('Regional information'), {'fields': ('oblast', 'raion')}),
        (_('Locality information'), {'fields': ('locality_type', 'locality')}),
        (_('Street information'), {'fields': ('street_address', 'postal_code')}),
        (_('Additional information'), {'fields': ('additional_info',)}),
    )

    def get_full_address(self, obj):
        return str(obj)
    get_full_address.short_description = _('Full address')

class StockInline(admin.TabularInline):
    model = Stock
    extra = 1
    show_change_link = True
    fields = ('name', 'location_code', 'capacity', 'length', 'width', 'height', 'is_occupied')
    readonly_fields = ('volume', 'is_occupied')

class WarehouseImageInline(admin.TabularInline):
    model = WarehouseImage
    extra = 1
    readonly_fields = ('image_preview', 'created_at')
    fields = ('image', 'title', 'image_preview', 'is_main', 'order')

    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="100" />')
        return _("No image")

    image_preview.short_description = _("Preview")

@admin.register(Warehouse)
class WarehouseAdmin(LWHBaseAdmin, WarehouseAdminExtension):
    list_display = ('name', 'owner', 'get_location', 'total_capacity', 'available_capacity', 'rating', 'is_active')
    # list_filter inherited from WarehouseAdminExtension
    # search_fields inherited from WarehouseAdminExtension
    inlines = [StockInline, WarehouseImageInline]

    fieldsets = (
        (None, {'fields': ('name', 'owner')}),
        (_('Address'), {'fields': ('address',)}),
        (_('Operation parameters'), {'fields': ('rating', 'operating_hours')}),
        (_('Capacity information'), {'fields': ('total_capacity', 'available_capacity')}),
        (_('Status'), {'fields': ('is_active',)}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    readonly_fields = ('created_at', 'updated_at', 'total_capacity', 'available_capacity')

    def get_location(self, obj):
        return f"{obj.address.locality}, {obj.address.street_address}" if obj.address else "-"
    get_location.short_description = _('Location')

class StockImageInline(admin.TabularInline):
    model = StockImage
    extra = 1
    readonly_fields = ('image_preview', 'created_at')
    fields = ('image', 'title', 'image_preview', 'is_main', 'order')

    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="100" />')
        return _("No image")

    image_preview.short_description = _("Preview")

@admin.register(Stock)
class StockAdmin(LWHBaseAdmin):
    list_display = ('name', 'location_code', 'warehouse', 'capacity', 'volume', 'is_occupied')
    list_filter = ('is_occupied', 'warehouse')
    search_fields = ('name', 'location_code', 'warehouse__name')
    inlines = [StockImageInline]

    fieldsets = (
        (None, {'fields': ('name', 'warehouse', 'location_code')}),
        (_('Dimensions'), {'fields': ('length', 'width', 'height', 'capacity')}),
        (_('Status'), {'fields': ('is_occupied', 'volume')}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    readonly_fields = ('created_at', 'updated_at', 'volume')

@admin.register(WarehouseImage)
class WarehouseImageAdmin(LWHImageAdmin):
    list_display = ('id', 'warehouse', 'title', 'is_main', 'order', 'created_at')
    list_filter = ('is_main', 'warehouse')
    search_fields = ('warehouse__name', 'title', 'description')

    fieldsets = (
        (None, {'fields': ('warehouse', 'image', 'title')}),
        (_('Details'), {'fields': ('description', 'is_main', 'order')}),
        (_('Preview'), {'fields': ('image_preview',)}),
        (_('Timestamps'), {'fields': ('created_at',), 'classes': ('collapse',)}),
    )
    readonly_fields = ('created_at', 'image_preview')

@admin.register(StockImage)
class StockImageAdmin(LWHImageAdmin):
    list_display = ('id', 'stock', 'title', 'is_main', 'order', 'created_at')
    list_filter = ('is_main', 'stock__warehouse')
    search_fields = ('stock__name', 'stock__warehouse__name', 'title', 'description')

    fieldsets = (
        (None, {'fields': ('stock', 'image', 'title')}),
        (_('Details'), {'fields': ('description', 'is_main', 'order')}),
        (_('Preview'), {'fields': ('image_preview',)}),
        (_('Timestamps'), {'fields': ('created_at',), 'classes': ('collapse',)}),
    )
    readonly_fields = ('created_at', 'image_preview')
