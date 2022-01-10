from authentication.models import Account
from django.db.models.deletion import CASCADE
from django.db import models
from storages.backends.s3boto3 import S3Boto3Storage
from centraspect.models import BaseModel


class QRCode(BaseModel):
    file_name = models.CharField(max_length=2000, blank=False, null=False)
    image = models.ImageField(upload_to='qr-codes/', storage=S3Boto3Storage())
    data = models.JSONField(null=False, blank=False)
    account = models.ForeignKey(Account, on_delete=CASCADE)