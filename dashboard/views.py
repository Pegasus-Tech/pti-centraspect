from django.shortcuts import render
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.serializers import serialize
from inspection_items.models import InspectionItem
from . import service


class DashboardView(LoginRequiredMixin, View):

    def get(self, *args, **kwargs):
        template_name = 'dashboard/index.html'
        account = self.request.user.account
        upcoming_inspections = service.get_upcoming_inspections_for_account(account)
        metrics = service.get_dashboard_metrics_for_account(account)
        return render(self.request, template_name,
                      {
                          "items": serialize('json', upcoming_inspections),
                          "metrics": metrics
                      })
