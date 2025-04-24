# backend/LWH/api/v1/warehouses/views.py
from django.shortcuts import render, get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

from .models import Warehouse, Stock, Address, WarehouseImage, StockImage
from .serializers import (
    WarehouseSerializer, StockSerializer, AddressSerializer,
    WarehouseImageSerializer, StockImageSerializer
)

from ..utils.image_services import validate_image, process_image, get_image_metadata, generate_thumbnails
from django.db.models import Max


@api_view(['GET', 'POST'])
def warehouse_list(request):
    """
    List all warehouses, or create a new warehouse.
    """
    if request.method == 'GET':
        warehouses = Warehouse.objects.all()
        serializer = WarehouseSerializer(warehouses, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = WarehouseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def warehouse_detail(request, pk):
    """
    Retrieve, update or delete a warehouse.
    """
    warehouse = get_object_or_404(Warehouse, pk=pk)

    if request.method == 'GET':
        serializer = WarehouseSerializer(warehouse)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = WarehouseSerializer(warehouse, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        warehouse.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
def stock_list(request, warehouse_id):
    """
    List all stocks in a warehouse, or create a new stock.
    """
    warehouse = get_object_or_404(Warehouse, pk=warehouse_id)

    if request.method == 'GET':
        stocks = Stock.objects.filter(warehouse=warehouse)
        serializer = StockSerializer(stocks, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = StockSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(warehouse=warehouse)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def stock_detail(request, warehouse_id, pk):
    """
    Retrieve, update or delete a stock.
    """
    warehouse = get_object_or_404(Warehouse, pk=warehouse_id)
    stock = get_object_or_404(Stock, pk=pk, warehouse=warehouse)

    if request.method == 'GET':
        serializer = StockSerializer(stock)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = StockSerializer(stock, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        stock.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
def address_list(request):
    """
    List all addresses, or create a new address.
    """
    if request.method == 'GET':
        addresses = Address.objects.all()
        serializer = AddressSerializer(addresses, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = AddressSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def address_detail(request, pk):
    """
    Retrieve, update or delete an address.
    """
    address = get_object_or_404(Address, pk=pk)

    if request.method == 'GET':
        serializer = AddressSerializer(address)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = AddressSerializer(address, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        address.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
@parser_classes([MultiPartParser, FormParser])
def warehouse_images(request, warehouse_id):
    """
    List all images for a warehouse, or create a new image.
    """
    warehouse = get_object_or_404(Warehouse, pk=warehouse_id)

    if request.method == 'GET':
        images = WarehouseImage.objects.filter(warehouse=warehouse).order_by('order', '-created_at')
        serializer = WarehouseImageSerializer(images, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        # Check if user is the warehouse owner
        if warehouse.owner != request.user:
            return Response(
                {"detail": "You don't have permission to add images to this warehouse."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Get image file from request
        image_file = request.FILES.get('image')
        if not image_file:
            return Response(
                {"detail": "No image file provided."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate image
        is_valid, error_message = validate_image(
            image_file,
            max_size=10 * 1024 * 1024,  # 10MB
            formats=['.jpg', '.jpeg', '.png', '.gif', '.webp']
        )
        if not is_valid:
            return Response(
                {"detail": error_message},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Process image
        processed_image = process_image(
            image_file,
            quality=85,
            max_width=2000,
            max_height=2000
        )

        # Get image metadata
        metadata = get_image_metadata(image_file)

        # Create a new serializer instance with processed file
        serializer_data = request.data.copy()
        serializer_data['image'] = processed_image

        serializer = WarehouseImageSerializer(data=serializer_data)
        if serializer.is_valid():
            # Add additional data
            serializer.validated_data['warehouse'] = warehouse

            # Determine if this is the main image
            is_main = warehouse.images.count() == 0 or request.data.get('is_main') == 'true'
            serializer.validated_data['is_main'] = is_main

            # Set order if not provided
            if 'order' not in serializer.validated_data:
                # Get the max order value and add 1
                max_order = warehouse.images.aggregate(Max('order'))['order__max'] or 0
                serializer.validated_data['order'] = max_order + 1

            # Save image
            image = serializer.save()

            # Generate thumbnails
            thumbnails = generate_thumbnails(
                image_file,
                image.image.name,
                sizes={
                    'small': (150, 150),
                    'medium': (300, 300),
                    'large': (600, 600)
                }
            )

            # Return response with metadata
            response_data = serializer.data
            response_data['thumbnails'] = thumbnails
            response_data['metadata'] = metadata

            return Response(response_data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@parser_classes([MultiPartParser, FormParser])
def warehouse_image_detail(request, warehouse_id, pk):
    """
    Retrieve, update or delete a warehouse image.
    """
    warehouse = get_object_or_404(Warehouse, pk=warehouse_id)
    image = get_object_or_404(WarehouseImage, pk=pk, warehouse=warehouse)

    if request.method == 'GET':
        serializer = WarehouseImageSerializer(image)

        # Add metadata to response
        response_data = serializer.data
        response_data['metadata'] = get_image_metadata(image.image)

        return Response(response_data)

    elif request.method == 'PUT':
        # Check permissions
        if warehouse.owner != request.user:
            return Response(
                {"detail": "You don't have permission to edit this warehouse's images."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Handle image file update if provided
        image_file = request.FILES.get('image')
        if image_file:
            # Validate image
            is_valid, error_message = validate_image(
                image_file,
                max_size=10 * 1024 * 1024,  # 10MB
                formats=['.jpg', '.jpeg', '.png', '.gif', '.webp']
            )
            if not is_valid:
                return Response(
                    {"detail": error_message},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Process image
            processed_image = process_image(
                image_file,
                quality=85,
                max_width=2000,
                max_height=2000
            )

            # Update serializer data with processed file
            serializer_data = request.data.copy()
            serializer_data['image'] = processed_image
        else:
            serializer_data = request.data

        serializer = WarehouseImageSerializer(image, data=serializer_data, partial=True)
        if serializer.is_valid():
            # Handle is_main flag
            if 'is_main' in request.data and request.data.get('is_main') == 'true':
                serializer.validated_data['is_main'] = True

            # Save updated image
            updated_image = serializer.save()

            # Return response with metadata
            response_data = serializer.data
            response_data['metadata'] = get_image_metadata(updated_image.image)

            return Response(response_data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        # Check permissions
        if warehouse.owner != request.user:
            return Response(
                {"detail": "You don't have permission to delete this warehouse's images."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Check if it's the main image and if there are other images
        if image.is_main and warehouse.images.count() > 1:
            # Find another image to set as main
            new_main = warehouse.images.exclude(pk=image.pk).first()
            if new_main:
                new_main.is_main = True
                new_main.save()

        # Delete the image
        image.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
@parser_classes([MultiPartParser, FormParser])
def stock_images(request, warehouse_id, stock_id):
    """
    List all images for a stock, or create a new image.
    """
    warehouse = get_object_or_404(Warehouse, pk=warehouse_id)
    stock = get_object_or_404(Stock, pk=stock_id, warehouse=warehouse)

    if request.method == 'GET':
        images = StockImage.objects.filter(stock=stock).order_by('order', '-created_at')
        serializer = StockImageSerializer(images, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        # Check if user is the warehouse owner
        if warehouse.owner != request.user:
            return Response(
                {"detail": "You don't have permission to add images to this stock."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Get image file from request
        image_file = request.FILES.get('image')
        if not image_file:
            return Response(
                {"detail": "No image file provided."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate image
        is_valid, error_message = validate_image(
            image_file,
            max_size=10 * 1024 * 1024,  # 10MB
            formats=['.jpg', '.jpeg', '.png', '.gif', '.webp']
        )
        if not is_valid:
            return Response(
                {"detail": error_message},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Process image
        processed_image = process_image(
            image_file,
            quality=85,
            max_width=2000,
            max_height=2000
        )

        # Get image metadata
        metadata = get_image_metadata(image_file)

        # Create a new serializer instance with processed file
        serializer_data = request.data.copy()
        serializer_data['image'] = processed_image

        serializer = StockImageSerializer(data=serializer_data)
        if serializer.is_valid():
            # Add additional data
            serializer.validated_data['stock'] = stock

            # Determine if this is the main image
            is_main = stock.images.count() == 0 or request.data.get('is_main') == 'true'
            serializer.validated_data['is_main'] = is_main

            # Set order if not provided
            if 'order' not in serializer.validated_data:
                # Get the max order value and add 1
                max_order = stock.images.aggregate(Max('order'))['order__max'] or 0
                serializer.validated_data['order'] = max_order + 1

            # Save image
            image = serializer.save()

            # Generate thumbnails
            thumbnails = generate_thumbnails(
                image_file,
                image.image.name,
                sizes={
                    'small': (150, 150),
                    'medium': (300, 300),
                    'large': (600, 600)
                }
            )

            # Return response with metadata
            response_data = serializer.data
            response_data['thumbnails'] = thumbnails
            response_data['metadata'] = metadata

            return Response(response_data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@parser_classes([MultiPartParser, FormParser])
def stock_image_detail(request, warehouse_id, stock_id, pk):
    """
    Retrieve, update or delete a stock image.
    """
    warehouse = get_object_or_404(Warehouse, pk=warehouse_id)
    stock = get_object_or_404(Stock, pk=stock_id, warehouse=warehouse)
    image = get_object_or_404(StockImage, pk=pk, stock=stock)

    if request.method == 'GET':
        serializer = StockImageSerializer(image)

        # Add metadata to response
        response_data = serializer.data
        response_data['metadata'] = get_image_metadata(image.image)

        return Response(response_data)

    elif request.method == 'PUT':
        # Check permissions
        if warehouse.owner != request.user:
            return Response(
                {"detail": "You don't have permission to edit this stock's images."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Handle image file update if provided
        image_file = request.FILES.get('image')
        if image_file:
            # Validate image
            is_valid, error_message = validate_image(
                image_file,
                max_size=10 * 1024 * 1024,  # 10MB
                formats=['.jpg', '.jpeg', '.png', '.gif', '.webp']
            )
            if not is_valid:
                return Response(
                    {"detail": error_message},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Process image
            processed_image = process_image(
                image_file,
                quality=85,
                max_width=2000,
                max_height=2000
            )

            # Update serializer data with processed file
            serializer_data = request.data.copy()
            serializer_data['image'] = processed_image
        else:
            serializer_data = request.data

        serializer = StockImageSerializer(image, data=serializer_data, partial=True)
        if serializer.is_valid():
            # Handle is_main flag
            if 'is_main' in request.data and request.data.get('is_main') == 'true':
                serializer.validated_data['is_main'] = True

            # Save updated image
            updated_image = serializer.save()

            # Return response with metadata
            response_data = serializer.data
            response_data['metadata'] = get_image_metadata(updated_image.image)

            return Response(response_data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        # Check permissions
        if warehouse.owner != request.user:
            return Response(
                {"detail": "You don't have permission to delete this stock's images."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Check if it's the main image and if there are other images
        if image.is_main and stock.images.count() > 1:
            # Find another image to set as main
            new_main = stock.images.exclude(pk=image.pk).first()
            if new_main:
                new_main.is_main = True
                new_main.save()

        # Delete the image
        image.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reorder_warehouse_images(request, warehouse_id):
    """
    Reorder warehouse images.
    """
    warehouse = get_object_or_404(Warehouse, pk=warehouse_id)

    # Check permissions
    if warehouse.owner != request.user:
        return Response(
            {"detail": "You don't have permission to reorder this warehouse's images."},
            status=status.HTTP_403_FORBIDDEN
        )

    # Get image_id to order mapping from request
    image_orders = request.data.get('image_orders', [])
    if not image_orders or not isinstance(image_orders, list):
        return Response(
            {"detail": "Invalid data format. Expected a list of {image_id: order} objects."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Update order for each image
    updated_images = []
    for item in image_orders:
        try:
            image_id = item.get('image_id')
            new_order = item.get('order')

            if not image_id or new_order is None:
                continue

            image = WarehouseImage.objects.get(pk=image_id, warehouse=warehouse)
            image.order = new_order
            image.save(update_fields=['order'])
            updated_images.append(image_id)
        except WarehouseImage.DoesNotExist:
            pass

    return Response({
        "detail": f"Successfully reordered {len(updated_images)} images.",
        "updated_images": updated_images
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reorder_stock_images(request, warehouse_id, stock_id):
    """
    Reorder stock images.
    """
    warehouse = get_object_or_404(Warehouse, pk=warehouse_id)
    stock = get_object_or_404(Stock, pk=stock_id, warehouse=warehouse)

    # Check permissions
    if warehouse.owner != request.user:
        return Response(
            {"detail": "You don't have permission to reorder this stock's images."},
            status=status.HTTP_403_FORBIDDEN
        )

    # Get image_id to order mapping from request
    image_orders = request.data.get('image_orders', [])
    if not image_orders or not isinstance(image_orders, list):
        return Response(
            {"detail": "Invalid data format. Expected a list of {image_id: order} objects."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Update order for each image
    updated_images = []
    for item in image_orders:
        try:
            image_id = item.get('image_id')
            new_order = item.get('order')

            if not image_id or new_order is None:
                continue

            image = StockImage.objects.get(pk=image_id, stock=stock)
            image.order = new_order
            image.save(update_fields=['order'])
            updated_images.append(image_id)
        except StockImage.DoesNotExist:
            pass

    return Response({
        "detail": f"Successfully reordered {len(updated_images)} images.",
        "updated_images": updated_images
    })
