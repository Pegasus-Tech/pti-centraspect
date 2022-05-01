from django.db.models import Q

from inspection_items.models import InspectionItem
from centraspect.utils.date_utils import DateUtils
from inspections.models import Inspection

from datetime import date, timedelta


def build_future_inspections(item: InspectionItem):
    """
        Async worker that will build and persist the inspections
        into the db when a new item is created.
    """
    print("starting the async build....")
    start_date = item.next_inspection_date
    expiration = item.expiration_date

    two_years = 365 * 2
    final_date = expiration if expiration is not None else start_date + timedelta(days=two_years)
    next_due_date = start_date

    print(f"Start Date: {start_date} :: Final Date: {final_date}")

    while next_due_date <= final_date:
        print(f"Creating inspection for {next_due_date}")
        inspection = Inspection(form=item.form, item=item, account=item.account, due_date=next_due_date)
        inspection.save()
        next_due_date = DateUtils.increase_date_by_interval(next_due_date, item.inspection_interval)
        print("done creating inspection...")


def delete_unlogged_inspections(item: InspectionItem):
    qs = Inspection.objects.get_all_for_item(item=item)
    qs = qs.filter(completed_date__isnull=True)\
        .filter(missed_inspection=False)\
        .filter(Q(failed_inspection=False) | Q(failed_inspection__isnull=True))

    for inspection in qs:
        inspection.is_deleted = True
        inspection.save()


def update_inspection_intervals(item):
    """
    TODO:
        if the inspection interval gets changed,
        we need to calc the future due dates
        from the last due date/completed date
        (could be completed if the inspection was completed past due or
        another inspection was added to the list)
    """
    print(f"Updating Intervals to :: {item}")
    items = Inspection.objects.get_all_for_item(item=item)

    if items.exists():
        last_due_inspection = items.filter(due_date__lte=date.today()).order_by('-due_date').first()
        if last_due_inspection is not None:
            # recalc all dates from the last_due_date
            next_due_date = last_due_inspection.due_date
            to_update = items.filter(due_date__gte=next_due_date).order_by('due_date')
            for insp in to_update:
                insp.due_date = next_due_date
                insp.save()
                next_due_date = DateUtils.increase_date_by_interval(next_due_date, item.inspection_interval)

        else:
            # get all dates and recalc them all
            ordered_inspections = items.order_by('due_date')
            next_due_date = ordered_inspections.first().due_date

            for insp in ordered_inspections:
                insp.due_date = next_due_date
                insp.save()
                next_due_date = DateUtils.increase_date_by_interval(next_due_date, item.inspection_interval)
    else:
        build_future_inspections(item=item)


def cache_inspection_updates(inspection):
    """
        async worker that will update a single object
        in the cache with the latest updates.
    """
    pass


def update_inspection_cache():
    """
        async worker that will update the cache with the latest inspection state
        This is also called from a scheduled task that runs nightly to keep the cache updated
    """
    pass
