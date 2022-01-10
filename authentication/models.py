from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from centraspect.models import BaseModel
import uuid


class Address(models.Model):
    city = models.CharField(max_length=255, unique=False, blank=False, null=False)
    state = models.CharField(max_length=2, blank=False, null=True)
    zipcode = models.CharField(max_length=15, blank=False, null=True)
    street_one = models.CharField(max_length=1024, blank=False, null=True)
    street_two = models.CharField(max_length=1024, blank=True, null=True)
        

class Account(BaseModel):
    name = models.CharField(max_length=255, unique=False, blank=False, null=False)
    address = models.OneToOneField(Address, on_delete=models.CASCADE, primary_key=False, null=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self) -> str:
        return f'[name: {self.name}, uuid: {self.uuid}, is_active: {self.is_active}]'
    
class Roles(models.TextChoices):
        USER = "base_user", _('User')
        INSPECTOR = "inspector", _('Inspector')
        ACCOUNT_ADMIN = "account_admin" , _('Account Admin')
        SYSTEM_ADMIN = "system_admin", _('Superuser')

class User(AbstractUser, PermissionsMixin):
    
    uuid = models.UUIDField(default=uuid.uuid4)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    role = models.CharField(max_length=250, choices=Roles.choices, default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f'{self.first_name} {self.last_name} - {self.username}'
    
    def get_full_name(self) -> str:
        return f'{self.first_name} {self.last_name}'
    
    @property
    def readable_role(self) -> str:
        lbl = ""
        for role in Roles:
            if role.value == self.role:
                return role.label
        return lbl