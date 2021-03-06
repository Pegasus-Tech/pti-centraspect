import datetime

from .models import Inspection


def get_inspection_by_item_in_date_range(item, date_range):
    print(f"Searching for inspections in date range :: {date_range}")
    qs = Inspection.objects.get_all_for_item(item=item)
    qs = qs.filter(completed_date__isnull=True).filter(due_date__range=date_range)
    return qs


def update_missed_inspection_for_item(item, prior_to_date):
    qs = Inspection.objects.get_all_for_item(item=item)\
        .filter(completed_date__isnull=True)\
        .filter(due_date__lt=prior_to_date)
    count = 0

    for inspection in qs.all():
        inspection.missed_inspection = True
        inspection.save()
        count += 1

    return count


def get_last_due_date_for_item(item):
    qs = Inspection.objects.get_all_for_item(item=item)
    qs = qs.filter(completed_date__isnull=False).order_by('-completed_date')
    return qs


def get_last_inspection_by_due_date(item):
    qs = Inspection.objects.get_all_for_item(item=item)
    qs = qs.filter(due_date__lte=datetime.date.today()).order_by('-due_date')
    return qs
