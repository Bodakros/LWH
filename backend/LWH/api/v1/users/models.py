from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_groups_set',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions_set',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
    )

    email = models.EmailField(unique=True, verbose_name=_("Email"))
    is_email_verified = models.BooleanField(default=False, verbose_name=_("Email verified"))
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name=_("Phone number"))
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True,
                                      verbose_name=_("Profile image"))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")

    def __str__(self):
        return f"{self.username} ({self.email})"

    @property
    def is_seller(self):
        return hasattr(self, 'seller_account') and self.seller_account.is_active

    @property
    def is_owner(self):
        return hasattr(self, 'owner_account') and self.owner_account.is_active

    def get_seller_account(self):
        return getattr(self, 'seller_account', None)

    def get_owner_account(self):
        return getattr(self, 'owner_account', None)


class BaseRoleAccount(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        verbose_name=_("User")
    )

    password = models.CharField(max_length=128, verbose_name=_("Password"))

    nickname = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Nickname"))
    description = models.TextField(blank=True, null=True, verbose_name=_("Description"))
    verified = models.BooleanField(default=False, verbose_name=_("Verified"))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))
    last_login = models.DateTimeField(null=True, blank=True, verbose_name=_("Last login"))

    is_active = models.BooleanField(default=True, verbose_name=_("Active"))

    class Meta:
        abstract = True

    def set_password(self, raw_password):
        from django.contrib.auth.hashers import make_password
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        from django.contrib.auth.hashers import check_password
        return check_password(raw_password, self.password)

    def save(self, *args, **kwargs):
        if self.password and not self.password.startswith(('pbkdf2_sha256$', 'bcrypt$', 'argon2$')):
            self.set_password(self.password)
        super().save(*args, **kwargs)


class SellerAccount(BaseRoleAccount):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='seller_account',
        verbose_name=_("User")
    )

    seller_image = models.ImageField(
        upload_to='seller_images/',
        blank=True,
        null=True,
        verbose_name=_("Seller image")
    )

    business_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_("Business name")
    )

    tax_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_("Tax number")
    )

    total_sales = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name=_("Total sales")
    )

    class Meta:
        verbose_name = _("Seller Account")
        verbose_name_plural = _("Seller Accounts")

    def __str__(self):
        return f"Seller: {self.user.username} ({self.nickname or 'No nickname'})"


class OwnerAccount(BaseRoleAccount):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='owner_account',
        verbose_name=_("User")
    )

    owner_image = models.ImageField(
        upload_to='owner_images/',
        blank=True,
        null=True,
        verbose_name=_("Owner image")
    )

    company_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_("Company name")
    )

    company_registration = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_("Company registration number")
    )

    warehouse_license = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_("Warehouse license")
    )

    class Meta:
        verbose_name = _("Owner Account")
        verbose_name_plural = _("Owner Accounts")

    def __str__(self):
        return f"Owner: {self.user.username} ({self.company_name or self.nickname or 'No name'})"


class UserSession(models.Model):
    SESSION_TYPES = [
        ('main', _('Main Account')),
        ('seller', _('Seller Account')),
        ('owner', _('Owner Account')),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sessions',
        verbose_name=_("User")
    )

    session_key = models.CharField(max_length=40, unique=True, verbose_name=_("Session key"))
    session_type = models.CharField(max_length=10, choices=SESSION_TYPES, verbose_name=_("Session type"))

    seller_account = models.ForeignKey(
        SellerAccount,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("Seller account")
    )

    owner_account = models.ForeignKey(
        OwnerAccount,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("Owner account")
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    expires_at = models.DateTimeField(verbose_name=_("Expires at"))
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))

    class Meta:
        verbose_name = _("User Session")
        verbose_name_plural = _("User Sessions")
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.get_session_type_display()}"

    def clean(self):
        if self.session_type == 'seller' and not self.seller_account:
            raise ValidationError(_("Seller account is required for seller session type"))

        if self.session_type == 'owner' and not self.owner_account:
            raise ValidationError(_("Owner account is required for owner session type"))

        if self.session_type == 'main' and (self.seller_account or self.owner_account):
            raise ValidationError(_("Main session type should not have seller or owner account"))

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)