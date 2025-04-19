# backend/LWH/api/v1/warehouses/views.py
from django.shortcuts import render, get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

from .models import Warehouse, Stock, Address, WarehouseImage, StockImage
from .serializers import (
    WarehouseSerializer, StockSerializer, AddressSerializer,
    WarehouseImageSerializer, StockImageSerializer
)


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
        images = WarehouseImage.objects.filter(warehouse=warehouse)
        serializer = WarehouseImageSerializer(images, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = WarehouseImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(warehouse=warehouse)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
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
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = WarehouseImageSerializer(image, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
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
        images = StockImage.objects.filter(stock=stock)
        serializer = StockImageSerializer(images, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = StockImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(stock=stock)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
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
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = StockImageSerializer(image, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        image.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
