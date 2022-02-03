from typing import Any, Dict, Union
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect, HttpResponsePermanentRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, CreateView, DetailView
from django.views.generic.base import View
from django.views.generic.edit import UpdateView

from qr_codes.behaviors import QRCodeGeneratorMixin
from .forms import InspectionItemForm
from .models import InspectionItem
from . import service


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

    def get_form(self, **kwargs: Any) -> InspectionItemForm:
        form_class = super().get_form(InspectionItemForm)
        form_class.fields['assigned_to'].queryset = self.request.user.account.user_set.all().filter(is_active=True)
        form_class.fields['form'].queryset = self.request.user.account.inspectionform_set.all()
        return form_class

    def post(self, **kwargs: Any) -> Union[HttpResponseRedirect, HttpResponsePermanentRedirect]:
        print(f'REQUEST :: {self.request.POST}')
        new_item = InspectionItemForm(self.request.POST or None).save(commit=False)

        new_item.account = self.request.user.account
        new_item.save()
        return redirect('inspection_items:list')


class InspectionItemDetailView(LoginRequiredMixin, DetailView):
    template_name = 'dashboard/inspection_items/inspection_item_detail.html'
    model = InspectionItem

    def get_object(self, queryset=None) -> InspectionItem:
        return InspectionItem.objects.get(uuid=self.kwargs.get('uuid'))

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['inspections'] = service.get_all_inspections_for_item(self.get_object())
        context['closure_rate'] = service.get_completion_rate_for_item(self.get_object())
        return context


class InspectionItemUpdateView(LoginRequiredMixin, UpdateView):
    model = InspectionItem

    def get(self, uuid, **kwargs: Any) -> HttpResponse:
        template_name = 'dashboard/inspection_items/update_inspection_item.html'
        inspection_item = get_object_or_404(InspectionItem, uuid=uuid)

        if inspection_item is not None:
            form = InspectionItemForm(None, instance=inspection_item)
            context = {"form": form, "inspection_item": inspection_item}
            return render(request=self.request, template_name=template_name, context=context)
        else:
            context = {"error_message": f"No Inspection Item found for id {uuid}"}
            return render(request=self.request, template_name='400.html')

    def post(self, uuid, **kwargs: Any) -> Union[HttpResponse, HttpResponseRedirect, HttpResponsePermanentRedirect]:
        inspection_item = get_object_or_404(InspectionItem, uuid=uuid)
        form = InspectionItemForm(self.request.POST or None, instance=inspection_item)

        if form.is_valid:
            form.save()
            return redirect(reverse("inspection_items:details", kwargs={"uuid": uuid}))
        else:
            return render(request=self.request, template_name='400.html', context={"error_msg": "error saving form"})


class InspectionItemDeleteView(LoginRequiredMixin, View):
    model = InspectionItem

    def get(self, uuid, **kwargs: Any) -> Union[HttpResponseRedirect, HttpResponsePermanentRedirect]:
        instance = get_object_or_404(InspectionItem, uuid=uuid)
        instance.is_active = False
        instance.is_deleted = True
        instance.save()
        return redirect(reverse_lazy('inspection_items:list'))
