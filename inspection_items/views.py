import json
from typing import Any, Dict, Union
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect, HttpResponsePermanentRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, CreateView, DetailView
from django.views.generic.base import View
from django.views.generic.edit import UpdateView
from django_q.tasks import async_task

from inspection_forms.models import InspectionForm
from qr_codes.behaviors import QRCodeGeneratorMixin
from .forms import InspectionItemForm, AddFormToItemForm
from .models import InspectionItem, SubItem
from .filters import InspectionItemsFilters
from . import service


class InspectionItemListView(LoginRequiredMixin, ListView):
    filter_set = None
    model = InspectionItem
    paginate_by = 10
    template_name = 'dashboard/inspection_items/all_inspection_items.html'

    def get_queryset(self):
        qs = super().get_queryset()
        self.filter_set = InspectionItemsFilters(self.request.GET, queryset=qs, request=self.request)
        return service.sort_queryset(qs=self.filter_set.qs, params=self.request.GET)

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super(InspectionItemListView, self).get_context_data(**kwargs)
        acct = self.request.user.account
        query_params = self.request.GET
        context['sort_col'] = query_params.get('sort_col') if query_params.get('sort_col') else 'next_inspection_date'
        context['sort_dir'] = query_params.get('sort_dir') if query_params.get('sort_dir') else 'asc'
        context['types'] = service.get_unique_item_types_for_account(account=acct)
        context['intervals'] = service.get_unique_inspection_intervals_for_account(account=acct)
        context['filter_form'] = self.filter_set.form
        return context

    def post(self, *args, **kwargs):
        print(self.request.POST)
        return redirect('inspection_items:list')


class InspectionItemCreateView(LoginRequiredMixin, QRCodeGeneratorMixin, CreateView):
    model = InspectionItem
    template_name = 'dashboard/inspection_items/new_inspection_item.html'

    def get_form(self, **kwargs: Any) -> InspectionItemForm:
        form_class = super().get_form(InspectionItemForm)
        form_class.fields['assigned_to'].queryset = self.request.user.account.user_set.all().filter(is_active=True)
        form_class.fields['form'].queryset = InspectionForm.objects.get_all_active_for_account(account=self.request.user.account)
        return form_class

    def post(self, request, **kwargs: Any) -> Union[HttpResponseRedirect, HttpResponsePermanentRedirect]:
        print(f'REQUEST :: {self.request.POST}')
        new_item = InspectionItemForm(self.request.user.account, self.request.POST or None).save(commit=False)

        new_item.account = self.request.user.account
        new_item.save()
        async_task('task_worker.service.build_future_inspections', new_item)
        return redirect('inspection_items:list')


class InspectionItemDetailView(LoginRequiredMixin, DetailView):
    template_name = 'dashboard/inspection_items/inspection_item_detail.html'
    model = InspectionItem

    def get_object(self, queryset=None) -> InspectionItem:
        return InspectionItem.objects.get(uuid=self.kwargs.get('uuid'))

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['form'] = AddFormToItemForm(account=self.request.user.account)
        context['inspections'] = service.get_all_completed_inspections_for_item(self.get_object())
        context['closure_rate'] = service.get_completion_rate_for_item(self.get_object())
        context['forms'] = InspectionForm.objects.get_all_active_for_account(self.request.user.account)
        return context


class InspectionItemUpdateView(LoginRequiredMixin, UpdateView):
    model = InspectionItem

    def get(self, request, uuid, **kwargs: Any) -> HttpResponse:
        template_name = 'dashboard/inspection_items/update_inspection_item.html'
        inspection_item = get_object_or_404(InspectionItem, uuid=uuid)

        if inspection_item is not None:
            form = InspectionItemForm(self.request.user.account, None, instance=inspection_item)
            context = {"form": form, "inspection_item": inspection_item}
            return render(request=self.request, template_name=template_name, context=context)
        else:
            context = {"error_message": f"No Inspection Item found for id {uuid}"}
            return render(request=self.request, template_name='400.html')

    def post(self, request, uuid, **kwargs: Any) -> \
            Union[HttpResponse, HttpResponseRedirect, HttpResponsePermanentRedirect]:
        inspection_item = get_object_or_404(InspectionItem, uuid=uuid)
        form = InspectionItemForm(self.request.user.account, self.request.POST or None, instance=inspection_item)

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

class InspectionSubItemCreateView(LoginRequiredMixin, View):
    model = SubItem

    def get(self, request):
        form = InspectionItemForm()
        form.fields['assigned_to'].queryset = self.request.user.account.user_set.all().filter(is_active=True)
        form.fields['form'].queryset = InspectionForm.objects.get_all_active_for_account(account=self.request.user.account)

        return render(request=request,
                      template_name='dashboard/inspection_items/new_inspection_kit.html',
                      context={"form": form})

def add_form_to_inspection_item(request, uuid):
    if request.POST:
        inspection_item = get_object_or_404(InspectionItem, uuid=uuid)
        form = AddFormToItemForm(request.user.account, request.POST)
        if form.is_valid():
            inspection_item.form = form.cleaned_data['form']
            inspection_item.save()
    return redirect('inspection_items:details', uuid=uuid)


def clear_filters(request):
    return redirect('inspection_items:list')


