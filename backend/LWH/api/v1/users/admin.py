from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User, SellerProfile, OwnerProfile
from ..admin import LWHBaseAdmin


class SellerProfileInline(admin.StackedInline):
    model = SellerProfile
    can_delete = False
    verbose_name_plural = _('Seller Profile')
    fk_name = 'user'
    max_num = 1


class OwnerProfileInline(admin.StackedInline):
    model = OwnerProfile
    can_delete = False
    verbose_name_plural = _('Owner Profile')
    fk_name = 'user'
    max_num = 1


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_seller', 'is_owner', 'is_staff')
    list_filter = ('is_seller', 'is_owner', 'is_staff', 'is_active', 'is_email_verified')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone_number')
    ordering = ('username',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'phone_number', 'profile_image')}),
        (_('Roles'), {'fields': ('is_seller', 'is_owner')}),
        (_('Status'), {'fields': ('is_email_verified',)}),
        (_('Account relation'), {'fields': ('parent_account',)}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_seller', 'is_owner'),
        }),
    )

    def get_inlines(self, request, obj=None):
        if not obj:
            return []

        inlines = []
        if obj.is_seller:
            inlines.append(SellerProfileInline)
        if obj.is_owner:
            inlines.append(OwnerProfileInline)

        return inlines

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        # Create profiles if needed
        if obj.is_seller and not hasattr(obj, 'seller_profile'):
            SellerProfile.objects.create(user=obj)

        if obj.is_owner and not hasattr(obj, 'owner_profile'):
            OwnerProfile.objects.create(user=obj)


@admin.register(SellerProfile)
class SellerProfileAdmin(LWHBaseAdmin):
    list_display = ('user', 'nickname', 'verified', 'created_at', 'updated_at')
    list_filter = ('verified', 'created_at')
    search_fields = ('user__username', 'user__email', 'nickname')
    raw_id_fields = ('user',)

    fieldsets = (
        (None, {'fields': ('user', 'nickname', 'verified')}),
        (_('Details'), {'fields': ('description', 'seller_image')}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    readonly_fields = ('created_at', 'updated_at')


@admin.register(OwnerProfile)
class OwnerProfileAdmin(LWHBaseAdmin):
    list_display = ('user', 'nickname', 'verified', 'created_at', 'updated_at')
    list_filter = ('verified', 'created_at')
    search_fields = ('user__username', 'user__email', 'nickname')
    raw_id_fields = ('user',)

    fieldsets = (
        (None, {'fields': ('user', 'nickname', 'verified')}),
        (_('Details'), {'fields': ('description', 'owner_image')}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    readonly_fields = ('created_at', 'updated_at')
