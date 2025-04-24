from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils.html import format_html, mark_safe
from django.utils import timezone

from .models import (
    AutomationRule, WarehouseSelectionRule, PricingRule,
    RestockRule, ProductComparisonSettings, ComparisonAttributeWeight
)
from ..admin import LWHBaseAdmin


# Base AutomationRule admin
@admin.register(AutomationRule)
class AutomationRuleAdmin(LWHBaseAdmin):
    list_display = ('name', 'rule_type_display', 'is_active', 'priority', 'created_by', 'get_specific_rule_link')
    list_filter = ('rule_type', 'is_active', 'created_at')
    search_fields = ('name', 'description', 'created_by__username')

    fieldsets = (
        (None, {'fields': ('name', 'description', 'rule_type')}),
        (_('Settings'), {'fields': ('is_active', 'priority')}),
        (_('Ownership'), {'fields': ('created_by',)}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    readonly_fields = ('created_at', 'updated_at')

    def rule_type_display(self, obj):
        return obj.get_rule_type_display()

    rule_type_display.short_description = _('Rule Type')

    def get_specific_rule_link(self, obj):
        """Generate a link to the specific rule implementation"""
        if obj.rule_type == 'warehouse_selection' and hasattr(obj, 'warehouse_selection_rule'):
            rule_id = obj.warehouse_selection_rule.id
            url = reverse('admin:automation_warehouseselectionrule_change', args=[rule_id])
            return format_html('<a href="{}">{}</a>', url, _('View Warehouse Selection Rule'))

        elif obj.rule_type == 'pricing' and hasattr(obj, 'pricing_rule'):
            rule_id = obj.pricing_rule.id
            url = reverse('admin:automation_pricingrule_change', args=[rule_id])
            return format_html('<a href="{}">{}</a>', url, _('View Pricing Rule'))

        elif obj.rule_type == 'restock' and hasattr(obj, 'restock_rule'):
            rule_id = obj.restock_rule.id
            url = reverse('admin:automation_restockrule_change', args=[rule_id])
            return format_html('<a href="{}">{}</a>', url, _('View Restock Rule'))

        elif obj.rule_type == 'product_comparison' and hasattr(obj, 'product_comparison_settings'):
            rule_id = obj.product_comparison_settings.id
            url = reverse('admin:automation_productcomparisonsettings_change', args=[rule_id])
            return format_html('<a href="{}">{}</a>', url, _('View Comparison Settings'))

        return "-"

    get_specific_rule_link.short_description = _('Specific Rule')


# Warehouse Selection Rule admin
class WarehouseSelectionRuleAdmin(LWHBaseAdmin):
    list_display = (
    'id', 'get_rule_name', 'get_rule_status', 'capacity_weight', 'rating_weight', 'price_weight', 'get_preferred_count')
    list_filter = ('base_rule__is_active',)
    search_fields = ('base_rule__name', 'base_rule__description')
    filter_horizontal = ('preferred_warehouses', 'excluded_warehouses')

    fieldsets = (
        (None, {'fields': ('base_rule',)}),
        (_('Weight Factors'), {
            'fields': ('capacity_weight', 'rating_weight', 'price_weight'),
            'description': _('These weights determine the importance of each factor when selecting warehouses.'),
        }),
        (_('Warehouse Lists'), {
            'fields': ('preferred_warehouses', 'excluded_warehouses'),
        }),
        (_('Constraints'), {
            'fields': ('minimum_capacity_required',),
        }),
    )

    def get_rule_name(self, obj):
        return obj.base_rule.name

    get_rule_name.short_description = _('Rule Name')

    def get_rule_status(self, obj):
        if obj.base_rule.is_active:
            return format_html('<span style="color: green;">✓ {}</span>', _('Active'))
        return format_html('<span style="color: red;">✗ {}</span>', _('Inactive'))

    get_rule_status.short_description = _('Status')

    def get_preferred_count(self, obj):
        preferred = obj.preferred_warehouses.count()
        excluded = obj.excluded_warehouses.count()
        return f"{preferred} preferred, {excluded} excluded"

    get_preferred_count.short_description = _('Warehouses')


# Pricing Rule admin
class PricingRuleAdmin(LWHBaseAdmin):
    list_display = ('id', 'get_rule_name', 'get_rule_status', 'adjustment_type', 'adjustment_value',
                    'get_categories_count', 'get_products_count')
    list_filter = ('base_rule__is_active', 'adjustment_type')
    search_fields = ('base_rule__name', 'base_rule__description', 'product_categories__name')
    filter_horizontal = ('product_categories', 'applies_to_products')

    fieldsets = (
        (None, {'fields': ('base_rule',)}),
        (_('Price Adjustment'), {
            'fields': ('adjustment_type', 'adjustment_value', 'formula'),
            'description': _('How prices should be adjusted. Formula is only used when adjustment type is "Formula".'),
        }),
        (_('Margin Constraints'), {
            'fields': ('min_margin', 'max_margin'),
            'description': _('Optional: Set limits for profit margins (in percentages).'),
        }),
        (_('Application Scope'), {
            'fields': ('product_categories', 'applies_to_products'),
            'description': _('Define which products this rule applies to.'),
        }),
        (_('Advanced Conditions'), {
            'fields': ('conditions',),
            'classes': ('collapse',),
            'description': _('JSON object with advanced conditions for rule application.'),
        }),
    )

    def get_rule_name(self, obj):
        return obj.base_rule.name

    get_rule_name.short_description = _('Rule Name')

    def get_rule_status(self, obj):
        if obj.base_rule.is_active:
            return format_html('<span style="color: green;">✓ {}</span>', _('Active'))
        return format_html('<span style="color: red;">✗ {}</span>', _('Inactive'))

    get_rule_status.short_description = _('Status')

    def get_categories_count(self, obj):
        return obj.product_categories.count()

    get_categories_count.short_description = _('Categories')

    def get_products_count(self, obj):
        return obj.applies_to_products.count()

    get_products_count.short_description = _('Products')


# Restock Rule admin
class RestockRuleAdmin(LWHBaseAdmin):
    list_display = ('id', 'get_rule_name', 'get_rule_status', 'product', 'minimum_quantity',
                    'reorder_quantity', 'auto_reorder', 'get_last_restock')
    list_filter = ('base_rule__is_active', 'auto_reorder', 'last_check_date')
    search_fields = ('base_rule__name', 'product__name', 'product__sku')
    filter_horizontal = ('warehouses',)
    raw_id_fields = ('product', 'preferred_supplier')

    fieldsets = (
        (None, {'fields': ('base_rule', 'product')}),
        (_('Restock Parameters'), {
            'fields': ('minimum_quantity', 'reorder_quantity', 'preferred_supplier'),
        }),
        (_('Notifications & Automation'), {
            'fields': ('notify_owner', 'auto_reorder'),
        }),
        (_('Warehouses'), {
            'fields': ('warehouses',),
            'description': _('Which warehouses this rule applies to. If none selected, it applies to all warehouses.'),
        }),
        (_('Status'), {
            'fields': ('last_check_date', 'last_restock_date'),
            'classes': ('collapse',),
        }),
    )
    readonly_fields = ('last_check_date', 'last_restock_date')

    def get_rule_name(self, obj):
        return obj.base_rule.name

    get_rule_name.short_description = _('Rule Name')

    def get_rule_status(self, obj):
        if obj.base_rule.is_active:
            return format_html('<span style="color: green;">✓ {}</span>', _('Active'))
        return format_html('<span style="color: red;">✗ {}</span>', _('Inactive'))

    get_rule_status.short_description = _('Status')

    def get_last_restock(self, obj):
        if obj.last_restock_date:
            days_ago = (timezone.now() - obj.last_restock_date).days
            return f"{days_ago} days ago"
        return _("Never")

    get_last_restock.short_description = _('Last Restock')


# Attribute Weight inline for ProductComparisonSettings
class ComparisonAttributeWeightInline(admin.TabularInline):
    model = ComparisonAttributeWeight
    extra = 1

    fieldsets = (
        (None, {
            'fields': ('attribute_name', 'weight', 'comparison_type'),
        }),
    )


# Product Comparison Settings admin
class ProductComparisonSettingsAdmin(LWHBaseAdmin):
    list_display = ('id', 'get_rule_name', 'get_rule_status', 'category',
                    'price_weight', 'rating_weight', 'availability_weight')
    list_filter = ('base_rule__is_active', 'category')
    search_fields = ('base_rule__name', 'category__name')
    inlines = [ComparisonAttributeWeightInline]

    fieldsets = (
        (None, {'fields': ('base_rule', 'category')}),
        (_('Weight Factors'), {
            'fields': ('price_weight', 'rating_weight', 'availability_weight'),
            'description': _('Weights for standard comparison factors.'),
        }),
        (_('Custom Attributes'), {
            'fields': ('custom_attributes',),
            'classes': ('collapse',),
            'description': _('JSON configuration for custom attribute comparison.'),
        }),
    )

    def get_rule_name(self, obj):
        return obj.base_rule.name

    get_rule_name.short_description = _('Rule Name')

    def get_rule_status(self, obj):
        if obj.base_rule.is_active:
            return format_html('<span style="color: green;">✓ {}</span>', _('Active'))
        return format_html('<span style="color: red;">✗ {}</span>', _('Inactive'))

    get_rule_status.short_description = _('Status')


# Register the specific rule implementations
admin.site.register(WarehouseSelectionRule, WarehouseSelectionRuleAdmin)
admin.site.register(PricingRule, PricingRuleAdmin)
admin.site.register(RestockRule, RestockRuleAdmin)
admin.site.register(ProductComparisonSettings, ProductComparisonSettingsAdmin)

# Create an Automation Dashboard view
from django.views.generic import TemplateView
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator


@method_decorator(staff_member_required, name='dispatch')
class AutomationDashboardView(TemplateView):
    template_name = 'admin/automation/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Count active rules by type
        context['active_warehouse_rules'] = WarehouseSelectionRule.objects.filter(base_rule__is_active=True).count()
        context['active_pricing_rules'] = PricingRule.objects.filter(base_rule__is_active=True).count()
        context['active_restock_rules'] = RestockRule.objects.filter(base_rule__is_active=True).count()
        context['active_comparison_rules'] = ProductComparisonSettings.objects.filter(base_rule__is_active=True).count()

        # Get recent restock events
        context['recent_restocks'] = RestockRule.objects.filter(
            last_restock_date__isnull=False
        ).order_by('-last_restock_date')[:5]

        # Get products needing restock
        from django.db.models import F, Sum
        from ..inventory.models import InventoryItem

        low_stock_products = []
        restock_rules = RestockRule.objects.filter(base_rule__is_active=True)

        for rule in restock_rules:
            inventory_sum = InventoryItem.objects.filter(
                product=rule.product,
                status='available'
            ).aggregate(total=Sum('quantity'))

            total_quantity = inventory_sum.get('total') or 0

            if total_quantity < rule.minimum_quantity:
                low_stock_products.append({
                    'product': rule.product,
                    'current_quantity': total_quantity,
                    'minimum_quantity': rule.minimum_quantity,
                    'reorder_quantity': rule.reorder_quantity,
                    'rule': rule
                })

        context['low_stock_products'] = low_stock_products

        return context


# Add dashboard to admin URLs
from django.urls import path

admin_urls = [
    path('automation/dashboard/', AutomationDashboardView.as_view(), name='automation_dashboard'),
]

# Try to add our URLs to admin.site.urls
try:
    from django.contrib import admin

    admin.site.get_urls()
    # This is a bit of a hack but it's the easiest way to add custom admin views
    admin_urlpatterns = list(admin.site.urls[0])
    admin_urlpatterns.extend(admin_urls)
    admin.site.urls = tuple([admin_urlpatterns] + list(admin.site.urls[1:]))
except:
    # If that fails (which it might in some Django versions), we'll handle this in the app's urls.py
    pass
