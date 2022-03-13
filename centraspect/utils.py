import random
import string
from enum import Enum

from django.utils.text import slugify
from django.core.files.uploadedfile import InMemoryUploadedFile
from io import BytesIO
from PIL import Image
import qrcode


class S3UploadType(Enum):
    QR_CODE = 'qr_codes'
    INSPECTION_IMAGE = 'inspections'


def generate_qr_code_image(account, instance_uuid, serialized_data):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)

    qr.add_data(serialized_data)
    qr.make(fit=True)

    img = qr.make_image(fill='black', back_color='white')

    image = BytesIO()
    img.save(image)

    file_buffer = upload_image(account=account,
                               instance_uuid=instance_uuid,
                               upload_type=S3UploadType.QR_CODE,
                               image=image)

    return file_buffer


def build_bucket_path(account, instance_uuid, upload_type, **kwargs):
    path = ''
    base_path = f'{slugify(account.name)}-{account.uuid}/'
    if upload_type == S3UploadType.QR_CODE:
        path = f'{base_path}{upload_type.value}/item-{instance_uuid}.png'

    elif upload_type == S3UploadType.INSPECTION_IMAGE:
        path = f"{base_path}{upload_type.value}/inspection-{instance_uuid}/{kwargs.pop('filename')}.png"

    else:
        raise ValueError(f"Invalid S3UploadType ({upload_type}) provided.")

    return path


def generate_filename():
    return ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits, k=21))


def upload_image(account, instance_uuid, upload_type, image):
    file_buffer = None

    if upload_type == S3UploadType.QR_CODE:
        filename = build_bucket_path(account, instance_uuid, upload_type)
        file_buffer = InMemoryUploadedFile(image, None, filename, 'image/png', image.getbuffer().nbytes, None)

    elif upload_type == S3UploadType.INSPECTION_IMAGE:
        temp_location = image.temporary_file_path()
        filename = generate_filename()

        img = Image.open(temp_location, mode='r')
        buffer = BytesIO()
        img.save(buffer, format='PNG')

        print("THE BUFFER :: " + str(img))

        bucket_path = build_bucket_path(account, instance_uuid, upload_type, filename=filename)
        file_buffer = InMemoryUploadedFile(img, None, bucket_path, 'image/png', buffer.getbuffer().nbytes, None)

    else:
        raise ValueError(f"Invalid S3UploadType ({upload_type}) provided.")

    return file_buffer
