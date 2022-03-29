import datetime
import random
import string
import qrcode

from enum import Enum
from io import BytesIO
from calendar import monthrange
from dateutil.relativedelta import relativedelta
from datetime import date, timedelta

from django.core.files import File
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
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

        if upload_type == S3UploadType.QR_CODE:
            filename = S3UploadUtils.build_bucket_path(account, instance_uuid, upload_type)
            file_buffer = InMemoryUploadedFile(image, None, filename, 'image/png', image.getbuffer().nbytes, None)

            if S3UploadUtils.__validate_file_type(file_buffer):
                return file_buffer

        elif upload_type == S3UploadType.INSPECTION_IMAGE:
            temp_path = image.temporary_file_path()

            if S3UploadUtils.__validate_file_type(image):
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

    @staticmethod
    def generate_filename():
        return ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits, k=21))

    @staticmethod
    def __validate_file_type(file):
        extension = S3UploadUtils.__get_file_extension(file)

        if extension.lower() != 'png' and extension.lower() != 'jpg' and extension.lower() != 'jpeg':
            raise TypeError(f"Invalid image type provided '.{extension}'. Accepted images types are .png, .jpg/.jpeg")

        else:
            return True

    @staticmethod
    def __get_file_extension(file):
        if isinstance(file, InMemoryUploadedFile):
            return file.name.split('.')[-1]
        elif isinstance(file, TemporaryUploadedFile):
            return file.temporary_file_path().split('.')[-1]
        else:
            raise TypeError(f"Unknown file type: '{type(file)}")


class DateUtils:

    def __init__(self):
        pass

    @staticmethod
    def __get_weekly_block():
        start = date.today()

        # calc the block start date
        days_from_start = start.weekday()
        start_date = start - timedelta(days=days_from_start)

        # calc the block end date
        days_from_end = 6 - start.weekday()
        end_date = start + timedelta(days=days_from_end)

        rtn = (start_date, end_date)
        return rtn

    @staticmethod
    def __get_bi_weekly_block():
        pass

    @staticmethod
    def __get_monthly_block():
        today = date.today()
        days_in_month = monthrange(today.year, today.month)[1]

        # calc the start date
        days_from_start = today.day
        start_date = today - timedelta(days=days_from_start-1)

        # calc the end date
        days_to_go = days_in_month - today.day
        end_date = today + timedelta(days=days_to_go)

        rtn = (start_date, end_date)
        return rtn

    @staticmethod
    def __get_quarterly_block():
        today = date.today()
        quarter_months = ((1, 2, 3), (4, 5, 6), (7, 8, 9), (10, 11, 12))
        rtn = ()

        quarter = 0

        for i, q in enumerate(quarter_months):
            if today.month in q:
                quarter = i + 1
                break

        if quarter == 1:
            start_date = date(today.year, 1, 1)
            end_date = date(today.year, 3, 31)
            rtn = (start_date, end_date)
        elif quarter == 2:
            start_date = date(today.year, 4, 1)
            end_date = date(today.year, 6, 30)
            rtn = (start_date, end_date)
        elif quarter == 3:
            start_date = date(today.year, 7, 1)
            end_date = date(today.year, 9, 30)
            rtn = (start_date, end_date)
        elif quarter == 4:
            start_date = date(today.year, 10, 1)
            end_date = date(today.year, 12, 31)
            rtn = (start_date, end_date)
        else:
            raise ValueError("Error finding date for current annual quarter")

        return rtn

    @staticmethod
    def __get_annual_block():
        today = date.today()
        start_date = date(today.year, 1, 1)
        end_date = date(today.year, 12, 31)
        rtn = (start_date, end_date)
        return rtn

    @staticmethod
    def __get_semi_annual_block():
        today = date.today()
        start_date = None
        end_date = None

        if today.month < 7:
            start_date = date(today.year, 1, 1)
            end_date = date(today.year, 6, 30)
        elif today.month > 6:
            start_date = date(today.year, 7, 1)
            end_date = date(today.year, 12, 31)
        else:
            raise ValueError("Error finding date for current semi-annual range")

        rtn = (start_date, end_date)
        return rtn

    @staticmethod
    def __get_biennial_block():
        pass


    @staticmethod
    def __get_triennial_block():
        pass

    @staticmethod
    def increase_date_by_interval(date, interval):
        if interval == 'daily':
            return date + relativedelta(days=1)
        elif interval == 'weekly':
            return date + relativedelta(weeks=1)
        elif interval == 'bi-weekly':
            return date + relativedelta(weeks=2)
        elif interval == 'monthly':
            return date + relativedelta(months=1)
        elif interval == 'quarterly':
            return date + relativedelta(months=3)
        elif interval == 'annually':
            return date + relativedelta(years=1)
        elif interval == 'semi-annually':
            return date + relativedelta(months=6)
        elif interval == 'biennial':
            return date + relativedelta(years=2)
        elif interval == 'triennial':
            return date + relativedelta(years=3)
        else:
            return 0

    @staticmethod
    def get_inspection_time_block(interval):
        if interval == 'daily':
            return (date.today(), date.today())

        elif interval == 'weekly':
            return DateUtils.__get_weekly_block()

        elif interval == 'monthly':
            return DateUtils.__get_monthly_block()

        elif interval == 'quarterly':
            return DateUtils.__get_quarterly_block()

        elif interval == 'annually':
            return DateUtils.__get_annual_block()

        elif interval == 'semi-annually':
            return DateUtils.__get_semi_annual_block()

        else:
            return 0

