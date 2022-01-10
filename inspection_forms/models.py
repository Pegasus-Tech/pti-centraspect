from django.db.models.deletion import CASCADE
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify

from authentication.models import Account
from centraspect.models import BaseModel

class InspectionFormManager(models.Manager):
    
    def get_all_for_account(self, account):
        if account is not None:
            qs = self.get_queryset().all()\
            .filter(account=account)\
            .filter(is_active=True)\
            .filter(is_deleted=False)
            return qs
        

class InspectionForm(BaseModel):
    class FormType(models.TextChoices):
        INSPECTION = 'inspection', _('Inspection')
    
    title = models.CharField(max_length=255, blank=False, null=False)
    form_json = models.JSONField()
    form_type = models.CharField(max_length=50, choices=FormType.choices, blank=False, null=False, default=FormType.INSPECTION)
    account = models.ForeignKey(Account, on_delete=CASCADE)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    objects = InspectionFormManager()
    
    def __str__(self) -> str:
        return self.title
    
    def get_absolute_url(self):
        return reverse('inspection_forms:details', kwargs={'uuid': self.uuid})