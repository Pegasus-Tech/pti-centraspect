from inspection_items.models import InspectionItem
from centraspect.utils import DateUtils
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
