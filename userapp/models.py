
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, first_name, last_name, email, phone, password=None, **extra_fields):
        if not email:
            raise ValueError('User must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, first_name, last_name, email, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(first_name, last_name, email, phone, password, **extra_fields)

class CustomUser(AbstractUser):
    STOWNER = 'Station Owner'
    VHOWNER = 'Vehicle Owner'
    ADMIN = 'Admin'

    ROLE_CHOICES = (
        (STOWNER, 'stowner'),
        (VHOWNER, 'vhowner'),
        (ADMIN, 'admin'),
    )
    username=None
    USERNAME_FIELD = 'email'
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.IntegerField(null=True)
    email = models.EmailField(max_length=100, unique=True)
    role = models.CharField(choices=ROLE_CHOICES,max_length=50, blank=True, null=True)

    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superadmin = models.BooleanField(default=False)

    
    REQUIRED_FIELDS = ['first_name','last_name', 'phone']

    objects = UserManager()

    def __str__(self):  # Use double underscores here
        return self.first_name
