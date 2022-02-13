from django.shortcuts import render
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.serializers import serialize
from inspection_items.models import InspectionItem
from inspection_items.service import get_all_items_for_account


class InspectionCalendarView(LoginRequiredMixin, View):
    
    def get(self, *args, **kwargs):
        template_name = 'dashboard/inspection_calendar/calendar.html'
        upcoming_inspections = get_all_items_for_account(account=self.request.user.account)
        return render(self.request, template_name, {"items": serialize('json', upcoming_inspections)})
