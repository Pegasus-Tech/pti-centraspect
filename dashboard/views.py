import json

from django.shortcuts import render
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from . import service


class DashboardView(LoginRequiredMixin, View):

    def get(self, *args, **kwargs):
        template_name = 'dashboard/index.html'
        account = self.request.user.account
        upcoming_inspections = service.get_upcoming_inspections_for_account(account)
        inspections_json = service.get_inspections_for_calendar(upcoming_inspections)
        metrics = service.get_dashboard_metrics_for_account(account)
        return render(self.request, template_name,
                      {
                          "inspections": json.dumps(inspections_json),
                          "metrics": metrics
                      })
