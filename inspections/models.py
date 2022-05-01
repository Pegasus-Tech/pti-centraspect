from django.db import models
from centraspect.models import BaseModel
from centraspect.utils.S3Utils import S3UploadType, S3UploadUtils
from inspection_forms.models import InspectionForm
from inspection_items.models import InspectionItem
from authentication.models import Account, User


def qr_directory_path(instance, filename):
    bucket_path = S3UploadUtils.build_upload_to_path(instance.inspection.account,
                                                instance.inspection.uuid,
                                                S3UploadType.INSPECTION_IMAGE,)
    path = f'inspections/{bucket_path}/{filename}'
    return path


class InspectionManager(models.Manager):
    def get_by_natural_key(self, uuid):
        return self.get(uuid=uuid)

    def get_all_for_account(self, account, *args, **kwargs):
        if account is not None:
            qs = self.get_queryset().all()
            qs = qs.filter(account=account)
            return qs
        else:
            return self.get_queryset().none()

    def get_all_active_for_account(self, account, *args, **kwargs):
        if account is not None:
            qs = self.get_queryset().all()
            qs = qs.filter(account=account).filter(is_deleted=False)
            return qs
        else:
            return self.get_queryset().none()

    def get_all_for_user(self, user, *args, **kwargs):
        if user is not None:
            qs = self.get_queryset().all()
            qs = qs.filter(user=user)
            return qs
        else:
            return self.get_queryset().none()

    def get_all_for_form(self, form, *args, **kwargs):
        if form is not None:
            qs = self.get_queryset().all()
            qs = qs.filter(form=form)
            return qs
        else:
            return self.get_queryset().none()

    def get_all_for_item(self, item, *args, **kwargs):
        if item is not None:
            qs = self.get_queryset().all()
            qs = qs.filter(item=item, is_deleted=False)
            return qs
        else:
            return self.get_queryset().none()


class Inspection(BaseModel):
    form = models.ForeignKey(InspectionForm, on_delete=models.PROTECT, null=True)
    item = models.ForeignKey(InspectionItem, on_delete=models.PROTECT)
    account = models.ForeignKey(Account, on_delete=models.PROTECT)
    json = models.JSONField(null=True, blank=True)
    completed_by = models.ForeignKey(User, on_delete=models.PROTECT, null=True)
    due_date = models.DateField(null=False)
    completed_date = models.DateTimeField(null=True)
    completed_past_due = models.BooleanField(null=True, default=False)
    missed_inspection = models.BooleanField(null=True, default=False)
    failed_inspection = models.BooleanField(null=True, default=False)
    is_deleted = models.BooleanField(null=True, default=False)
    objects = InspectionManager()

    def to_json(self):
        return {
            "uuid": str(self.uuid),
            "due_date": str(self.due_date),
            "title": self.item.title,
            "item_uuid": str(self.item.uuid),
            "inspection_type": self.item.inspection_type,
            "completed_date": str(self.completed_date),
            "completed_past_due": self.completed_past_due,
            "missed": self.missed_inspection,
            "failed_inspection": self.failed_inspection
        }


class InspectionImage(BaseModel):
    inspection = models.ForeignKey(Inspection, on_delete=models.PROTECT)
    image = models.ImageField(upload_to=qr_directory_path, max_length=1000, blank=True, null=True)
