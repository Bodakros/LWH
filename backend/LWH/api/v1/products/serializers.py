from rest_framework import serializers
from .models import (
    ProductCategory, TaxRate, Product, ProductImage,
    Attribute, AttributeOption, ProductAttributeValue,
    ProductMultipleAttributeValue, FoodSpecificAttributes,
    IndustrialSpecificAttributes, TaxType
)


class ProductCategorySerializer(serializers.ModelSerializer):
    """Серіалізатор для категорій продуктів"""
    children = serializers.SerializerMethodField()

    class Meta:
        model = ProductCategory
        fields = [
            'id', 'name', 'slug', 'parent', 'description',
            'image', 'children', 'created_at', 'updated_at'
        ]
        read_only_fields = ['slug', 'created_at', 'updated_at']

    def get_children(self, obj):
        """Отримує дочірні категорії"""
        children = ProductCategory.objects.filter(parent=obj)
        serializer = ProductCategoryListSerializer(children, many=True)
        return serializer.data


class ProductCategoryListSerializer(serializers.ModelSerializer):
    """Спрощений серіалізатор для списку категорій продуктів"""
    class Meta:
        model = ProductCategory
        fields = ['id', 'name', 'slug']


class TaxTypeSerializer(serializers.ModelSerializer):
    """Серіалізатор для типів податків"""
    rates_count = serializers.SerializerMethodField()

    class Meta:
        model = TaxType
        fields = [
            'id', 'code', 'name', 'description', 'is_active',
            'rates_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_rates_count(self, obj):
        return obj.rates.count()


class TaxRateSerializer(serializers.ModelSerializer):
    """Серіалізатор для податкових ставок"""
    tax_type_details = TaxTypeSerializer(source='tax_type', read_only=True)
    applicable_categories = ProductCategoryListSerializer(many=True, read_only=True)
    applicable_category_ids = serializers.PrimaryKeyRelatedField(
        queryset=ProductCategory.objects.all(),
        write_only=True,
        source='applicable_categories',
        many=True,
        required=False
    )

    class Meta:
        model = TaxRate
        fields = [
            'id', 'tax_type', 'tax_type_details', 'name', 'calculation_type',
            'rate_percentage', 'fixed_amount', 'formula',
            'applicable_categories', 'applicable_category_ids',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate(self, data):
        calculation_type = data.get('calculation_type')

        # Перевіряємо наявність необхідних полів в залежності від типу розрахунку
        if calculation_type == 'percentage' and not data.get('rate_percentage'):
            raise serializers.ValidationError(
                {"rate_percentage": "Це поле обов'язкове для типу розрахунку 'Відсоток від вартості'"}
            )

        if calculation_type in ['fixed', 'quantity_based'] and not data.get('fixed_amount'):
            raise serializers.ValidationError(
                {"fixed_amount": f"Це поле обов'язкове для типу розрахунку '{dict(TaxRate.TAX_CALCULATION_TYPES)[calculation_type]}'"}
            )

        if calculation_type == 'formula_based' and not data.get('formula'):
            raise serializers.ValidationError(
                {"formula": "Це поле обов'язкове для типу розрахунку 'На основі формули'"}
            )

        return data


class AttributeOptionSerializer(serializers.ModelSerializer):
    """Серіалізатор для варіантів значень атрибутів"""
    class Meta:
        model = AttributeOption
        fields = ['id', 'value', 'order']


class AttributeSerializer(serializers.ModelSerializer):
    """Серіалізатор для атрибутів продуктів"""
    options = AttributeOptionSerializer(many=True, read_only=True)
    categories = ProductCategoryListSerializer(many=True, read_only=True)
    category_ids = serializers.PrimaryKeyRelatedField(
        queryset=ProductCategory.objects.all(),
        write_only=True,
        source='categories',
        many=True,
        required=False
    )

    class Meta:
        model = Attribute
        fields = [
            'id', 'name', 'slug', 'description', 'categories', 'category_ids',
            'attribute_type', 'required', 'is_filterable', 'is_displayed',
            'options', 'created_at', 'updated_at'
        ]
        read_only_fields = ['slug', 'created_at', 'updated_at']


class ProductImageSerializer(serializers.ModelSerializer):
    """Серіалізатор для зображень продуктів"""
    class Meta:
        model = ProductImage
        fields = [
            'id', 'product', 'image', 'title', 'is_main', 'order', 'created_at',
            'thumbnail_small', 'thumbnail_medium', 'thumbnail_large'
        ]
        read_only_fields = ['created_at']

    def get_thumbnail_small(self, obj):
        """Get small thumbnail URL"""
        from ..utils.image_services import get_thumbnail_url
        request = self.context.get('request')
        if request and obj.image:
            image_url = request.build_absolute_uri(obj.image.url)
            return get_thumbnail_url(image_url, size='small')
        return None

    def get_thumbnail_medium(self, obj):
        """Get medium thumbnail URL"""
        from ..utils.image_services import get_thumbnail_url
        request = self.context.get('request')
        if request and obj.image:
            image_url = request.build_absolute_uri(obj.image.url)
            return get_thumbnail_url(image_url, size='medium')
        return None

    def get_thumbnail_large(self, obj):
        """Get large thumbnail URL"""
        from ..utils.image_services import get_thumbnail_url
        request = self.context.get('request')
        if request and obj.image:
            image_url = request.build_absolute_uri(obj.image.url)
            return get_thumbnail_url(image_url, size='large')
        return None


class ProductAttributeValueSerializer(serializers.ModelSerializer):
    """Серіалізатор для значень атрибутів продуктів"""
    attribute_name = serializers.CharField(source='attribute.name', read_only=True)
    attribute_type = serializers.CharField(source='attribute.attribute_type', read_only=True)

    # Для відображення вибраних значень
    select_value_display = serializers.CharField(source='select_value.value', read_only=True)
    multiple_values = serializers.SerializerMethodField()

    class Meta:
        model = ProductAttributeValue
        fields = [
            'id', 'product', 'attribute', 'attribute_name', 'attribute_type',
            'text_value', 'number_value', 'boolean_value', 'date_value',
            'select_value', 'select_value_display', 'multiple_values'
        ]

    def get_multiple_values(self, obj):
        """Отримує всі значення для атрибутів multiple_select"""
        if obj.attribute.attribute_type == Attribute.MULTIPLE_SELECT:
            values = obj.multiple_values.all()
            return [{'id': val.attribute_option.id, 'value': val.attribute_option.value}
                    for val in values]
        return None


class ProductMultipleAttributeValueSerializer(serializers.ModelSerializer):
    """Серіалізатор для множинних значень атрибутів продуктів"""
    class Meta:
        model = ProductMultipleAttributeValue
        fields = ['id', 'product_attribute', 'attribute_option']


class ProductListSerializer(serializers.ModelSerializer):
    """Спрощений серіалізатор для списку продуктів"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    seller_name = serializers.CharField(source='seller.username', read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'sku', 'seller', 'seller_name',
            'category', 'category_name', 'base_price', 'product_type',
            'main_image', 'is_active'
        ]


class ProductSerializer(serializers.ModelSerializer):
    """Повний серіалізатор для продуктів з динамічними атрибутами"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    seller_name = serializers.CharField(source='seller.username', read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    attribute_values = ProductAttributeValueSerializer(many=True, read_only=True)

    # Поля для маніпуляції з атрибутами
    dynamic_attributes = serializers.JSONField(
        source='attributes_json',
        required=False,
        help_text="JSON об'єкт з динамічними атрибутами"
    )

    # Податки
    applicable_tax_types = TaxTypeSerializer(many=True, read_only=True)
    applicable_tax_type_ids = serializers.PrimaryKeyRelatedField(
        queryset=TaxType.objects.all(),
        write_only=True,
        source='applicable_tax_types',
        many=True,
        required=False
    )

    custom_tax_rates = TaxRateSerializer(many=True, read_only=True)
    custom_tax_rate_ids = serializers.PrimaryKeyRelatedField(
        queryset=TaxRate.objects.all(),
        write_only=True,
        source='custom_tax_rates',
        many=True,
        required=False
    )

    # Обчислювані поля для податків
    tax_breakdown = serializers.SerializerMethodField()
    total_tax_amount = serializers.SerializerMethodField()
    final_price = serializers.SerializerMethodField()

    # Специфічні поля для харчових продуктів
    food_expiration_date = serializers.CharField(
        write_only=True, required=False,
        help_text="Термін придатності для харчових продуктів"
    )
    food_storage_temp = serializers.CharField(
        write_only=True, required=False,
        help_text="Температура зберігання для харчових продуктів"
    )
    food_ingredients = serializers.CharField(
        write_only=True, required=False,
        help_text="Інгредієнти для харчових продуктів"
    )

    # Специфічні поля для промислових продуктів
    industrial_warranty_period = serializers.CharField(
        write_only=True, required=False,
        help_text="Гарантійний термін для промислових продуктів"
    )
    industrial_material = serializers.CharField(
        write_only=True, required=False,
        help_text="Матеріал промислового продукту"
    )
    industrial_brand = serializers.CharField(
        write_only=True, required=False,
        help_text="Бренд промислового продукту"
    )

    # Обчислювані властивості
    volume = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'sku', 'seller', 'seller_name',
            'category', 'category_name', 'description', 'base_price',
            'length', 'width', 'height', 'weight', 'volume',
            'product_type', 'taxable', 'dynamic_attributes',
            'applicable_tax_types', 'applicable_tax_type_ids',
            'custom_tax_rates', 'custom_tax_rate_ids',
            'tax_breakdown', 'total_tax_amount', 'final_price',
            'main_image', 'images', 'attribute_values', 'is_active',
            'created_at', 'updated_at',
            # Специфічні поля для типів продуктів
            'food_expiration_date', 'food_storage_temp', 'food_ingredients',
            'industrial_warranty_period', 'industrial_material', 'industrial_brand'
        ]
        read_only_fields = ['slug', 'created_at', 'updated_at', 'volume',
                            'tax_breakdown', 'total_tax_amount', 'final_price']

    def get_tax_breakdown(self, obj):
        """Повертає детальний розрахунок податків"""
        quantity = self.context.get('request').query_params.get('quantity', 1)
        try:
            quantity = int(quantity)
        except (ValueError, TypeError):
            quantity = 1

        return obj.calculate_taxes(quantity=quantity)

    def get_total_tax_amount(self, obj):
        """Повертає загальну суму податків"""
        quantity = self.context.get('request').query_params.get('quantity', 1)
        try:
            quantity = int(quantity)
        except (ValueError, TypeError):
            quantity = 1

        return obj.calculate_total_tax_amount(quantity=quantity)

    def get_final_price(self, obj):
        """Повертає кінцеву ціну продукту з урахуванням податків"""
        quantity = self.context.get('request').query_params.get('quantity', 1)
        try:
            quantity = int(quantity)
        except (ValueError, TypeError):
            quantity = 1

        include_taxes = self.context.get('request').query_params.get('include_taxes', 'true').lower() == 'true'
        return obj.calculate_final_price(quantity=quantity, include_taxes=include_taxes)

    def create(self, validated_data):
        """Створює продукт з динамічними атрибутами"""
        # Вилучаємо ManyToMany поля
        applicable_tax_types = validated_data.pop('applicable_tax_types', None)
        custom_tax_rates = validated_data.pop('custom_tax_rates', None)

        # Вилучаємо спеціальні атрибути для різних типів продуктів
        food_attrs = {}
        industrial_attrs = {}

        for attr in list(validated_data.keys()):
            if attr.startswith('food_'):
                food_attrs[attr] = validated_data.pop(attr)
            elif attr.startswith('industrial_'):
                industrial_attrs[attr] = validated_data.pop(attr)

        # Створюємо продукт
        product = Product.objects.create(**validated_data)

        # Додаємо ManyToMany зв'язки
        if applicable_tax_types:
            product.applicable_tax_types.set(applicable_tax_types)

        if custom_tax_rates:
            product.custom_tax_rates.set(custom_tax_rates)

        # Додаємо специфічні атрибути для типу продукту
        if product.product_type == 'food':
            for key, value in food_attrs.items():
                product.set_attribute(key, value)
        elif product.product_type == 'industrial':
            for key, value in industrial_attrs.items():
                product.set_attribute(key, value)

        return product

    def update(self, instance, validated_data):
        """Оновлює продукт з динамічними атрибутами"""
        # Вилучаємо ManyToMany поля
        applicable_tax_types = validated_data.pop('applicable_tax_types', None)
        custom_tax_rates = validated_data.pop('custom_tax_rates', None)

        # Вилучаємо спеціальні атрибути для різних типів продуктів
        food_attrs = {}
        industrial_attrs = {}

        for attr in list(validated_data.keys()):
            if attr.startswith('food_'):
                food_attrs[attr] = validated_data.pop(attr)
            elif attr.startswith('industrial_'):
                industrial_attrs[attr] = validated_data.pop(attr)

        # Оновлюємо базові поля продукту
        for attr, value in validated_data.items():
            if attr != 'attributes_json':  # Обробляємо окремо
                setattr(instance, attr, value)

        # Оновлюємо ManyToMany зв'язки
        if applicable_tax_types is not None:
            instance.applicable_tax_types.set(applicable_tax_types)

        if custom_tax_rates is not None:
            instance.custom_tax_rates.set(custom_tax_rates)

        # Додаємо специфічні атрибути для типу продукту
        if instance.product_type == 'food':
            for key, value in food_attrs.items():
                instance.set_attribute(key, value)
        elif instance.product_type == 'industrial':
            for key, value in industrial_attrs.items():
                instance.set_attribute(key, value)

        instance.save()
        return instance