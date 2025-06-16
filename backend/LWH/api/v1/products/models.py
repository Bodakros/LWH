from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.conf import settings
import uuid
import json


class ProductCategory(models.Model):
    """Model for product categories with hierarchy support"""
    name = models.CharField(max_length=255, verbose_name=_("Category Name"))
    slug = models.SlugField(max_length=255, unique=True, verbose_name=_("URL-slug"))
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name=_("Parent Category")
    )
    description = models.TextField(blank=True, verbose_name=_("Category Description"))
    image = models.ImageField(upload_to='category_images/', blank=True, null=True,
                              verbose_name=_("Category Image"))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated"))

    class Meta:
        verbose_name = _("Product Category")
        verbose_name_plural = _("Product Categories")
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class TaxType(models.Model):
    """Model for tax types (e.g., VAT, tobacco excise, etc.)"""
    code = models.CharField(max_length=20, unique=True, verbose_name=_("Tax Code"))
    name = models.CharField(max_length=100, verbose_name=_("Tax Type Name"))
    description = models.TextField(blank=True, verbose_name=_("Tax Description"))
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated"))

    class Meta:
        verbose_name = _("Tax Type")
        verbose_name_plural = _("Tax Types")
        ordering = ['code', 'name']

    def __str__(self):
        return f"{self.name} ({self.code})"


class TaxRate(models.Model):
    """Model for storing tax rates"""
    TAX_CALCULATION_TYPES = [
        ('percentage', _('Percentage of value')),
        ('fixed', _('Fixed amount')),
        ('quantity_based', _('Quantity-based')),
        ('formula_based', _('Formula-based')),
    ]

    tax_type = models.ForeignKey(
        TaxType,
        on_delete=models.PROTECT,
        related_name='rates',
        verbose_name=_("Tax Type")
    )
    name = models.CharField(max_length=100, verbose_name=_("Tax Rate Name"))
    calculation_type = models.CharField(
        max_length=20,
        choices=TAX_CALCULATION_TYPES,
        default='percentage',
        verbose_name=_("Calculation Type")
    )

    # For percentage calculations
    rate_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name=_("Tax Percentage"),
        null=True,
        blank=True,
        help_text=_("Used for 'Percentage of value' calculation type")
    )

    # For fixed and quantity-based calculations
    fixed_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("Fixed Amount"),
        null=True,
        blank=True,
        help_text=_("Used for 'Fixed amount' and 'Quantity-based' calculation types")
    )

    # For formula-based calculations
    formula = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Calculation Formula"),
        help_text=_(
            "Used for 'Formula-based' calculation type. Use variables like price, quantity, etc.")
    )

    applicable_categories = models.ManyToManyField(
        ProductCategory,
        blank=True,
        related_name='tax_rates',
        verbose_name=_("Applicable to Categories")
    )

    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated"))

    class Meta:
        verbose_name = _("Tax Rate")
        verbose_name_plural = _("Tax Rates")
        ordering = ['tax_type', 'name']

    def __str__(self):
        if self.calculation_type == 'percentage':
            return f"{self.name} ({self.rate_percentage}%)"
        elif self.calculation_type == 'fixed':
            return f"{self.name} ({self.fixed_amount} USD)"
        elif self.calculation_type == 'quantity_based':
            return f"{self.name} ({self.fixed_amount} USD/unit)"
        else:
            return f"{self.name} (formula)"

    def calculate_tax(self, base_price, quantity=1, **kwargs):
        """
        Calculates tax based on price and quantity

        Args:
            base_price: Base price of the product
            quantity: Product quantity
            **kwargs: Additional parameters for formula calculation

        Returns:
            Decimal: Tax amount
        """
        if not self.is_active:
            return 0

        if self.calculation_type == 'percentage':
            if self.rate_percentage is not None:
                return (base_price * quantity) * (self.rate_percentage / 100)
            return 0

        elif self.calculation_type == 'fixed':
            if self.fixed_amount is not None:
                return self.fixed_amount
            return 0

        elif self.calculation_type == 'quantity_based':
            if self.fixed_amount is not None:
                return self.fixed_amount * quantity
            return 0

        elif self.calculation_type == 'formula_based' and self.formula:
            try:
                # Basic variables for formula
                variables = {
                    'price': float(base_price),
                    'quantity': quantity,
                    **kwargs
                }

                # Safe way to execute formula - using eval()
                # In production environment, you should use safer libraries
                # for formula calculation, such as simpleeval or safer_eval
                result = eval(self.formula, {"__builtins__": {}}, variables)
                return result
            except Exception as e:
                # Log the error and return 0 in case of an error
                # In a real application, proper logging should be added here
                print(f"Error calculating tax using formula: {e}")
                return 0

        return 0


class Product(models.Model):
    """Base product model with support for different types and dynamic attributes"""
    PRODUCT_TYPE_CHOICES = [
        ('food', _('Food')),
        ('industrial', _('Industrial')),
        ('tobacco', _('Tobacco Products')),
        ('alcohol', _('Alcoholic Beverages')),
        ('electronics', _('Electronics')),
        ('clothing', _('Clothing')),
        ('other', _('Other')),
    ]

    # Basic product data
    name = models.CharField(max_length=255, verbose_name=_("Product Name"))
    slug = models.SlugField(max_length=255, unique=True, verbose_name=_("URL-slug"))
    sku = models.CharField(max_length=50, unique=True, verbose_name=_("SKU"))

    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'is_seller': True},
        related_name='products',
        verbose_name=_("Seller")
    )

    category = models.ForeignKey(
        ProductCategory,
        on_delete=models.PROTECT,
        related_name='products',
        verbose_name=_("Category")
    )

    description = models.TextField(blank=True, verbose_name=_("Description"))
    base_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Base Price"))

    # Physical characteristics
    length = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name=_("Length (cm)"))
    width = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name=_("Width (cm)"))
    height = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name=_("Height (cm)"))
    weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name=_("Weight (g)"))

    # Product type and taxes
    product_type = models.CharField(
        max_length=20,
        choices=PRODUCT_TYPE_CHOICES,
        default='other',
        verbose_name=_("Product Type")
    )
    taxable = models.BooleanField(default=True, verbose_name=_("Taxable"))

    # Connection with tax types
    applicable_tax_types = models.ManyToManyField(
        'TaxType',
        related_name='products',
        blank=True,
        verbose_name=_("Applicable Tax Types")
    )

    # Defined tax rates (if custom for specific product)
    custom_tax_rates = models.ManyToManyField(
        'TaxRate',
        related_name='custom_products',
        blank=True,
        verbose_name=_("Custom Tax Rates")
    )

    # Field for storing dynamic attributes in JSON format
    attributes_json = models.JSONField(default=dict, blank=True, verbose_name=_("Dynamic Attributes"))

    # Product image (main image)
    main_image = models.ImageField(upload_to='product_images/', blank=True, null=True,
                                   verbose_name=_("Main Image"))

    # Status and timestamps
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated"))

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.sku})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def volume(self):
        """Calculates the product volume if all dimensions are specified"""
        if self.length and self.width and self.height:
            return self.length * self.width * self.height
        return None

    def set_attribute(self, key, value):
        """Sets a dynamic product attribute"""
        attributes = self.attributes_json
        attributes[key] = value
        self.attributes_json = attributes
        self.save(update_fields=['attributes_json'])

    def get_attribute(self, key, default=None):
        """Gets a dynamic attribute value"""
        return self.attributes_json.get(key, default)

    def remove_attribute(self, key):
        """Removes a dynamic attribute"""
        attributes = self.attributes_json
        if key in attributes:
            del attributes[key]
            self.attributes_json = attributes
            self.save(update_fields=['attributes_json'])
            return True
        return False

    def get_applicable_tax_rates(self):
        """Gets all applicable tax rates for the product"""
        if not self.taxable:
            return []

        # First include custom rates for the product, if any
        tax_rates = list(self.custom_tax_rates.filter(is_active=True))

        # If there are explicitly specified tax types for the product
        if self.applicable_tax_types.exists():
            tax_types = self.applicable_tax_types.filter(is_active=True)
            for tax_type in tax_types:
                tax_rates.extend(list(tax_type.rates.filter(is_active=True)))

        # Add rates from the product category
        category_rates = self.category.tax_rates.filter(is_active=True)
        for rate in category_rates:
            if rate not in tax_rates:
                tax_rates.append(rate)

        # Add rates for the product type (e.g., tobacco excise)
        from django.db.models import Q
        product_type_rates = TaxRate.objects.filter(
            Q(tax_type__code=self.product_type),
            is_active=True
        )
        for rate in product_type_rates:
            if rate not in tax_rates:
                tax_rates.append(rate)

        return tax_rates

    def calculate_taxes(self, quantity=1, **kwargs):
        """
        Calculates all taxes for the product

        Args:
            quantity: Product quantity
            **kwargs: Additional parameters for tax calculation

        Returns:
            dict: Dictionary with taxes {tax_name: tax_amount}
        """
        if not self.taxable:
            return {}

        tax_rates = self.get_applicable_tax_rates()
        taxes = {}

        for rate in tax_rates:
            tax_amount = rate.calculate_tax(self.base_price, quantity, **kwargs)
            if tax_amount > 0:
                tax_name = f"{rate.tax_type.name} - {rate.name}"
                taxes[tax_name] = tax_amount

        return taxes

    def calculate_total_tax_amount(self, quantity=1, **kwargs):
        # To calculate total tax from others taxes
        taxes = self.calculate_taxes(quantity, **kwargs)
        return sum(taxes.values())

    def calculate_final_price(self, quantity=1, include_taxes=True, **kwargs):
        # To calculate final price from total tax
        base_total = self.base_price * quantity

        if include_taxes and self.taxable:
            tax_amount = self.calculate_total_tax_amount(quantity, **kwargs)
            return base_total + tax_amount

        return base_total


class ProductImage(models.Model):
    """Model for storing additional product images"""
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name=_("Product")
    )
    image = models.ImageField(upload_to='product_images/', verbose_name=_("Image"))
    title = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("Image Title"))
    is_main = models.BooleanField(default=False, verbose_name=_("Main Image"))
    order = models.PositiveIntegerField(default=0, verbose_name=_("Display Order"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created"))

    class Meta:
        verbose_name = _("Product Image")
        verbose_name_plural = _("Product Images")
        ordering = ['product', 'order']

    def __str__(self):
        return f"Image for {self.product.name}"

    def save(self, *args, **kwargs):
        # If this is the main image, update the main_image field in the product
        # and unset the "main" flag from other images
        if self.is_main:
            # Update other images
            ProductImage.objects.filter(
                product=self.product,
                is_main=True
            ).exclude(pk=self.pk).update(is_main=False)

            # Update the main_image field in the product
            if self.image:
                self.product.main_image = self.image
                self.product.save(update_fields=['main_image'])

        super().save(*args, **kwargs)


class Attribute(models.Model):
    """Model for defining product attribute types"""
    TEXT = 'text'
    NUMBER = 'number'
    BOOLEAN = 'boolean'
    SELECT = 'select'
    MULTIPLE_SELECT = 'multiple_select'
    DATE = 'date'

    ATTRIBUTE_TYPE_CHOICES = [
        (TEXT, _('Text')),
        (NUMBER, _('Number')),
        (BOOLEAN, _('Yes/No')),
        (SELECT, _('Single Select')),
        (MULTIPLE_SELECT, _('Multiple Select')),
        (DATE, _('Date')),
    ]

    name = models.CharField(max_length=255, verbose_name=_("Attribute Name"))
    slug = models.SlugField(max_length=255, unique=True, verbose_name=_("URL-slug"))
    description = models.TextField(blank=True, verbose_name=_("Attribute Description"))

    categories = models.ManyToManyField(
        ProductCategory,
        blank=True,
        related_name='attributes',
        verbose_name=_("Categories")
    )

    attribute_type = models.CharField(
        max_length=20,
        choices=ATTRIBUTE_TYPE_CHOICES,
        default=TEXT,
        verbose_name=_("Attribute Type")
    )

    required = models.BooleanField(default=False, verbose_name=_("Required"))
    is_filterable = models.BooleanField(default=False, verbose_name=_("Used for Filtering"))
    is_displayed = models.BooleanField(default=True, verbose_name=_("Displayed in Product Details"))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated"))

    class Meta:
        verbose_name = _("Attribute")
        verbose_name_plural = _("Attributes")
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class AttributeOption(models.Model):
    """Model for attribute value options for SELECT and MULTIPLE_SELECT types"""
    attribute = models.ForeignKey(
        Attribute,
        on_delete=models.CASCADE,
        related_name='options',
        verbose_name=_("Attribute")
    )
    value = models.CharField(max_length=255, verbose_name=_("Value"))
    order = models.PositiveIntegerField(default=0, verbose_name=_("Display Order"))

    class Meta:
        verbose_name = _("Attribute Option")
        verbose_name_plural = _("Attribute Options")
        unique_together = ('attribute', 'value')
        ordering = ['attribute', 'order', 'value']

    def __str__(self):
        return f"{self.attribute.name}: {self.value}"


class ProductAttributeValue(models.Model):
    """Model for linking products with specific attribute values"""
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='attribute_values',
        verbose_name=_("Product")
    )
    attribute = models.ForeignKey(
        Attribute,
        on_delete=models.CASCADE,
        verbose_name=_("Attribute")
    )

    # Different types of attribute values
    text_value = models.TextField(blank=True, null=True, verbose_name=_("Text Value"))
    number_value = models.DecimalField(max_digits=15, decimal_places=6, blank=True, null=True,
                                       verbose_name=_("Number Value"))
    boolean_value = models.BooleanField(blank=True, null=True, verbose_name=_("Boolean Value"))
    date_value = models.DateField(blank=True, null=True, verbose_name=_("Date Value"))

    # For SELECT type attributes (single selection)
    select_value = models.ForeignKey(
        AttributeOption,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='product_single_values',
        verbose_name=_("Single Select Value")
    )

    class Meta:
        verbose_name = _("Product Attribute Value")
        verbose_name_plural = _("Product Attribute Values")
        unique_together = ('product', 'attribute')

    def __str__(self):
        attribute_name = self.attribute.name

        if self.attribute.attribute_type == Attribute.TEXT and self.text_value:
            return f"{attribute_name}: {self.text_value}"
        elif self.attribute.attribute_type == Attribute.NUMBER and self.number_value:
            return f"{attribute_name}: {self.number_value}"
        elif self.attribute.attribute_type == Attribute.BOOLEAN and self.boolean_value is not None:
            return f"{attribute_name}: {_('Yes') if self.boolean_value else _('No')}"
        elif self.attribute.attribute_type == Attribute.SELECT and self.select_value:
            return f"{attribute_name}: {self.select_value.value}"
        elif self.attribute.attribute_type == Attribute.DATE and self.date_value:
            return f"{attribute_name}: {self.date_value}"

        return f"{attribute_name}: {_('(Not set)')}"

    def save(self, *args, **kwargs):
        # Validate value according to attribute type
        if self.attribute.attribute_type == Attribute.TEXT:
            self.number_value = None
            self.boolean_value = None
            self.date_value = None
            self.select_value = None
        elif self.attribute.attribute_type == Attribute.NUMBER:
            self.text_value = None
            self.boolean_value = None
            self.date_value = None
            self.select_value = None
        elif self.attribute.attribute_type == Attribute.BOOLEAN:
            self.text_value = None
            self.number_value = None
            self.date_value = None
            self.select_value = None
        elif self.attribute.attribute_type == Attribute.DATE:
            self.text_value = None
            self.number_value = None
            self.boolean_value = None
            self.select_value = None
        elif self.attribute.attribute_type == Attribute.SELECT:
            self.text_value = None
            self.number_value = None
            self.boolean_value = None
            self.date_value = None

        super().save(*args, **kwargs)

        # Synchronize with the product's JSON field for quick access
        self._sync_with_product_json()

    def _sync_with_product_json(self):
        """Synchronizes attribute value with the product's JSON field"""
        attributes = self.product.attributes_json

        # Key for JSON
        key = f"attr_{self.attribute.slug}"

        # Determine value to write to JSON
        if self.attribute.attribute_type == Attribute.TEXT and self.text_value:
            value = self.text_value
        elif self.attribute.attribute_type == Attribute.NUMBER and self.number_value:
            value = float(self.number_value)
        elif self.attribute.attribute_type == Attribute.BOOLEAN:
            value = bool(self.boolean_value) if self.boolean_value is not None else None
        elif self.attribute.attribute_type == Attribute.DATE and self.date_value:
            value = str(self.date_value)
        elif self.attribute.attribute_type == Attribute.SELECT and self.select_value:
            value = self.select_value.value
        elif self.attribute.attribute_type == Attribute.MULTIPLE_SELECT:
            # Get all values for multiple select
            values = [val.attribute_option.value for val in
                      self.multiple_values.all()]
            value = values if values else None
        else:
            value = None

        if value is not None:
            attributes[key] = value
        elif key in attributes:
            del attributes[key]

        # Update the product's JSON field
        Product.objects.filter(pk=self.product.pk).update(attributes_json=attributes)


class ProductMultipleAttributeValue(models.Model):
    """Model for storing multiple attribute values for products (for multiple_select type)"""
    product_attribute = models.ForeignKey(
        ProductAttributeValue,
        on_delete=models.CASCADE,
        related_name='multiple_values',
        verbose_name=_("Product Attribute")
    )
    attribute_option = models.ForeignKey(
        AttributeOption,
        on_delete=models.CASCADE,
        verbose_name=_("Option Value")
    )

    class Meta:
        verbose_name = _("Multiple Attribute Value")
        verbose_name_plural = _("Multiple Attribute Values")
        unique_together = ('product_attribute', 'attribute_option')

    def __str__(self):
        return f"{self.product_attribute.product.name} - {self.attribute_option.value}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # After saving, update the product's JSON field
        self.product_attribute._sync_with_product_json()


# Additional models specific to different product types
# Instead of creating separate tables, we use attributes

class FoodSpecificAttributes:
    """
    Helper class for working with food product attributes.
    Use these constants to access specific attributes in JSON.
    """
    EXPIRATION_DATE = 'food_expiration_date'
    STORAGE_TEMP = 'food_storage_temp'
    CALORIES = 'food_calories'
    INGREDIENTS = 'food_ingredients'
    ALLERGENS = 'food_allergens'
    NUTRITION_FACTS = 'food_nutrition_facts'

    @staticmethod
    def get_expiration_date(product):
        """Gets the product expiration date"""
        return product.get_attribute(FoodSpecificAttributes.EXPIRATION_DATE)

    @staticmethod
    def set_expiration_date(product, date_str):
        """Sets the product expiration date"""
        product.set_attribute(FoodSpecificAttributes.EXPIRATION_DATE, date_str)


class IndustrialSpecificAttributes:
    """
    Helper class for working with industrial product attributes.
    Use these constants to access specific attributes in JSON.
    """
    WARRANTY_PERIOD = 'industrial_warranty_period'
    MATERIAL = 'industrial_material'
    BRAND = 'industrial_brand'
    MODEL = 'industrial_model'
    COUNTRY_OF_ORIGIN = 'industrial_country_of_origin'
    SAFETY_CERTIFICATE = 'industrial_safety_certificate'

    @staticmethod
    def get_warranty_period(product):
        """Gets the product warranty period"""
        return product.get_attribute(IndustrialSpecificAttributes.WARRANTY_PERIOD)

    @staticmethod
    def set_warranty_period(product, period):
        """Sets the product warranty period"""
        product.set_attribute(IndustrialSpecificAttributes.WARRANTY_PERIOD, period)
