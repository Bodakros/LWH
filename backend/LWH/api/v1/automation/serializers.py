from rest_framework import serializers
from .models import (
    AutomationRule, WarehouseSelectionRule, PricingRule,
    RestockRule, ProductComparisonSettings, ComparisonAttributeWeight
)
from ..products.serializers import ProductSerializer, ProductCategorySerializer
from ..warehouses.serializers import WarehouseSerializer


class AutomationRuleSerializer(serializers.ModelSerializer):
    """Serializer for the base AutomationRule model"""
    created_by_username = serializers.ReadOnlyField(source='created_by.username')
    rule_type_display = serializers.ReadOnlyField(source='get_rule_type_display')

    class Meta:
        model = AutomationRule
        fields = [
            'id', 'name', 'description', 'rule_type', 'rule_type_display',
            'is_active', 'priority', 'created_by', 'created_by_username',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class WarehouseSelectionRuleSerializer(serializers.ModelSerializer):
    """Serializer for warehouse selection rules"""
    base_rule = AutomationRuleSerializer()
    preferred_warehouses_details = WarehouseSerializer(source='preferred_warehouses', many=True, read_only=True)
    excluded_warehouses_details = WarehouseSerializer(source='excluded_warehouses', many=True, read_only=True)

    class Meta:
        model = WarehouseSelectionRule
        fields = [
            'id', 'base_rule', 'capacity_weight', 'rating_weight', 'price_weight',
            'preferred_warehouses', 'preferred_warehouses_details',
            'excluded_warehouses', 'excluded_warehouses_details',
            'minimum_capacity_required'
        ]

    def create(self, validated_data):
        base_rule_data = validated_data.pop('base_rule')
        preferred_warehouses = validated_data.pop('preferred_warehouses', [])
        excluded_warehouses = validated_data.pop('excluded_warehouses', [])

        # Create base rule first
        base_rule = AutomationRule.objects.create(**base_rule_data)

        # Create warehouse selection rule
        warehouse_selection_rule = WarehouseSelectionRule.objects.create(
            base_rule=base_rule, **validated_data
        )

        # Add warehouses relationships
        if preferred_warehouses:
            warehouse_selection_rule.preferred_warehouses.set(preferred_warehouses)
        if excluded_warehouses:
            warehouse_selection_rule.excluded_warehouses.set(excluded_warehouses)

        return warehouse_selection_rule

    def update(self, instance, validated_data):
        base_rule_data = validated_data.pop('base_rule', None)
        preferred_warehouses = validated_data.pop('preferred_warehouses', None)
        excluded_warehouses = validated_data.pop('excluded_warehouses', None)

        # Update base rule if provided
        if base_rule_data:
            for attr, value in base_rule_data.items():
                setattr(instance.base_rule, attr, value)
            instance.base_rule.save()

        # Update warehouse selection rule
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Update warehouses relationships
        if preferred_warehouses is not None:
            instance.preferred_warehouses.set(preferred_warehouses)
        if excluded_warehouses is not None:
            instance.excluded_warehouses.set(excluded_warehouses)

        instance.save()
        return instance


class PricingRuleSerializer(serializers.ModelSerializer):
    """Serializer for pricing rules"""
    base_rule = AutomationRuleSerializer()
    product_categories_details = ProductCategorySerializer(source='product_categories', many=True, read_only=True)
    adjustment_type_display = serializers.ReadOnlyField(source='get_adjustment_type_display')

    class Meta:
        model = PricingRule
        fields = [
            'id', 'base_rule', 'product_categories', 'product_categories_details',
            'adjustment_type', 'adjustment_type_display', 'adjustment_value',
            'formula', 'min_margin', 'max_margin', 'applies_to_products',
            'conditions'
        ]

    def create(self, validated_data):
        base_rule_data = validated_data.pop('base_rule')
        product_categories = validated_data.pop('product_categories', [])
        applies_to_products = validated_data.pop('applies_to_products', [])

        # Create base rule first
        base_rule = AutomationRule.objects.create(**base_rule_data)

        # Create pricing rule
        pricing_rule = PricingRule.objects.create(
            base_rule=base_rule, **validated_data
        )

        # Add relationships
        if product_categories:
            pricing_rule.product_categories.set(product_categories)
        if applies_to_products:
            pricing_rule.applies_to_products.set(applies_to_products)

        return pricing_rule

    def update(self, instance, validated_data):
        base_rule_data = validated_data.pop('base_rule', None)
        product_categories = validated_data.pop('product_categories', None)
        applies_to_products = validated_data.pop('applies_to_products', None)

        # Update base rule if provided
        if base_rule_data:
            for attr, value in base_rule_data.items():
                setattr(instance.base_rule, attr, value)
            instance.base_rule.save()

        # Update pricing rule
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Update relationships
        if product_categories is not None:
            instance.product_categories.set(product_categories)
        if applies_to_products is not None:
            instance.applies_to_products.set(applies_to_products)

        instance.save()
        return instance


class RestockRuleSerializer(serializers.ModelSerializer):
    """Serializer for inventory restock rules"""
    base_rule = AutomationRuleSerializer()
    product_details = ProductSerializer(source='product', read_only=True)
    warehouses_details = WarehouseSerializer(source='warehouses', many=True, read_only=True)
    preferred_supplier_username = serializers.ReadOnlyField(source='preferred_supplier.username')

    class Meta:
        model = RestockRule
        fields = [
            'id', 'base_rule', 'product', 'product_details',
            'minimum_quantity', 'reorder_quantity', 'preferred_supplier',
            'preferred_supplier_username', 'notify_owner', 'auto_reorder',
            'warehouses', 'warehouses_details', 'last_check_date',
            'last_restock_date'
        ]
        read_only_fields = ['last_check_date', 'last_restock_date']

    def create(self, validated_data):
        base_rule_data = validated_data.pop('base_rule')
        warehouses = validated_data.pop('warehouses', [])

        # Create base rule first
        base_rule = AutomationRule.objects.create(**base_rule_data)

        # Create restock rule
        restock_rule = RestockRule.objects.create(
            base_rule=base_rule, **validated_data
        )

        # Add warehouses
        if warehouses:
            restock_rule.warehouses.set(warehouses)

        return restock_rule

    def update(self, instance, validated_data):
        base_rule_data = validated_data.pop('base_rule', None)
        warehouses = validated_data.pop('warehouses', None)

        # Update base rule if provided
        if base_rule_data:
            for attr, value in base_rule_data.items():
                setattr(instance.base_rule, attr, value)
            instance.base_rule.save()

        # Update restock rule
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Update warehouses
        if warehouses is not None:
            instance.warehouses.set(warehouses)

        instance.save()
        return instance


class ComparisonAttributeWeightSerializer(serializers.ModelSerializer):
    """Serializer for product comparison attribute weights"""
    comparison_type_display = serializers.ReadOnlyField(source='get_comparison_type_display')

    class Meta:
        model = ComparisonAttributeWeight
        fields = [
            'id', 'comparison_settings', 'attribute_name', 'weight',
            'comparison_type', 'comparison_type_display'
        ]


class ProductComparisonSettingsSerializer(serializers.ModelSerializer):
    """Serializer for product comparison settings"""
    base_rule = AutomationRuleSerializer()
    category_details = ProductCategorySerializer(source='category', read_only=True)
    attribute_weights = ComparisonAttributeWeightSerializer(many=True, read_only=True)

    class Meta:
        model = ProductComparisonSettings
        fields = [
            'id', 'base_rule', 'category', 'category_details',
            'price_weight', 'rating_weight', 'availability_weight',
            'custom_attributes', 'attribute_weights'
        ]

    def create(self, validated_data):
        base_rule_data = validated_data.pop('base_rule')

        # Create base rule first
        base_rule = AutomationRule.objects.create(**base_rule_data)

        # Create comparison settings
        comparison_settings = ProductComparisonSettings.objects.create(
            base_rule=base_rule, **validated_data
        )

        return comparison_settings

    def update(self, instance, validated_data):
        base_rule_data = validated_data.pop('base_rule', None)

        # Update base rule if provided
        if base_rule_data:
            for attr, value in base_rule_data.items():
                setattr(instance.base_rule, attr, value)
            instance.base_rule.save()

        # Update comparison settings
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance