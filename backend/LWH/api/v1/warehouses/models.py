from django.db import models
from django.conf import settings
from django.db.models import Sum, Case, When, F, Value, IntegerField


# Create your models here.

class Address(models.Model):
    LOCALITY_TYPE_CHOICES = [
        ('city', 'Місто'),
        ('village', 'Село'),
        ('urban_settlement', 'Селище міського типу'),
        ('settlement', 'Селище'),
        ('district', 'Район у місті'),
        ('other', 'Інше'),
    ]

    country = models.CharField(max_length=100, verbose_name="Країна", db_index=True, default="Україна")
    oblast = models.CharField(max_length=100, verbose_name="Область", blank=True, null=True,
                              help_text="Наприклад: Київська, Львівська, Харківська")
    locality_type = models.CharField(
        max_length=20,
        choices=LOCALITY_TYPE_CHOICES,
        default='city',
        verbose_name="Тип населеного пункту"
    )
    raion = models.CharField(max_length=100, verbose_name="Район", blank=True, null=True,
                             help_text="Адміністративний район в області")
    locality = models.CharField(max_length=100, verbose_name="Населений пункт")
    street_address = models.CharField(max_length=255, verbose_name="Вулиця, будинок")
    postal_code = models.CharField(max_length=20, verbose_name="Поштовий індекс", db_index=True)
    additional_info = models.TextField(blank=True, null=True, verbose_name="Додаткові примітки (напр., вхід)")

    def get_full_street(self):
        """Повертає повну назву вулиці з типом"""
        if not self.street:
            return ""
        if self.street_type:
            return f"{self.street_type} {self.street}"
        return self.street

    def __str__(self):
        locality_prefix = self.get_locality_type_display()

        address_parts = [
            self.country,
            f"{self.oblast} область" if self.oblast else None,
            f"{self.raion} район" if self.raion else None,
            f"{self.hromada} ТГ" if self.hromada else None,
            f"{locality_prefix} {self.locality}",
            self.get_full_street() if self.get_full_street() else None,
            f"буд. {self.building}"
        ]
        # Прибираємо пусті елементи
        formatted_address = ", ".join(filter(None, address_parts))
        return formatted_address

    class Meta:
        verbose_name = "Адреса складу"
        verbose_name_plural = "Адреси складів"
        ordering = ['country', 'oblast', 'raion', 'locality']


class Warehouse(models.Model):
    name = models.CharField(max_length=200, unique=True, verbose_name="Назва складу", db_index=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='owned_warehouses',
        verbose_name="Власник складу",
        limit_choices_to={'is_owner': True}
    )
    address = models.OneToOneField(
        'Address',
        on_delete=models.CASCADE,
        related_name='warehouse'
    )

    ## Віртуальний тур
    # virtual_tour_url = models.URLField(
    #     blank=True,
    #     null=True,
    #     verbose_name="URL віртуального туру"
    # )

    @property
    def total_capacity(self):
        """Обчислює загальну ємність складу"""
        total = self.stocks.aggregate(
            total=Sum('capacity')
        )['total'] or 0
        return total

    @property
    def available_capacity(self):
        """Обчислює доступну ємність складу"""
        available = self.stocks.aggregate(
            available=Sum(
                Case(
                    When(is_occupied=False, then=F('capacity')),
                    default=Value(0),
                    output_field=IntegerField()
                )
            )
        )['available'] or 0
        return available

    rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True,
                                 verbose_name="Рейтинг (1-5)")  # Потребує механізму оновлення
    operating_hours = models.CharField(max_length=100, blank=True, verbose_name="Години роботи")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата оновлення")

    class Meta:
        verbose_name = "Склад"
        verbose_name_plural = "Склади"
        ordering = ['name']

    def __str__(self):
        return self.name


class Stock(models.Model):
    """Модель для зберігання інформації про комірки в складі"""
    warehouse = models.ForeignKey(
        'Warehouse',
        on_delete=models.CASCADE,
        related_name='stocks'
    )
    name = models.CharField(max_length=100)
    capacity = models.PositiveIntegerField(help_text="Ємність комірки")
    length = models.FloatField(help_text="Довжина у метрах")
    width = models.FloatField(help_text="Ширина у метрах")
    height = models.FloatField(help_text="Висота у метрах")
    is_occupied = models.BooleanField(default=False)
    location_code = models.CharField(max_length=50, unique=True, help_text="Унікальний код локації комірки")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def volume(self):
        """Обчислює об'єм комірки"""
        return self.length * self.width * self.height

    def __str__(self):
        return f"{self.name} ({self.location_code})"

    class Meta:
        verbose_name = "Комірка складу"
        verbose_name_plural = "Комірки складу"
        ordering = ['warehouse', 'location_code']


class WarehouseImage(models.Model):
    """Модель для зберігання зображень складу"""
    warehouse = models.ForeignKey(
        'Warehouse',
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name="Склад"
    )
    image = models.ImageField(
        upload_to='warehouse_images/',
        verbose_name="Зображення"
    )
    title = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Назва зображення"
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Опис зображення"
    )
    is_main = models.BooleanField(
        default=False,
        verbose_name="Головне зображення"
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Порядок відображення"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Зображення складу"
        verbose_name_plural = "Зображення складів"
        ordering = ['warehouse', 'order', '-created_at']

    def __str__(self):
        return f"Зображення {self.id} для складу {self.warehouse.name}"

    def save(self, *args, **kwargs):
        # Якщо це головне зображення, знімаємо прапорець "головне" з інших зображень цього складу
        if self.is_main:
            WarehouseImage.objects.filter(
                warehouse=self.warehouse,
                is_main=True
            ).exclude(pk=self.pk).update(is_main=False)
        super().save(*args, **kwargs)


class StockImage(models.Model):
    """Модель для зберігання зображень комірки"""
    stock = models.ForeignKey(
        'Stock',
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name="Комірка"
    )
    image = models.ImageField(
        upload_to='stock_images/',
        verbose_name="Зображення"
    )
    title = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Назва зображення"
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Опис зображення"
    )
    is_main = models.BooleanField(
        default=False,
        verbose_name="Головне зображення"
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Порядок відображення"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Зображення комірки"
        verbose_name_plural = "Зображення комірок"
        ordering = ['stock', 'order', '-created_at']

    def __str__(self):
        return f"Зображення {self.id} для комірки {self.stock.name}"

    def save(self, *args, **kwargs):
        # Якщо це головне зображення, знімаємо прапорець "головне" з інших зображень цієї комірки
        if self.is_main:
            StockImage.objects.filter(
                stock=self.stock,
                is_main=True
            ).exclude(pk=self.pk).update(is_main=False)
        super().save(*args, **kwargs)
