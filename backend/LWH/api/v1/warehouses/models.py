from django.db import models
from django.conf import settings
from django.db.models import Sum, Case, When, F, Value, IntegerField


# Create your models here.

class Address(models.Model):
    LOCALITY_TYPE_CHOICES = [
        ('city', 'City'),
        ('village', 'Village'),
        ('urban_settlement', 'Urban settlement'),
        ('settlement', 'Settlement'),
        ('district', 'City district'),
        ('other', 'Other'),
    ]

    country = models.CharField(max_length=100, verbose_name="Country", db_index=True, default="Ukraine")
    oblast = models.CharField(max_length=100, verbose_name="Region", blank=True, null=True,
                              help_text="For example: Kyiv, Lviv, Kharkiv")
    locality_type = models.CharField(
        max_length=20,
        choices=LOCALITY_TYPE_CHOICES,
        default='city',
        verbose_name="Settlement type"
    )
    raion = models.CharField(max_length=100, verbose_name="District", blank=True, null=True,
                             help_text="Administrative district in the region")
    locality = models.CharField(max_length=100, verbose_name="Settlement")
    street_address = models.CharField(max_length=255, verbose_name="Street, building")
    postal_code = models.CharField(max_length=20, verbose_name="Postal code", db_index=True)
    additional_info = models.TextField(blank=True, null=True, verbose_name="Additional notes (e.g., entrance)")

    def get_full_street(self):
        """Returns the full street name with type"""
        if not self.street:
            return ""
        if self.street_type:
            return f"{self.street_type} {self.street}"
        return self.street

    def __str__(self):
        locality_prefix = self.get_locality_type_display()

        address_parts = [
            self.country,
            f"{self.oblast} region" if self.oblast else None,
            f"{self.raion} district" if self.raion else None,
            f"{locality_prefix} {self.locality}",
            self.street_address,
        ]
        # Remove empty elements
        formatted_address = ", ".join(filter(None, address_parts))
        return formatted_address

    class Meta:
        verbose_name = "Warehouse address"
        verbose_name_plural = "Warehouse addresses"
        ordering = ['country', 'oblast', 'raion', 'locality']


class Warehouse(models.Model):
    name = models.CharField(max_length=200, unique=True, verbose_name="Warehouse name", db_index=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='owned_warehouses',
        verbose_name="Warehouse owner"
    )
    address = models.OneToOneField(
        'Address',
        on_delete=models.CASCADE,
        related_name='warehouse'
    )

    ## Virtual tour
    # virtual_tour_url = models.URLField(
    #     blank=True,
    #     null=True,
    #     verbose_name="Virtual tour URL"
    # )

    @property
    def total_capacity(self):
        """The amount of general capacity"""
        total = self.stocks.aggregate(
            total=Sum('capacity')
        )['total'] or 0
        return total

    @property
    def available_capacity(self):
        """The amount of available capacity"""
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
                                 verbose_name="Rating (1-5)")  # Requires update mechanism
    operating_hours = models.CharField(max_length=100, blank=True, verbose_name="Operating hours")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creation date")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Update date")

    class Meta:
        verbose_name = "Warehouse"
        verbose_name_plural = "Warehouses"
        ordering = ['name']

    def __str__(self):
        return self.name


class Stock(models.Model):
    """Model for storing information about storage units in the warehouse"""
    warehouse = models.ForeignKey(
        'Warehouse',
        on_delete=models.CASCADE,
        related_name='stocks'
    )
    name = models.CharField(max_length=100)
    capacity = models.PositiveIntegerField(help_text="Storage unit capacity")
    length = models.FloatField(help_text="Length in meters")
    width = models.FloatField(help_text="Width in meters")
    height = models.FloatField(help_text="Height in meters")
    is_occupied = models.BooleanField(default=False)
    location_code = models.CharField(max_length=50, unique=True, help_text="Unique location code for the storage unit")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def volume(self):
        if self.length and self.width and self.height:
            return self.length * self.width * self.height
        return None

    def __str__(self):
        return f"{self.name} ({self.location_code})"

    class Meta:
        verbose_name = "Storage unit"
        verbose_name_plural = "Storage units"
        ordering = ['warehouse', 'location_code']


class WarehouseImage(models.Model):
    """Model for storing warehouse images"""
    warehouse = models.ForeignKey(
        'Warehouse',
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name="Warehouse"
    )
    image = models.ImageField(
        upload_to='warehouse_images/',
        verbose_name="Image"
    )
    title = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Image title"
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Image description"
    )
    is_main = models.BooleanField(
        default=False,
        verbose_name="Main image"
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Display order"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Warehouse image"
        verbose_name_plural = "Warehouse images"
        ordering = ['warehouse', 'order', '-created_at']

    def __str__(self):
        return f"Image {self.id} for warehouse {self.warehouse.name}"

    def save(self, *args, **kwargs):
        # For changing the main image
        if self.is_main:
            WarehouseImage.objects.filter(
                warehouse=self.warehouse,
                is_main=True
            ).exclude(pk=self.pk).update(is_main=False)
        super().save(*args, **kwargs)


class StockImage(models.Model):
    """Model for storing storage unit images"""
    stock = models.ForeignKey(
        'Stock',
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name="Storage unit"
    )
    image = models.ImageField(
        upload_to='stock_images/',
        verbose_name="Image"
    )
    title = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Image title"
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Image description"
    )
    is_main = models.BooleanField(
        default=False,
        verbose_name="Main image"
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Display order"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Storage unit image"
        verbose_name_plural = "Storage unit images"
        ordering = ['stock', 'order', '-created_at']

    def __str__(self):
        return f"Image {self.id} for storage unit {self.stock.name}"

    def save(self, *args, **kwargs):
        # If this is the main image, remove the "main" flag from other images of this storage unit
        if self.is_main:
            StockImage.objects.filter(
                stock=self.stock,
                is_main=True
            ).exclude(pk=self.pk).update(is_main=False)
        super().save(*args, **kwargs)