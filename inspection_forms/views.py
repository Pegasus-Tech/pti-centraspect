from typing import Any, Dict
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.checks import messages
from django.http import request
from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import TemplateView, ListView, DetailView, DeleteView, View
from django.urls import reverse, reverse_lazy

from .forms import InspectionFormForm
from .models import InspectionForm

import json

class FormBuilderTemplateView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/form_builder/new_form.html'
    model = InspectionForm
    

class InspectionFormDetailView(LoginRequiredMixin, DetailView):
    template_name = 'dashboard/form_builder/form_detail.html'
    model = InspectionForm
    
    def get_object(self, queryset=None):
        return InspectionForm.objects.get(uuid=self.kwargs.get('uuid'))
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        form_json = context.get('object').form_json
        context['form_json'] = json.dumps(form_json)
        return context
        
class InspectionFormListView(LoginRequiredMixin, ListView):
    template_name = 'dashboard/form_builder/all_forms.html'
    model = InspectionForm
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        forms = InspectionForm.objects.get_all_for_account(self.request.user.account)
        context['forms'] = forms
        return context


class InspectionFormUpdateView(LoginRequiredMixin, View):
    model = InspectionForm
    
    def get(self, request, uuid):
        template_name = 'dashboard/form_builder/edit_form.html'
        inspection_form = InspectionForm.objects.filter(uuid=uuid).first()
        if inspection_form is not None:
            form_json = inspection_form.form_json
            context = {"inspection_form": inspection_form, "form_json": json.dumps(form_json)} 
            return render(request=request, template_name=template_name, context=context)
        else:
            context = {"error_message": f"No Inspection Form found for id {uuid}"}
            return render(request=request, template_name='400.html', context=context)
        
        
    def post(self, request, uuid):
        inspection_form = get_object_or_404(InspectionForm, uuid=uuid)
        form = InspectionFormForm(request.POST or None, instance=inspection_form)
        
        if(form.is_valid):
            form.save()
            return redirect(reverse("inspection_forms:details", kwargs={"uuid": uuid}))
        else:
           return render(request=request, template_name='400.html', context={"error_msg": "error saving form"})
       

class InspectionFormDeleteView(LoginRequiredMixin, View):
    model = InspectionForm
    def get(self, request, uuid):
       inspection_form = get_object_or_404(InspectionForm, uuid=uuid)
       inspection_form.is_active = False
       inspection_form.is_deleted = True
       inspection_form.save()
       return redirect(reverse_lazy('inspection_forms:list'))
    

@login_required
def create_form_ajax_view(request):
    print(f'got request {request}')
    form = InspectionFormForm(request.POST or None)
    new_form = form.save(commit=False)
    new_form.account = request.user.account
    new_form.save()
    resp = {'url': new_form.get_absolute_url()}
    return JsonResponse(resp)

@login_required
def update_form_ajax_view(request):
    pass