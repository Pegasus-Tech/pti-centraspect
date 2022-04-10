import uuid

from django.test import Client
from django.test import TestCase

from authentication.models import Account, User
from centraspect import messages
from inspection_items.models import InspectionItem, InspectionInterval, InspectionType
from inspection_forms.models import InspectionForm

from datetime import date, timedelta
import json


class LogInspectionTestCase(TestCase):

    client = Client()

    def setUp(self):
        acct = Account.objects.create(name='Test Account')
        user = User.objects.create(first_name='Test', last_name='User', email='test@user.com',
                                   username='test@user.com', password='abadone', account=acct,
                                   )
        today = date.today()
        next_week = today + timedelta(days=7)
        form = InspectionForm.objects.create(title="Test Form",
                                      form_json=json.loads('{"field_one": "key_one"}'),
                                      account=acct)
        InspectionItem.objects.create(title="Test Inspection", description="testing",
                                      inspection_interval=InspectionInterval.WEEKLY,
                                      inspection_type=InspectionType.PPE, serial_number='abc123',
                                      model_number='123abc', first_inspection_date=date.today(),
                                      next_inspection_date=next_week, account=acct, form=form)

    def test_api_get_form_response_success(self):
        item = InspectionItem.objects.get(title='Test Inspection')
        resp = self.client.get(f'/api/forms/{item.uuid}')
        self.assertEqual(resp.status_code, 200)

        data = json.loads(resp.content)

        self.assertIn("inspection_item_title", data.keys())
        self.assertIn("inspection_item_uuid", data.keys())
        self.assertIn("inspection_item_owner", data.keys())
        self.assertIn("inspection_item_owner_uuid", data.keys())
        self.assertIn("inspection_form_title", data.keys())
        self.assertIn("inspection_form_uuid", data.keys())
        self.assertIn("inspection_form", data.keys())

        self.assertTrue(data['inspection_item_uuid'] == str(item.uuid))
        self.assertTrue(data['inspection_form_uuid'] == str(item.form.uuid))

    def test_api_get_form_response_with_invalid_uuid(self):
        new_uuid = uuid.uuid4()
        resp = self.client.get(f'/api/forms/{new_uuid}')
        self.assertEqual(resp.status_code, 404)
        data = json.loads(resp.content)

        self.assertNotIn("inspection_item_title", data.keys())
        self.assertNotIn("inspection_item_uuid", data.keys())
        self.assertNotIn("inspection_item_owner", data.keys())
        self.assertNotIn("inspection_item_owner_uuid", data.keys())
        self.assertNotIn("inspection_form_title", data.keys())
        self.assertNotIn("inspection_form_uuid", data.keys())
        self.assertNotIn("inspection_form", data.keys())

        self.assertEqual(data['error_message'], messages.INVALID_INSPECTION_ITEM_UUID)

    def test_api_post_new_inspection_log_success(self):
        the_item = InspectionItem.objects.get(title='Test Inspection')
        body = {"disposition": "passed", "inspection_form_filled": "{'test_field':'test_answer'}"}
        resp = self.client.post(path=f"/api/forms/{the_item.uuid}", data=body)

        data = json.loads(resp.content)

        self.assertEqual(resp.status_code, 201)
        self.assertIn('url', data.keys())
        self.assertIn('inspection_log', data.keys())

    def test_api_post_new_inspection_log_with_empty_form_json(self):
        the_item = InspectionItem.objects.get(title='Test Inspection')
        body = {"disposition": "passed", "inspection_form_filled": ""}
        resp = self.client.post(path=f"/api/forms/{the_item.uuid}", data=body)

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(json.loads(resp.content)['error_message'], messages.NO_FORM_ATTACHED_ERROR)

    def test_api_post_new_inspection_log_with_no_form_json(self):
        the_item = InspectionItem.objects.get(title='Test Inspection')
        body = {"disposition": "passed"}
        resp = self.client.post(path=f"/api/forms/{the_item.uuid}", data=body)

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(json.loads(resp.content)['error_message'], messages.NO_FORM_ATTACHED_ERROR)
