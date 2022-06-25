from django.db import models

from authentication.models import Account, User
from centraspect.models import BaseModel
from inspection_items.models import InspectionItem


class SiteManager(models.Manager):

    def get_all_active_for_account(self, account):
        if account is not None:
            return self.get_queryset().all().filter(account=account, is_active=True)
        else:
            return self.get_queryset().none()


class Site(BaseModel):
    name = models.CharField(max_length=500, null=False, blank=False)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    users = models.ManyToManyField(User)
    equipment = models.ForeignKey(InspectionItem, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    objects = SiteManager()
