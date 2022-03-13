import random
import string
import qrcode

from enum import Enum
from io import BytesIO

from django.core.files import File
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils.text import slugify
from PIL import Image

from centraspect.settings import MAX_IMAGE_SIZE


class S3UploadType(Enum):
    QR_CODE = 'qr_codes'
    INSPECTION_IMAGE = 'inspections'


class S3UploadUtils:

    @staticmethod
    def build_upload_to_path(account, uuid, upload_type):
        path = ''
        base_path = f'{slugify(account.name)}-{account.uuid}/'

        if upload_type == S3UploadType.QR_CODE:
            path = f'{base_path}{upload_type.value}'

        elif upload_type == S3UploadType.INSPECTION_IMAGE:
            path = f"{base_path}{upload_type.value}/inspection-{uuid}"

        else:
            raise ValueError(f"Invalid S3UploadType ({upload_type}) provided.")

        return path

    @staticmethod
    def generate_qr_code_image(account, instance_uuid, serialized_data):
        qr = qrcode.QRCode(version=1, box_size=10, border=5)

        qr.add_data(serialized_data)
        qr.make(fit=True)

        img = qr.make_image(fill='black', back_color='white')

        image = BytesIO()
        img.save(image)

        file_buffer = S3UploadUtils.upload_image(account=account,
                                   instance_uuid=instance_uuid,
                                   upload_type=S3UploadType.QR_CODE,
                                   image=image)

        return file_buffer

    @staticmethod
    def build_bucket_path(account, instance_uuid, upload_type, **kwargs):
        path = ''
        base_path = f'{slugify(account.name)}-{account.uuid}/'
        if upload_type == S3UploadType.QR_CODE:
            path = f'{base_path}{upload_type.value}/item-{instance_uuid}.png'

        elif upload_type == S3UploadType.INSPECTION_IMAGE:
            path = f"{base_path}{upload_type.value}/inspection-{instance_uuid}/{kwargs.pop('filename')}"

        else:
            raise ValueError(f"Invalid S3UploadType ({upload_type}) provided.")

        return path

    @staticmethod
    def upload_image(account, instance_uuid, upload_type, image):
        file_buffer = None

        if upload_type == S3UploadType.QR_CODE:
            filename = S3UploadUtils.build_bucket_path(account, instance_uuid, upload_type)
            file_buffer = InMemoryUploadedFile(image, None, filename, 'image/png', image.getbuffer().nbytes, None)

        elif upload_type == S3UploadType.INSPECTION_IMAGE:
            temp_path = image.temporary_file_path()

            # open the image with Pillow
            img = Image.open(temp_path, mode='r')
            img.thumbnail(size=MAX_IMAGE_SIZE)

            # Create a bytes buffer and save the image into the buffer
            img_buffer = BytesIO()
            img.save(img_buffer, format='PNG', quality=25, optimize=True)

            # create a Django friendly file
            the_image = File(img_buffer, name=f'{S3UploadUtils.generate_filename()}.png')
            return the_image

        else:
            raise ValueError(f"Invalid S3UploadType ({upload_type}) provided.")

        return file_buffer

    @staticmethod
    def generate_filename():
        return ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits, k=21))
