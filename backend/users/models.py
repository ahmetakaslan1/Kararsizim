from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    """Custom manager for User model."""

    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('E-posta adresi zorunludur.')
        if not username:
            raise ValueError('Kullanıcı adı zorunludur.')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(email, username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User modeli.
    - email: benzersiz, asla API response'larında dönülmez
    - username: benzersiz, anketlerde görünür
    """
    email = models.EmailField(unique=True, verbose_name='E-posta')
    username = models.CharField(max_length=50, unique=True, verbose_name='Kullanıcı adı')
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name='Kayıt tarihi')
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'Kullanıcı'
        verbose_name_plural = 'Kullanıcılar'

    def __str__(self):
        return self.username
