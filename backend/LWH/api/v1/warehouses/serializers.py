# backend/LWH/api/v1/warehouses/serializers.py
from rest_framework import serializers
from .models import Warehouse, Stock, Address

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'

class StockSerializer(serializers.ModelSerializer):
    volume = serializers.ReadOnlyField()

    class Meta:
        model = Stock
        fields = '__all__'
        read_only_fields = ('warehouse',)

class WarehouseSerializer(serializers.ModelSerializer):
    address = AddressSerializer()
    total_capacity = serializers.ReadOnlyField()
    available_capacity = serializers.ReadOnlyField()

    class Meta:
        model = Warehouse
        fields = '__all__'
        read_only_fields = ('owner',)

    def create(self, validated_data):
        address_data = validated_data.pop('address')
        address = Address.objects.create(**address_data)
        warehouse = Warehouse.objects.create(address=address, **validated_data)
        return warehouse

    def update(self, instance, validated_data):
        address_data = validated_data.pop('address', None)

        if address_data:
            address_serializer = AddressSerializer(instance.address, data=address_data)
            address_serializer.is_valid(raise_exception=True)
            address_serializer.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance