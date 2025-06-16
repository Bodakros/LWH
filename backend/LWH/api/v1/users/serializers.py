# api/v1/users/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import SellerProfile, OwnerProfile

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    is_seller = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()
    phone_number = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name',
                  'is_seller', 'is_owner', 'phone_number')
        read_only_fields = ('id',)

    def get_is_seller(self, obj):
        return hasattr(obj, 'seller_profile')

    def get_is_owner(self, obj):
        return hasattr(obj, 'owner_profile')

    def get_phone_number(self, obj):
        if hasattr(obj, 'user_profile'):
            return obj.user_profile.phone_number
        return None


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'email', 'first_name', 'last_name')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Паролі не співпадають"})
        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class SellerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellerProfile
        fields = ('nickname', 'description', 'verified', 'seller_image')


class OwnerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = OwnerProfile
        fields = ('nickname', 'description', 'verified', 'owner_image')
