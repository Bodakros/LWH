from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.db.models import Q
from django.utils import timezone

# Переконаємося, що всі необхідні константи статусів доступні
from rest_framework.status import (
    HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND
)

from .models import (
    InventoryItem, InventoryMovement, InventoryAudit,
    ReceivingRecord, ReceivingItem
)
from .serializers import (
    InventoryItemSerializer, InventoryMovementSerializer, InventoryAuditSerializer,
    ReceivingRecordSerializer, ReceivingItemSerializer
)
from ..users.permissions import IsSeller, IsOwner


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def inventory_item_list(request):
    """
    Список інвентарних записів або створення нового запису.
    """
    if request.method == 'GET':
        # Фільтрація за різними параметрами
        product_id = request.query_params.get('product')
        stock_id = request.query_params.get('stock')
        warehouse_id = request.query_params.get('warehouse')
        status = request.query_params.get('status')
        batch_number = request.query_params.get('batch_number')

        # Базова фільтрація за правами доступу
        if request.user.is_seller:
            # Продавці бачать тільки свої товари
            queryset = InventoryItem.objects.filter(seller=request.user)
        elif request.user.is_owner:
            # Власники складів бачать товари на своїх складах
            queryset = InventoryItem.objects.filter(warehouse__owner=request.user)
        else:
            # Звичайні користувачі не мають доступу до інвентарю
            return Response({"detail": "Немає достатніх прав для перегляду інвентарю"},
                            status=HTTP_403_FORBIDDEN)

        # Додаткові фільтри
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        if stock_id:
            queryset = queryset.filter(stock_id=stock_id)
        if warehouse_id:
            queryset = queryset.filter(warehouse_id=warehouse_id)
        if status:
            queryset = queryset.filter(status=status)
        if batch_number:
            queryset = queryset.filter(batch_number=batch_number)

        serializer = InventoryItemSerializer(queryset, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        # Тільки продавці можуть створювати інвентарні записи
        if not request.user.is_seller:
            return Response({"detail": "Тільки продавці можуть створювати інвентарні записи"},
                            status=HTTP_403_FORBIDDEN)

        serializer = InventoryItemSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=HTTP_201_CREATED)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def inventory_item_detail(request, pk):
    """
    Отримання, оновлення або видалення інвентарного запису.
    """
    try:
        inventory_item = InventoryItem.objects.get(pk=pk)
    except InventoryItem.DoesNotExist:
        return Response({"detail": "Інвентарний запис не знайдено"}, status=HTTP_404_NOT_FOUND)

    # Перевірка прав доступу
    if request.user.is_seller and inventory_item.seller != request.user:
        return Response({"detail": "Ви не маєте прав доступу до цього інвентарного запису"},
                        status=HTTP_403_FORBIDDEN)

    if request.user.is_owner and inventory_item.warehouse.owner != request.user:
        return Response({"detail": "Ви не маєте прав доступу до цього інвентарного запису"},
                        status=status.HTTP_403_FORBIDDEN)

    if not (request.user.is_seller or request.user.is_owner):
        return Response({"detail": "Немає достатніх прав для доступу до інвентарю"},
                        status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        serializer = InventoryItemSerializer(inventory_item)
        return Response(serializer.data)

    elif request.method == 'PUT':
        # Тільки продавець, якому належить запис, може його оновлювати
        if inventory_item.seller != request.user:
            return Response({"detail": "Ви не маєте прав для редагування цього запису"},
                            status=status.HTTP_403_FORBIDDEN)

        serializer = InventoryItemSerializer(inventory_item, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        # Тільки продавець, якому належить запис, може його видаляти
        if inventory_item.seller != request.user:
            return Response({"detail": "Ви не маєте прав для видалення цього запису"},
                            status=status.HTTP_403_FORBIDDEN)

        inventory_item.delete()
        return Response(status=HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def inventory_movement_list(request):
    """
    Список переміщень інвентарю або створення нового переміщення.
    """
    if request.method == 'GET':
        # Фільтрація за різними параметрами
        product_id = request.query_params.get('product')
        source_stock_id = request.query_params.get('source_stock')
        destination_stock_id = request.query_params.get('destination_stock')
        reason = request.query_params.get('reason')

        # Базова фільтрація за правами доступу
        if request.user.is_seller:
            # Продавці бачать тільки свої переміщення
            queryset = InventoryMovement.objects.filter(seller=request.user)
        elif request.user.is_owner:
            # Власники складів бачать переміщення на своїх складах
            warehouse_ids = list(request.user.owned_warehouses.values_list('id', flat=True))
            queryset = InventoryMovement.objects.filter(
                Q(source_stock__warehouse__id__in=warehouse_ids) |
                Q(destination_stock__warehouse__id__in=warehouse_ids)
            )
        else:
            # Звичайні користувачі не мають доступу до переміщень
            return Response({"detail": "Немає достатніх прав для перегляду переміщень інвентарю"},
                            status=status.HTTP_403_FORBIDDEN)

        # Додаткові фільтри
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        if source_stock_id:
            queryset = queryset.filter(source_stock_id=source_stock_id)
        if destination_stock_id:
            queryset = queryset.filter(destination_stock_id=destination_stock_id)
        if reason:
            queryset = queryset.filter(reason=reason)

        serializer = InventoryMovementSerializer(queryset, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        # Тільки продавці можуть створювати переміщення
        if not request.user.is_seller:
            return Response({"detail": "Тільки продавці можуть створювати переміщення інвентарю"},
                            status=status.HTTP_403_FORBIDDEN)

        serializer = InventoryMovementSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            movement = serializer.save()

            # Тут логіка оновлення вихідного та цільового інвентарних записів
            # В реальному додатку це може бути винесено в сервісний шар або сигнали

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def inventory_movement_detail(request, pk):
    """
    Отримання детальної інформації про переміщення інвентарю.
    """
    try:
        movement = InventoryMovement.objects.get(pk=pk)
    except InventoryMovement.DoesNotExist:
        return Response({"detail": "Переміщення не знайдено"}, status=status.HTTP_404_NOT_FOUND)

    # Перевірка прав доступу
    is_seller_owner = request.user.is_seller and movement.seller == request.user
    is_warehouse_owner = request.user.is_owner and (
            movement.source_stock.warehouse.owner == request.user or
            movement.destination_stock.warehouse.owner == request.user
    )

    if not (is_seller_owner or is_warehouse_owner):
        return Response({"detail": "Ви не маєте прав доступу до цього переміщення"},
                        status=status.HTTP_403_FORBIDDEN)

    serializer = InventoryMovementSerializer(movement)
    return Response(serializer.data)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def inventory_audit_list(request):
    """
    Список аудитів інвентарю або створення нового аудиту.
    """
    if request.method == 'GET':
        # Фільтрація за різними параметрами
        inventory_item_id = request.query_params.get('inventory_item')
        resolved = request.query_params.get('resolved')

        # Базова фільтрація за правами доступу
        if request.user.is_seller:
            # Продавці бачать аудити своїх товарів
            queryset = InventoryAudit.objects.filter(inventory_item__seller=request.user)
        elif request.user.is_owner:
            # Власники складів бачать аудити на своїх складах
            queryset = InventoryAudit.objects.filter(inventory_item__warehouse__owner=request.user)
        else:
            # Звичайні користувачі не мають доступу до аудитів
            return Response({"detail": "Немає достатніх прав для перегляду аудитів інвентарю"},
                            status=status.HTTP_403_FORBIDDEN)

        # Додаткові фільтри
        if inventory_item_id:
            queryset = queryset.filter(inventory_item_id=inventory_item_id)
        if resolved is not None:
            resolved_bool = resolved.lower() == 'true'
            queryset = queryset.filter(resolved=resolved_bool)

        serializer = InventoryAuditSerializer(queryset, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        # Продавці та власники складів можуть створювати аудити
        if not (request.user.is_seller or request.user.is_owner):
            return Response({"detail": "Немає достатніх прав для створення аудитів"},
                            status=status.HTTP_403_FORBIDDEN)

        serializer = InventoryAuditSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def inventory_audit_detail(request, pk):
    """
    Отримання або оновлення аудиту інвентарю.
    """
    try:
        audit = InventoryAudit.objects.get(pk=pk)
    except InventoryAudit.DoesNotExist:
        return Response({"detail": "Аудит не знайдено"}, status=status.HTTP_404_NOT_FOUND)

    # Перевірка прав доступу
    is_seller_owner = request.user.is_seller and audit.inventory_item.seller == request.user
    is_warehouse_owner = request.user.is_owner and audit.inventory_item.warehouse.owner == request.user

    if not (is_seller_owner or is_warehouse_owner):
        return Response({"detail": "Ви не маєте прав доступу до цього аудиту"},
                        status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        serializer = InventoryAuditSerializer(audit)
        return Response(serializer.data)

    elif request.method == 'PUT':
        # Перевірка чи аудит вже вирішено
        if audit.resolved and not request.user.is_staff:
            return Response({"detail": "Цей аудит вже вирішено і не може бути змінений"},
                            status=status.HTTP_400_BAD_REQUEST)

        # Часткове оновлення для вирішення аудиту
        serializer = InventoryAuditSerializer(audit, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            # Якщо змінюється статус на "вирішено"
            if not audit.resolved and serializer.validated_data.get('resolved', False):
                serializer.validated_data['resolution_date'] = timezone.now()
                serializer.validated_data['resolved_by'] = request.user

            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def receiving_record_list(request):
    """
    Список записів про надходження або створення нового запису.
    """
    if request.method == 'GET':
        # Фільтрація за різними параметрами
        warehouse_id = request.query_params.get('warehouse')
        status_param = request.query_params.get('status')

        # Базова фільтрація за правами доступу
        if request.user.is_owner:
            # Власники складів бачать надходження на свої склади
            queryset = ReceivingRecord.objects.filter(warehouse__owner=request.user)
        elif request.user.is_seller:
            # Продавці бачать надходження, де вони є постачальниками
            queryset = ReceivingRecord.objects.filter(supplier_user=request.user)
        else:
            # Звичайні користувачі не мають доступу до надходжень
            return Response({"detail": "Немає достатніх прав для перегляду записів про надходження"},
                            status=status.HTTP_403_FORBIDDEN)

        # Додаткові фільтри
        if warehouse_id:
            queryset = queryset.filter(warehouse_id=warehouse_id)
        if status_param:
            queryset = queryset.filter(status=status_param)

        serializer = ReceivingRecordSerializer(queryset, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        # Тільки власники складів можуть створювати записи про надходження
        if not request.user.is_owner:
            return Response({"detail": "Тільки власники складів можуть створювати записи про надходження"},
                            status=status.HTTP_403_FORBIDDEN)

        serializer = ReceivingRecordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            # Перевірка, чи користувач є власником вказаного складу
            warehouse = serializer.validated_data.get('warehouse')
            if warehouse.owner != request.user:
                return Response({"detail": "Ви можете створювати записи про надходження тільки для своїх складів"},
                                status=status.HTTP_403_FORBIDDEN)

            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def receiving_record_detail(request, pk):
    """
    Отримання, оновлення або видалення запису про надходження.
    """
    try:
        receiving_record = ReceivingRecord.objects.get(pk=pk)
    except ReceivingRecord.DoesNotExist:
        return Response({"detail": "Запис про надходження не знайдено"}, status=status.HTTP_404_NOT_FOUND)

    # Перевірка прав доступу
    is_warehouse_owner = request.user.is_owner and receiving_record.warehouse.owner == request.user
    is_receiver = receiving_record.received_by == request.user

    if not (is_warehouse_owner or is_receiver):
        return Response({"detail": "Ви не маєте прав доступу до цього запису про надходження"},
                        status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        serializer = ReceivingRecordSerializer(receiving_record)
        return Response(serializer.data)

    elif request.method == 'PUT':
        # Тільки власник складу може оновлювати запис
        if not is_warehouse_owner:
            return Response({"detail": "Тільки власник складу може оновлювати запис про надходження"},
                            status=status.HTTP_403_FORBIDDEN)

        serializer = ReceivingRecordSerializer(receiving_record, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        # Тільки власник складу може видаляти запис
        if not is_warehouse_owner:
            return Response({"detail": "Тільки власник складу може видаляти запис про надходження"},
                            status=status.HTTP_403_FORBIDDEN)

        # Перевірка, чи можна видалити запис
        if receiving_record.status not in ['pending', 'cancelled']:
            return Response({"detail": "Можна видаляти тільки записи зі статусом 'Очікується' або 'Скасовано'"},
                            status=status.HTTP_400_BAD_REQUEST)

        receiving_record.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def receiving_item_list(request, receiving_record_id):
    """
    Список елементів надходження або створення нового елемента.
    """
    try:
        receiving_record = ReceivingRecord.objects.get(pk=receiving_record_id)
    except ReceivingRecord.DoesNotExist:
        return Response({"detail": "Запис про надходження не знайдено"}, status=status.HTTP_404_NOT_FOUND)

    # Перевірка прав доступу
    is_warehouse_owner = request.user.is_owner and receiving_record.warehouse.owner == request.user
    is_receiver = receiving_record.received_by == request.user

    if not (is_warehouse_owner or is_receiver):
        return Response({"detail": "Ви не маєте прав доступу до цього запису про надходження"},
                        status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        items = ReceivingItem.objects.filter(receiving_record=receiving_record)
        serializer = ReceivingItemSerializer(items, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        # Тільки власник складу або призначений приймальник може додавати елементи
        request.data['receiving_record'] = receiving_record_id

        serializer = ReceivingItemSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            # Перевірка статусу запису
            if receiving_record.status == 'cancelled':
                return Response({"detail": "Неможливо додати елементи до скасованого запису про надходження"},
                                status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def receiving_item_detail(request, receiving_record_id, pk):
    """
    Отримання, оновлення або видалення елемента надходження.
    """
    try:
        receiving_record = ReceivingRecord.objects.get(pk=receiving_record_id)
        receiving_item = ReceivingItem.objects.get(pk=pk, receiving_record=receiving_record)
    except ReceivingRecord.DoesNotExist:
        return Response({"detail": "Запис про надходження не знайдено"}, status=status.HTTP_404_NOT_FOUND)
    except ReceivingItem.DoesNotExist:
        return Response({"detail": "Елемент надходження не знайдено"}, status=status.HTTP_404_NOT_FOUND)

    # Перевірка прав доступу
    is_warehouse_owner = request.user.is_owner and receiving_record.warehouse.owner == request.user
    is_receiver = receiving_record.received_by == request.user

    if not (is_warehouse_owner or is_receiver):
        return Response({"detail": "Ви не маєте прав доступу до цього елемента надходження"},
                        status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        serializer = ReceivingItemSerializer(receiving_item)
        return Response(serializer.data)

    elif request.method == 'PUT':
        # Перевірка статусу запису
        if receiving_record.status == 'cancelled':
            return Response({"detail": "Неможливо оновити елементи скасованого запису про надходження"},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = ReceivingItemSerializer(receiving_item, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            # Якщо оновлюється кількість отриманого товару, оновити складські записи
            old_received_quantity = receiving_item.received_quantity
            new_received_quantity = serializer.validated_data.get('received_quantity', old_received_quantity)

            # Тут може бути логіка для оновлення складського запасу
            # Якщо нова кількість більша, додати різницю до інвентарю
            # Якщо менша, відняти різницю (якщо це можливо)

            item = serializer.save()

            # Оновити інвентарний запис, якщо він уже існує
            if item.inventory_item and old_received_quantity != new_received_quantity:
                inventory_item = item.inventory_item
                quantity_difference = new_received_quantity - old_received_quantity

                inventory_item.quantity += quantity_difference
                inventory_item.save()

            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        # Тільки власник складу може видаляти елементи
        if not is_warehouse_owner:
            return Response({"detail": "Тільки власник складу може видаляти елементи надходження"},
                            status=status.HTTP_403_FORBIDDEN)

        # Перевірка, чи елемент ще не оброблено
        if receiving_item.status != 'pending':
            return Response({"detail": "Можна видаляти тільки елементи зі статусом 'Очікується'"},
                            status=status.HTTP_400_BAD_REQUEST)

        receiving_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def receive_item(request, receiving_record_id, pk):
    """
    Прийняття елемента надходження - створення інвентарного запису.
    """
    try:
        receiving_record = ReceivingRecord.objects.get(pk=receiving_record_id)
        receiving_item = ReceivingItem.objects.get(pk=pk, receiving_record=receiving_record)
    except ReceivingRecord.DoesNotExist:
        return Response({"detail": "Запис про надходження не знайдено"}, status=status.HTTP_404_NOT_FOUND)
    except ReceivingItem.DoesNotExist:
        return Response({"detail": "Елемент надходження не знайдено"}, status=status.HTTP_404_NOT_FOUND)

    # Перевірка прав доступу
    is_warehouse_owner = request.user.is_owner and receiving_record.warehouse.owner == request.user
    is_receiver = receiving_record.received_by == request.user

    if not (is_warehouse_owner or is_receiver):
        return Response({"detail": "Ви не маєте прав для прийняття товарів"},
                        status=status.HTTP_403_FORBIDDEN)

    # Перевірка, чи елемент уже прийнято
    if receiving_item.status == 'received':
        return Response({"detail": "Цей елемент уже прийнято"},
                        status=status.HTTP_400_BAD_REQUEST)

    # Перевірка, чи вказано комірку складу
    if not receiving_item.stock:
        return Response({"detail": "Необхідно вказати комірку складу для розміщення товару"},
                        status=status.HTTP_400_BAD_REQUEST)

    # Перевірка, чи вказано отриману кількість
    if receiving_item.received_quantity <= 0:
        return Response({"detail": "Отримана кількість повинна бути більше нуля"},
                        status=status.HTTP_400_BAD_REQUEST)

    # Знаходження власника продукту (продавця)
    if receiving_record.supplier_user and receiving_record.supplier_user.is_seller:
        seller = receiving_record.supplier_user
    else:
        # Якщо постачальник не є користувачем системи, використовуємо власника складу
        seller = receiving_record.warehouse.owner

    # Створення інвентарного запису
    inventory_item = InventoryItem.objects.create(
        product=receiving_item.product,
        stock=receiving_item.stock,
        warehouse=receiving_item.stock.warehouse,
        seller=seller,
        quantity=receiving_item.received_quantity,
        unit=receiving_item.unit,
        custom_unit=receiving_item.custom_unit,
        status='available',
        batch_number=receiving_item.batch_number,
        expiration_date=receiving_item.expiration_date,
        purchase_price=receiving_item.purchase_price,
        purchase_price_per_unit=receiving_item.purchase_price / receiving_item.received_quantity if receiving_item.purchase_price else None
    )

    # Оновлення елемента надходження
    receiving_item.inventory_item = inventory_item
    receiving_item.status = 'received'
    receiving_item.received_at = timezone.now()
    receiving_item.received_by = request.user
    receiving_item.save()

    # Оновлення запису про надходження
    receiving_record.received_items_count += 1
    if receiving_record.received_items_count >= receiving_record.expected_items_count:
        receiving_record.status = 'fully_received'
        receiving_record.completed_date = timezone.now()
    elif receiving_record.received_items_count > 0:
        receiving_record.status = 'partially_received'
    receiving_record.save()

    serializer = ReceivingItemSerializer(receiving_item)
    return Response(serializer.data)