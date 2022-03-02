import json
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
from .models import InspectionItem, InspectionItemFilters
from . import service


class InspectionItemListView(LoginRequiredMixin, ListView):
    model = InspectionItem
    paginate_by = 10
    template_name = 'dashboard/inspection_items/all_inspection_items.html'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super(InspectionItemListView, self).get_context_data(**kwargs)
        acct = self.request.user.account
        query_params = self.request.GET
        context['sort_col'] = query_params.get('sort_col') if query_params.get('sort_col') else 'inspection_type'
        context['sort_dir'] = query_params.get('sort_dir') if query_params.get('sort_dir') else 'desc'
        context['types'] = service.get_unique_item_types_for_account(account=acct)
        context['intervals'] = service.get_unique_inspection_intervals_for_account(account=acct)

        filters_qs = InspectionItemFilters.objects.get_queryset().filter(created_by=self.request.user).filter(is_filtering=True)
        if filters_qs.count() > 0:
            filters = json.loads(filters_qs.get().filters)
            context['next_due_start'] = filters.get('next_due_start')[0]
            context['next_due_end'] = filters.get('next_due_end')[0]
            context['last_start'] = filters.get('last_start')[0]
            context['last_end'] = filters.get('last_end')[0]
            context['expiration_start'] = filters.get('expiration_start')[0]
            context['expiration_end'] = filters.get('expiration_end')[0]
            context['type'] = filters.get('type')
            context['interval'] = filters.get('interval')

        return context

    def get_queryset(self):
        req = self.request.GET
        qs = service.get_all_items_for_account(account=self.request.user.account, params=req)
        filters_qs = InspectionItemFilters.objects.get_queryset().filter(created_by=self.request.user).filter(is_filtering=True)

        if filters_qs.count() > 0:
            qs = service.set_filters_on_equipment(filters=filters_qs.first())

        return qs

    def post(self, *args, **kwargs):
        filters = {}
        print(self.request.POST)
        for k, v in self.request.POST.lists():
            if k != 'csrfmiddlewaretoken':
                filters[k] = v

        filter_obj = InspectionItemFilters.objects.filter(created_by=self.request.user).get()

        if filter_obj is None:
            filter_obj = InspectionItemFilters()

        filter_obj.filters = json.dumps(filters)
        filter_obj.is_filtering = True
        filter_obj.created_by = self.request.user

        filter_obj.save()
        return redirect('inspection_items:list')


class InspectionItemCreateView(LoginRequiredMixin, QRCodeGeneratorMixin, CreateView):
    model = InspectionItem
    template_name = 'dashboard/inspection_items/new_inspection_item.html'

    def get_form(self, **kwargs: Any) -> InspectionItemForm:
        form_class = super().get_form(InspectionItemForm)
        form_class.fields['assigned_to'].queryset = self.request.user.account.user_set.all().filter(is_active=True)
        form_class.fields['form'].queryset = self.request.user.account.inspectionform_set.all()
        return form_class

    def post(self, request, **kwargs: Any) -> Union[HttpResponseRedirect, HttpResponsePermanentRedirect]:
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

    def get(self, request, uuid, **kwargs: Any) -> HttpResponse:
        template_name = 'dashboard/inspection_items/update_inspection_item.html'
        inspection_item = get_object_or_404(InspectionItem, uuid=uuid)

        if inspection_item is not None:
            form = InspectionItemForm(None, instance=inspection_item)
            context = {"form": form, "inspection_item": inspection_item}
            return render(request=self.request, template_name=template_name, context=context)
        else:
            context = {"error_message": f"No Inspection Item found for id {uuid}"}
            return render(request=self.request, template_name='400.html')

    def post(self, request, uuid, **kwargs: Any) -> \
            Union[HttpResponse, HttpResponseRedirect, HttpResponsePermanentRedirect]:
        inspection_item = get_object_or_404(InspectionItem, uuid=uuid)
        form = InspectionItemForm(self.request.POST or None, instance=inspection_item)

        if form.is_valid:
            form.save()
            return redirect(reverse("inspection_items:details", kwargs={"uuid": uuid}))
        else:
            return render(request=self.request, template_name='400.html', context={"error_msg": "error saving form"})


class InspectionItemDeleteView(LoginRequiredMixin, View):
    model = InspectionItem

    def get(self, request, uuid, **kwargs: Any) -> Union[HttpResponseRedirect, HttpResponsePermanentRedirect]:
        instance = get_object_or_404(InspectionItem, uuid=uuid)
        instance.is_active = False
        instance.is_deleted = True
        instance.save()
        return redirect(reverse_lazy('inspection_items:list'))


def clear_filters(request):
    return redirect('inspection_items:list')
