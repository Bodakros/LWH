"""
Asynchronous tasks for automation module.
These tasks are executed in the background using Celery.
Tasks can be enabled or disabled through the AUTOMATION_SETTINGS in settings.py.
"""
from django.utils import timezone
from django.db.models import F, Sum, Q
from django.conf import settings
from django.core.mail import send_mail
from celery import shared_task

from .models import RestockRule, AutomationRule
from .services import check_restock_needs


def is_task_enabled(task_name):
    """
    Check if a specific background task is enabled in settings

    Args:
        task_name: Name of the task to check

    Returns:
        bool: True if the task is enabled, False otherwise
    """
    # Check master switch first
    if not getattr(settings, 'AUTOMATION_SETTINGS', {}).get('ENABLE_BACKGROUND_TASKS', False):
        return False

    # Check specific task setting
    task_settings = getattr(settings, 'AUTOMATION_SETTINGS', {}).get('TASKS', {}).get(task_name, {})
    return task_settings.get('enabled', False)


@shared_task
def check_all_inventory_levels():
    """
    Periodic task to check inventory levels for all products and generate restock alerts.
    This is scheduled to run at regular intervals.
    """
    # Check if this task is enabled
    if not is_task_enabled('inventory_check'):
        print("Inventory check task is disabled in settings")
        return

    print("Running inventory check task...")

    # Get active restock rules
    active_rules = RestockRule.objects.filter(
        base_rule__is_active=True,
        auto_reorder=True
    )

    for rule in active_rules:
        # Update last check date
        rule.last_check_date = timezone.now()
        rule.save(update_fields=['last_check_date'])

        # Check inventory levels
        result = rule.check_inventory_levels()

        if result['needs_restock']:
            # Handle restock notification
            handle_restock_notification.delay(rule.id, result)

            # If auto_reorder is enabled, create restock order
            if rule.auto_reorder:
                create_restock_order.delay(rule.id, result)

    return f"Checked inventory levels for {active_rules.count()} active restock rules"


@shared_task
def handle_restock_notification(rule_id, result):
    """
    Send notification about low inventory levels

    Args:
        rule_id: ID of RestockRule that triggered the notification
        result: Result of inventory check
    """
    try:
        rule = RestockRule.objects.get(id=rule_id)
    except RestockRule.DoesNotExist:
        print(f"RestockRule with id {rule_id} not found")
        return

    if not rule.notify_owner:
        return

    # Get product and seller information
    product = rule.product
    seller = product.seller

    # Prepare notification message
    warehouses_needing_restock = [
        f"- {result['warehouses'][wh_id]['warehouse_name']}: "
        f"Current: {result['warehouses'][wh_id]['current_quantity']}, "
        f"Minimum: {result['warehouses'][wh_id]['minimum_quantity']}"
        for wh_id in result['warehouses']
        if result['warehouses'][wh_id]['needs_restock']
    ]

    warehouses_text = "\n".join(warehouses_needing_restock)

    # Prepare email message
    subject = f"Low inventory alert: {product.name}"
    message = (
        f"Low inventory alert for product: {product.name} (SKU: {product.sku})\n\n"
        f"The following warehouses need restocking:\n"
        f"{warehouses_text}\n\n"
        f"Suggested reorder quantity: {rule.reorder_quantity}\n\n"
        f"This is an automated message from the LWH system."
    )

    # Send email if email sending is enabled
    email_setting = getattr(settings, 'EMAIL_ENABLED', True)
    if email_setting and seller.email:
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [seller.email],
                fail_silently=False,
            )
            return f"Sent restock notification email to {seller.email}"
        except Exception as e:
            # Log the error but continue processing
            error_msg = f"Error sending restock notification email: {e}"
            print(error_msg)
            return error_msg
    else:
        # Just log the notification for now
        log_msg = f"Notification would be sent to {seller.username}: {subject}"
        print(log_msg)
        print(message)
        return log_msg


@shared_task
def create_restock_order(rule_id, result):
    """
    Create a restock order based on inventory levels

    Args:
        rule_id: ID of RestockRule that triggered the restock
        result: Result of inventory check
    """
    try:
        rule = RestockRule.objects.get(id=rule_id)
    except RestockRule.DoesNotExist:
        print(f"RestockRule with id {rule_id} not found")
        return

    # In a real implementation, this would create an order in the ordering system
    # For now, we'll just mark that a restock was initiated
    rule.last_restock_date = timezone.now()
    rule.save(update_fields=['last_restock_date'])

    # Here you would typically:
    # 1. Create a purchase order
    # 2. Send it to the preferred supplier if one is set
    # 3. Track the order status
    # Since we don't have those models yet, we'll just log the action
    log_msg = f"Automatic restock initiated for product {rule.product.name} (Rule: {rule.base_rule.name})"
    print(log_msg)
    return log_msg


@shared_task
def update_product_prices():
    """
    Periodic task to update product prices based on pricing rules
    """
    # Check if this task is enabled
    if not is_task_enabled('price_update'):
        print("Price update task is disabled in settings")
        return

    print("Running price update task...")

    # Get active pricing rules
    active_rules = AutomationRule.objects.filter(
        rule_type='pricing',
        is_active=True
    ).select_related('pricing_rule')

    updated_count = 0

    for rule in active_rules:
        pricing_rule = rule.pricing_rule

        # Get applicable products
        products = []

        # Add products from specific product selections
        if pricing_rule.applies_to_products.exists():
            products.extend(pricing_rule.applies_to_products.all())

        # Add products from categories
        if pricing_rule.product_categories.exists():
            from ..products.models import Product
            for category in pricing_rule.product_categories.all():
                cat_products = Product.objects.filter(category=category)
                products.extend(cat_products)

        # Remove duplicates
        products = list(set(products))

        # Update prices for each product
        for product in products:
            # Only adjust prices for products owned by the rule creator
            if product.seller != rule.created_by:
                continue

            # Get the current base price
            base_price = product.base_price

            # Calculate the new price
            adjusted_price = pricing_rule.calculate_price_adjustment(
                product,
                base_price
            )

            # Update the product price if different
            if adjusted_price != base_price:
                # In a real implementation, you might want to log this change
                # or create a price history record
                product.base_price = adjusted_price
                product.save(update_fields=['base_price'])
                updated_count += 1

                print(f"Updated price for {product.name} from "
                      f"{base_price} to {adjusted_price} using rule: {rule.base_rule.name}")

    return f"Updated prices for {updated_count} products using {active_rules.count()} active pricing rules"


@shared_task
def analyze_product_comparisons():
    """
    Periodic task to analyze and compare products from different sellers
    """
    # Check if this task is enabled
    if not is_task_enabled('product_comparison'):
        print("Product comparison task is disabled in settings")
        return

    print("Running product comparison analysis task...")

    # Get active comparison settings
    active_rules = AutomationRule.objects.filter(
        rule_type='product_comparison',
        is_active=True
    ).select_related('product_comparison_settings')

    analysis_count = 0

    for rule in active_rules:
        comparison_settings = rule.product_comparison_settings
        category = comparison_settings.category
        user = rule.created_by

        # Find all products in this category
        from ..products.models import Product
        products = Product.objects.filter(category=category)

        # Skip if not enough products to compare
        if products.count() < 2:
            continue

        # Use the comparison settings to compare products
        scored_products = comparison_settings.compare_products(products)
        analysis_count += 1

        # If the user is a seller, analyze their products compared to others
        if user.is_seller:
            user_products = [p for p, score in scored_products if p.seller == user]

            if user_products:
                # Generate some insights here
                # (This would typically send a report to the seller)
                print(f"Generated comparison report for {user.username}'s products in {category.name}")

    return f"Completed product comparison analysis for {analysis_count} categories"

@shared_task
def run_task_by_name(task_name):
    """
    Run a specific task by name
    This allows manually triggering tasks from the API

    Args:
        task_name: Name of the task to run
    """
    if task_name == 'inventory_check':
        return check_all_inventory_levels()
    elif task_name == 'price_update':
        return update_product_prices()
    elif task_name == 'product_comparison':
        return analyze_product_comparisons()
    else:
        return f"Unknown task: {task_name}"

