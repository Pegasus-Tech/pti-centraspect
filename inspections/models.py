from django.db import models
from centraspect.models import BaseModel
from centraspect.utils import S3UploadType, S3UploadUtils
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
            qs = qs.filter(item=item)
            return qs
        else:
            return self.get_queryset().none()


class Inspection(BaseModel):
    form = models.ForeignKey(InspectionForm, on_delete=models.PROTECT)
    item = models.ForeignKey(InspectionItem, on_delete=models.PROTECT)
    account = models.ForeignKey(Account, on_delete=models.PROTECT)
    json = models.JSONField(null=False, blank=False)
    completed_by = models.ForeignKey(User, on_delete=models.PROTECT)
    completed_date = models.DateTimeField(auto_now_add=True)
    completed_past_due = models.BooleanField()
    failed_inspection = models.BooleanField(null=False)

    def to_json(self):
        return {
            "uuid": self.uuid,
            "completed_data": self.completed_date,
            "completed_past_due": self.completed_past_due,
            "failed_inspection": self.failed_inspection
        }


class InspectionImage(BaseModel):
    inspection = models.ForeignKey(Inspection, on_delete=models.PROTECT)
    image = models.ImageField(upload_to=qr_directory_path, max_length=1000, blank=True, null=True)
