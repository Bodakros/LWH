from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.db.models import Sum

from .models import (
    InventoryItem, InventoryMovement, InventoryAudit,
    ReceivingRecord, ReceivingItem
)
from ..admin import LWHBaseAdmin
from ..search.admin import InventoryItemAdminExtension

@admin.register(InventoryItem)
class InventoryItemAdmin(LWHBaseAdmin, InventoryItemAdminExtension):
    list_display = ('id', 'product_info', 'quantity_with_unit', 'stock_location', 'status', 'expiration_date', 'received_date')
    # list_filter inherited from InventoryItemAdminExtension
    # search_fields inherited from InventoryItemAdminExtension
    raw_id_fields = ('product', 'stock', 'warehouse', 'seller')
    date_hierarchy = 'received_date'

    fieldsets = (
        (None, {'fields': ('product', 'seller', 'stock', 'warehouse')}),
        (_('Quantity'), {'fields': ('quantity', 'unit', 'custom_unit')}),
        (_('Status & Batch'), {'fields': ('status', 'batch_number', 'expiration_date')}),
        (_('Pricing'), {'fields': ('purchase_price', 'purchase_price_per_unit')}),
        (_('Timestamps'), {'fields': ('received_date', 'created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    readonly_fields = ('warehouse', 'created_at', 'updated_at')

    def product_info(self, obj):
        return f"{obj.product.name} ({obj.product.sku})"
    product_info.short_description = _('Product')

    def quantity_with_unit(self, obj):
        unit_display = obj.custom_unit if obj.unit == 'other' and obj.custom_unit else obj.get_unit_display()
        return f"{obj.quantity} {unit_display}"
    quantity_with_unit.short_description = _('Quantity')

    def stock_location(self, obj):
        return f"{obj.warehouse.name} / {obj.stock.location_code}"
    stock_location.short_description = _('Location')

class ReceivingItemInline(admin.TabularInline):
    model = ReceivingItem
    extra = 1
    raw_id_fields = ('product', 'stock')
    fields = ('product', 'expected_quantity', 'received_quantity', 'unit', 'stock', 'status')
    readonly_fields = ('status',)

@admin.register(ReceivingRecord)
class ReceivingRecordAdmin(LWHBaseAdmin):
    list_display = ('id', 'supplier', 'warehouse', 'receipt_date', 'reference_number', 'status', 'progress_display')
    list_filter = ('status', 'warehouse', 'receipt_date')
    search_fields = ('supplier', 'reference_number', 'warehouse__name')
    raw_id_fields = ('warehouse', 'received_by', 'supplier_user')
    inlines = [ReceivingItemInline]
    date_hierarchy = 'receipt_date'

    fieldsets = (
        (None, {'fields': ('supplier', 'supplier_user', 'warehouse', 'reference_number')}),
        (_('Receipt information'), {'fields': ('status', 'receipt_date', 'received_by')}),
        (_('Items count'), {'fields': ('expected_items_count', 'received_items_count')}),
        (_('Additional information'), {'fields': ('notes',)}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at', 'completed_date'), 'classes': ('collapse',)}),
    )
    readonly_fields = ('receipt_date', 'received_items_count', 'created_at', 'updated_at', 'completed_date')

    def progress_display(self, obj):
        if obj.expected_items_count == 0:
            return "-"

        progress = (obj.received_items_count / obj.expected_items_count) * 100
        color = "green" if progress == 100 else "orange" if progress > 0 else "red"

        return format_html(
            '<div style="width:100px; background-color:#f1f1f1; border-radius:3px;">'
            '<div style="width:{}%; background-color:{}; height:10px; border-radius:3px;"></div>'
            '</div> {}%',
            min(100, progress), color, round(progress, 1)
        )
    progress_display.short_description = _('Progress')

@admin.register(ReceivingItem)
class ReceivingItemAdmin(LWHBaseAdmin):
    list_display = ('id', 'receiving_record_ref', 'product_info', 'expected_vs_received', 'status', 'received_at')
    list_filter = ('status', 'receiving_record__warehouse', 'received_at')
    search_fields = ('product__name', 'product__sku', 'receiving_record__reference_number', 'batch_number')
    raw_id_fields = ('receiving_record', 'product', 'stock', 'inventory_item', 'received_by')

    fieldsets = (
        (None, {'fields': ('receiving_record', 'product', 'batch_number')}),
        (_('Quantity'), {'fields': ('expected_quantity', 'received_quantity', 'unit', 'custom_unit')}),
        (_('Storage'), {'fields': ('stock', 'expiration_date')}),
        (_('Pricing'), {'fields': ('purchase_price',)}),
        (_('Status'), {'fields': ('status', 'received_at', 'received_by', 'inventory_item')}),
        (_('Additional information'), {'fields': ('notes',)}),
    )
    readonly_fields = ('received_at', 'inventory_item')

    def receiving_record_ref(self, obj):
        return f"#{obj.receiving_record.id} - {obj.receiving_record.reference_number or 'No reference'}"
    receiving_record_ref.short_description = _('Receiving record')

    def product_info(self, obj):
        return f"{obj.product.name} ({obj.product.sku})"
    product_info.short_description = _('Product')

    def expected_vs_received(self, obj):
        unit_display = obj.custom_unit if obj.unit == 'other' and obj.custom_unit else obj.get_unit_display()
        return f"{obj.received_quantity} / {obj.expected_quantity} {unit_display}"
    expected_vs_received.short_description = _('Received / Expected')

@admin.register(InventoryMovement)
class InventoryMovementAdmin(LWHBaseAdmin):
    list_display = ('id', 'timestamp', 'product_info', 'source_to_destination', 'quantity_with_unit', 'reason', 'initiated_by')
    list_filter = ('reason', 'timestamp', 'unit')
    search_fields = ('product__name', 'product__sku', 'source_stock__name', 'destination_stock__name')
    raw_id_fields = ('source_stock', 'destination_stock', 'product', 'seller', 'initiated_by',
                     'source_inventory_item', 'destination_inventory_item')
    date_hierarchy = 'timestamp'

    fieldsets = (
        (None, {'fields': ('product', 'seller', 'quantity', 'unit', 'custom_unit')}),
        (_('Locations'), {'fields': ('source_stock', 'destination_stock')}),
        (_('Related items'), {'fields': ('source_inventory_item', 'destination_inventory_item')}),
        (_('Details'), {'fields': ('reason', 'notes', 'initiated_by')}),
        (_('Timestamps'), {'fields': ('timestamp',), 'classes': ('collapse',)}),
    )
    readonly_fields = ('timestamp',)

    def product_info(self, obj):
        return f"{obj.product.name} ({obj.product.sku})"
    product_info.short_description = _('Product')

    def source_to_destination(self, obj):
        return f"{obj.source_stock.location_code} → {obj.destination_stock.location_code}"
    source_to_destination.short_description = _('Movement')

    def quantity_with_unit(self, obj):
        unit_display = obj.custom_unit if obj.unit == 'other' and obj.custom_unit else obj.get_unit_display()
        return f"{obj.quantity} {unit_display}"
    quantity_with_unit.short_description = _('Quantity')

@admin.register(InventoryAudit)
class InventoryAuditAdmin(LWHBaseAdmin):
    list_display = ('id', 'inventory_item_info', 'expected_vs_actual', 'discrepancy', 'audit_date', 'resolved', 'resolution_type')
    list_filter = ('resolved', 'resolution_type', 'audit_date')
    search_fields = ('inventory_item__product__name', 'inventory_item__product__sku', 'inventory_item__batch_number')
    raw_id_fields = ('inventory_item', 'audited_by', 'resolved_by')
    date_hierarchy = 'audit_date'

    fieldsets = (
        (None, {'fields': ('inventory_item', 'audit_date', 'audited_by')}),
        (_('Quantities'), {'fields': ('expected_quantity', 'actual_quantity', 'discrepancy', 'unit', 'custom_unit')}),
        (_('Audit notes'), {'fields': ('notes',)}),
        (_('Resolution'), {'fields': ('resolved', 'resolution_type', 'resolution_date', 'resolved_by', 'resolution_notes')}),
    )
    readonly_fields = ('audit_date', 'discrepancy')

    def inventory_item_info(self, obj):
        item = obj.inventory_item
        return f"{item.product.name} (Batch: {item.batch_number or 'N/A'})"
    inventory_item_info.short_description = _('Inventory item')

    def expected_vs_actual(self, obj):
        unit_display = obj.custom_unit if obj.unit == 'other' and obj.custom_unit else obj.get_unit_display()
        return f"{obj.actual_quantity} / {obj.expected_quantity} {unit_display}"
    expected_vs_actual.short_description = _('Actual / Expected')
