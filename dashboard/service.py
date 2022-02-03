from datetime import datetime, timedelta
from inspection_items.models import InspectionItem
from inspections.models import Inspection


def get_upcoming_inspections_for_account(account):
    return InspectionItem.objects.get_all_for_account(account)


def get_dashboard_metrics_for_account(account):
    starting_day_of_current_year = datetime.now().date().replace(month=1, day=1)
    opd_counts = get_open_past_due_counts(account, starting_day_of_current_year)
    rtn = {
        "closure_rate": get_on_time_closure_rate(account, starting_day_of_current_year),
        "open_past_due_count": opd_counts['opd'],
        "total_completed": opd_counts['all'],
        "pending_inspections": get_pending_next_30_days(account)
    }
    return rtn


def get_all_inspections_for_this_year(account, start_date):
    qs = Inspection.objects.filter(account=account)
    all_this_year = qs.filter(completed_date__gte=start_date)
    return all_this_year


def get_on_time_closure_rate(account, start_date):
    all_this_year = get_all_inspections_for_this_year(account, start_date)
    on_time_completions = all_this_year.filter(completed_past_due=False)

    if all_this_year.count() <= 0:
        return 0

    closure_rate = (on_time_completions.count() / all_this_year.count()) * 100
    return round(closure_rate, 0)


def get_open_past_due_counts(account, start_date):
    rtn = {"all": 0, "opd": 0}

    all_this_year = get_all_inspections_for_this_year(account, start_date)
    rtn['all'] = all_this_year.count()

    # get inspection items that are past due
    items = InspectionItem.objects.filter(account=account)
    items_this_year = items.filter(next_inspection_date__gte=start_date)
    opd = items_this_year.filter(next_inspection_date__lt=datetime.now().date())
    rtn['opd'] = opd.count()

    return rtn


def get_pending_next_30_days(account):
    today = datetime.now().date()
    qs = InspectionItem.objects.filter(account=account)
    today_or_greater = qs.filter(next_inspection_date__gte=today)
    next_30_days = today_or_greater.filter(next_inspection_date__lte=today + timedelta(days=30))

    return next_30_days.count()
