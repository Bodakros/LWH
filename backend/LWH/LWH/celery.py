import os
from celery import Celery
from ..api.v1.automation.tasks import (
    check_all_inventory_levels,
    update_product_prices,
    analyze_product_comparisons
)
# Set the default Django settings module for the 'celery' program
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LWH.settings')

# Create the celery app
app = Celery('LWH')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs
app.autodiscover_tasks()

# Define the dynamic beat schedule based on settings
@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    """
    Set up periodic tasks dynamically based on settings
    """
    from django.conf import settings

    automation_settings = getattr(settings, 'AUTOMATION_SETTINGS', {})

    # Check if background tasks are globally enabled
    if not automation_settings.get('ENABLE_BACKGROUND_TASKS', False):
        return

    # Get task settings
    tasks_config = automation_settings.get('TASKS', {})

    # # Import tasks here to avoid circular imports
    # from api.v1.automation.tasks import (
    #     check_all_inventory_levels,
    #     update_product_prices,
    #     analyze_product_comparisons
    # )

    # Configure inventory check task
    inventory_check = tasks_config.get('inventory_check', {})
    if inventory_check.get('enabled', False):
        sender.add_periodic_task(
            inventory_check.get('schedule', 3600),  # Default: 1 hour
            check_all_inventory_levels.s(),
            name='inventory-check'
        )

    # Configure price update task
    price_update = tasks_config.get('price_update', {})
    if price_update.get('enabled', False):
        sender.add_periodic_task(
            price_update.get('schedule', 86400),  # Default: 1 day
            update_product_prices.s(),
            name='price-update'
        )

    # Configure product comparison task
    product_comparison = tasks_config.get('product_comparison', {})
    if product_comparison.get('enabled', False):
        sender.add_periodic_task(
            product_comparison.get('schedule', 43200),  # Default: 12 hours
            analyze_product_comparisons.s(),
            name='product-comparison'
        )
