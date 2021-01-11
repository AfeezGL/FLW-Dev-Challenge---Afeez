from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from phonenumber_field.modelfields import PhoneNumberField
from django.conf import settings


class MyAccountManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, password=None):
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(
            email = self.normalize_email(email),
            first_name = first_name,
            last_name = last_name,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, password):
        user = self.create_user(
            email = self.normalize_email(email),
            first_name = first_name,
            last_name = last_name,
            password = password
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    email = models.EmailField(verbose_name="email", max_length=60, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    profile_picture = models.ImageField()
    phone_number = PhoneNumberField()
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    object = MyAccountManager()

    def __str__(self):
        return self.email
    
    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, perm, obj=None):
        return self.is_superuser


class Customer(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE, related_name="customer")
    device_id = models.CharField(max_length=30, unique=True, null=True, blank=True)

    def __str__(self):
        if self.user:
            name = self.user.email
        else:
            name = self.device_id
        return str(name)

class Address(models.Model):
    customer = models.ForeignKey(Customer, on_delete = models.CASCADE)
    first_name = models.CharField(max_length = 250, null = True)
    last_name = models.CharField(max_length = 250, null = True)
    email = models.EmailField(max_length = 250, null = True, blank = True)
    address_line_1 = models.CharField(max_length = 250, null = True)
    address_line_2 = models.CharField(max_length = 250, null = True, blank = True)
    city = models.CharField(max_length = 250, null = True)
    state = models.CharField(max_length = 250, null = True)
    country = models.CharField(max_length = 250, default = "Nigeria")
    postal_code = models.PositiveIntegerField(null = True)
    phone_number = PhoneNumberField()