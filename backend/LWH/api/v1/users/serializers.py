from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import SellerAccount, OwnerAccount, UserSession

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    is_seller = serializers.ReadOnlyField()
    is_owner = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'phone_number', 'profile_image', 'is_email_verified',
            'is_seller', 'is_owner', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_email_verified']


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'password2', 'email', 'first_name', 'last_name', 'phone_number']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user


class SellerAccountSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = SellerAccount
        fields = [
            'id', 'nickname', 'description', 'seller_image', 'business_name',
            'tax_number', 'verified', 'is_active', 'password', 'password2',
            'total_sales', 'created_at', 'updated_at', 'last_login'
        ]
        read_only_fields = ['id', 'verified', 'total_sales', 'created_at', 'updated_at', 'last_login']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = self.context['request'].user

        if hasattr(user, 'seller_account'):
            raise serializers.ValidationError("User already has a seller account")

        seller_account = SellerAccount.objects.create(user=user, **validated_data)
        return seller_account

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        validated_data.pop('password2', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()
        return instance


class OwnerAccountSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = OwnerAccount
        fields = [
            'id', 'nickname', 'description', 'owner_image', 'company_name',
            'company_registration', 'warehouse_license', 'verified', 'is_active',
            'password', 'password2', 'created_at', 'updated_at', 'last_login'
        ]
        read_only_fields = ['id', 'verified', 'created_at', 'updated_at', 'last_login']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = self.context['request'].user

        if hasattr(user, 'owner_account'):
            raise serializers.ValidationError("User already has an owner account")

        owner_account = OwnerAccount.objects.create(user=user, **validated_data)
        return owner_account

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        validated_data.pop('password2', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()
        return instance


class UserSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSession
        fields = [
            'id', 'session_key', 'session_type', 'seller_account', 'owner_account',
            'created_at', 'expires_at', 'is_active'
        ]
        read_only_fields = ['id', 'session_key', 'created_at']


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    account_type = serializers.ChoiceField(
        choices=[('main', 'Main'), ('seller', 'Seller'), ('owner', 'Owner')],
        default='main'
    )

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        account_type = attrs.get('account_type')

        if not username or not password:
            raise serializers.ValidationError("Username and password are required")

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid credentials")

        if account_type == 'main':
            if not user.check_password(password):
                raise serializers.ValidationError("Invalid credentials")
            attrs['user'] = user
            attrs['account'] = None

        elif account_type == 'seller':
            if not hasattr(user, 'seller_account'):
                raise serializers.ValidationError("User doesn't have a seller account")

            seller_account = user.seller_account
            if not seller_account.check_password(password):
                raise serializers.ValidationError("Invalid credentials")

            attrs['user'] = user
            attrs['account'] = seller_account

        elif account_type == 'owner':
            if not hasattr(user, 'owner_account'):
                raise serializers.ValidationError("User doesn't have an owner account")

            owner_account = user.owner_account
            if not owner_account.check_password(password):
                raise serializers.ValidationError("Invalid credentials")

            attrs['user'] = user
            attrs['account'] = owner_account

        return attrs


class UserDetailSerializer(serializers.ModelSerializer):
    seller_account = SellerAccountSerializer(read_only=True)
    owner_account = OwnerAccountSerializer(read_only=True)
    current_session = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'phone_number', 'profile_image', 'is_email_verified',
            'is_seller', 'is_owner', 'seller_account', 'owner_account',
            'current_session', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'username', 'is_email_verified', 'created_at', 'updated_at']

    def get_current_session(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'session'):
            try:
                session = UserSession.objects.get(
                    session_key=request.session.session_key,
                    user=obj,
                    is_active=True
                )
                return UserSessionSerializer(session).data
            except UserSession.DoesNotExist:
                return None
        return None


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password2 = serializers.CharField(required=True)
    account_type = serializers.ChoiceField(
        choices=[('main', 'Main'), ('seller', 'Seller'), ('owner', 'Owner')],
        default='main'
    )

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({"new_password": "Password fields didn't match."})
        return attrs

    def validate_old_password(self, value):
        user = self.context['request'].user
        account_type = self.initial_data.get('account_type', 'main')

        if account_type == 'main':
            if not user.check_password(value):
                raise serializers.ValidationError("Old password is incorrect")
        elif account_type == 'seller':
            if not hasattr(user, 'seller_account') or not user.seller_account.check_password(value):
                raise serializers.ValidationError("Old password is incorrect")
        elif account_type == 'owner':
            if not hasattr(user, 'owner_account') or not user.owner_account.check_password(value):
                raise serializers.ValidationError("Old password is incorrect")

        return value

    def save(self):
        user = self.context['request'].user
        new_password = self.validated_data['new_password']
        account_type = self.validated_data['account_type']

        if account_type == 'main':
            user.set_password(new_password)
            user.save()
        elif account_type == 'seller':
            user.seller_account.set_password(new_password)
            user.seller_account.save()
        elif account_type == 'owner':
            user.owner_account.set_password(new_password)
            user.owner_account.save()
