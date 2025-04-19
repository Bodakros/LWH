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
    is_email_verified = models.BooleanField(default=False, verbose_name="Email підтверджено")
    is_seller = models.BooleanField(default=False, verbose_name="Продавець")
    is_owner = models.BooleanField(default=False, verbose_name="Власник складу")
    # Зв'язок з основним акаунтом користувача (якщо це другий акаунт)
    parent_account = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='related_accounts',
        verbose_name="Пов'язаний основний акаунт"
    )

    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="Номер телефону")
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True,
                                      verbose_name="Зображення профілю")

    class Meta:
        verbose_name = "Користувач"
        verbose_name_plural = "Користувачі"

    def __str__(self):
        role = []
        if self.is_seller:
            role.append("Продавець")
        if self.is_owner:
            role.append("Власник")
        if not role:
            role.append("Клієнт")

        return f"{self.username} ({', '.join(role)})"


class SellerProfile(models.Model):
    """Профіль продавця з додатковими даними"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='seller_profile',
        verbose_name="Користувач"
    )
    nickname = models.CharField(max_length=255, blank=True, null=True, verbose_name="Нік")
    description = models.TextField(blank=True, null=True, verbose_name="Опис продавця")
    verified = models.BooleanField(default=False, verbose_name="Верифікований продавець")
    seller_image = models.ImageField(upload_to='seller_images/', blank=True, null=True,
                                     verbose_name="Зображення продавця")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата оновлення")

    class Meta:
        verbose_name = "Профіль продавця"
        verbose_name_plural = "Профілі продавців"

    def __str__(self):
        return f"Профіль продавця: {self.user.username}"


class OwnerProfile(models.Model):
    """Профіль власника складу з додатковими даними"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owner_profile',
        verbose_name="Користувач"
    )
    nickname = models.CharField(max_length=255, blank=True, null=True, verbose_name="Нік")
    description = models.TextField(blank=True, null=True, verbose_name="Опис компанії")
    verified = models.BooleanField(default=False, verbose_name="Верифікований власник")
    owner_image = models.ImageField(upload_to='owner_images/', blank=True, null=True,
                                    verbose_name="Зображення власника")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата оновлення")

    class Meta:
        verbose_name = "Профіль власника складу"
        verbose_name_plural = "Профілі власників складів"

    def __str__(self):
        return f"Профіль власника складу: {self.user.username}"
