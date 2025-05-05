from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class User(AbstractUser):

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_groups_set',  # Changed from custom_user_set
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions_set',  # Changed from custom_user_set
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
    )

    email = models.EmailField(unique=True, verbose_name="Email")
    is_email_verified = models.BooleanField(default=False, verbose_name="Email verified")
    is_seller = models.BooleanField(default=False, verbose_name="Seller")
    is_owner = models.BooleanField(default=False, verbose_name="Warehouse owner")
    # Connection with main user account (if this is a secondary account)
    parent_account = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='related_accounts',
        verbose_name="Related general account"
    )

    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="Phone number")
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True,
                                      verbose_name="Profile image")

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        role = []
        if self.is_seller:
            role.append("Seller")
        if self.is_owner:
            role.append("Owner")
        if not role:
            role.append("Client")

        return f"{self.username} ({', '.join(role)})"


class SellerProfile(models.Model):
    """Seller profile with additional data"""
    user = models.OneToOneField(
        User,  # Use Django's User model directly
        on_delete=models.CASCADE,
        related_name='seller_profile',
        verbose_name="User"
    )
    # Additional seller fields
    nickname = models.CharField(max_length=255, blank=True, null=True, verbose_name="Nickname")
    description = models.TextField(blank=True, null=True, verbose_name="Seller description")
    verified = models.BooleanField(default=False, verbose_name="Verified seller")
    seller_image = models.ImageField(upload_to='seller_images/', blank=True, null=True,
                                     verbose_name="Seller image")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created at")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated at")

    # Add these fields that were previously in the custom User model
    is_seller = models.BooleanField(default=True, verbose_name="Is seller")

    class Meta:
        verbose_name = "Seller Profile"
        verbose_name_plural = "Seller Profiles"

    def __str__(self):
        return f"Seller Profile: {self.user.username}"


class OwnerProfile(models.Model):
    """Warehouse owner profile with additional data"""
    user = models.OneToOneField(
        User,  # Use Django's User model directly
        on_delete=models.CASCADE,
        related_name='owner_profile',
        verbose_name="User"
    )
    # Additional owner fields
    nickname = models.CharField(max_length=255, blank=True, null=True, verbose_name="Nickname")
    description = models.TextField(blank=True, null=True, verbose_name="Company description")
    verified = models.BooleanField(default=False, verbose_name="Verified owner")
    owner_image = models.ImageField(upload_to='owner_images/', blank=True, null=True,
                                    verbose_name="Owner image")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created at")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated at")

    # Add these fields that were previously in the custom User model
    is_owner = models.BooleanField(default=True, verbose_name="Is warehouse owner")

    class Meta:
        verbose_name = "Warehouse Owner Profile"
        verbose_name_plural = "Warehouse Owner Profiles"

    def __str__(self):
        return f"Warehouse Owner Profile: {self.user.username}"
