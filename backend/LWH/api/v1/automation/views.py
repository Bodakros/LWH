from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.utils import timezone

from .models import (
    AutomationRule, WarehouseSelectionRule, PricingRule,
    RestockRule, ProductComparisonSettings, ComparisonAttributeWeight
)
from .serializers import (
    AutomationRuleSerializer, WarehouseSelectionRuleSerializer,
    PricingRuleSerializer, RestockRuleSerializer,
    ProductComparisonSettingsSerializer, ComparisonAttributeWeightSerializer
)
from ..users.permissions import IsSeller, IsOwner


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def automation_rule_list(request):
    """
    List all automation rules or create a new rule
    """
    if request.method == 'GET':
        rule_type = request.query_params.get('rule_type')
        is_active = request.query_params.get('is_active')

        # Filter rules by user
        rules = AutomationRule.objects.filter(created_by=request.user)

        # Apply additional filters
        if rule_type:
            rules = rules.filter(rule_type=rule_type)
        if is_active is not None:
            is_active_bool = is_active.lower() == 'true'
            rules = rules.filter(is_active=is_active_bool)

        serializer = AutomationRuleSerializer(rules, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = AutomationRuleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def automation_rule_detail(request, pk):
    """
    Retrieve, update or delete an automation rule
    """
    rule = get_object_or_404(AutomationRule, pk=pk)

    # Check permissions
    if rule.created_by != request.user:
        return Response({"detail": "You do not have permission to access this rule."},
                        status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        serializer = AutomationRuleSerializer(rule)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = AutomationRuleSerializer(rule, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        rule.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def warehouse_selection_rule_list(request):
    """
    List all warehouse selection rules or create a new rule
    """
    if request.method == 'GET':
        # Filter rules by user
        base_rules = AutomationRule.objects.filter(
            created_by=request.user,
            rule_type='warehouse_selection'
        )

        rules = WarehouseSelectionRule.objects.filter(base_rule__in=base_rules)

        serializer = WarehouseSelectionRuleSerializer(rules, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        # Only sellers can create warehouse selection rules
        if not request.user.is_seller:
            return Response({"detail": "Only sellers can create warehouse selection rules."},
                            status=status.HTTP_403_FORBIDDEN)

        # Set rule type to warehouse_selection
        if 'base_rule' in request.data:
            request.data['base_rule']['rule_type'] = 'warehouse_selection'
            request.data['base_rule']['created_by'] = request.user.id

        serializer = WarehouseSelectionRuleSerializer(data=request.data)
        if serializer.is_valid():
            rule = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def warehouse_selection_rule_detail(request, pk):
    """
    Retrieve, update or delete a warehouse selection rule
    """
    rule = get_object_or_404(WarehouseSelectionRule, pk=pk)

    # Check permissions
    if rule.base_rule.created_by != request.user:
        return Response({"detail": "You do not have permission to access this rule."},
                        status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        serializer = WarehouseSelectionRuleSerializer(rule)
        return Response(serializer.data)

    elif request.method == 'PUT':
        # Set rule type to warehouse_selection for consistency
        if 'base_rule' in request.data:
            request.data['base_rule']['rule_type'] = 'warehouse_selection'

        serializer = WarehouseSelectionRuleSerializer(rule, data=request.data, partial=True)
        if serializer.is_valid():
            rule = serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        # Delete the base rule as well
        base_rule = rule.base_rule
        rule.delete()
        base_rule.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsSeller])
def find_best_warehouses(request):
    """
    Find the best warehouses based on specified criteria and existing rules
    """
    rule_id = request.data.get('rule_id')
    required_capacity = request.data.get('required_capacity', 0)
    limit = min(int(request.data.get('limit', 5)), 20)  # Maximum 20 warehouses

    if rule_id:
        # Find warehouses using a specific rule
        rule = get_object_or_404(WarehouseSelectionRule, pk=rule_id)

        # Check if the user owns the rule
        if rule.base_rule.created_by != request.user:
            return Response({"detail": "You do not have permission to use this rule."},
                            status=status.HTTP_403_FORBIDDEN)

        # Use the rule to find the best warehouses
        if not rule.base_rule.is_active:
            return Response(
                {"detail": "This rule is inactive and cannot be used."},
                status=status.HTTP_400_BAD_REQUEST
            )

        scored_warehouses = rule.get_best_warehouses(
            required_capacity=float(required_capacity),
            limit=limit
        )

        results = [
            {
                "warehouse_id": warehouse.id,
                "name": warehouse.name,
                "score": score,
                "total_capacity": warehouse.total_capacity,
                "available_capacity": warehouse.available_capacity,
                "rating": warehouse.rating
            }
            for warehouse, score in scored_warehouses
        ]

        return Response({
            "rule_id": rule.id,
            "rule_name": rule.base_rule.name,
            "required_capacity": required_capacity,
            "results": results
        })

    else:
        # Find best warehouses using default logic or the user's highest priority rule
        user_rules = WarehouseSelectionRule.objects.filter(
            base_rule__created_by=request.user,
            base_rule__is_active=True,
            base_rule__rule_type='warehouse_selection'
        ).order_by('-base_rule__priority')

        if user_rules.exists():
            # Use the highest priority rule
            rule = user_rules.first()
            scored_warehouses = rule.get_best_warehouses(
                required_capacity=float(required_capacity),
                limit=limit
            )

            results = [
                {
                    "warehouse_id": warehouse.id,
                    "name": warehouse.name,
                    "score": score,
                    "total_capacity": warehouse.total_capacity,
                    "available_capacity": warehouse.available_capacity,
                    "rating": warehouse.rating
                }
                for warehouse, score in scored_warehouses
            ]

            return Response({
                "rule_id": rule.id,
                "rule_name": rule.base_rule.name,
                "required_capacity": required_capacity,
                "results": results
            })

        else:
            # User has no rules, return a message
            return Response(
                {"detail": "No active warehouse selection rules found. Please create one first."},
                status=status.HTTP_404_NOT_FOUND
            )


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def pricing_rule_list(request):
    """
    List all pricing rules or create a new rule
    """
    if request.method == 'GET':
        # Filter rules by user
        base_rules = AutomationRule.objects.filter(
            created_by=request.user,
            rule_type='pricing'
        )

        rules = PricingRule.objects.filter(base_rule__in=base_rules)

        # Filter by category if provided
        category_id = request.query_params.get('category')
        if category_id:
            rules = rules.filter(product_categories__id=category_id)

        serializer = PricingRuleSerializer(rules, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        # Only sellers can create pricing rules
        if not request.user.is_seller:
            return Response({"detail": "Only sellers can create pricing rules."},
                            status=status.HTTP_403_FORBIDDEN)

        # Set rule type to pricing
        if 'base_rule' in request.data:
            request.data['base_rule']['rule_type'] = 'pricing'
            request.data['base_rule']['created_by'] = request.user.id

        serializer = PricingRuleSerializer(data=request.data)
        if serializer.is_valid():
            rule = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def pricing_rule_detail(request, pk):
    """
    Retrieve, update or delete a pricing rule
    """
    rule = get_object_or_404(PricingRule, pk=pk)

    # Check permissions
    if rule.base_rule.created_by != request.user:
        return Response({"detail": "You do not have permission to access this rule."},
                        status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        serializer = PricingRuleSerializer(rule)
        return Response(serializer.data)

    elif request.method == 'PUT':
        # Set rule type to pricing for consistency
        if 'base_rule' in request.data:
            request.data['base_rule']['rule_type'] = 'pricing'

        serializer = PricingRuleSerializer(rule, data=request.data, partial=True)
        if serializer.is_valid():
            rule = serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        # Delete the base rule as well
        base_rule = rule.base_rule
        rule.delete()
        base_rule.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsSeller])
def calculate_price(request):
    """
    Calculate price adjustment based on pricing rules
    """
    product_id = request.data.get('product_id')
    base_price = request.data.get('base_price')
    cost_price = request.data.get('cost_price')
    rule_id = request.data.get('rule_id')

    if not product_id or base_price is None:
        return Response(
            {"detail": "Product ID and base price are required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    from ..products.models import Product

    try:
        product = Product.objects.get(pk=product_id)
        base_price = float(base_price)
        cost_price = float(cost_price) if cost_price is not None else None
    except (Product.DoesNotExist, ValueError):
        return Response(
            {"detail": "Invalid product ID or price values."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Check if the product belongs to the user
    if product.seller != request.user:
        return Response(
            {"detail": "You can only calculate prices for your own products."},
            status=status.HTTP_403_FORBIDDEN
        )

    if rule_id:
        # Calculate using a specific rule
        try:
            rule = PricingRule.objects.get(pk=rule_id)

            # Check if the user owns the rule
            if rule.base_rule.created_by != request.user:
                return Response(
                    {"detail": "You do not have permission to use this rule."},
                    status=status.HTTP_403_FORBIDDEN
                )

            if not rule.base_rule.is_active:
                return Response(
                    {"detail": "This rule is inactive and cannot be used."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            adjusted_price = rule.calculate_price_adjustment(product, base_price, cost_price)

            return Response({
                "product_id": product.id,
                "product_name": product.name,
                "base_price": base_price,
                "cost_price": cost_price,
                "adjusted_price": float(adjusted_price),
                "rule_used": {
                    "id": rule.id,
                    "name": rule.base_rule.name,
                    "adjustment_type": rule.adjustment_type,
                    "adjustment_value": float(rule.adjustment_value)
                }
            })

        except PricingRule.DoesNotExist:
            return Response(
                {"detail": "Pricing rule not found."},
                status=status.HTTP_404_NOT_FOUND
            )

    else:
        # Find all applicable rules and apply the highest priority one
        applicable_rules = PricingRule.objects.filter(
            Q(base_rule__created_by=request.user) &
            Q(base_rule__is_active=True) &
            Q(base_rule__rule_type='pricing') &
            (
                    Q(product_categories=product.category) |
                    Q(applies_to_products=product)
            )
        ).order_by('-base_rule__priority')

        if applicable_rules.exists():
            rule = applicable_rules.first()
            adjusted_price = rule.calculate_price_adjustment(product, base_price, cost_price)

            return Response({
                "product_id": product.id,
                "product_name": product.name,
                "base_price": base_price,
                "cost_price": cost_price,
                "adjusted_price": float(adjusted_price),
                "rule_used": {
                    "id": rule.id,
                    "name": rule.base_rule.name,
                    "adjustment_type": rule.adjustment_type,
                    "adjustment_value": float(rule.adjustment_value)
                }
            })

        else:
            # No applicable rules found
            return Response({
                "product_id": product.id,
                "product_name": product.name,
                "base_price": base_price,
                "cost_price": cost_price,
                "adjusted_price": base_price,  # No adjustment
                "rule_used": None
            })


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def restock_rule_list(request):
    """
    List all restock rules or create a new rule
    """
    if request.method == 'GET':
        # Filter rules by user
        base_rules = AutomationRule.objects.filter(
            created_by=request.user,
            rule_type='restock'
        )

        rules = RestockRule.objects.filter(base_rule__in=base_rules)

        # Filter by product if provided
        product_id = request.query_params.get('product')
        if product_id:
            rules = rules.filter(product_id=product_id)

        # Filter by warehouse if provided
        warehouse_id = request.query_params.get('warehouse')
        if warehouse_id:
            rules = rules.filter(warehouses__id=warehouse_id)

        serializer = RestockRuleSerializer(rules, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        # Only sellers can create restock rules
        if not request.user.is_seller:
            return Response({"detail": "Only sellers can create restock rules."},
                            status=status.HTTP_403_FORBIDDEN)

        # Set rule type to restock
        if 'base_rule' in request.data:
            request.data['base_rule']['rule_type'] = 'restock'
            request.data['base_rule']['created_by'] = request.user.id

        # Check if product belongs to the user
        from ..products.models import Product
        product_id = request.data.get('product')
        if product_id:
            try:
                product = Product.objects.get(pk=product_id)
                if product.seller != request.user:
                    return Response(
                        {"detail": "You can only create restock rules for your own products."},
                        status=status.HTTP_403_FORBIDDEN
                    )
            except Product.DoesNotExist:
                return Response(
                    {"detail": "Product not found."},
                    status=status.HTTP_404_NOT_FOUND
                )

        serializer = RestockRuleSerializer(data=request.data)
        if serializer.is_valid():
            rule = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def restock_rule_detail(request, pk):
    """
    Retrieve, update or delete a restock rule
    """
    rule = get_object_or_404(RestockRule, pk=pk)

    # Check permissions
    if rule.base_rule.created_by != request.user:
        return Response({"detail": "You do not have permission to access this rule."},
                        status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        serializer = RestockRuleSerializer(rule)
        return Response(serializer.data)

    elif request.method == 'PUT':
        # Set rule type to restock for consistency
        if 'base_rule' in request.data:
            request.data['base_rule']['rule_type'] = 'restock'

        # Check if product is being changed and belongs to the user
        product_id = request.data.get('product')
        if product_id:
            from ..products.models import Product
            try:
                product = Product.objects.get(pk=product_id)
                if product.seller != request.user:
                    return Response(
                        {"detail": "You can only use your own products in restock rules."},
                        status=status.HTTP_403_FORBIDDEN
                    )
            except Product.DoesNotExist:
                return Response(
                    {"detail": "Product not found."},
                    status=status.HTTP_404_NOT_FOUND
                )

        serializer = RestockRuleSerializer(rule, data=request.data, partial=True)
        if serializer.is_valid():
            rule = serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        # Delete the base rule as well
        base_rule = rule.base_rule
        rule.delete()
        base_rule.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsSeller])
def check_inventory_levels(request):
    """
    Check inventory levels and determine if restocking is needed
    """
    rule_id = request.data.get('rule_id')
    product_id = request.data.get('product_id')

    if rule_id:
        # Check using a specific rule
        rule = get_object_or_404(RestockRule, pk=rule_id)

        # Check permissions
        if rule.base_rule.created_by != request.user:
            return Response({"detail": "You do not have permission to use this rule."},
                            status=status.HTTP_403_FORBIDDEN)

        if not rule.base_rule.is_active:
            return Response(
                {"detail": "This rule is inactive and cannot be used."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update last check date
        rule.last_check_date = timezone.now()
        rule.save(update_fields=['last_check_date'])

        # Check inventory levels
        result = rule.check_inventory_levels()
        return Response(result)

    elif product_id:
        # Check for a specific product using the user's rules
        from ..products.models import Product
        try:
            product = Product.objects.get(pk=product_id)

            # Check if the product belongs to the user
            if product.seller != request.user:
                return Response(
                    {"detail": "You can only check inventory levels for your own products."},
                    status=status.HTTP_403_FORBIDDEN
                )

            # Find all restock rules for this product
            rules = RestockRule.objects.filter(
                product=product,
                base_rule__created_by=request.user,
                base_rule__is_active=True
            )

            if not rules.exists():
                return Response(
                    {"detail": "No active restock rules found for this product."},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Check inventory levels for all rules
            results = []
            for rule in rules:
                # Update last check date
                rule.last_check_date = timezone.now()
                rule.save(update_fields=['last_check_date'])

                # Check inventory levels
                result = rule.check_inventory_levels()
                results.append({
                    "rule_id": rule.id,
                    "rule_name": rule.base_rule.name,
                    "result": result
                })

            return Response({
                "product_id": product.id,
                "product_name": product.name,
                "rules_checked": len(results),
                "results": results
            })

        except Product.DoesNotExist:
            return Response(
                {"detail": "Product not found."},
                status=status.HTTP_404_NOT_FOUND
            )

    else:
        return Response(
            {"detail": "Either rule_id or product_id must be provided."},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def product_comparison_settings_list(request):
    """
    List all product comparison settings or create new settings
    """
    if request.method == 'GET':
        # Filter settings by user
        base_rules = AutomationRule.objects.filter(
            created_by=request.user,
            rule_type='product_comparison'
        )

        settings = ProductComparisonSettings.objects.filter(base_rule__in=base_rules)

        # Filter by category if provided
        category_id = request.query_params.get('category')
        if category_id:
            settings = settings.filter(category_id=category_id)

        serializer = ProductComparisonSettingsSerializer(settings, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        # Set rule type to product_comparison
        if 'base_rule' in request.data:
            request.data['base_rule']['rule_type'] = 'product_comparison'
            request.data['base_rule']['created_by'] = request.user.id

        serializer = ProductComparisonSettingsSerializer(data=request.data)
        if serializer.is_valid():
            settings = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def product_comparison_settings_detail(request, pk):
    """
    Retrieve, update or delete product comparison settings
    """
    settings = get_object_or_404(ProductComparisonSettings, pk=pk)

    # Check permissions
    if settings.base_rule.created_by != request.user:
        return Response({"detail": "You do not have permission to access these settings."},
                        status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        serializer = ProductComparisonSettingsSerializer(settings)
        return Response(serializer.data)

    elif request.method == 'PUT':
        # Set rule type to product_comparison for consistency
        if 'base_rule' in request.data:
            request.data['base_rule']['rule_type'] = 'product_comparison'

        serializer = ProductComparisonSettingsSerializer(settings, data=request.data, partial=True)
        if serializer.is_valid():
            settings = serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        # Delete the base rule as well
        base_rule = settings.base_rule
        settings.delete()
        base_rule.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def comparison_attribute_weight_list(request, settings_id):
    """
    List all attribute weights for comparison settings or create a new weight
    """
    settings = get_object_or_404(ProductComparisonSettings, pk=settings_id)

    # Check permissions
    if settings.base_rule.created_by != request.user:
        return Response({"detail": "You do not have permission to access these settings."},
                        status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        weights = ComparisonAttributeWeight.objects.filter(comparison_settings=settings)
        serializer = ComparisonAttributeWeightSerializer(weights, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        # Add settings ID to the data
        request.data['comparison_settings'] = settings_id

        serializer = ComparisonAttributeWeightSerializer(data=request.data)
        if serializer.is_valid():
            weight = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def comparison_attribute_weight_detail(request, settings_id, pk):
    """
    Retrieve, update or delete a comparison attribute weight
    """
    settings = get_object_or_404(ProductComparisonSettings, pk=settings_id)
    weight = get_object_or_404(ComparisonAttributeWeight, pk=pk, comparison_settings=settings)

    # Check permissions
    if settings.base_rule.created_by != request.user:
        return Response({"detail": "You do not have permission to access these settings."},
                        status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        serializer = ComparisonAttributeWeightSerializer(weight)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = ComparisonAttributeWeightSerializer(weight, data=request.data, partial=True)
        if serializer.is_valid():
            weight = serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        weight.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def compare_products(request):
    """
    Compare products based on comparison settings
    """
    settings_id = request.data.get('settings_id')
    product_ids = request.data.get('product_ids', [])

    if not settings_id or not product_ids:
        return Response(
            {"detail": "Settings ID and product IDs are required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Get comparison settings
    settings = get_object_or_404(ProductComparisonSettings, pk=settings_id)

    # Check permissions
    if settings.base_rule.created_by != request.user and not settings.base_rule.is_active:
        return Response({"detail": "You do not have permission to use these settings."},
                        status=status.HTTP_403_FORBIDDEN)

    # Get products
    from ..products.models import Product
    products = Product.objects.filter(id__in=product_ids)

    if not products.exists():
        return Response(
            {"detail": "No valid products found with the provided IDs."},
            status=status.HTTP_404_NOT_FOUND
        )

    # Compare products
    scored_products = settings.compare_products(products)

    # Format results
    results = []
    for product, score in scored_products:
        results.append({
            "product_id": product.id,
            "product_name": product.name,
            "product_sku": product.sku,
            "score": score,
            "base_price": float(product.base_price),
            "seller_id": product.seller.id,
            "seller_name": product.seller.username
        })

    return Response({
        "settings_id": settings.id,
        "settings_name": settings.base_rule.name,
        "category": {
            "id": settings.category.id,
            "name": settings.category.name
        },
        "products_compared": len(results),
        "results": results
    })

@api_view(['GET', 'PUT', 'POST'])
@permission_classes([IsAuthenticated])
def manage_automation_tasks(request):
    """
    GET: Get current automation tasks configuration
    PUT: Update automation tasks configuration (admin only)
    POST: Manually trigger a specific task
    """
    from django.conf import settings

    # Get current settings
    automation_settings = getattr(settings, 'AUTOMATION_SETTINGS', {
        'ENABLE_BACKGROUND_TASKS': False,
        'TASKS': {
            'inventory_check': {'enabled': False, 'schedule': 3600},
            'price_update': {'enabled': False, 'schedule': 86400},
            'product_comparison': {'enabled': False, 'schedule': 43200}
        }
    })

    if request.method == 'GET':
        # Get celery worker status if possible
        worker_status = {"status": "Unknown"}
        try:
            from celery.task.control import inspect
            insp = inspect()
            active = insp.active()
            worker_status = {
                "status": "Online" if active else "Offline",
                "active_tasks": active if active else {}
            }
        except:
            pass  # Ignore errors if we can't connect to Celery

        return Response({
            "settings": automation_settings,
            "worker_status": worker_status
        })

    elif request.method == 'PUT':
        # Check if user has permission to modify settings
        if not request.user.is_staff:
            return Response(
                {"detail": "Only admin users can modify automation task settings."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Update settings
        new_settings = request.data

        # Validate settings structure
        if 'ENABLE_BACKGROUND_TASKS' not in new_settings:
            return Response(
                {"detail": "ENABLE_BACKGROUND_TASKS key is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if 'TASKS' not in new_settings:
            return Response(
                {"detail": "TASKS key is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if tasks have the correct format
        for task_name, task_config in new_settings['TASKS'].items():
            if 'enabled' not in task_config:
                return Response(
                    {"detail": f"Task {task_name} must have 'enabled' key."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if 'schedule' not in task_config:
                return Response(
                    {"detail": f"Task {task_name} must have 'schedule' key."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Update the settings in memory
        # In production, you'd want to store this in a database
        settings.AUTOMATION_SETTINGS = new_settings

        # Restart celery beat to apply new schedule
        # This is a simplified approach - in production you'd use a more robust method
        try:
            from celery.task.control import broadcast
            broadcast('pool_restart', arguments={'reload': True})
            restart_status = "Celery workers signaled to restart"
        except Exception as e:
            restart_status = f"Failed to restart Celery workers: {str(e)}"

        return Response({
            "settings": settings.AUTOMATION_SETTINGS,
            "restart_status": restart_status
        })

    elif request.method == 'POST':
        # Manually trigger a task
        task_name = request.data.get('task_name')

        if not task_name:
            return Response(
                {"detail": "task_name parameter is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if task exists
        valid_tasks = ['inventory_check', 'price_update', 'product_comparison']
        if task_name not in valid_tasks:
            return Response(
                {"detail": f"Invalid task name. Valid values are: {', '.join(valid_tasks)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Only sellers and admins can run tasks
        if not (request.user.is_seller or request.user.is_staff):
            return Response(
                {"detail": "Only sellers and admins can trigger tasks."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Import and run the task asynchronously
        from .tasks import run_task_by_name
        task = run_task_by_name.delay(task_name)

        return Response({
            "task_id": task.id,
            "task_name": task_name,
            "status": "Task started",
            "message": f"The task '{task_name}' has been triggered and is running in the background"
        })
