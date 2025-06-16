from rest_framework import permissions
from .models import UserSession


class IsOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        session_key = request.session.session_key
        if not session_key:
            return False

        try:
            session = UserSession.objects.get(
                user=request.user,
                session_key=session_key,
                session_type='owner',
                is_active=True
            )
            return session.owner_account and session.owner_account.is_active
        except UserSession.DoesNotExist:
            return False


class IsSeller(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        session_key = request.session.session_key
        if not session_key:
            return False

        try:
            session = UserSession.objects.get(
                user=request.user,
                session_key=session_key,
                session_type='seller',
                is_active=True
            )
            return session.seller_account and session.seller_account.is_active
        except UserSession.DoesNotExist:
            return False


class IsWarehouseOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False

        session_key = request.session.session_key
        if not session_key:
            return False

        try:
            session = UserSession.objects.get(
                user=request.user,
                session_key=session_key,
                session_type='owner',
                is_active=True
            )
            if not session.owner_account or not session.owner_account.is_active:
                return False

            return obj.owner == request.user
        except UserSession.DoesNotExist:
            return False


class IsProductSeller(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False

        session_key = request.session.session_key
        if not session_key:
            return False

        try:
            session = UserSession.objects.get(
                user=request.user,
                session_key=session_key,
                session_type='seller',
                is_active=True
            )
            if not session.seller_account or not session.seller_account.is_active:
                return False

            return obj.seller == request.user
        except UserSession.DoesNotExist:
            return False


class HasActiveSession(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        session_key = request.session.session_key
        if not session_key:
            return False

        try:
            session = UserSession.objects.get(
                user=request.user,
                session_key=session_key,
                is_active=True
            )
            return True
        except UserSession.DoesNotExist:
            return False


class IsMainAccount(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        session_key = request.session.session_key
        if not session_key:
            return False

        try:
            session = UserSession.objects.get(
                user=request.user,
                session_key=session_key,
                session_type='main',
                is_active=True
            )
            return True
        except UserSession.DoesNotExist:
            return False


class IsSellerOrOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        session_key = request.session.session_key
        if not session_key:
            return False

        try:
            session = UserSession.objects.get(
                user=request.user,
                session_key=session_key,
                is_active=True
            )

            if session.session_type == 'seller':
                return session.seller_account and session.seller_account.is_active
            elif session.session_type == 'owner':
                return session.owner_account and session.owner_account.is_active

            return False
        except UserSession.DoesNotExist:
            return False


class CanCreateSellerAccount(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        return not hasattr(request.user, 'seller_account')


class CanCreateOwnerAccount(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        return not hasattr(request.user, 'owner_account')


def get_current_session(request):
    if not request.user or not request.user.is_authenticated:
        return None

    session_key = request.session.session_key
    if not session_key:
        return None

    try:
        return UserSession.objects.get(
            user=request.user,
            session_key=session_key,
            is_active=True
        )
    except UserSession.DoesNotExist:
        return None


def get_current_account(request):
    session = get_current_session(request)
    if not session:
        return None

    if session.session_type == 'seller':
        return session.seller_account
    elif session.session_type == 'owner':
        return session.owner_account

    return None


def is_seller_session(request):
    session = get_current_session(request)
    return session and session.session_type == 'seller'


def is_owner_session(request):
    session = get_current_session(request)
    return session and session.session_type == 'owner'


def is_main_session(request):
    session = get_current_session(request)
    return session and session.session_type == 'main'