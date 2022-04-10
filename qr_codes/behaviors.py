from django.core.serializers import serialize
from django.core.files import File
from django.conf import settings
from django.utils.text import slugify
from storages.backends.s3boto3 import S3Boto3Storage
import boto3
from .models import QRCode
from io import BytesIO
import qrcode
import os


class QRCodeGeneratorMixin:
    
    def generate_qr_code(self, *args, **kwargs):
        instance = kwargs.get('inspection_item')
        bucket_path = self._build_bucket_path(instance.account)
        file_name = f'item-{instance.uuid}.png'
        
        qr_file_path = os.path.join(
            bucket_path,
            file_name
        )
        
        qr_data = serialize('json', [instance,] )
        
        out = BytesIO()
       
        qr = qrcode.QRCode(version=1,box_size=10,border=5)
        qr.add_data(qr_data)
        qr.make(fit=True)
        qr_img = qr.make_image(fill='black', back_color='white')
        qr_img.save(out, 'PNG')
        
        qr = QRCode()
        qr.data = qr_data
        qr.account = instance.account
        qr.file_name = qr_file_path
        qr.image = File(out, qr_file_path)
        qr.save()   
        
        return qr

    def _build_bucket_path(self, account):
        return f'qr_codes/{slugify(account.name)}-{account.uuid}/codes'
