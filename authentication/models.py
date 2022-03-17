import binascii
import datetime
import os
import uuid

from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.shortcuts import reverse
from django.utils.translation import gettext_lazy as _

from centraspect.exceptions import InvalidTokenError
from centraspect.models import BaseModel
from centraspect.settings import AUTH_TOKEN_EXPIRY


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
    ACCOUNT_ADMIN = "account_admin", _('Account Admin')
    SYSTEM_ADMIN = "system_admin", _('Superuser')


class User(AbstractUser, PermissionsMixin):
    uuid = models.UUIDField(default=uuid.uuid4)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    role = models.CharField(max_length=250, choices=Roles.choices, default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f'{self.first_name} {self.last_name} - {self.username}'

    @property
    def get_full_name(self) -> str:
        return f'{self.first_name} {self.last_name}'

    @property
    def absolute_url(self):
        return reverse("users:details", kwargs={"uuid": self.uuid})

    @property
    def readable_role(self) -> str:
        lbl = ""
        for role in Roles:
            if role.value == self.role:
                return role.label
        return lbl


class TokenManager(models.Manager):

    def token_expired(self, auth_token):
        qs = self.get_queryset().filter(auth_token=auth_token)
        token = qs.get() or None

        if token is None:
            raise InvalidTokenError("Invalid token provided")

        now = datetime.datetime.now(tz=None)
        print(f"Is Expired? {(now.timestamp() - token.updated_at.timestamp()) > AUTH_TOKEN_EXPIRY}")
        return (now.timestamp() - token.updated_at.timestamp()) > AUTH_TOKEN_EXPIRY


class Token(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    auth_token = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=500, null=False, blank=False, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = TokenManager()

    def save(self, *args, **kwargs):
        if not self.refresh_token:
            self.refresh_token = self.generate_refresh_token()
        if not self.auth_token:
            self.auth_token = self.generate_auth_token()
        super().save(*args, **kwargs)

    def refresh_auth_token(self, provided_refresh):
        if provided_refresh != self.refresh_token:
            raise InvalidTokenError("Invalid Refresh Token Provided")
        new_auth = self.generate_auth_token()
        self.auth_token = new_auth
        self.updated_at = datetime.datetime.now()
        self.save()

    @classmethod
    def generate_auth_token(cls):
        return binascii.hexlify(os.urandom(50)).decode()

    @classmethod
    def generate_refresh_token(cls):
        return binascii.hexlify(os.urandom(100)).decode()

    @classmethod
    def is_auth_token_expired(cls, updated_at):
        now = datetime.datetime.now()
        return (now - updated_at) > AUTH_TOKEN_EXPIRY

    @property
    def to_json(self):
        roles = self.user.readable_role if self.user.readable_role != "" and self.user.readable_role is not None else []
        return {
            "account_uuid": self.user.account.uuid,
            "auth_token": self.auth_token,
            "expires": AUTH_TOKEN_EXPIRY,
            "refresh_token": self.refresh_token,
            "ROLES": roles
        }
