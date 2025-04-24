from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import mark_safe

from .models import (
    ProductCategory, TaxType, TaxRate, Product, ProductImage,
    Attribute, AttributeOption, ProductAttributeValue,
    ProductMultipleAttributeValue
)
from ..admin import LWHBaseAdmin, LWHImageAdmin
from ..search.admin import ProductAdminExtension

# Category admin
@admin.register(ProductCategory)
class ProductCategoryAdmin(LWHBaseAdmin):
    list_display = ('name', 'slug', 'parent', 'created_at', 'updated_at')
    list_filter = ('parent', 'created_at')
    search_fields = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (None, {'fields': ('name', 'slug', 'parent')}),
        (_('Details'), {'fields': ('description', 'image')}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

# Tax related models
@admin.register(TaxType)
class TaxTypeAdmin(LWHBaseAdmin):
    list_display = ('code', 'name', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('code', 'name', 'description')

    fieldsets = (
        (None, {'fields': ('code', 'name', 'is_active')}),
        (_('Details'), {'fields': ('description',)}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    readonly_fields = ('created_at', 'updated_at')

@admin.register(TaxRate)
class TaxRateAdmin(LWHBaseAdmin):
    list_display = ('name', 'tax_type', 'calculation_type', 'get_rate_display', 'is_active')
    list_filter = ('tax_type', 'calculation_type', 'is_active')
    search_fields = ('name', 'tax_type__name', 'tax_type__code')
    filter_horizontal = ('applicable_categories',)

    fieldsets = (
        (None, {'fields': ('tax_type', 'name', 'is_active')}),
        (_('Calculation'), {
            'fields': ('calculation_type', 'rate_percentage', 'fixed_amount', 'formula'),
            'description': _('Fields used depend on the calculation type.')
        }),
        (_('Applications'), {'fields': ('applicable_categories',)}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    readonly_fields = ('created_at', 'updated_at')

    def get_rate_display(self, obj):
        if obj.calculation_type == 'percentage':
            return f"{obj.rate_percentage}%"
        elif obj.calculation_type == 'fixed':
            return f"{obj.fixed_amount} UAH"
        elif obj.calculation_type == 'quantity_based':
            return f"{obj.fixed_amount} UAH per unit"
        return "Formula based"
    get_rate_display.short_description = _('Rate')

# Product attribute models
class AttributeOptionInline(admin.TabularInline):
    model = AttributeOption
    extra = 1

@admin.register(Attribute)
class AttributeAdmin(LWHBaseAdmin):
    list_display = ('name', 'slug', 'attribute_type', 'required', 'is_filterable', 'is_displayed')
    list_filter = ('attribute_type', 'required', 'is_filterable', 'is_displayed')
    search_fields = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [AttributeOptionInline]
    filter_horizontal = ('categories',)

    fieldsets = (
        (None, {'fields': ('name', 'slug', 'attribute_type')}),
        (_('Options'), {'fields': ('required', 'is_filterable', 'is_displayed')}),
        (_('Categories'), {'fields': ('categories',)}),
        (_('Description'), {'fields': ('description',)}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    readonly_fields = ('created_at', 'updated_at')

# Product image inline for product admin
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    readonly_fields = ('created_at', 'image_preview')

    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="100" />')
        return _("No image")

    image_preview.short_description = _("Preview")

class ProductAttributeValueInline(admin.TabularInline):
    model = ProductAttributeValue
    extra = 1
    readonly_fields = ('get_attribute_type',)

    def get_attribute_type(self, obj):
        return obj.attribute.get_attribute_type_display() if obj.attribute else ""
    get_attribute_type.short_description = _("Attribute Type")

@admin.register(Product)
class ProductAdmin(LWHBaseAdmin, ProductAdminExtension):
    list_display = ('name', 'sku', 'seller', 'category', 'base_price', 'product_type', 'is_active')
    # list_filter inherited from ProductAdminExtension
    # search_fields inherited from ProductAdminExtension
    filter_horizontal = ('applicable_tax_types', 'custom_tax_rates')
    inlines = [ProductImageInline, ProductAttributeValueInline]

    fieldsets = (
        (None, {'fields': ('name', 'slug', 'sku', 'seller', 'category', 'description')}),
        (_('Pricing'), {'fields': ('base_price', 'taxable')}),
        (_('Dimensions'), {'fields': ('length', 'width', 'height', 'weight')}),
        (_('Classification'), {'fields': ('product_type',)}),
        (_('Taxes'), {'fields': ('applicable_tax_types', 'custom_tax_rates')}),
        (_('Dynamic Attributes'), {'fields': ('attributes_json',)}),
        (_('Image'), {'fields': ('main_image',)}),
        (_('Status'), {'fields': ('is_active',)}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    readonly_fields = ('created_at', 'updated_at', 'slug')

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)

        # Set first image as main if no main image is set
        instance = form.instance
        if not instance.main_image:
            first_image = instance.images.first()
            if first_image:
                first_image.is_main = True
                first_image.save()

                # Update product's main_image
                instance.main_image = first_image.image
                instance.save(update_fields=['main_image'])

@admin.register(ProductImage)
class ProductImageAdmin(LWHImageAdmin):
    list_display = ('id', 'product', 'is_main', 'order', 'created_at')
    list_filter = ('is_main', 'created_at')
    search_fields = ('product__name', 'product__sku', 'title')

    fieldsets = (
        (None, {'fields': ('product', 'image', 'title')}),
        (_('Options'), {'fields': ('is_main', 'order')}),
        (_('Preview'), {'fields': ('image_preview',)}),
        (_('Timestamps'), {'fields': ('created_at',), 'classes': ('collapse',)}),
    )
    readonly_fields = ('created_at', 'image_preview')

@admin.register(ProductAttributeValue)
class ProductAttributeValueAdmin(LWHBaseAdmin):
    list_display = ('product', 'attribute', 'get_value_display')
    list_filter = ('attribute__attribute_type',)
    search_fields = ('product__name', 'product__sku', 'attribute__name')
    raw_id_fields = ('product', 'attribute', 'select_value')

    fieldsets = (
        (None, {'fields': ('product', 'attribute')}),
        (_('Values'), {
            'fields': ('text_value', 'number_value', 'boolean_value', 'date_value', 'select_value')
        }),
    )

    def get_value_display(self, obj):
        if obj.attribute.attribute_type == 'text' and obj.text_value:
            return obj.text_value
        elif obj.attribute.attribute_type == 'number' and obj.number_value:
            return obj.number_value
        elif obj.attribute.attribute_type == 'boolean':
            return _('Yes') if obj.boolean_value else _('No')
        elif obj.attribute.attribute_type == 'date' and obj.date_value:
            return obj.date_value
        elif obj.attribute.attribute_type == 'select' and obj.select_value:
            return obj.select_value.value
        elif obj.attribute.attribute_type == 'multiple_select':
            values = obj.multiple_values.all()
            return ', '.join(val.attribute_option.value for val in values)
        return "-"
    get_value_display.short_description = _("Value")
