from django.shortcuts import render
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.serializers import serialize
from inspection_items.models import InspectionItem


class DashboardView(LoginRequiredMixin, View):

    def get(self, *args, **kwargs):
        template_name = 'dashboard/index.html'
        upcoming_inspections = InspectionItem.objects.get_all_for_account(self.request.user.account)
        return render(self.request, template_name, {"items": serialize('json', upcoming_inspections)})
