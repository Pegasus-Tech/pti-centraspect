from typing import Any, Dict
from django.db.models.query import QuerySet
from django.forms.models import ModelChoiceIterator
from django.http import request
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView, CreateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import View
from django.views.generic.edit import UpdateView
from django.urls import reverse, reverse_lazy

from authentication.models import User
from inspection_forms.models import InspectionForm
from qr_codes.behaviors import QRCodeGeneratorMixin
from .forms import InspectionItemForm
from .models import InspectionInterval, InspectionItem, InspectionType


class InspectionItemListView(LoginRequiredMixin, ListView):
    template_name = 'dashboard/inspection_items/all_inspection_items.html'
    model = InspectionItem
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super(InspectionItemListView, self).get_context_data(**kwargs)
        items = InspectionItem.objects.get_all_for_account(self.request.user.account)
        context['inspection_items'] = items
        return context
    
class InspectionItemCreateView(LoginRequiredMixin, QRCodeGeneratorMixin, CreateView):
    model = InspectionItem
    template_name = 'dashboard/inspection_items/new_inspection_item.html'

    def get_form(self):
        form_class = super().get_form(InspectionItemForm)
        form_class.fields['assigned_to'].queryset = self.request.user.account.user_set.all().filter(is_active=True) 
        form_class.fields['form'].queryset = self.request.user.account.inspectionform_set.all()
        return form_class
    
    
    def post(self, request):
        print(f'REQUEST :: {request.POST}')
        new_item = InspectionItemForm(request.POST or None).save(commit=False)
        
        new_item.account = request.user.account
        new_item.save()
        return redirect('inspection_items:list')

class InspectionItemDetailView(LoginRequiredMixin, DetailView):
    template_name = 'dashboard/inspection_items/inspection_item_detail.html'
    model = InspectionItem
    
    def get_object(self, queryset=None) -> InspectionItem:
        return InspectionItem.objects.get(uuid=self.kwargs.get('uuid'))
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        
        return context

class InspectionItemUpdateView(LoginRequiredMixin, UpdateView):
    model = InspectionItem

    def get(self, request, uuid):
        template_name = 'dashboard/inspection_items/update_inspection_item.html'
        inspection_item = get_object_or_404(InspectionItem, uuid=uuid)
        
        if inspection_item is not None:
            form = InspectionItemForm(None, instance=inspection_item)
            return render(request=request, template_name=template_name, context={"form":form, "inspection_item":inspection_item})
        else:
            context = {"error_message": f"No Inspection Item found for id {uuid}"}
            return render(request=request, template_name='400.html')
        
        
    def post(self, request, uuid):
        inspection_item = get_object_or_404(InspectionItem, uuid=uuid)
        form = InspectionItemForm(request.POST or None, instance=inspection_item)
        
        if(form.is_valid):
            form.save()
            return redirect(reverse("inspection_items:details", kwargs={"uuid": uuid}))
        else:
           return render(request=request, template_name='400.html', context={"error_msg": "error saving form"})


class InspectionItemDeleteView(LoginRequiredMixin, View):
    model = InspectionItem

    def get(self, request, uuid):
        instance = get_object_or_404(InspectionItem, uuid=uuid)
        instance.is_active = False
        instance.is_deleted = True
        instance.save()
        return redirect(reverse_lazy('inspection_items:list'))