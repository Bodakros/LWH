# backend/LWH/api/v1/warehouses/serializers.py
from rest_framework import serializers
from .models import Warehouse, Stock, Address, WarehouseImage, StockImage

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'

class WarehouseImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = WarehouseImage
        fields = '__all__'
        read_only_fields = ('warehouse',)

class StockImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockImage
        fields = '__all__'
        read_only_fields = ('stock',)

class StockSerializer(serializers.ModelSerializer):
    volume = serializers.ReadOnlyField()
    images = StockImageSerializer(many=True, read_only=True)

    class Meta:
        model = Stock
        fields = '__all__'
        read_only_fields = ('warehouse',)

class WarehouseSerializer(serializers.ModelSerializer):
    address = AddressSerializer()
    total_capacity = serializers.ReadOnlyField()
    available_capacity = serializers.ReadOnlyField()
    images = WarehouseImageSerializer(many=True, read_only=True)
    main_image = serializers.SerializerMethodField()

    class Meta:
        model = Warehouse
        fields = '__all__'
        read_only_fields = ('owner',)

    def get_main_image(self, obj):
        main_image = obj.images.filter(is_main=True).first()
        if main_image:
            return WarehouseImageSerializer(main_image).data
        return None

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