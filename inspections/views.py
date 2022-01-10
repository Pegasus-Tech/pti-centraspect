from django.shortcuts import render
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import JsonResponse
from inspection_items.models import InspectionItem
from .mixins import LogInspectionMixin
import json

# Create your views here.

class LogNewInspectionView(LoginRequiredMixin, LogInspectionMixin, View):
    
    def get(self, request, uuid, *args, **kwargs):
        template_name = 'dashboard/inspections/new_inspection.html'
        context = {}
        
        item = InspectionItem.objects.get(uuid=uuid)
        context['item'] = item
        context['form_json'] = json.dumps(item.form.form_json)
        return render(request, template_name, context)
    
    def post(self, request, uuid, *args, **kwargs):
        template_name = 'dashboard/inspections/new_inspection.html'
        context = {}
        
        item = InspectionItem.objects.get(uuid=uuid)
        form = self.request.POST
        
        print(f'Got Form :: {form}')
        inspection = self.log_inspection(inspection_item=item, 
                                         logged_by=self.request.user, 
                                         completed_form=form.get('form_json'),
                                         inspection_disposition=form.get('disposition'))
        
        if inspection.get('success'):
            print(f"SUCCESS :: {inspection.get('inspection')}")
            item = self.update_inspection_item_due_dates(inspection=inspection.get('inspection'))
            resp = {'url': f'/dashboard/inspection-items/{item.uuid}'}
            return JsonResponse(resp)
        else:
            print(f"FAILURE :: {inspection.get('inspection')}")
            context['item'] = item
            context['form_json'] = json.dumps(item.form.form_json)
            resp = {'url': f'/dashboard/inspections/new/{item.uuid}'}
            return JsonResponse(resp)