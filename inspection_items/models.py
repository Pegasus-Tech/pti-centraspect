from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.serializers import serialize
from django.db import models
from django.db.models.deletion import CASCADE
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from authentication.models import User, Account
from centraspect.models import BaseModel
from centraspect.utils import generate_qr_code_image, _build_bucket_path
from inspection_forms.models import InspectionForm
from datetime import date
from .utils import serialize_inspection_item


from io import BytesIO, StringIO
import qrcode

def qr_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return f'qr_codes/{_build_bucket_path(instance.account, instance.uuid)}'


class InspectionItemManager(models.Manager):
    
    def get_all_for_account(self, account):
        if account is not None:
            qs = self.get_queryset().all()
            qs = qs.filter(account=account)
            return qs.filter(is_active=True)
    
        
    

class InspectionInterval(models.TextChoices):
    DAILY = 'daily', _('Daily')
    WEEKLY = 'weekly', _('Weekly')
    BI_WEEKLY = 'bi-weekly', _('Bi-Weekly')
    SEMI_WEEKLY = 'semi-weekly', _('Semi-Weekly')
    TEN_DAY = 'ten day', _('10 Day')
    MONTHLY = 'monthly', _('Monthly')
    SEMI_MONTHLY = 'semi-monthly', _('Semi-Monthly')
    QUARTERLY = 'quarterly', _('Quarterly')
    ANNUALLY = 'annually', _('Annually')
    SEMI_ANNUALLY = 'semi-annually', _('Semi-Annually')
    BIENNIAL = 'biennial', _('Biennial')
    TRIENNIAL = 'triennial', _('Triennial')


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
        qr_code = generate_qr_code_image(account=instance.account, instance_uuid=instance.uuid, serialized_data=data)
        instance.qr_code = qr_code
        instance.save()
