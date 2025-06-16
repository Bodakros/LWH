from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from decimal import Decimal

from ..products.models import Product
from ..warehouses.models import Stock, Warehouse


class InventoryItem(models.Model):
    """Модель для відстеження конкретних партій товарів на складі"""

    STATUS_CHOICES = [
        ('available', _('Available')),
        ('reserved', _('Reserved')),
        ('damaged', _('Damaged')),
        ('expired', _('Expired')),
        ('in_transit', _('In transit')),
    ]

    UNIT_CHOICES = [
        ('pcs', _('Pieces')),
        ('kg', _('Kilograms')),
        ('g', _('Grams')),
        ('l', _('Liter')),
        ('ml', _('Milliliters')),
        ('m', _('Metres')),
        ('cm', _('Centimeters')),
        ('box', _('Boxes')),
        ('pallet', _('Pallets')),
        ('other', _('Other')),
    ]

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='inventory_items',
        verbose_name=_("Product")
    )
    stock = models.ForeignKey(
        Stock,
        on_delete=models.CASCADE,
        related_name='inventory_items',
        verbose_name=_("Stock")
    )
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name='inventory_items',
        verbose_name=_("Warehouse"),
        editable=False  # Автоматично заповнюється з stock
    )
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='inventory_items',
        verbose_name=_("Seller"),
        limit_choices_to={'is_seller': True}
    )
    quantity = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        verbose_name=_("Quantity")
    )
    unit = models.CharField(
        max_length=10,
        choices=UNIT_CHOICES,
        default='pcs',
        verbose_name=_("Unit of measurement")
    )
    custom_unit = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_("Custom unit of measurement"),
        help_text=_("Used if unit of measure is 'Other'")
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='available',
        verbose_name=_("Status")
    )
    batch_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_("Batch number")
    )
    expiration_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_("Expiration date")
    )
    received_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Receiving date")
    )
    purchase_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name=_("Purchase price")
    )
    purchase_price_per_unit = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        blank=True,
        null=True,
        verbose_name=_("Price per unit")
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Створено"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Оновлено"))

    class Meta:
        verbose_name = _("Inventory record")
        verbose_name_plural = _("Inventory record")
        ordering = ['-received_date']
        indexes = [
            models.Index(fields=['product', 'stock']),
            models.Index(fields=['status']),
            models.Index(fields=['batch_number']),
            models.Index(fields=['expiration_date']),
            models.Index(fields=['unit']),
        ]

    def __str__(self):
        unit_display = self.custom_unit if self.unit == 'other' and self.custom_unit else self.get_unit_display()
        return f"{self.product.name} - {self.quantity} {unit_display} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        # Автоматично встановлюємо warehouse з stock
        if self.stock and not self.warehouse_id:
            self.warehouse = self.stock.warehouse

        # Автоматично обчислюємо ціну за одиницю, якщо вона не вказана
        if self.purchase_price and self.quantity and not self.purchase_price_per_unit:
            self.purchase_price_per_unit = self.purchase_price / self.quantity

        super().save(*args, **kwargs)


class InventoryMovement(models.Model):
    """Модель для відстеження переміщення товарів між комірками"""

    REASON_CHOICES = [
        ('relocation', _('Relocation')),
        ('consolidation', _('Consolidation')),
        ('quality_check', _('Quality check')),
        ('stocktaking', _('Stocktaking')),
        ('order_fulfillment', _('Order fulfillment')),
        ('return_processing', _('Return processing')),
        ('other', _('Other')),
    ]

    source_stock = models.ForeignKey(
        Stock,
        on_delete=models.CASCADE,
        related_name='source_movements',
        verbose_name=_("Output stock")
    )
    destination_stock = models.ForeignKey(
        Stock,
        on_delete=models.CASCADE,
        related_name='destination_movements',
        verbose_name=_("End stock")
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='movements',
        verbose_name=_("Product")
    )
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='inventory_movements',
        verbose_name=_("Seller"),
        limit_choices_to={'is_seller': True}
    )
    quantity = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        verbose_name=_("Quantity")
    )
    unit = models.CharField(
        max_length=10,
        choices=InventoryItem.UNIT_CHOICES,
        default='pcs',
        verbose_name=_("Unit of measurement")
    )
    custom_unit = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_("Custom unit of measurement"),
        help_text=_("Used if unit of measure is 'Other'")
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Time to move")
    )
    initiated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='initiated_movements',
        verbose_name=_("User-initiated")
    )
    reason = models.CharField(
        max_length=20,
        choices=REASON_CHOICES,
        default='relocation',
        verbose_name=_("The reason for the move")
    )
    source_inventory_item = models.ForeignKey(
        InventoryItem,
        on_delete=models.SET_NULL,
        null=True,
        related_name='outbound_movements',
        verbose_name=_("Outgoing inventory record")
    )
    destination_inventory_item = models.ForeignKey(
        InventoryItem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inbound_movements',
        verbose_name=_("Closing inventory record")
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Notes")
    )

    class Meta:
        verbose_name = _("Moving inventory")
        verbose_name_plural = _("Moving inventory")
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['source_stock']),
            models.Index(fields=['destination_stock']),
            models.Index(fields=['product']),
            models.Index(fields=['seller']),
            models.Index(fields=['timestamp']),
        ]

    def __str__(self):
        unit_display = self.custom_unit if self.unit == 'other' and self.custom_unit else self.get_unit_display()
        return (f"{self.product.name} - {self.quantity} {unit_display} from {self.source_stock} "
                f"to {self.destination_stock}")


class InventoryAudit(models.Model):
    """Модель для перевірки інвентарю - перевірка фактичної наявності"""

    RESOLUTION_CHOICES = [
        ('adjusted', _('Expected quantity')),
        ('investigated', _('Checked')),
        ('ignored', _('Ignored')),
        ('error', _('Calculation error')),
    ]

    inventory_item = models.ForeignKey(
        InventoryItem,
        on_delete=models.CASCADE,
        related_name='audits',
        verbose_name=_("Inventory record")
    )
    expected_quantity = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        verbose_name=_("Expected quantity")
    )
    actual_quantity = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        verbose_name=_("Actual quantity")
    )
    unit = models.CharField(
        max_length=10,
        choices=InventoryItem.UNIT_CHOICES,
        verbose_name=_("Unit of measurement")
    )
    custom_unit = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_("Custom unit of measurement")
    )
    discrepancy = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        verbose_name=_("Divergence"),
        editable=False
    )
    audit_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Audit date")
    )
    audited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='conducted_audits',
        verbose_name=_("Auditor")
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Notes")
    )
    resolved = models.BooleanField(
        default=False,
        verbose_name=_("Disagreement resolved")
    )
    resolution_type = models.CharField(
        max_length=15,
        choices=RESOLUTION_CHOICES,
        blank=True,
        null=True,
        verbose_name=_("Type of solution")
    )
    resolution_date = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_("Resolution date")
    )
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_audits',
        verbose_name=_("User solved")
    )
    resolution_notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Solution Notes")
    )

    class Meta:
        verbose_name = _("Inventory audit")
        verbose_name_plural = _("Inventory audit")
        ordering = ['-audit_date']
        indexes = [
            models.Index(fields=['inventory_item']),
            models.Index(fields=['audit_date']),
            models.Index(fields=['resolved']),
        ]

    def __str__(self):
        unit_display = self.custom_unit if self.unit == 'other' and self.custom_unit else self.get_unit_display()
        return f"Audit {self.inventory_item.product.name} - Divergence: {self.discrepancy} {unit_display}"

    def save(self, *args, **kwargs):
        # Автоматично обчислюємо розбіжність
        self.discrepancy = self.actual_quantity - self.expected_quantity

        # Копіюємо одиницю виміру з інвентарного запису, якщо не вказано
        if not self.unit and self.inventory_item:
            self.unit = self.inventory_item.unit
            self.custom_unit = self.inventory_item.custom_unit

        super().save(*args, **kwargs)


class ReceivingRecord(models.Model):
    """Model for documenting goods receipts at the warehouse"""

    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('partially_received', _('Partially Received')),
        ('fully_received', _('Fully Received')),
        ('cancelled', _('Cancelled')),
    ]

    supplier = models.CharField(max_length=200, verbose_name=_("Supplier"))
    supplier_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='supplied_receivings',
        verbose_name=_("Supplier (user)"),
        limit_choices_to={'is_seller': True}
    )
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name='receiving_records',
        verbose_name=_("Warehouse")
    )
    receipt_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Receipt Date")
    )
    reference_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_("Reference Number")
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name=_("Status")
    )
    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='processed_receivings',
        verbose_name=_("Received By")
    )
    expected_items_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Expected Items Count")
    )
    received_items_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Received Items Count")
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Notes")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created At")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Updated At")
    )
    completed_date = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_("Completion Date")
    )

    class Meta:
        verbose_name = _("Receiving Record")
        verbose_name_plural = _("Receiving Records")
        ordering = ['-receipt_date']
        indexes = [
            models.Index(fields=['warehouse']),
            models.Index(fields=['status']),
            models.Index(fields=['receipt_date']),
            models.Index(fields=['reference_number']),
        ]

    def __str__(self):
        return f"Receipt #{self.id} - {self.supplier} ({self.get_status_display()})"

    def update_status(self):
        # Updating of receiving status
        if self.expected_items_count == 0:
            return

        if self.received_items_count >= self.expected_items_count:
            self.status = 'fully_received'
            self.completed_date = timezone.now()
        elif self.received_items_count > 0:
            self.status = 'partially_received'

        self.save(update_fields=['status', 'completed_date'])


class ReceivingItem(models.Model):
    """Model for detailing received goods"""

    receiving_record = models.ForeignKey(
        ReceivingRecord,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_("Receiving Record")
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='receiving_items',
        verbose_name=_("Product")
    )
    expected_quantity = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        verbose_name=_("Expected Quantity")
    )
    received_quantity = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        default=0,
        verbose_name=_("Received Quantity")
    )
    unit = models.CharField(
        max_length=10,
        choices=InventoryItem.UNIT_CHOICES,
        default='pcs',
        verbose_name=_("Unit of Measure")
    )
    custom_unit = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_("Custom Unit of Measure"),
        help_text=_("Used if unit is 'Other'")
    )
    stock = models.ForeignKey(
        Stock,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='receiving_items',
        verbose_name=_("Stock Location")
    )
    batch_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_("Batch Number")
    )
    expiration_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_("Expiration Date")
    )
    purchase_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Purchase Price")
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Notes")
    )
    inventory_item = models.ForeignKey(
        InventoryItem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='receiving_items',
        verbose_name=_("Created Inventory Item")
    )
    received_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_("Receipt Date")
    )
    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='received_items',
        verbose_name=_("Received By")
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', _('Pending')),
            ('received', _('Received')),
            ('partial', _('Partially Received')),
            ('missing', _('Missing')),
            ('damaged', _('Damaged')),
        ],
        default='pending',
        verbose_name=_("Status")
    )

    class Meta:
        verbose_name = _("Receiving Item")
        verbose_name_plural = _("Receiving Items")
        ordering = ['receiving_record', 'id']
        indexes = [
            models.Index(fields=['receiving_record']),
            models.Index(fields=['product']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        unit_display = self.custom_unit if self.unit == 'other' and self.custom_unit else self.get_unit_display()
        return f"{self.product.name} - {self.received_quantity}/{self.expected_quantity} {unit_display}"

    def save(self, *args, **kwargs):
        # Update item status
        if self.received_quantity == self.expected_quantity:
            self.status = 'received'
        elif self.received_quantity > 0:
            self.status = 'partial'
        elif self.status == 'pending' and self.received_quantity == 0:
            pass  # Keep status as "pending"

        # If this item was just received
        is_new_reception = False
        if self.pk:
            # Get previous version
            old_item = ReceivingItem.objects.get(pk=self.pk)
            if old_item.received_quantity != self.received_quantity and self.received_quantity > 0:
                is_new_reception = True
        else:
            if self.received_quantity > 0:
                is_new_reception = True

        # If this is a new reception, update the receipt date
        if is_new_reception:
            self.received_at = timezone.now()

        super().save(*args, **kwargs)

        # Update the received items counter in the parent record
        self.receiving_record.received_items_count = ReceivingItem.objects.filter(
            receiving_record=self.receiving_record,
            status__in=['received', 'partial']
        ).count()

        # Update the status of the parent record
        self.receiving_record.update_status()

