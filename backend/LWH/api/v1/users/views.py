from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import uuid

from .models import SellerAccount, OwnerAccount, UserSession
from .serializers import (
    UserSerializer, UserRegistrationSerializer, SellerAccountSerializer,
    OwnerAccountSerializer, LoginSerializer, UserDetailSerializer,
    ChangePasswordSerializer
)

User = get_user_model()


@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        user_serializer = UserSerializer(user)
        return Response(user_serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        account = serializer.validated_data['account']
        account_type = serializer.validated_data['account_type']

        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key

        UserSession.objects.filter(
            user=user,
            session_key=session_key
        ).update(is_active=False)

        expires_at = timezone.now() + timedelta(days=7)

        session_data = {
            'user': user,
            'session_key': session_key,
            'session_type': account_type,
            'expires_at': expires_at
        }

        if account_type == 'seller':
            session_data['seller_account'] = account
            account.last_login = timezone.now()
            account.save(update_fields=['last_login'])
        elif account_type == 'owner':
            session_data['owner_account'] = account
            account.last_login = timezone.now()
            account.save(update_fields=['last_login'])

        user_session = UserSession.objects.create(**session_data)

        request.session['user_id'] = user.id
        request.session['session_type'] = account_type
        request.session['account_id'] = account.id if account else None

        response_data = {
            'user': UserSerializer(user).data,
            'session_type': account_type,
            'message': f'Logged in as {account_type} account'
        }

        if account:
            if account_type == 'seller':
                response_data['seller_account'] = SellerAccountSerializer(account).data
            elif account_type == 'owner':
                response_data['owner_account'] = OwnerAccountSerializer(account).data

        return Response(response_data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    session_key = request.session.session_key
    if session_key:
        UserSession.objects.filter(
            user=request.user,
            session_key=session_key,
            is_active=True
        ).update(is_active=False)

    request.session.flush()
    return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    user = request.user

    if request.method == 'GET':
        serializer = UserDetailSerializer(user, context={'request': request})
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_seller_account(request):
    if hasattr(request.user, 'seller_account'):
        return Response(
            {"error": "User already has a seller account"},
            status=status.HTTP_400_BAD_REQUEST
        )

    serializer = SellerAccountSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        seller_account = serializer.save()
        return Response(
            SellerAccountSerializer(seller_account).data,
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def seller_account_detail(request):
    if not hasattr(request.user, 'seller_account'):
        return Response(
            {"error": "User doesn't have a seller account"},
            status=status.HTTP_404_NOT_FOUND
        )

    seller_account = request.user.seller_account

    if request.method == 'GET':
        serializer = SellerAccountSerializer(seller_account)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = SellerAccountSerializer(
            seller_account,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_owner_account(request):
    if hasattr(request.user, 'owner_account'):
        return Response(
            {"error": "User already has an owner account"},
            status=status.HTTP_400_BAD_REQUEST
        )

    serializer = OwnerAccountSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        owner_account = serializer.save()
        return Response(
            OwnerAccountSerializer(owner_account).data,
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def owner_account_detail(request):
    if not hasattr(request.user, 'owner_account'):
        return Response(
            {"error": "User doesn't have an owner account"},
            status=status.HTTP_404_NOT_FOUND
        )

    owner_account = request.user.owner_account

    if request.method == 'GET':
        serializer = OwnerAccountSerializer(owner_account)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = OwnerAccountSerializer(
            owner_account,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Password changed successfully'}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def switch_account(request):
    account_type = request.data.get('account_type')
    password = request.data.get('password')

    if not account_type or not password:
        return Response(
            {"error": "Account type and password are required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = request.user
    account = None

    if account_type == 'main':
        if not user.check_password(password):
            return Response(
                {"error": "Invalid password"},
                status=status.HTTP_400_BAD_REQUEST
            )
    elif account_type == 'seller':
        if not hasattr(user, 'seller_account'):
            return Response(
                {"error": "User doesn't have a seller account"},
                status=status.HTTP_400_BAD_REQUEST
            )
        account = user.seller_account
        if not account.check_password(password):
            return Response(
                {"error": "Invalid password"},
                status=status.HTTP_400_BAD_REQUEST
            )
    elif account_type == 'owner':
        if not hasattr(user, 'owner_account'):
            return Response(
                {"error": "User doesn't have an owner account"},
                status=status.HTTP_400_BAD_REQUEST
            )
        account = user.owner_account
        if not account.check_password(password):
            return Response(
                {"error": "Invalid password"},
                status=status.HTTP_400_BAD_REQUEST
            )
    else:
        return Response(
            {"error": "Invalid account type"},
            status=status.HTTP_400_BAD_REQUEST
        )

    session_key = request.session.session_key
    if session_key:
        UserSession.objects.filter(
            user=user,
            session_key=session_key,
            is_active=True
        ).update(is_active=False)

    expires_at = timezone.now() + timedelta(days=7)

    session_data = {
        'user': user,
        'session_key': session_key,
        'session_type': account_type,
        'expires_at': expires_at
    }

    if account_type == 'seller':
        session_data['seller_account'] = account
        account.last_login = timezone.now()
        account.save(update_fields=['last_login'])
    elif account_type == 'owner':
        session_data['owner_account'] = account
        account.last_login = timezone.now()
        account.save(update_fields=['last_login'])

    UserSession.objects.create(**session_data)

    request.session['session_type'] = account_type
    request.session['account_id'] = account.id if account else None

    response_data = {
        'message': f'Switched to {account_type} account',
        'session_type': account_type,
        'user': UserSerializer(user).data
    }

    if account:
        if account_type == 'seller':
            response_data['seller_account'] = SellerAccountSerializer(account).data
        elif account_type == 'owner':
            response_data['owner_account'] = OwnerAccountSerializer(account).data

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_session(request):
    session_key = request.session.session_key
    if not session_key:
        return Response(
            {"error": "No active session"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user_session = UserSession.objects.get(
            user=request.user,
            session_key=session_key,
            is_active=True
        )

        response_data = {
            'session_type': user_session.session_type,
            'user': UserSerializer(request.user).data,
            'expires_at': user_session.expires_at
        }

        if user_session.session_type == 'seller' and user_session.seller_account:
            response_data['seller_account'] = SellerAccountSerializer(user_session.seller_account).data
        elif user_session.session_type == 'owner' and user_session.owner_account:
            response_data['owner_account'] = OwnerAccountSerializer(user_session.owner_account).data

        return Response(response_data, status=status.HTTP_200_OK)

    except UserSession.DoesNotExist:
        return Response(
            {"error": "No active session found"},
            status=status.HTTP_404_NOT_FOUND
        )