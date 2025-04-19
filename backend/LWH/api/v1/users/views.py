# api/v1/users/views.py
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import UserSerializer, RegisterSerializer, SellerProfileSerializer, OwnerProfileSerializer
from .models import User, SellerProfile, OwnerProfile
from django.shortcuts import get_object_or_404


@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        user_serializer = UserSerializer(user)
        return Response(user_serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    user = request.user

    if request.method == 'GET':
        serializer = UserSerializer(user)
        data = serializer.data

        # Додаємо інформацію про профілі, якщо вони існують
        if hasattr(user, 'seller_profile'):
            seller_serializer = SellerProfileSerializer(user.seller_profile)
            data['seller_profile'] = seller_serializer.data

        if hasattr(user, 'owner_profile'):
            owner_serializer = OwnerProfileSerializer(user.owner_profile)
            data['owner_profile'] = owner_serializer.data

        return Response(data)

    elif request.method == 'PUT':
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_seller_profile(request):
    user = request.user

    # Перевіряємо, чи вже є профіль продавця
    if hasattr(user, 'seller_profile'):
        return Response({"error": "У вас вже є профіль продавця"}, status=status.HTTP_400_BAD_REQUEST)

    serializer = SellerProfileSerializer(data=request.data)
    if serializer.is_valid():
        # Створюємо профіль і оновлюємо статус користувача
        serializer.save(user=user)
        user.is_seller = True
        user.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_owner_profile(request):
    user = request.user

    # Перевіряємо, чи вже є профіль власника
    if hasattr(user, 'owner_profile'):
        return Response({"error": "У вас вже є профіль власника складу"}, status=status.HTTP_400_BAD_REQUEST)

    serializer = OwnerProfileSerializer(data=request.data)
    if serializer.is_valid():
        # Створюємо профіль і оновлюємо статус користувача
        serializer.save(user=user)
        user.is_owner = True
        user.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    user = request.user

    # Перевіряємо чи надані обидва паролі
    if 'old_password' not in request.data or 'new_password' not in request.data:
        return Response({"error": "Потрібні поля old_password і new_password"},
                        status=status.HTTP_400_BAD_REQUEST)

    # Перевіряємо старий пароль
    if not user.check_password(request.data['old_password']):
        return Response({"error": "Неправильний поточний пароль"},
                        status=status.HTTP_400_BAD_REQUEST)

    # Встановлюємо новий пароль
    user.set_password(request.data['new_password'])
    user.save()

    return Response({"success": "Пароль успішно змінено"})
