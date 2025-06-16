from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.utils import timezone

from .models import User, SellerAccount, OwnerAccount, UserSession
from ..admin import LWHBaseAdmin


class SellerAccountInline(admin.StackedInline):
    model = SellerAccount
    can_delete = False
    verbose_name_plural = _('Seller Account')
    fk_name = 'user'
    max_num = 1
    fields = (
        'nickname', 'description', 'seller_image', 'business_name',
        'tax_number', 'verified', 'is_active', 'total_sales',
        'created_at', 'updated_at', 'last_login'
    )
    readonly_fields = ('created_at', 'updated_at', 'last_login', 'total_sales')


class OwnerAccountInline(admin.StackedInline):
    model = OwnerAccount
    can_delete = False
    verbose_name_plural = _('Owner Account')
    fk_name = 'user'
    max_num = 1
    fields = (
        'nickname', 'description', 'owner_image', 'company_name',
        'company_registration', 'warehouse_license', 'verified', 'is_active',
        'created_at', 'updated_at', 'last_login'
    )
    readonly_fields = ('created_at', 'updated_at', 'last_login')


class UserSessionInline(admin.TabularInline):
    model = UserSession
    extra = 0
    fields = ('session_type', 'is_active', 'created_at', 'expires_at')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        'username', 'email', 'first_name', 'last_name',
        'has_seller_account', 'has_owner_account', 'is_email_verified',
        'is_staff', 'is_active'
    )
    list_filter = (
        'is_staff', 'is_active', 'is_email_verified', 'created_at'
    )
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone_number')
    ordering = ('username',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {
            'fields': ('first_name', 'last_name', 'email', 'phone_number', 'profile_image')
        }),
        (_('Status'), {
            'fields': ('is_email_verified',)
        }),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',),
        }),
        (_('Important dates'), {
            'fields': ('last_login', 'date_joined', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )

    readonly_fields = ('created_at', 'updated_at')
    inlines = [SellerAccountInline, OwnerAccountInline, UserSessionInline]

    def has_seller_account(self, obj):
        return hasattr(obj, 'seller_account')
    has_seller_account.boolean = True
    has_seller_account.short_description = _('Has Seller Account')

    def has_owner_account(self, obj):
        return hasattr(obj, 'owner_account')
    has_owner_account.boolean = True
    has_owner_account.short_description = _('Has Owner Account')


@admin.register(SellerAccount)
class SellerAccountAdmin(LWHBaseAdmin):
    list_display = (
        'user', 'nickname', 'business_name', 'verified',
        'is_active', 'total_sales', 'last_login', 'created_at'
    )
    list_filter = ('verified', 'is_active', 'created_at')
    search_fields = (
        'user__username', 'user__email', 'nickname',
        'business_name', 'tax_number'
    )
    raw_id_fields = ('user',)

    fieldsets = (
        (_('User'), {'fields': ('user',)}),
        (_('Profile'), {
            'fields': ('nickname', 'description', 'seller_image')
        }),
        (_('Business Information'), {
            'fields': ('business_name', 'tax_number')
        }),
        (_('Status'), {
            'fields': ('verified', 'is_active', 'total_sales')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at', 'last_login'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at', 'last_login', 'total_sales')


@admin.register(OwnerAccount)
class OwnerAccountAdmin(LWHBaseAdmin):
    list_display = (
        'user', 'nickname', 'company_name', 'verified',
        'is_active', 'last_login', 'created_at'
    )
    list_filter = ('verified', 'is_active', 'created_at')
    search_fields = (
        'user__username', 'user__email', 'nickname',
        'company_name', 'company_registration'
    )
    raw_id_fields = ('user',)

    fieldsets = (
        (_('User'), {'fields': ('user',)}),
        (_('Profile'), {
            'fields': ('nickname', 'description', 'owner_image')
        }),
        (_('Company Information'), {
            'fields': ('company_name', 'company_registration', 'warehouse_license')
        }),
        (_('Status'), {
            'fields': ('verified', 'is_active')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at', 'last_login'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at', 'last_login')


@admin.register(UserSession)
class UserSessionAdmin(LWHBaseAdmin):
    list_display = (
        'user', 'session_type_display', 'account_info',
        'is_active', 'created_at', 'expires_at'
    )
    list_filter = ('session_type', 'is_active', 'created_at')
    search_fields = ('user__username', 'user__email', 'session_key')
    raw_id_fields = ('user', 'seller_account', 'owner_account')
    date_hierarchy = 'created_at'

    fieldsets = (
        (_('Session Info'), {
            'fields': ('user', 'session_key', 'session_type')
        }),
        (_('Account References'), {
            'fields': ('seller_account', 'owner_account')
        }),
        (_('Status'), {
            'fields': ('is_active', 'created_at', 'expires_at')
        }),
    )
    readonly_fields = ('created_at',)

    def session_type_display(self, obj):
        colors = {
            'main': '#28a745',
            'seller': '#007bff',
            'owner': '#dc3545'
        }
        color = colors.get(obj.session_type, '#6c757d')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_session_type_display()
        )
    session_type_display.short_description = _('Session Type')

    def account_info(self, obj):
        if obj.session_type == 'seller' and obj.seller_account:
            return f"Seller: {obj.seller_account.nickname or obj.seller_account.business_name or 'No name'}"
        elif obj.session_type == 'owner' and obj.owner_account:
            return f"Owner: {obj.owner_account.nickname or obj.owner_account.company_name or 'No name'}"
        return "Main Account"
    account_info.short_description = _('Account Info')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('user', 'seller_account', 'owner_account')


admin.site.site_header = _("LWH - User Management")
admin.site.site_title = _("LWH Users")
admin.site.index_title = _("User Administration")