from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from decimal import Decimal

from ..products.models import Product, ProductCategory
from ..warehouses.models import Warehouse, Stock


class AutomationRule(models.Model):
    """Base model for different types of automation rules"""

    RULE_TYPES = [
        ('warehouse_selection', _('Warehouse Selection')),
        ('pricing', _('Pricing')),
        ('restock', _('Restock')),
        ('product_comparison', _('Product Comparison')),
    ]

    name = models.CharField(max_length=255, verbose_name=_("Rule Name"))
    description = models.TextField(blank=True, null=True, verbose_name=_("Rule Description"))
    rule_type = models.CharField(max_length=50, choices=RULE_TYPES, verbose_name=_("Rule Type"))
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    priority = models.PositiveIntegerField(
        default=10,
        verbose_name=_("Priority"),
        help_text=_("Higher priority means the rule will be applied first (in case of conflicts)")
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='automation_rules',
        verbose_name=_("Created by")
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))

    class Meta:
        verbose_name = _("Automation Rule")
        verbose_name_plural = _("Automation Rules")
        ordering = ['-priority', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_rule_type_display()})"


class WarehouseSelectionRule(models.Model):
    """Model for automatic determination of optimal warehouse"""

    base_rule = models.OneToOneField(
        AutomationRule,
        on_delete=models.CASCADE,
        related_name='warehouse_selection_rule',
        verbose_name=_("Base Rule")
    )

    capacity_weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=1.0,
        verbose_name=_("Capacity Factor Weight"),
        help_text=_("Weight coefficient for available capacity when selecting a warehouse")
    )

    rating_weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=1.0,
        verbose_name=_("Rating Factor Weight"),
        help_text=_("Weight coefficient for warehouse rating when selecting")
    )

    price_weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=1.0,
        verbose_name=_("Price Factor Weight"),
        help_text=_("Weight coefficient for storage cost when selecting a warehouse")
    )

    # Selection constraints
    preferred_warehouses = models.ManyToManyField(
        Warehouse,
        blank=True,
        related_name='selection_rules',
        verbose_name=_("Preferred Warehouses")
    )

    excluded_warehouses = models.ManyToManyField(
        Warehouse,
        blank=True,
        related_name='exclusion_rules',
        verbose_name=_("Excluded Warehouses")
    )

    minimum_capacity_required = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Minimum Required Capacity")
    )

    class Meta:
        verbose_name = _("Warehouse Selection Rule")
        verbose_name_plural = _("Warehouse Selection Rules")

    def __str__(self):
        return f"Warehouse Selection Rule: {self.base_rule.name}"

    def calculate_warehouse_score(self, warehouse, required_capacity=0):
        """
        Calculate a score for a warehouse based on defined criteria

        Args:
            warehouse: Warehouse object to evaluate
            required_capacity: Required capacity for product placement

        Returns:
            float: Warehouse score (higher is better)
        """
        score = 0

        # Check minimum capacity
        if self.minimum_capacity_required and warehouse.available_capacity < self.minimum_capacity_required:
            return 0  # Warehouse doesn't meet minimum requirements

        # Check if in excluded list
        if warehouse in self.excluded_warehouses.all():
            return 0  # Warehouse is excluded

        # Check sufficient capacity for the order
        if required_capacity > 0 and warehouse.available_capacity < required_capacity:
            return 0  # Not enough space

        # Calculate score based on capacity
        capacity_score = min(1.0, warehouse.available_capacity / max(1, required_capacity * 2))
        score += capacity_score * float(self.capacity_weight)

        # Calculate score based on rating
        if warehouse.rating:
            rating_score = float(warehouse.rating) / 5.0  # Assuming rating from 0 to 5
            score += rating_score * float(self.rating_weight)

        # Additional points for preferred warehouses
        if warehouse in self.preferred_warehouses.all():
            score *= 1.5  # 50% bonus for preferred warehouses

        return score

    def get_best_warehouses(self, required_capacity=0, limit=5):
        """
        Returns a list of best warehouses according to the rule

        Args:
            required_capacity: Required capacity
            limit: Maximum number of warehouses to return

        Returns:
            list: List of tuples (warehouse, score) sorted by score
        """
        warehouses = Warehouse.objects.filter(is_active=True)

        # Calculate scores for all warehouses
        scored_warehouses = []
        for warehouse in warehouses:
            score = self.calculate_warehouse_score(warehouse, required_capacity)
            if score > 0:  # Include only warehouses with positive score
                scored_warehouses.append((warehouse, score))

        # Sort by score (from highest to lowest)
        scored_warehouses.sort(key=lambda x: x[1], reverse=True)

        return scored_warehouses[:limit]


class PricingRule(models.Model):
    """Model for automatic price calculation"""

    ADJUSTMENT_TYPES = [
        ('percentage', _('Percentage')),
        ('fixed', _('Fixed Amount')),
        ('formula', _('Formula')),
    ]

    base_rule = models.OneToOneField(
        AutomationRule,
        on_delete=models.CASCADE,
        related_name='pricing_rule',
        verbose_name=_("Base Rule")
    )

    product_categories = models.ManyToManyField(
        ProductCategory,
        blank=True,
        related_name='pricing_rules',
        verbose_name=_("Product Categories")
    )

    adjustment_type = models.CharField(
        max_length=20,
        choices=ADJUSTMENT_TYPES,
        default='percentage',
        verbose_name=_("Adjustment Type")
    )

    adjustment_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("Adjustment Value"),
        help_text=_("For percentages: 10.00 = +10%; -10.00 = -10%. For fixed: amount in currency.")
    )

    formula = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Calculation Formula"),
        help_text=_("Used for 'Formula' type. Available variables: base_price, cost_price")
    )

    min_margin = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Minimum Margin (%)"),
        help_text=_("Minimum margin to be preserved during adjustment")
    )

    max_margin = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Maximum Margin (%)"),
        help_text=_("Maximum margin that can be applied during adjustment")
    )

    applies_to_products = models.ManyToManyField(
        Product,
        blank=True,
        related_name='pricing_rules',
        verbose_name=_("Applies to Products")
    )

    conditions = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_("Application Conditions"),
        help_text=_("JSON with rule application conditions (e.g., {'inventory_level': '>50'}")
    )

    class Meta:
        verbose_name = _("Pricing Rule")
        verbose_name_plural = _("Pricing Rules")

    def __str__(self):
        return f"Pricing Rule: {self.base_rule.name}"

    def calculate_price_adjustment(self, product, base_price, cost_price=None):
        """
        Calculate new price according to the rule

        Args:
            product: Product for which the price is calculated
            base_price: Initial price
            cost_price: Cost price (optional)

        Returns:
            Decimal: Newly calculated price
        """
        adjusted_price = Decimal(base_price)

        # Check category match
        if self.product_categories.exists() and product.category not in self.product_categories.all():
            return base_price  # Rule doesn't apply to this category

        # Calculate based on adjustment type
        if self.adjustment_type == 'percentage':
            adjustment = base_price * (self.adjustment_value / Decimal('100.0'))
            adjusted_price += adjustment

        elif self.adjustment_type == 'fixed':
            adjusted_price += self.adjustment_value

        elif self.adjustment_type == 'formula' and self.formula:
            try:
                # Basic variables for formula
                variables = {
                    'base_price': float(base_price),
                    'cost_price': float(cost_price) if cost_price else 0,
                }

                # Calculate formula (in a real project, use safer solutions)
                result = eval(self.formula, {"__builtins__": {}}, variables)
                adjusted_price = Decimal(str(result))
            except Exception as e:
                # Log error and return base price
                print(f"Error calculating price with formula: {e}")
                return base_price

        # Apply margin constraints if specified and cost_price is known
        if cost_price and (self.min_margin is not None or self.max_margin is not None):
            margin_percent = ((adjusted_price - cost_price) / cost_price) * 100

            if self.min_margin is not None and margin_percent < self.min_margin:
                # Adjust to minimum margin
                adjusted_price = cost_price * (1 + (self.min_margin / 100))

            if self.max_margin is not None and margin_percent > self.max_margin:
                # Adjust to maximum margin
                adjusted_price = cost_price * (1 + (self.max_margin / 100))

        # Ensure price doesn't become negative
        return max(adjusted_price, Decimal('0.01'))


class RestockRule(models.Model):
    """Model for automatic inventory replenishment"""

    base_rule = models.OneToOneField(
        AutomationRule,
        on_delete=models.CASCADE,
        related_name='restock_rule',
        verbose_name=_("Base Rule")
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='restock_rules',
        verbose_name=_("Product")
    )

    minimum_quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("Minimum Quantity"),
        help_text=_("When product quantity falls below this threshold, replenishment is initiated")
    )

    reorder_quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("Reorder Quantity"),
        help_text=_("How many units to order during replenishment")
    )

    preferred_supplier = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='supplier_restock_rules',
        verbose_name=_("Preferred Supplier"),
        limit_choices_to={'is_seller': True}
    )

    notify_owner = models.BooleanField(
        default=True,
        verbose_name=_("Notify Owner"),
        help_text=_("Send notification to owner about low inventory levels")
    )

    auto_reorder = models.BooleanField(
        default=False,
        verbose_name=_("Automatic Reorder"),
        help_text=_("Automatically create replenishment orders")
    )

    warehouses = models.ManyToManyField(
        Warehouse,
        blank=True,
        related_name='restock_rules',
        verbose_name=_("Applies to Warehouses")
    )

    last_check_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Last Check Date")
    )

    last_restock_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Last Restock Date")
    )

    class Meta:
        verbose_name = _("Restock Rule")
        verbose_name_plural = _("Restock Rules")
        unique_together = ('product', 'base_rule')

    def __str__(self):
        return f"Restock Rule for {self.product.name}"

    def check_inventory_levels(self):
        """
        Check product inventory levels across all warehouses or specified warehouses

        Returns:
            dict: Check result with information about replenishment needs
        """
        from django.db.models import Sum
        from ..inventory.models import InventoryItem

        # Determine list of warehouses to check
        warehouses_to_check = self.warehouses.all() if self.warehouses.exists() else Warehouse.objects.all()

        results = {}
        needs_restock = False

        for warehouse in warehouses_to_check:
            # Get total quantity of available product in the warehouse
            inventory_sum = InventoryItem.objects.filter(
                product=self.product,
                warehouse=warehouse,
                status='available'
            ).aggregate(total_quantity=Sum('quantity'))

            total_quantity = inventory_sum['total_quantity'] or 0

            # Check if replenishment is needed
            if total_quantity < self.minimum_quantity:
                needs_restock = True

                results[warehouse.id] = {
                    'warehouse_name': warehouse.name,
                    'current_quantity': total_quantity,
                    'minimum_quantity': self.minimum_quantity,
                    'quantity_to_reorder': self.reorder_quantity,
                    'needs_restock': True
                }
            else:
                results[warehouse.id] = {
                    'warehouse_name': warehouse.name,
                    'current_quantity': total_quantity,
                    'minimum_quantity': self.minimum_quantity,
                    'needs_restock': False
                }

        return {
            'product_id': self.product.id,
            'product_name': self.product.name,
            'needs_restock': needs_restock,
            'warehouses': results
        }


class ProductComparisonSettings(models.Model):
    """Model for product comparison settings from different sellers"""

    COMPARISON_TYPES = [
        ('less_better', _('Less is Better')),
        ('more_better', _('More is Better')),
        ('equal_better', _('Equal is Better')),
    ]

    base_rule = models.OneToOneField(
        AutomationRule,
        on_delete=models.CASCADE,
        related_name='product_comparison_settings',
        verbose_name=_("Base Rule")
    )

    category = models.ForeignKey(
        ProductCategory,
        on_delete=models.CASCADE,
        related_name='comparison_settings',
        verbose_name=_("Product Category")
    )

    # Weights for different comparison attributes
    price_weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=1.0,
        verbose_name=_("Price Weight")
    )

    rating_weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.5,
        verbose_name=_("Rating Weight")
    )

    availability_weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.8,
        verbose_name=_("Availability Weight")
    )

    # Custom attributes comparison
    custom_attributes = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_("Custom Attributes"),
        help_text=_("JSON with custom attribute comparison settings")
    )

    class Meta:
        verbose_name = _("Product Comparison Settings")
        verbose_name_plural = _("Product Comparison Settings")

    def __str__(self):
        return f"Comparison Settings for {self.category.name}"

    def compare_products(self, products):
        """
        Compare products based on defined settings

        Args:
            products: List of products to compare

        Returns:
            list: Products sorted by comparison score
        """
        scored_products = []

        for product in products:
            # Skip products not in the chosen category
            if product.category != self.category:
                continue

            score = 0

            # Price score (lower is better by default)
            price_score = 0
            if len(products) > 1:
                max_price = max(p.base_price for p in products)
                min_price = min(p.base_price for p in products)
                price_range = max_price - min_price

                if price_range > 0:
                    normalized_price = (max_price - product.base_price) / price_range
                    price_score = normalized_price * float(self.price_weight)
            score += price_score

            # Add other scoring factors here

            scored_products.append((product, score))

        # Sort by score (from highest to lowest)
        scored_products.sort(key=lambda x: x[1], reverse=True)

        return scored_products


class ComparisonAttributeWeight(models.Model):
    """Model for defining weights of specific attributes in product comparison"""

    comparison_settings = models.ForeignKey(
        ProductComparisonSettings,
        on_delete=models.CASCADE,
        related_name='attribute_weights',
        verbose_name=_("Comparison Settings")
    )

    attribute_name = models.CharField(
        max_length=100,
        verbose_name=_("Attribute Name")
    )

    weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=1.0,
        verbose_name=_("Weight")
    )

    comparison_type = models.CharField(
        max_length=20,
        choices=ProductComparisonSettings.COMPARISON_TYPES,
        default='more_better',
        verbose_name=_("Comparison Type")
    )

    class Meta:
        verbose_name = _("Comparison Attribute Weight")
        verbose_name_plural = _("Comparison Attribute Weights")
        unique_together = ('comparison_settings', 'attribute_name')

    def __str__(self):
        return f"{self.attribute_name} ({self.weight}) for {self.comparison_settings.category.name}"