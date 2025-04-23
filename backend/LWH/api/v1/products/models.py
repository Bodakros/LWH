from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.conf import settings
import uuid
import json


class ProductCategory(models.Model):
    """Модель для категорій продуктів з підтримкою ієрархії"""
    name = models.CharField(max_length=255, verbose_name=_("Назва категорії"))
    slug = models.SlugField(max_length=255, unique=True, verbose_name=_("URL-slug"))
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name=_("Батьківська категорія")
    )
    description = models.TextField(blank=True, verbose_name=_("Опис категорії"))
    image = models.ImageField(upload_to='category_images/', blank=True, null=True,
                              verbose_name=_("Зображення категорії"))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Створено"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Оновлено"))

    class Meta:
        verbose_name = _("Категорія продукту")
        verbose_name_plural = _("Категорії продуктів")
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class TaxType(models.Model):
    """Модель для типів податків (наприклад, ПДВ, акциз на сигарети, тощо)"""
    code = models.CharField(max_length=20, unique=True, verbose_name=_("Код податку"))
    name = models.CharField(max_length=100, verbose_name=_("Назва типу податку"))
    description = models.TextField(blank=True, verbose_name=_("Опис податку"))
    is_active = models.BooleanField(default=True, verbose_name=_("Активний"))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Створено"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Оновлено"))

    class Meta:
        verbose_name = _("Тип податку")
        verbose_name_plural = _("Типи податків")
        ordering = ['code', 'name']

    def __str__(self):
        return f"{self.name} ({self.code})"


class TaxRate(models.Model):
    """Модель для зберігання податкових ставок"""
    TAX_CALCULATION_TYPES = [
        ('percentage', _('Відсоток від вартості')),
        ('fixed', _('Фіксована сума')),
        ('quantity_based', _('На основі кількості')),
        ('formula_based', _('На основі формули')),
    ]

    tax_type = models.ForeignKey(
        TaxType,
        on_delete=models.PROTECT,
        related_name='rates',
        verbose_name=_("Тип податку")
    )
    name = models.CharField(max_length=100, verbose_name=_("Назва податкової ставки"))
    calculation_type = models.CharField(
        max_length=20,
        choices=TAX_CALCULATION_TYPES,
        default='percentage',
        verbose_name=_("Тип розрахунку")
    )

    # Для розрахунків за відсотком
    rate_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name=_("Відсоток податку"),
        null=True,
        blank=True,
        help_text=_("Використовується для типу розрахунку 'Відсоток від вартості'")
    )

    # Для фіксованих та кількісних розрахунків
    fixed_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("Фіксована сума"),
        null=True,
        blank=True,
        help_text=_("Використовується для типів розрахунку 'Фіксована сума' та 'На основі кількості'")
    )

    # Для формульних розрахунків
    formula = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Формула розрахунку"),
        help_text=_(
            "Використовується для типу розрахунку 'На основі формули'. Використовуйте змінні price, quantity, etc.")
    )

    applicable_categories = models.ManyToManyField(
        ProductCategory,
        blank=True,
        related_name='tax_rates',
        verbose_name=_("Застосовується до категорій")
    )

    is_active = models.BooleanField(default=True, verbose_name=_("Активна"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Створено"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Оновлено"))

    class Meta:
        verbose_name = _("Податкова ставка")
        verbose_name_plural = _("Податкові ставки")
        ordering = ['tax_type', 'name']

    def __str__(self):
        if self.calculation_type == 'percentage':
            return f"{self.name} ({self.rate_percentage}%)"
        elif self.calculation_type == 'fixed':
            return f"{self.name} ({self.fixed_amount} грн)"
        elif self.calculation_type == 'quantity_based':
            return f"{self.name} ({self.fixed_amount} грн/од.)"
        else:
            return f"{self.name} (формула)"

    def calculate_tax(self, base_price, quantity=1, **kwargs):
        """
        Розраховує податок на основі ціни та кількості

        Args:
            base_price: Базова ціна товару
            quantity: Кількість товару
            **kwargs: Додаткові параметри для розрахунку формули

        Returns:
            Decimal: Сума податку
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
                # Базові змінні для формули
                variables = {
                    'price': float(base_price),
                    'quantity': quantity,
                    **kwargs
                }

                # Безпечний спосіб виконання формули - використовуємо eval()
                # У продакшн-середовищі варто використовувати більш безпечні бібліотеки
                # для обчислення формул, такі як simpleeval або safer_eval
                result = eval(self.formula, {"__builtins__": {}}, variables)
                return result
            except Exception as e:
                # Логування помилки та повернення 0 у випадку помилки
                # В реальному додатку тут варто додати належне логування
                print(f"Помилка обчислення податку за формулою: {e}")
                return 0

        return 0


class Product(models.Model):
    """Базова модель продукту з підтримкою різних типів та динамічних атрибутів"""
    PRODUCT_TYPE_CHOICES = [
        ('food', _('Харчовий')),
        ('industrial', _('Промисловий')),
        ('tobacco', _('Тютюнові вироби')),
        ('alcohol', _('Алкогольні напої')),
        ('electronics', _('Електроніка')),
        ('clothing', _('Одяг')),
        ('other', _('Інший')),
    ]

    # Базові дані продукту
    name = models.CharField(max_length=255, verbose_name=_("Назва продукту"))
    slug = models.SlugField(max_length=255, unique=True, verbose_name=_("URL-slug"))
    sku = models.CharField(max_length=50, unique=True, verbose_name=_("Артикул"))

    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'is_seller': True},
        related_name='products',
        verbose_name=_("Продавець")
    )

    category = models.ForeignKey(
        ProductCategory,
        on_delete=models.PROTECT,
        related_name='products',
        verbose_name=_("Категорія")
    )

    description = models.TextField(blank=True, verbose_name=_("Опис"))
    base_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Базова ціна"))

    # Фізичні характеристики
    length = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name=_("Довжина (см)"))
    width = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name=_("Ширина (см)"))
    height = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name=_("Висота (см)"))
    weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name=_("Вага (г)"))

    # Тип продукту і податки
    product_type = models.CharField(
        max_length=20,
        choices=PRODUCT_TYPE_CHOICES,
        default='other',
        verbose_name=_("Тип продукту")
    )
    taxable = models.BooleanField(default=True, verbose_name=_("Оподатковується"))

    # Зв'язок з типами податків
    applicable_tax_types = models.ManyToManyField(
        'TaxType',
        related_name='products',
        blank=True,
        verbose_name=_("Застосовні типи податків")
    )

    # Визначені ставки податків (якщо кастомні для конкретного продукту)
    custom_tax_rates = models.ManyToManyField(
        'TaxRate',
        related_name='custom_products',
        blank=True,
        verbose_name=_("Кастомні ставки податків")
    )

    # Поле для зберігання динамічних атрибутів у форматі JSON
    attributes_json = models.JSONField(default=dict, blank=True, verbose_name=_("Динамічні атрибути"))

    # Зображення продукту (головне зображення)
    main_image = models.ImageField(upload_to='product_images/', blank=True, null=True,
                                   verbose_name=_("Головне зображення"))

    # Статуси і часові мітки
    is_active = models.BooleanField(default=True, verbose_name=_("Активний"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Створено"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Оновлено"))

    class Meta:
        verbose_name = _("Продукт")
        verbose_name_plural = _("Продукти")
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.sku})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def volume(self):
        """Розраховує об'єм продукту, якщо вказані всі розміри"""
        if self.length and self.width and self.height:
            return self.length * self.width * self.height
        return None

    def set_attribute(self, key, value):
        """Встановлює динамічний атрибут продукту"""
        attributes = self.attributes_json
        attributes[key] = value
        self.attributes_json = attributes
        self.save(update_fields=['attributes_json'])

    def get_attribute(self, key, default=None):
        """Отримує значення динамічного атрибуту"""
        return self.attributes_json.get(key, default)

    def remove_attribute(self, key):
        """Видаляє динамічний атрибут"""
        attributes = self.attributes_json
        if key in attributes:
            del attributes[key]
            self.attributes_json = attributes
            self.save(update_fields=['attributes_json'])
            return True
        return False

    def get_applicable_tax_rates(self):
        """Отримує всі застосовні податкові ставки для продукту"""
        if not self.taxable:
            return []

        # Спочатку включаємо кастомні ставки для продукту, якщо вони є
        tax_rates = list(self.custom_tax_rates.filter(is_active=True))

        # Якщо є явно вказані типи податків для продукту
        if self.applicable_tax_types.exists():
            tax_types = self.applicable_tax_types.filter(is_active=True)
            for tax_type in tax_types:
                tax_rates.extend(list(tax_type.rates.filter(is_active=True)))

        # Додаємо ставки з категорії продукту
        category_rates = self.category.tax_rates.filter(is_active=True)
        for rate in category_rates:
            if rate not in tax_rates:
                tax_rates.append(rate)

        # Додаємо ставки для типу продукту (наприклад, акциз на тютюн)
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
        Розраховує всі податки для продукту

        Args:
            quantity: Кількість продукту
            **kwargs: Додаткові параметри для розрахунку податків

        Returns:
            dict: Словник з податками {tax_name: tax_amount}
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
        """
        Розраховує загальну суму податків для продукту

        Args:
            quantity: Кількість продукту
            **kwargs: Додаткові параметри для розрахунку податків

        Returns:
            Decimal: Загальна сума податків
        """
        taxes = self.calculate_taxes(quantity, **kwargs)
        return sum(taxes.values())

    def calculate_final_price(self, quantity=1, include_taxes=True, **kwargs):
        """
        Розраховує кінцеву ціну продукту з урахуванням податків

        Args:
            quantity: Кількість продукту
            include_taxes: Чи включати податки в розрахунок
            **kwargs: Додаткові параметри для розрахунку податків

        Returns:
            Decimal: Кінцева ціна
        """
        base_total = self.base_price * quantity

        if include_taxes and self.taxable:
            tax_amount = self.calculate_total_tax_amount(quantity, **kwargs)
            return base_total + tax_amount

        return base_total


class ProductImage(models.Model):
    """Модель для зберігання додаткових зображень продукту"""
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name=_("Продукт")
    )
    image = models.ImageField(upload_to='product_images/', verbose_name=_("Зображення"))
    title = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("Назва зображення"))
    is_main = models.BooleanField(default=False, verbose_name=_("Головне зображення"))
    order = models.PositiveIntegerField(default=0, verbose_name=_("Порядок відображення"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Створено"))

    class Meta:
        verbose_name = _("Зображення продукту")
        verbose_name_plural = _("Зображення продуктів")
        ordering = ['product', 'order']

    def __str__(self):
        return f"Зображення для {self.product.name}"

    def save(self, *args, **kwargs):
        # Якщо це головне зображення, оновлюємо поле main_image у продукту
        # та знімаємо прапорець "головне" з інших зображень
        if self.is_main:
            # Оновлюємо інші зображення
            ProductImage.objects.filter(
                product=self.product,
                is_main=True
            ).exclude(pk=self.pk).update(is_main=False)

            # Оновлюємо поле main_image у продукту
            if self.image:
                self.product.main_image = self.image
                self.product.save(update_fields=['main_image'])

        super().save(*args, **kwargs)


class Attribute(models.Model):
    """Модель для визначення типів атрибутів продуктів"""
    TEXT = 'text'
    NUMBER = 'number'
    BOOLEAN = 'boolean'
    SELECT = 'select'
    MULTIPLE_SELECT = 'multiple_select'
    DATE = 'date'

    ATTRIBUTE_TYPE_CHOICES = [
        (TEXT, _('Текст')),
        (NUMBER, _('Число')),
        (BOOLEAN, _('Так/Ні')),
        (SELECT, _('Вибір одного')),
        (MULTIPLE_SELECT, _('Вибір кількох')),
        (DATE, _('Дата')),
    ]

    name = models.CharField(max_length=255, verbose_name=_("Назва атрибуту"))
    slug = models.SlugField(max_length=255, unique=True, verbose_name=_("URL-slug"))
    description = models.TextField(blank=True, verbose_name=_("Опис атрибуту"))

    categories = models.ManyToManyField(
        ProductCategory,
        blank=True,
        related_name='attributes',
        verbose_name=_("Категорії")
    )

    attribute_type = models.CharField(
        max_length=20,
        choices=ATTRIBUTE_TYPE_CHOICES,
        default=TEXT,
        verbose_name=_("Тип атрибуту")
    )

    required = models.BooleanField(default=False, verbose_name=_("Обов'язковий"))
    is_filterable = models.BooleanField(default=False, verbose_name=_("Використовується для фільтрації"))
    is_displayed = models.BooleanField(default=True, verbose_name=_("Відображається у деталях продукту"))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Створено"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Оновлено"))

    class Meta:
        verbose_name = _("Атрибут")
        verbose_name_plural = _("Атрибути")
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class AttributeOption(models.Model):
    """Модель для варіантів значень атрибутів типу SELECT та MULTIPLE_SELECT"""
    attribute = models.ForeignKey(
        Attribute,
        on_delete=models.CASCADE,
        related_name='options',
        verbose_name=_("Атрибут")
    )
    value = models.CharField(max_length=255, verbose_name=_("Значення"))
    order = models.PositiveIntegerField(default=0, verbose_name=_("Порядок відображення"))

    class Meta:
        verbose_name = _("Варіант значення атрибуту")
        verbose_name_plural = _("Варіанти значень атрибутів")
        unique_together = ('attribute', 'value')
        ordering = ['attribute', 'order', 'value']

    def __str__(self):
        return f"{self.attribute.name}: {self.value}"


class ProductAttributeValue(models.Model):
    """Модель для зв'язування продуктів з конкретними значеннями атрибутів"""
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='attribute_values',
        verbose_name=_("Продукт")
    )
    attribute = models.ForeignKey(
        Attribute,
        on_delete=models.CASCADE,
        verbose_name=_("Атрибут")
    )

    # Різні типи значень атрибутів
    text_value = models.TextField(blank=True, null=True, verbose_name=_("Текстове значення"))
    number_value = models.DecimalField(max_digits=15, decimal_places=6, blank=True, null=True,
                                       verbose_name=_("Числове значення"))
    boolean_value = models.BooleanField(blank=True, null=True, verbose_name=_("Логічне значення"))
    date_value = models.DateField(blank=True, null=True, verbose_name=_("Значення дати"))

    # Для атрибутів типу SELECT (одиночний вибір)
    select_value = models.ForeignKey(
        AttributeOption,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='product_single_values',
        verbose_name=_("Значення одиночного вибору")
    )

    class Meta:
        verbose_name = _("Значення атрибуту продукту")
        verbose_name_plural = _("Значення атрибутів продуктів")
        unique_together = ('product', 'attribute')

    def __str__(self):
        attribute_name = self.attribute.name

        if self.attribute.attribute_type == Attribute.TEXT and self.text_value:
            return f"{attribute_name}: {self.text_value}"
        elif self.attribute.attribute_type == Attribute.NUMBER and self.number_value:
            return f"{attribute_name}: {self.number_value}"
        elif self.attribute.attribute_type == Attribute.BOOLEAN and self.boolean_value is not None:
            return f"{attribute_name}: {_('Так') if self.boolean_value else _('Ні')}"
        elif self.attribute.attribute_type == Attribute.SELECT and self.select_value:
            return f"{attribute_name}: {self.select_value.value}"
        elif self.attribute.attribute_type == Attribute.DATE and self.date_value:
            return f"{attribute_name}: {self.date_value}"

        return f"{attribute_name}: {_('(Не встановлено)')}"

    def save(self, *args, **kwargs):
        # Валідація значення відповідно до типу атрибуту
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

        # Синхронізуємо з JSON-полем продукту для швидкого доступу
        self._sync_with_product_json()

    def _sync_with_product_json(self):
        """Синхронізує значення атрибуту з JSON-полем продукту"""
        attributes = self.product.attributes_json

        # Ключ для JSON
        key = f"attr_{self.attribute.slug}"

        # Визначаємо значення для запису в JSON
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
            # Отримуємо всі значення для multiple select
            values = [val.attribute_option.value for val in
                      self.multiple_values.all()]
            value = values if values else None
        else:
            value = None

        if value is not None:
            attributes[key] = value
        elif key in attributes:
            del attributes[key]

        # Оновлюємо JSON-поле продукту
        Product.objects.filter(pk=self.product.pk).update(attributes_json=attributes)


class ProductMultipleAttributeValue(models.Model):
    """Модель для зберігання множинних значень атрибутів продуктів (для типу multiple_select)"""
    product_attribute = models.ForeignKey(
        ProductAttributeValue,
        on_delete=models.CASCADE,
        related_name='multiple_values',
        verbose_name=_("Атрибут продукту")
    )
    attribute_option = models.ForeignKey(
        AttributeOption,
        on_delete=models.CASCADE,
        verbose_name=_("Варіант значення")
    )

    class Meta:
        verbose_name = _("Множинне значення атрибуту продукту")
        verbose_name_plural = _("Множинні значення атрибутів продуктів")
        unique_together = ('product_attribute', 'attribute_option')

    def __str__(self):
        return f"{self.product_attribute.product.name} - {self.attribute_option.value}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Після збереження оновлюємо JSON-поле продукту
        self.product_attribute._sync_with_product_json()


# Додаткові моделі, специфічні для різних типів продуктів
# Замість створення окремих таблиць, ми використовуємо атрибути

class FoodSpecificAttributes:
    """
    Клас-хелпер для роботи з атрибутами харчових продуктів.
    Використовуйте ці константи для доступу до специфічних атрибутів в JSON.
    """
    EXPIRATION_DATE = 'food_expiration_date'
    STORAGE_TEMP = 'food_storage_temp'
    CALORIES = 'food_calories'
    INGREDIENTS = 'food_ingredients'
    ALLERGENS = 'food_allergens'
    NUTRITION_FACTS = 'food_nutrition_facts'

    @staticmethod
    def get_expiration_date(product):
        """Отримує термін придатності продукту"""
        return product.get_attribute(FoodSpecificAttributes.EXPIRATION_DATE)

    @staticmethod
    def set_expiration_date(product, date_str):
        """Встановлює термін придатності продукту"""
        product.set_attribute(FoodSpecificAttributes.EXPIRATION_DATE, date_str)


class IndustrialSpecificAttributes:
    """
    Клас-хелпер для роботи з атрибутами промислових продуктів.
    Використовуйте ці константи для доступу до специфічних атрибутів в JSON.
    """
    WARRANTY_PERIOD = 'industrial_warranty_period'
    MATERIAL = 'industrial_material'
    BRAND = 'industrial_brand'
    MODEL = 'industrial_model'
    COUNTRY_OF_ORIGIN = 'industrial_country_of_origin'
    SAFETY_CERTIFICATE = 'industrial_safety_certificate'

    @staticmethod
    def get_warranty_period(product):
        """Отримує гарантійний термін продукту"""
        return product.get_attribute(IndustrialSpecificAttributes.WARRANTY_PERIOD)

    @staticmethod
    def set_warranty_period(product, period):
        """Встановлює гарантійний термін продукту"""
        product.set_attribute(IndustrialSpecificAttributes.WARRANTY_PERIOD, period)
