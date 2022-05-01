import json
from typing import Any, Dict, Union
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect, HttpResponsePermanentRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, CreateView, DetailView
from django.views.generic.base import View
from django.views.generic.edit import UpdateView
from django_q.tasks import async_task

from authentication.mixins import GroupRequiredMixin
from centraspect import settings
from inspection_forms.models import InspectionForm
from qr_codes.behaviors import QRCodeGeneratorMixin
from .forms import InspectionItemForm, AddFormToItemForm, SubComponentForm, SubComponentFailureReasonForm
from .models import InspectionItem, SubItem
from .filters import InspectionItemsFilters
from . import service

from datetime import datetime


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


class InspectionItemCreateView(GroupRequiredMixin, LoginRequiredMixin, QRCodeGeneratorMixin, CreateView):
    group_names = [settings.ACCOUNT_ADMIN_GROUP, settings.INSPECTOR_GROUP]
    model = InspectionItem
    template_name = 'dashboard/inspection_items/new_inspection_item.html'

    def get_form(self, **kwargs: Any) -> InspectionItemForm:
        form_class = super().get_form(InspectionItemForm)
        form_class.fields['assigned_to'].queryset = self.request.user.account.user_set.all().filter(is_active=True)\
            .filter(groups__name__in=[settings.ACCOUNT_ADMIN_GROUP, settings.INSPECTOR_GROUP, settings.USER_GROUP])
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
        if self.get_object().is_kit:
            context['components'] = service.get_all_components_for_kit(kit=self.get_object())
        return context


class InspectionItemUpdateView(GroupRequiredMixin, LoginRequiredMixin, UpdateView):
    group_names = [settings.ACCOUNT_ADMIN_GROUP, settings.INSPECTOR_GROUP]
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
            if inspection_item.inspection_interval != request.POST.get('inspection_interval'):
                form.save()
                async_task('task_worker.service.update_inspection_intervals', inspection_item)
            else:
                form.save()
            return redirect(reverse("inspection_items:details", kwargs={"uuid": uuid}))
        else:
            return render(request=self.request, template_name='400.html', context={"error_msg": "error saving form"})


class InspectionItemDeleteView(GroupRequiredMixin, LoginRequiredMixin, View):
    group_names = [settings.ACCOUNT_ADMIN_GROUP, ]
    model = InspectionItem

    def get(self, request, uuid, **kwargs: Any) -> Union[HttpResponseRedirect, HttpResponsePermanentRedirect]:
        instance = get_object_or_404(InspectionItem, uuid=uuid)
        instance.is_active = False
        instance.is_deleted = True
        instance.save()
        async_task('task_worker.service.delete_unlogged_inspections', instance)
        return redirect(reverse_lazy('inspection_items:list'))


class InspectionSubItemCreateView(GroupRequiredMixin, LoginRequiredMixin, View):
    group_names = [settings.ACCOUNT_ADMIN_GROUP, settings.INSPECTOR_GROUP]
    model = SubItem

    def get(self, request):
        form = InspectionItemForm()
        form.fields['assigned_to'].queryset = self.request.user.account.user_set.all().filter(is_active=True)
        form.fields['form'].queryset = InspectionForm.objects.get_all_active_for_account(account=self.request.user.account)

        return render(request=request,
                      template_name='dashboard/inspection_items/new_inspection_kit.html',
                      context={"form": form})

    def post(self, request, **kwargs):
        data = json.loads(request.body)
        print(f'Kit Request Data :: {data}')
        try:
            form_id = data['form'] if data['form'] != '' else None
            assigned_to_id = data['assigned_to'] if data['assigned_to'] != '' else None
            expiration_date = datetime.strptime(data['expiration_date'], '%Y-%m-%d') if data['expiration_date'] else None
            item = InspectionItem.objects.create(title=data['title'],
                                                 is_kit=True,
                                                 account=request.user.account,
                                                 description=data['description'],
                                                 serial_number=data['serial_number'],
                                                 model_number=data['model_number'],
                                                 inspection_type=data['inspection_type'],
                                                 inspection_interval=data['inspection_interval'],
                                                 assigned_to_id=assigned_to_id,
                                                 form_id=form_id,
                                                 next_inspection_date=datetime.strptime(data['next_inspection_date'],
                                                                                        '%Y-%m-%d'),
                                                 expiration_date=expiration_date)

            print(f'created it {item}')
            sub_items = data['subItems']

            for sub_item in sub_items:
                expiration = sub_item['expiration_date'] if sub_item['expiration_date'] else None
                SubItem.objects.create(kit=item,
                                       title=sub_item['name'],
                                       serial_number=sub_item['serial_number'],
                                       model_number=sub_item['model_number'],
                                       expiration_date=expiration)
            messages.success(request, f"Success! A new kit was created.")
            async_task('task_worker.service.build_future_inspections', item)
            return JsonResponse(status=200, data={"item_uuid": str(item.uuid)})

        except Exception as e:
            print(e)
            return JsonResponse(status=500, data={"error": str(e)})


@login_required
def add_component_to_kit(request, uuid):
    if request.POST:
        kit = get_object_or_404(InspectionItem, uuid=uuid)
        form = SubComponentForm(request.POST)
        if form.is_valid():
            comp = form.save(commit=False)
            comp.kit = kit

            try:
                comp.save()
                messages.success(request, f"Added {comp.title} to Kit: {kit.title}")
                return redirect('inspection_items:details', uuid=uuid)
            except Exception as e:
                print("ERROR ADDING COMPONENT TO KIT", e)
                return JsonResponse(status=400, data={"error_message": "Error adding component to kit"})
        else:
            return JsonResponse(status=400, data={"error_message": "Invalid Form Submitted"})


@login_required
def edit_component(request, uuid):
    if request.POST:
        component = get_object_or_404(SubItem, uuid=uuid)
        form = SubComponentForm(request.POST)
        if form.is_valid():
            component.title = form.cleaned_data['title']
            component.serial_number = form.cleaned_data['serial_number']
            component.model_number = form.cleaned_data['model_number']
            component.expiration_date = form.cleaned_data['expiration_date']
            component.save()
            messages.success(request, f"Successfully updated {component.title}")
            return redirect('inspection_items:details', uuid=component.kit.uuid)
        else:
            messages.error(request, f"Unexpected error occurred updated {component.title}")
            return redirect('inspection_items:details', uuid=component.kit.uuid)


@login_required
def delete_component(request, uuid):
    print(f"IN DELETE METHOD FOR UUID :: {uuid}")
    if request.POST:
        component = get_object_or_404(SubItem, uuid=uuid)
        component.is_deleted = True
        component.is_active = False
        try:
            component.save()
            messages.success(request, f"{component.title} successfully removed from kit {component.kit.title}")
            return redirect('inspection_items:details', uuid=component.kit.uuid)
        except Exception as e:
            print('ERROR: Error deleting component ', e)
            messages.error(request, f"Unexpected error occurred trying to delete component {component.title}")
            return redirect('inspection_items:details', uuid=component.kit.uuid)


@login_required
def mark_component_failed(request, uuid):
    if request.POST:
        component = get_object_or_404(SubItem, uuid=uuid)
        form = SubComponentFailureReasonForm(request.POST)
        if form.is_valid():
            component.failed_inspection = True
            component.is_active = False
            component.failure_reason = form.cleaned_data['failure_reason']
            try:
                component.save()
                messages.warning(request, f"{component.title} permanently marked as failed/defective")
                return redirect('inspection_items:details', uuid=component.kit.uuid)
            except Exception as e:
                print('ERROR: Error marking component failed/defective ', e)
                messages.error(request, f"Unexpected error occurred trying to mark component {component.title} failed/defective")
                return redirect('inspection_items:details', uuid=component.kit.uuid)


@login_required
def add_form_to_inspection_item(request, uuid):
    if request.POST:
        inspection_item = get_object_or_404(InspectionItem, uuid=uuid)
        form = AddFormToItemForm(request.user.account, request.POST)
        if form.is_valid():
            inspection_item.form = form.cleaned_data['form']
            inspection_item.save()
    return redirect('inspection_items:details', uuid=uuid)


@login_required
def clear_filters(request):
    return redirect('inspection_items:list')


