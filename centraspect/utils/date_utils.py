
from calendar import monthrange
from dateutil.relativedelta import relativedelta
from datetime import date, timedelta
from inspections.service import get_last_due_date_for_item, get_last_inspection_by_due_date


class DateUtils:

    def __init__(self):
        pass

    @staticmethod
    def __get_weekly_block():
        start = date.today()

        # calc the block start date
        days_from_start = start.weekday()
        start_date = start - timedelta(days=days_from_start)

        # calc the block end date
        days_from_end = 6 - start.weekday()
        end_date = start + timedelta(days=days_from_end)

        rtn = (start_date, end_date)
        return rtn

    @staticmethod
    def __get_bi_weekly_block(item):
        last_due_inspection = get_last_due_date_for_item(item=item).first()
        print(f'last_due_inspection :: {last_due_inspection}')
        if last_due_inspection is not None:
            print(f'got inspection :: {last_due_inspection}')
            start_date = last_due_inspection.due_date
            end_date = (start_date + timedelta(weeks=2)) - timedelta(days=1)
            rtn = (start_date, end_date)
            return rtn
        else:
            last_due = get_last_inspection_by_due_date(item).first()

            if last_due is None:
                # if no due date exists, then just return today + 2 weeks
                rtn = (date.today(), (date.today() + timedelta(weeks=2)) - timedelta(days=1))
                return rtn

            start_date = last_due.due_date
            end_date = (last_due.due_date + timedelta(weeks=2)) - timedelta(days=1)
            rtn = (start_date, end_date)
            return rtn

    @staticmethod
    def __get_monthly_block():
        today = date.today()
        days_in_month = monthrange(today.year, today.month)[1]

        # calc the start date
        days_from_start = today.day
        start_date = today - timedelta(days=days_from_start-1)

        # calc the end date
        days_to_go = days_in_month - today.day
        end_date = today + timedelta(days=days_to_go)

        rtn = (start_date, end_date)
        return rtn

    @staticmethod
    def __get_quarterly_block():
        today = date.today()
        quarter_months = ((1, 2, 3), (4, 5, 6), (7, 8, 9), (10, 11, 12))
        rtn = ()

        quarter = 0

        for i, q in enumerate(quarter_months):
            if today.month in q:
                quarter = i + 1
                break

        if quarter == 1:
            start_date = date(today.year, 1, 1)
            end_date = date(today.year, 3, 31)
            rtn = (start_date, end_date)
        elif quarter == 2:
            start_date = date(today.year, 4, 1)
            end_date = date(today.year, 6, 30)
            rtn = (start_date, end_date)
        elif quarter == 3:
            start_date = date(today.year, 7, 1)
            end_date = date(today.year, 9, 30)
            rtn = (start_date, end_date)
        elif quarter == 4:
            start_date = date(today.year, 10, 1)
            end_date = date(today.year, 12, 31)
            rtn = (start_date, end_date)
        else:
            raise ValueError("Error finding date for current annual quarter")

        return rtn

    @staticmethod
    def __get_annual_block():
        today = date.today()
        start_date = date(today.year, 1, 1)
        end_date = date(today.year, 12, 31)
        rtn = (start_date, end_date)
        return rtn

    @staticmethod
    def __get_semi_annual_block():
        today = date.today()
        start_date = None
        end_date = None

        if today.month < 7:
            start_date = date(today.year, 1, 1)
            end_date = date(today.year, 6, 30)
        elif today.month > 6:
            start_date = date(today.year, 7, 1)
            end_date = date(today.year, 12, 31)
        else:
            raise ValueError("Error finding date for current semi-annual range")

        rtn = (start_date, end_date)
        return rtn

    @staticmethod
    def __get_biennial_block():
        pass


    @staticmethod
    def __get_triennial_block():
        pass

    @staticmethod
    def increase_date_by_interval(date, interval):
        if interval == 'daily':
            return date + relativedelta(days=1)
        elif interval == 'weekly':
            return date + relativedelta(weeks=1)
        elif interval == 'bi-weekly':
            return date + relativedelta(weeks=2)
        elif interval == 'monthly':
            return date + relativedelta(months=1)
        elif interval == 'quarterly':
            return date + relativedelta(months=3)
        elif interval == 'annually':
            return date + relativedelta(years=1)
        elif interval == 'semi-annually':
            return date + relativedelta(months=6)
        elif interval == 'biennial':
            return date + relativedelta(years=2)
        elif interval == 'triennial':
            return date + relativedelta(years=3)
        else:
            return 0

    @staticmethod
    def get_inspection_time_block(item):
        interval = item.inspection_interval

        if interval == 'daily':
            return (date.today(), date.today())

        elif interval == 'weekly':
            return DateUtils.__get_weekly_block()

        elif interval == 'bi-weekly':
            print('bi-weekly block')
            return DateUtils.__get_bi_weekly_block(item)

        elif interval == 'monthly':
            return DateUtils.__get_monthly_block()

        elif interval == 'quarterly':
            return DateUtils.__get_quarterly_block()

        elif interval == 'annually':
            return DateUtils.__get_annual_block()

        elif interval == 'semi-annually':
            return DateUtils.__get_semi_annual_block()

        else:
            return 0

