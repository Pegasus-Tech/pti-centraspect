from .models import Inspection
from datetime import date, timedelta

import json

class LogInspectionMixin:

    def log_inspection(self, *args, **kwargs):
        """
            When an inspection is logged, we need to update the related inspection item
            to have the updated inpsection date, next due date, and then save the created 
            inspection log
        """
        rtn = {"success": False, "inspection": None}

        item = kwargs.get('inspection_item')
        user = kwargs.get('logged_by')
        json_form = kwargs.get('completed_form')
        disposition = kwargs.get('inspection_disposition')

        print(f"Got JSON form :: {json_form}")

        try:
            inspection = Inspection.objects.create(
                item=item,
                form=item.form,
                account=item.account,
                json=json_form,
                completed_by=user,
                completed_past_due=self.get_is_past_due(item.next_inspection_date),
                failed_inspection=self.is_failed_inspection(disposition)
            )
            rtn['inspection'] = inspection
            rtn['success'] = True
        except Exception as e:
            print(e)
        finally:
            return rtn

    def update_inspection_item_due_dates(self, *args, **kwargs):
        inspection = kwargs.get('inspection')
        item = inspection.item

        if inspection.failed_inspection:
            item.failed_inspection = True
            item.save()
        else:
            days = self.get_days_to_add(item.inspection_interval)
            next_due_date = inspection.completed_date + timedelta(days=days)
            item.next_inspection_date = next_due_date
            item.last_inspection_date = inspection.completed_date
            item.save()

        return item

    def get_days_to_add(self, interval):

        if interval == 'daily':
            return 1
        elif interval == 'weekly':
            return 7
        elif interval == 'bi-weekly':
            return 14
        elif interval == 'semi-weekly':
            return 4
        elif interval == 'ten day':
            return 10
        elif interval == 'monthly':
            return 28
        elif interval == 'semi-monthly':
            return 15
        elif interval == 'quarterly':
            return 84
        elif interval == 'annually':
            return 365
        elif interval == 'semi-annually':
            return 183
        elif interval == 'biennial':
            return 730
        elif interval == 'triennial':
            return 1095
        else:
            return 0

    def get_is_past_due(self, the_date):
        return date.today() > the_date

    def is_failed_inspection(self, disposition):
        print(f'DISPOSITION :: {disposition}')
        return disposition == 'fail'
