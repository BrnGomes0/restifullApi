import os
import uuid
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
from django.db import models
from django.utils import timezone

def user_image_field(instace, filename):
    ext = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{ext}'

    return os.path.join('uploads', 'avatar', filename)

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fiels):
        if not email:
            raise ValueError("O usuário precisa de um e-mail")

        user = self.model(email=self.normalize_email(email), **extra_fiels)
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255, null=False)
    last_name = models.CharField(max_length=255, null=False)
    cpf = models.CharField(max_length=11, unique=True)
    url_image = models.ImageField(null=True, upload_to=user_image_field)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'email'

    def __str__(self) -> str:
        return f'{self.first_name} {self.last_name}'

class Adress(models.Model):
    id = models.AutoField(primary_key=True)
    client_adress = models.ForeignKey(User, on_delete=models.CASCADE)
    address_logradouro = models.CharField(max_length=10, blank=False, null=False)
    address_neighborhood = models.CharField(max_length=30, blank=False, null=False)
    city_address = models.CharField(max_length=30, blank=False, null=False)
    address_street = models.CharField(max_length=20, blank=False, null=False)
    address_uf = models.CharField(max_length=2, blank=False, null=False)
    address_cep = models.CharField(max_length=8, blank=False, null=False)

class Contact(models.Model):
    id = models.AutoField(primary_key=True)
    client_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    contact_number = models.CharField(max_length=15, blank=False, null=False, unique=True)
    contact_email = models.EmailField(max_length=50, blank=False, null=False, unique=True)


class Account(models.Model):
    id = models.AutoField(primary_key=True)
    client_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    account_agency = models.CharField(max_length=4, blank=False, null=False, default=9090)
    account_number = models.CharField(max_length=8, blank=False, null=False, unique=True)
    account_type = models.CharField(max_length=20, blank=False, null=False, default='Standart')
    account_balance = models.FloatField(max_length=20, default=0.00, null=False, blank=False)
    created_at = models.DateField(default=timezone.now)

    def __str__(self) -> str:
        return f'{self.account_agency} - {self.account_number}'


class Card(models.Model):
    id = models.AutoField(primary_key=True)
    account_id = models.ForeignKey(Account, on_delete=models.CASCADE)
    card_number = models.CharField(max_length=19, blank=False, null=False, unique=True)
    card_cvv = models.CharField(max_length=3, blank=False, null=False)
    card_valid = models.DateField(blank=False, null=False)
    card_flag = models.CharField(max_length=20, blank=False, null=False)

    def __str__(self):
        return self.account_id


class Transfer(models.Model):
    origin_id_account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='account_origin')
    account_id_destination = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='account_destinantion')
    value = models.FloatField()
    obs = models.TextField(max_length=100, blank=True)
    type_transfer = models.CharField(max_length=20)
    created_at = models.DateTimeField(default=timezone.now)


class Movimentation(models.Model):
    id = models.AutoField(primary_key=True)
    account_id = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='account_id_movimentation')
    transfer = models.ForeignKey(Transfer, on_delete=models.CASCADE)
    movimentation_value = models.FloatField()
    movimentation_obs = models.TextField(max_length=100)
    

class Loan(models.Model):
    id = models.AutoField(primary_key=True)
    account_id = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='id_loan')
    loan_value = models.FloatField(blank=False, null=False)
    loan_interest = models.FloatField(blank=False, null=False)
    loan_quantity_parcelas = models.IntegerField(blank=False, null=False)
    loan_obs = models.TextField(max_length=100)
    created_at = models.DateTimeField(default=timezone.now)


# class Investiment(models.Model):
#     id = models.AutoField(primary_key=True)
#     account_id = models.ForeignKey(Account, on_delete=models.CASCADE)
#     investment_contribution = models.FloatField(blank=False, null=False)
#     investment_term = models.DateField(blank=True)
#     investment_obs = models.TextField(max_length=100)

class Extract(models.Model):
    account_id = models.ForeignKey(Account, on_delete=models.CASCADE)
    transaction_date = models.DateTimeField(auto_now_add=True)
    transaction_type = models.CharField(max_length=20)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.account_id} - {self.transaction_type} - {self.transaction_date}"