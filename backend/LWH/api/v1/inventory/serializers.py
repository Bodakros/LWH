from rest_framework import serializers
from .models import (
    InventoryItem, InventoryMovement, InventoryAudit,
    ReceivingRecord, ReceivingItem
)
from ..products.serializers import ProductSerializer
from ..warehouses.serializers import StockSerializer, WarehouseSerializer


class InventoryItemSerializer(serializers.ModelSerializer):
    """Серіалізатор для інвентарних записів"""
    product_details = serializers.SerializerMethodField(read_only=True)
    stock_details = serializers.SerializerMethodField(read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    custom_unit_display = serializers.SerializerMethodField(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = InventoryItem
        fields = [
            'id', 'product', 'product_details', 'stock', 'stock_details',
            'warehouse', 'warehouse_name', 'seller', 'quantity', 'unit',
            'custom_unit', 'custom_unit_display', 'status', 'status_display',
            'batch_number', 'expiration_date', 'received_date',
            'purchase_price', 'purchase_price_per_unit', 'created_at', 'updated_at'
        ]
        read_only_fields = ['warehouse', 'created_at', 'updated_at']

    def get_product_details(self, obj):
        """Отримує базові деталі про продукт"""
        return {
            'id': obj.product.id,
            'name': obj.product.name,
            'sku': obj.product.sku,
            'category': obj.product.category.name if obj.product.category else None,
            'base_price': obj.product.base_price
        }

    def get_stock_details(self, obj):
        """Отримує базові деталі про комірку складу"""
        return {
            'id': obj.stock.id,
            'name': obj.stock.name,
            'location_code': obj.stock.location_code,
            'capacity': obj.stock.capacity
        }

    def get_custom_unit_display(self, obj):
        """Повертає відформатоване значення одиниці виміру"""
        if obj.unit == 'other' and obj.custom_unit:
            return obj.custom_unit
        return obj.get_unit_display()

    def validate(self, data):
        """Перевіряє правильність даних інвентарного запису"""
        # Перевіряємо, чи користувач є продавцем
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            if not request.user.is_seller:
                raise serializers.ValidationError("Тільки продавці можуть управляти інвентарем")

            # Перевіряємо, чи продавець є власником продукту
            product = data.get('product')
            if product and product.seller != request.user:
                raise serializers.ValidationError("Ви можете управляти тільки власними продуктами")

            # Встановлюємо продавця як поточного користувача
            data['seller'] = request.user

        # Перевіряємо, що комірка належить до відповідного складу
        stock = data.get('stock')
        if stock:
            data['warehouse'] = stock.warehouse

        # Перевіряємо одиницю виміру
        if data.get('unit') == 'other' and not data.get('custom_unit'):
            raise serializers.ValidationError({"custom_unit": "Необхідно вказати назву одиниці виміру для типу 'Інше'"})

        return data


class InventoryMovementSerializer(serializers.ModelSerializer):
    """Серіалізатор для руху інвентарю"""
    source_stock_details = serializers.SerializerMethodField(read_only=True)
    destination_stock_details = serializers.SerializerMethodField(read_only=True)
    product_details = serializers.SerializerMethodField(read_only=True)
    reason_display = serializers.CharField(source='get_reason_display', read_only=True)
    custom_unit_display = serializers.SerializerMethodField(read_only=True)
    initiated_by_username = serializers.CharField(source='initiated_by.username', read_only=True)

    class Meta:
        model = InventoryMovement
        fields = [
            'id', 'source_stock', 'source_stock_details', 'destination_stock',
            'destination_stock_details', 'product', 'product_details', 'seller',
            'quantity', 'unit', 'custom_unit', 'custom_unit_display', 'timestamp',
            'initiated_by', 'initiated_by_username', 'reason', 'reason_display',
            'source_inventory_item', 'destination_inventory_item', 'notes'
        ]
        read_only_fields = ['timestamp', 'initiated_by']

    def get_source_stock_details(self, obj):
        """Отримує базові деталі про вихідну комірку"""
        return {
            'id': obj.source_stock.id,
            'name': obj.source_stock.name,
            'location_code': obj.source_stock.location_code,
            'warehouse': obj.source_stock.warehouse.name
        }

    def get_destination_stock_details(self, obj):
        """Отримує базові деталі про цільову комірку"""
        return {
            'id': obj.destination_stock.id,
            'name': obj.destination_stock.name,
            'location_code': obj.destination_stock.location_code,
            'warehouse': obj.destination_stock.warehouse.name
        }

    def get_product_details(self, obj):
        """Отримує базові деталі про продукт"""
        return {
            'id': obj.product.id,
            'name': obj.product.name,
            'sku': obj.product.sku
        }

    def get_custom_unit_display(self, obj):
        """Повертає відформатоване значення одиниці виміру"""
        if obj.unit == 'other' and obj.custom_unit:
            return obj.custom_unit
        return obj.get_unit_display()

    def validate(self, data):
        """Перевіряє правильність даних для переміщення інвентарю"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            # Тільки продавці можуть створювати переміщення
            if not request.user.is_seller:
                raise serializers.ValidationError("Тільки продавці можуть переміщувати інвентар")

            # Встановлюємо ініціатора та продавця
            data['initiated_by'] = request.user
            data['seller'] = request.user

        # Перевірка, чи вихідна і цільова комірки відрізняються
        if data.get('source_stock') == data.get('destination_stock'):
            raise serializers.ValidationError({"destination_stock": "Вихідна і цільова комірки повинні відрізнятися"})

        # Перевірка доступності продукту у вихідній комірці
        source_stock = data.get('source_stock')
        product = data.get('product')
        quantity = data.get('quantity')

        if source_stock and product and quantity:
            # Перевіряємо наявність товару у вихідній комірці
            inventory_items = InventoryItem.objects.filter(
                stock=source_stock,
                product=product,
                status='available'
            )

            total_available = sum(item.quantity for item in inventory_items)

            if total_available < quantity:
                raise serializers.ValidationError({
                    "quantity": f"Недостатня кількість доступного товару. Доступно: {total_available}"
                })

        # Перевірка одиниці виміру
        if data.get('unit') == 'other' and not data.get('custom_unit'):
            raise serializers.ValidationError({"custom_unit": "Необхідно вказати назву одиниці виміру для типу 'Інше'"})

        return data


class InventoryAuditSerializer(serializers.ModelSerializer):
    """Серіалізатор для аудиту інвентарю"""
    inventory_item_details = serializers.SerializerMethodField(read_only=True)
    unit_display = serializers.SerializerMethodField(read_only=True)
    audited_by_username = serializers.CharField(source='audited_by.username', read_only=True)
    resolution_type_display = serializers.CharField(source='get_resolution_type_display', read_only=True)

    class Meta:
        model = InventoryAudit
        fields = [
            'id', 'inventory_item', 'inventory_item_details', 'expected_quantity',
            'actual_quantity', 'unit', 'custom_unit', 'unit_display', 'discrepancy',
            'audit_date', 'audited_by', 'audited_by_username', 'notes', 'resolved',
            'resolution_type', 'resolution_type_display', 'resolution_date',
            'resolved_by', 'resolution_notes'
        ]
        read_only_fields = ['discrepancy', 'audit_date', 'audited_by']

    def get_inventory_item_details(self, obj):
        """Отримує базові деталі про інвентарний запис"""
        inventory_item = obj.inventory_item
        return {
            'id': inventory_item.id,
            'product': {
                'id': inventory_item.product.id,
                'name': inventory_item.product.name,
                'sku': inventory_item.product.sku
            },
            'stock': {
                'id': inventory_item.stock.id,
                'name': inventory_item.stock.name,
                'location_code': inventory_item.stock.location_code
            },
            'warehouse': inventory_item.warehouse.name,
            'status': inventory_item.get_status_display()
        }

    def get_unit_display(self, obj):
        """Повертає відформатоване значення одиниці виміру"""
        if obj.unit == 'other' and obj.custom_unit:
            return obj.custom_unit
        return obj.get_unit_display()

    def validate(self, data):
        """Перевіряє правильність даних аудиту"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            # Перевіряємо права доступу
            inventory_item = data.get('inventory_item')
            if inventory_item and inventory_item.seller != request.user and not request.user.is_owner:
                raise serializers.ValidationError("Ви можете проводити аудит тільки власних товарів або як власник складу")

            # Встановлюємо аудитора
            data['audited_by'] = request.user

        # Перевірка одиниці виміру
        if data.get('unit') == 'other' and not data.get('custom_unit'):
            raise serializers.ValidationError({"custom_unit": "Необхідно вказати назву одиниці виміру для типу 'Інше'"})

        return data


class ReceivingItemSerializer(serializers.ModelSerializer):
    """Серіалізатор для елементів надходження"""
    product_details = serializers.SerializerMethodField(read_only=True)
    stock_details = serializers.SerializerMethodField(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    custom_unit_display = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ReceivingItem
        fields = [
            'id', 'receiving_record', 'product', 'product_details', 'expected_quantity',
            'received_quantity', 'unit', 'custom_unit', 'custom_unit_display', 'stock',
            'stock_details', 'batch_number', 'expiration_date', 'purchase_price',
            'notes', 'inventory_item', 'received_at', 'received_by', 'status', 'status_display'
        ]
        read_only_fields = ['received_at', 'inventory_item']

    def get_product_details(self, obj):
        """Отримує базові деталі про продукт"""
        return {
            'id': obj.product.id,
            'name': obj.product.name,
            'sku': obj.product.sku
        }

    def get_stock_details(self, obj):
        """Отримує базові деталі про комірку"""
        if not obj.stock:
            return None
        return {
            'id': obj.stock.id,
            'name': obj.stock.name,
            'location_code': obj.stock.location_code,
            'warehouse': obj.stock.warehouse.name
        }

    def get_custom_unit_display(self, obj):
        """Повертає відформатоване значення одиниці виміру"""
        if obj.unit == 'other' and obj.custom_unit:
            return obj.custom_unit
        return obj.get_unit_display()

    def validate(self, data):
        """Перевіряє правильність даних елемента надходження"""
        # Перевірка одиниці виміру
        if data.get('unit') == 'other' and not data.get('custom_unit'):
            raise serializers.ValidationError({"custom_unit": "Необхідно вказати назву одиниці виміру для типу 'Інше'"})

        # Перевірка кількості
        received_quantity = data.get('received_quantity', 0)
        if received_quantity < 0:
            raise serializers.ValidationError({"received_quantity": "Кількість не може бути від'ємною"})

        # Перевірка прав доступу
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            receiving_record = data.get('receiving_record')

            # Перевіряємо, чи користувач має право змінювати цей запис
            if receiving_record and request.method != 'GET':
                # Перевіряємо, чи це власник складу або користувач, призначений для приймання
                warehouse_owner = receiving_record.warehouse.owner == request.user
                is_receiver = receiving_record.received_by == request.user

                if not (warehouse_owner or is_receiver) and not request.user.is_staff:
                    raise serializers.ValidationError("Ви не маєте прав для зміни цього запису про надходження")

        return data


class ReceivingRecordSerializer(serializers.ModelSerializer):
    """Серіалізатор для записів про надходження"""
    items = ReceivingItemSerializer(many=True, read_only=True)
    warehouse_details = serializers.SerializerMethodField(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    received_by_username = serializers.CharField(source='received_by.username', read_only=True)

    class Meta:
        model = ReceivingRecord
        fields = [
            'id', 'supplier', 'supplier_user', 'warehouse', 'warehouse_details',
            'receipt_date', 'reference_number', 'status', 'status_display',
            'received_by', 'received_by_username', 'expected_items_count',
            'received_items_count', 'notes', 'created_at', 'updated_at',
            'completed_date', 'items'
        ]
        read_only_fields = ['receipt_date', 'received_items_count', 'created_at', 'updated_at', 'completed_date']

    def get_warehouse_details(self, obj):
        """Отримує базові деталі про склад"""
        return {
            'id': obj.warehouse.id,
            'name': obj.warehouse.name,
            'owner': {
                'id': obj.warehouse.owner.id,
                'username': obj.warehouse.owner.username
            },
            'address': str(obj.warehouse.address)
        }

    def validate(self, data):
        """Перевіряє правильність даних запису про надходження"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            # Перевіряємо права доступу
            warehouse = data.get('warehouse')

            if warehouse and request.method != 'GET':
                # Чи користувач є власником складу або призначеним для приймання
                is_warehouse_owner = warehouse.owner == request.user

                if not is_warehouse_owner and not request.user.is_staff:
                    raise serializers.ValidationError("Ви не маєте прав для створення/редагування записів про надходження для цього складу")

            # Встановлюємо користувача, який прийняв товар
            if not data.get('received_by'):
                data['received_by'] = request.user

        # Перевірка постачальника
        if not data.get('supplier') and not data.get('supplier_user'):
            raise serializers.ValidationError("Необхідно вказати постачальника (назву компанії або користувача)")

        return data