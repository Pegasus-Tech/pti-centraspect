from django.db import models
from django.db.models.deletion import CASCADE
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from authentication.models import User, Account
from centraspect.models import BaseModel
from centraspect.utils import S3UploadType, S3UploadUtils
from inspection_forms.models import InspectionForm
from datetime import date
from .utils import serialize_inspection_item


def qr_directory_path(instance, filename):
    upload_path = S3UploadUtils.build_upload_to_path(instance.account,instance.uuid, S3UploadType.QR_CODE)
    return f'qr_codes/{upload_path}/{filename}'


class InspectionItemManager(models.Manager):

    def get_all_active_for_account(self, account):
        if account is not None:
            qs = self.get_queryset().all().filter(is_active=True)\
                .filter(is_deleted=False)\
                .filter(failed_inspection=False)
            return qs
        else:
            raise ValueError("Account cannot be None")


    def get_count_past_due(self, account):
        if account is not None:
            qs = self.get_queryset().all()
            qs.filter(account=account)
            qs.filter(next_inspection_date__lt=date.today())
            return qs.filter(is_active=True)

    def get_closure_rate_for_account(self, account):
        if account is not None:
            qs = self.get_queryset().all()
            qs = qs.filter(account=account)
            qs = qs.filter(is_active=True)

            total = qs
            on_time = qs.filter()

            return


class InspectionInterval(models.TextChoices):
    DAILY = 'daily', _('Daily')
    WEEKLY = 'weekly', _('Weekly')
    MONTHLY = 'monthly', _('Monthly')
    QUARTERLY = 'quarterly', _('Quarterly')
    SEMI_ANNUALLY = 'semi-annually', _('Semi-Annually')
    ANNUALLY = 'annually', _('Annually')


class InspectionType(models.TextChoices):
    FACILITY = 'facility', _('Facility')
    PPE = 'ppe', _('PPE')
    EQUIPMENT = 'equipment', _('Equipment')
    RESCUE = 'rescue', _('Rescue Equipment')
    FIRST_AID = 'first aid', _('First Aid')
    VEHICLE = 'vehicle', _('Vehicle')
    OTHER = 'other', _('Other')


class InspectionItem(BaseModel):
    title = models.CharField(max_length=255, blank=False, null=False)
    description = models.TextField(max_length=1024, null=True, blank=True)
    inspection_interval = models.TextField(max_length=50, choices=InspectionInterval.choices, blank=False, null=False)
    inspection_type = models.TextField(max_length=50, choices=InspectionType.choices, blank=False, null=False)
    serial_number = models.CharField(max_length=250, blank=True, null=True)
    model_number = models.CharField(max_length=250, blank=True, null=True)
    first_inspection_date = models.DateField(null=True, blank=True)
    last_inspection_date = models.DateField(null=True, blank=True)
    next_inspection_date = models.DateField(null=False, blank=False)
    expiration_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    failed_inspection = models.BooleanField(default=False)
    
    form = models.ForeignKey(InspectionForm, on_delete=CASCADE, null=True, blank=True)
    assigned_to = models.ForeignKey(User, on_delete=CASCADE, null=True)
    account = models.ForeignKey(Account, on_delete=CASCADE)
    qr_code = models.ImageField(upload_to=qr_directory_path, blank=True, null=True)
    
    objects = InspectionItemManager()
    
    def get_absolute_url(self):
        return reverse("inspection_items:details", kwargs={"uuid": self.uuid})
    
    @property
    def is_past_due(self):
        return date.today() > self.next_inspection_date
    
    @property
    def is_due_today(self):
        return date.today() == self.next_inspection_date


@receiver(post_save, sender=InspectionItem)
def generate_qr_code_callback(sender, instance, created, *args, **kwargs):
    if created:
        data = serialize_inspection_item(instance)
        qr_code = S3UploadUtils.generate_qr_code_image(account=instance.account,
                                                       instance_uuid=instance.uuid,
                                                       serialized_data=data)
        instance.qr_code = qr_code
        instance.save()


@receiver(post_save, sender=InspectionItem)
def generate_inspections(sender, instance, created, *args, **kwargs):
    if created:
        pass
    return None