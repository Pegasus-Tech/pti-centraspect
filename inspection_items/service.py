from django.db.models import QuerySet
from .models import InspectionItem
from inspections.models import Inspection


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
