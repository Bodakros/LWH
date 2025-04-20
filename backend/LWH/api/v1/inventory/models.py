from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from backend.LWH.api.v1.products.models import Product
from backend.LWH.api.v1.warehouses.models import Warehouse, Stock
from decimal import Decimal


class InventoryItem(models.Model):
    """Модель для відстеження конкретних партій товарів на складі"""

    STATUS_CHOICES = [
        ('available', _('Доступно')),
        ('reserved', _('Зарезервовано')),
        ('damaged', _('Пошкоджено')),
        ('expired', _('Термін придатності вийшов')),
        ('in_transit', _('В дорозі')),
    ]

    UNIT_CHOICES = [
        ('pcs', _('Штуки')),
        ('kg', _('Кілограми')),
        ('g', _('Грами')),
        ('l', _('Літри')),
        ('ml', _('Мілілітри')),
        ('m', _('Метри')),
        ('cm', _('Сантиметри')),
        ('box', _('Коробки')),
        ('pallet', _('Палети')),
        ('other', _('Інше')),
    ]

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='inventory_items',
        verbose_name=_("Продукт")
    )
    stock = models.ForeignKey(
        Stock,
        on_delete=models.CASCADE,
        related_name='inventory_items',
        verbose_name=_("Комірка складу")
    )
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name='inventory_items',
        verbose_name=_("Склад"),
        editable=False  # Автоматично заповнюється з stock
    )
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='inventory_items',
        verbose_name=_("Продавець"),
        limit_choices_to={'is_seller': True}
    )
    quantity = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        verbose_name=_("Кількість")
    )
    unit = models.CharField(
        max_length=10,
        choices=UNIT_CHOICES,
        default='pcs',
        verbose_name=_("Одиниця виміру")
    )
    custom_unit = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_("Власна одиниця виміру"),
        help_text=_("Використовується, якщо одиниця виміру 'Інше'")
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='available',
        verbose_name=_("Статус")
    )
    batch_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_("Номер партії")
    )
    expiration_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_("Термін придатності")
    )
    received_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Дата надходження")
    )
    purchase_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name=_("Ціна закупівлі")
    )
    purchase_price_per_unit = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        blank=True,
        null=True,
        verbose_name=_("Ціна за одиницю")
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Створено"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Оновлено"))

    class Meta:
        verbose_name = _("Інвентарний запис")
        verbose_name_plural = _("Інвентарні записи")
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
        ('relocation', _('Переміщення')),
        ('consolidation', _('Консолідація')),
        ('quality_check', _('Перевірка якості')),
        ('stocktaking', _('Інвентаризація')),
        ('order_fulfillment', _('Виконання замовлення')),
        ('return_processing', _('Обробка повернення')),
        ('other', _('Інше')),
    ]

    source_stock = models.ForeignKey(
        Stock,
        on_delete=models.CASCADE,
        related_name='source_movements',
        verbose_name=_("Вихідна комірка")
    )
    destination_stock = models.ForeignKey(
        Stock,
        on_delete=models.CASCADE,
        related_name='destination_movements',
        verbose_name=_("Кінцева комірка")
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='movements',
        verbose_name=_("Продукт")
    )
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='inventory_movements',
        verbose_name=_("Продавець"),
        limit_choices_to={'is_seller': True}
    )
    quantity = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        verbose_name=_("Кількість")
    )
    unit = models.CharField(
        max_length=10,
        choices=InventoryItem.UNIT_CHOICES,
        default='pcs',
        verbose_name=_("Одиниця виміру")
    )
    custom_unit = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_("Власна одиниця виміру"),
        help_text=_("Використовується, якщо одиниця виміру 'Інше'")
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Час переміщення")
    )
    initiated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='initiated_movements',
        verbose_name=_("Ініційовано користувачем")
    )
    reason = models.CharField(
        max_length=20,
        choices=REASON_CHOICES,
        default='relocation',
        verbose_name=_("Причина переміщення")
    )
    source_inventory_item = models.ForeignKey(
        InventoryItem,
        on_delete=models.SET_NULL,
        null=True,
        related_name='outbound_movements',
        verbose_name=_("Вихідний інвентарний запис")
    )
    destination_inventory_item = models.ForeignKey(
        InventoryItem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inbound_movements',
        verbose_name=_("Кінцевий інвентарний запис")
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Примітки")
    )

    class Meta:
        verbose_name = _("Переміщення інвентарю")
        verbose_name_plural = _("Переміщення інвентарю")
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
        return (f"{self.product.name} - {self.quantity} {unit_display} від {self.source_stock} "
                f"до {self.destination_stock}")


class InventoryAudit(models.Model):
    """Модель для перевірки інвентарю - перевірка фактичної наявності"""

    RESOLUTION_CHOICES = [
        ('adjusted', _('Очікувана кількість')),
        ('investigated', _('Проведено перевірено')),
        ('ignored', _('Проігноровано')),
        ('error', _('Помилка при підрахунку')),
    ]

    inventory_item = models.ForeignKey(
        InventoryItem,
        on_delete=models.CASCADE,
        related_name='audits',
        verbose_name=_("Інвентарний запис")
    )
    expected_quantity = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        verbose_name=_("Очікувана кількість")
    )
    actual_quantity = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        verbose_name=_("Фактична кількість")
    )
    unit = models.CharField(
        max_length=10,
        choices=InventoryItem.UNIT_CHOICES,
        verbose_name=_("Одиниця виміру")
    )
    custom_unit = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_("Власна одиниця виміру")
    )
    discrepancy = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        verbose_name=_("Розбіжність"),
        editable=False  # Автоматично розраховується
    )
    audit_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Дата аудиту")
    )
    audited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='conducted_audits',
        verbose_name=_("Аудитор")
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Примітки")
    )
    resolved = models.BooleanField(
        default=False,
        verbose_name=_("Розбіжність вирішена")
    )
    resolution_type = models.CharField(
        max_length=15,
        choices=RESOLUTION_CHOICES,
        blank=True,
        null=True,
        verbose_name=_("Тип вирішення")
    )
    resolution_date = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_("Дата вирішення")
    )
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_audits',
        verbose_name=_("Вирішено користувачем")
    )
    resolution_notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Примітки щодо вирішення")
    )

    class Meta:
        verbose_name = _("Аудит інвентарю")
        verbose_name_plural = _("Аудити інвентарю")
        ordering = ['-audit_date']
        indexes = [
            models.Index(fields=['inventory_item']),
            models.Index(fields=['audit_date']),
            models.Index(fields=['resolved']),
        ]

    def __str__(self):
        unit_display = self.custom_unit if self.unit == 'other' and self.custom_unit else self.get_unit_display()
        return f"Аудит {self.inventory_item.product.name} - Розбіжність: {self.discrepancy} {unit_display}"

    def save(self, *args, **kwargs):
        # Автоматично обчислюємо розбіжність
        self.discrepancy = self.actual_quantity - self.expected_quantity

        # Копіюємо одиницю виміру з інвентарного запису, якщо не вказано
        if not self.unit and self.inventory_item:
            self.unit = self.inventory_item.unit
            self.custom_unit = self.inventory_item.custom_unit

        super().save(*args, **kwargs)


class ReceivingRecord(models.Model):
    """Модель для документування надходження товарів на склад"""

    STATUS_CHOICES = [
        ('pending', _('Очікується')),
        ('partially_received', _('Частково отримано')),
        ('fully_received', _('Повністю отримано')),
        ('cancelled', _('Скасовано')),
    ]

    supplier = models.CharField(max_length=200, verbose_name=_("Постачальник"))
    supplier_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='supplied_receivings',
        verbose_name=_("Постачальник (користувач)"),
        limit_choices_to={'is_seller': True}
    )
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name='receiving_records',
        verbose_name=_("Склад")
    )
    receipt_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Дата отримання")
    )
    reference_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_("Номер накладної")
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name=_("Статус")
    )
    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='processed_receivings',
        verbose_name=_("Прийняв")
    )
    expected_items_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Очікувана кількість позицій")
    )
    received_items_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Отримана кількість позицій")
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Примітки")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Створено")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Оновлено")
    )
    completed_date = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_("Дата завершення")
    )

    class Meta:
        verbose_name = _("Запис про надходження")
        verbose_name_plural = _("Записи про надходження")
        ordering = ['-receipt_date']
        indexes = [
            models.Index(fields=['warehouse']),
            models.Index(fields=['status']),
            models.Index(fields=['receipt_date']),
            models.Index(fields=['reference_number']),
        ]

    def __str__(self):
        return f"Надходження №{self.id} - {self.supplier} ({self.get_status_display()})"

    def update_status(self):
        """Оновлює статус надходження на основі отриманих товарів"""
        if self.expected_items_count == 0:
            return

        # Якщо всі позиції отримані повністю
        if self.received_items_count >= self.expected_items_count:
            self.status = 'fully_received'
            self.completed_date = timezone.now()
        # Якщо отримані деякі позиції
        elif self.received_items_count > 0:
            self.status = 'partially_received'

        self.save(update_fields=['status', 'completed_date'])


class ReceivingItem(models.Model):
    """Модель для деталізації отриманих товарів"""

    receiving_record = models.ForeignKey(
        ReceivingRecord,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_("Запис про надходження")
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='receiving_items',
        verbose_name=_("Продукт")
    )
    expected_quantity = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        verbose_name=_("Очікувана кількість")
    )
    received_quantity = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        default=0,
        verbose_name=_("Отримана кількість")
    )
    unit = models.CharField(
        max_length=10,
        choices=InventoryItem.UNIT_CHOICES,
        default='pcs',
        verbose_name=_("Одиниця виміру")
    )
    custom_unit = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_("Власна одиниця виміру"),
        help_text=_("Використовується, якщо одиниця виміру 'Інше'")
    )
    stock = models.ForeignKey(
        Stock,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='receiving_items',
        verbose_name=_("Комірка розміщення")
    )
    batch_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_("Номер партії")
    )
    expiration_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_("Термін придатності")
    )
    purchase_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Ціна закупівлі")
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Примітки")
    )
    inventory_item = models.ForeignKey(
        InventoryItem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='receiving_items',
        verbose_name=_("Створений інвентарний запис")
    )
    received_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_("Дата отримання")
    )
    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='received_items',
        verbose_name=_("Отримав")
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', _('Очікується')),
            ('received', _('Отримано')),
            ('partial', _('Частково отримано')),
            ('missing', _('Відсутній')),
            ('damaged', _('Пошкоджений')),
        ],
        default='pending',
        verbose_name=_("Статус")
    )

    class Meta:
        verbose_name = _("Елемент надходження")
        verbose_name_plural = _("Елементи надходження")
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
        # Оновлюємо статус елемента
        if self.received_quantity == self.expected_quantity:
            self.status = 'received'
        elif self.received_quantity > 0:
            self.status = 'partial'
        elif self.status == 'pending' and self.received_quantity == 0:
            pass  # Залишаємо статус "очікується"

        # Якщо цей елемент щойно отримали
        is_new_reception = False
        if self.pk:
            # Отримуємо попередню версію
            old_item = ReceivingItem.objects.get(pk=self.pk)
            if old_item.received_quantity != self.received_quantity and self.received_quantity > 0:
                is_new_reception = True
        else:
            if self.received_quantity > 0:
                is_new_reception = True

        # Якщо це нове отримання, оновлюємо дату отримання
        if is_new_reception:
            self.received_at = timezone.now()

        super().save(*args, **kwargs)

        # Оновлюємо лічильник отриманих елементів у батьківському записі
        self.receiving_record.received_items_count = ReceivingItem.objects.filter(
            receiving_record=self.receiving_record,
            status__in=['received', 'partial']
        ).count()

        # Оновлюємо статус батьківського запису
        self.receiving_record.update_status()

        