"""
Service functions for automation module that can be reused across different parts of the application.
These functions provide core business logic for automation features.
"""
from django.db.models import Q, Sum
from django.utils import timezone
from decimal import Decimal

from .models import (
    AutomationRule, WarehouseSelectionRule, PricingRule,
    RestockRule, ProductComparisonSettings
)
from ..products.models import Product
from ..warehouses.models import Warehouse, Stock
from ..inventory.models import InventoryItem


def find_optimal_warehouses(product, quantity, user=None, limit=5):
    """
    Find optimal warehouses for a product based on user's preferences and product requirements.

    Args:
        product: Product object to find warehouses for
        quantity: Quantity needed for storage
        user: User making the request (to use their rules if available)
        limit: Maximum number of warehouses to return

    Returns:
        list: List of tuples (warehouse, score) sorted by score
    """
    required_capacity = product.volume * quantity if product.volume else 0

    # Try to find user's warehouse selection rules
    if user:
        user_rules = WarehouseSelectionRule.objects.filter(
            base_rule__created_by=user,
            base_rule__is_active=True,
            base_rule__rule_type='warehouse_selection'
        ).order_by('-base_rule__priority')

        if user_rules.exists():
            return user_rules.first().get_best_warehouses(
                required_capacity=required_capacity,
                limit=limit
            )

    # Default warehouse selection if no user rules exist
    warehouses = Warehouse.objects.filter(is_active=True)
    scored_warehouses = []

    for warehouse in warehouses:
        # Skip warehouses with insufficient capacity
        if warehouse.available_capacity < required_capacity:
            continue

        # Calculate base score from capacity and rating
        score = 0

        # Capacity score (higher available capacity = higher score)
        capacity_ratio = min(1.0, warehouse.available_capacity / max(1, required_capacity * 2))
        score += capacity_ratio * 1.0  # Default weight of 1.0

        # Rating score
        if warehouse.rating:
            rating_score = float(warehouse.rating) / 5.0  # Normalize to 0-1
            score += rating_score * 1.0  # Default weight of 1.0

        scored_warehouses.append((warehouse, score))

    # Sort by score (highest first)
    scored_warehouses.sort(key=lambda x: x[1], reverse=True)

    return scored_warehouses[:limit]


def calculate_adjusted_price(product, base_price=None, cost_price=None, user=None):
    """
    Calculate adjusted price for a product based on pricing rules.

    Args:
        product: Product object
        base_price: Optional base price (defaults to product.base_price)
        cost_price: Optional cost price for margin calculations
        user: User making the request (to use their rules if available)

    Returns:
        tuple: (adjusted_price, rule_used)
    """
    # Use product's base price if not specified
    if base_price is None:
        base_price = product.base_price

    # Convert to Decimal for precise calculations
    base_price = Decimal(str(base_price))
    if cost_price is not None:
        cost_price = Decimal(str(cost_price))

    rule_used = None

    # Try to find applicable pricing rules
    if user:
        applicable_rules = PricingRule.objects.filter(
            Q(base_rule__created_by=user) &
            Q(base_rule__is_active=True) &
            Q(base_rule__rule_type='pricing') &
            (
                    Q(product_categories=product.category) |
                    Q(applies_to_products=product)
            )
        ).order_by('-base_rule__priority')

        if applicable_rules.exists():
            rule = applicable_rules.first()
            rule_used = rule
            adjusted_price = rule.calculate_price_adjustment(product, base_price, cost_price)
            return adjusted_price, rule_used

    # No applicable rules or user not provided, return original price
    return base_price, rule_used


def check_restock_needs(user=None, product=None):
    """
    Check if any products need restocking based on inventory levels.

    Args:
        user: Optional user to check only their restock rules
        product: Optional product to check only rules for this product

    Returns:
        list: List of dictionaries with restock information
    """
    # Build query for restock rules
    query = Q(base_rule__is_active=True)

    if user:
        query &= Q(base_rule__created_by=user)

    if product:
        query &= Q(product=product)

    restock_rules = RestockRule.objects.filter(query)

    restock_needs = []

    for rule in restock_rules:
        # Update last check date
        rule.last_check_date = timezone.now()
        rule.save(update_fields=['last_check_date'])

        # Check inventory levels
        result = rule.check_inventory_levels()

        if result['needs_restock']:
            restock_needs.append({
                'rule_id': rule.id,
                'rule_name': rule.base_rule.name,
                'product_id': rule.product.id,
                'product_name': rule.product.name,
                'seller_id': rule.product.seller.id,
                'seller_name': rule.product.seller.username,
                'warehouses_needing_restock': [
                    {
                        'warehouse_id': int(wh_id),
                        'warehouse_name': wh_data['warehouse_name'],
                        'current_quantity': wh_data['current_quantity'],
                        'minimum_quantity': wh_data['minimum_quantity'],
                        'quantity_to_reorder': wh_data['quantity_to_reorder']
                    }
                    for wh_id, wh_data in result['warehouses'].items()
                    if wh_data['needs_restock']
                ],
                'last_check_date': rule.last_check_date,
                'auto_reorder': rule.auto_reorder
            })

    return restock_needs


def compare_product_pricing(products, category=None):
    """
    Compare prices of similar products to identify pricing opportunities.

    Args:
        products: List of products to compare
        category: Optional category for comparison (if not provided, will use products' categories)

    Returns:
        dict: Dictionary with price comparison analysis
    """
    if not products:
        return {'error': 'No products provided for comparison'}

    # If category not specified, use the category of the first product
    if not category and products:
        category = products[0].category

    # Filter products by the selected category
    if category:
        products = [p for p in products if p.category == category]

    if not products:
        return {'error': 'No products match the category criteria'}

    # Calculate basic price statistics
    prices = [p.base_price for p in products]
    avg_price = sum(prices) / len(prices) if prices else 0
    min_price = min(prices) if prices else 0
    max_price = max(prices) if prices else 0

    # Create price analysis for each product
    product_analysis = []

    for product in products:
        # Calculate price difference from average
        price_diff_pct = (
            ((product.base_price - avg_price) / avg_price) * 100
            if avg_price > 0 else 0
        )

        # Determine if price is competitive
        is_below_avg = product.base_price < avg_price
        price_rank = sorted(prices).index(product.base_price) + 1

        product_analysis.append({
            'product_id': product.id,
            'product_name': product.name,
            'seller_id': product.seller.id,
            'seller_name': product.seller.username,
            'price': float(product.base_price),
            'diff_from_avg': float(product.base_price - avg_price),
            'diff_from_avg_percent': float(price_diff_pct),
            'is_below_avg': is_below_avg,
            'price_rank': price_rank,
            'price_competitiveness': 'High' if is_below_avg else 'Low'
        })

    return {
        'category': category.name if category else 'Multiple categories',
        'products_compared': len(products),
        'avg_price': float(avg_price),
        'min_price': float(min_price),
        'max_price': float(max_price),
        'price_range': float(max_price - min_price),
        'product_analysis': product_analysis
    }