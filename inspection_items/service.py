import json
from typing import Iterable, Any
from django.db.models import QuerySet
from django.http.request import QueryDict
from .models import InspectionItem
from inspections.models import Inspection
from authentication.models import Account


def get_all_inspections_for_item(inspection_item) -> QuerySet:
    qs = Inspection.objects.filter(item=inspection_item).order_by('-completed_date')
    return qs


def get_completion_rate_for_item(inspection_item) -> int:
    qs = Inspection.objects.filter(item=inspection_item)
    on_time = qs.filter(completed_past_due=False)
    if qs.count() == 0:
        return 0

    closure_rate = (on_time.count() / qs.count()) * 100
    return round(closure_rate, 0)


# TODO: pull is_active=True into a decorator
def get_all_items_for_account(*, account: Account,
                              params: QueryDict = None,
                              ) -> Iterable[InspectionItem]:

    order_str = 'inspection_type'

    if params is not None:
        sort_col = params.get('sort_col') if params.get('sort_col') else 'inspection_type'
        sort_dir = params.get('sort_dir') if params.get('sort_dir') else 'desc'
        order_str_prepend = '-' if sort_dir == 'desc' else ''
        order_str = f'{order_str_prepend}{sort_col}'

    if account is not None:
        qs = InspectionItem.objects.all().filter(is_active=True).order_by(order_str)
        qs = qs.filter(account=account)
        return qs

    return []


def sort_queryset(*, qs: QuerySet, params: QueryDict = None) -> Iterable[InspectionItem]:
    if params is not None:
        sort_col = params.get('sort_col') if params.get('sort_col') else 'next_inspection_date'
        sort_dir = params.get('sort_dir') if params.get('sort_dir') else 'asc'
        order_str_prepend = '-' if sort_dir == 'desc' else ''
        order_str = f'{order_str_prepend}{sort_col}'

        return qs.order_by(order_str)


def get_unique_item_types_for_account(*, account: Account) -> Iterable[str]:
    if account is not None:
        qs = InspectionItem.objects.all().filter(is_active=True)
        return qs.order_by('inspection_type')\
            .values_list('inspection_type', flat=True)\
            .distinct('inspection_type')


def get_unique_inspection_intervals_for_account(*, account: Account) -> Iterable[str]:
    if account is not None:
        qs = InspectionItem.objects.all().filter(is_active=True)
        return qs.order_by('inspection_interval')\
            .values_list('inspection_interval', flat=True)\
            .distinct('inspection_interval')