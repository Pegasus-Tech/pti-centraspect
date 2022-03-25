from django.test import Client, TestCase

from .models import Account, Roles, User
from inspection_forms.models import InspectionForm
from inspection_items.models import InspectionItem, InspectionInterval, InspectionType

from datetime import date, timedelta
import json


class TestAuthenticationAPI(TestCase):

    def setUp(self) -> None:
        client = Client()
        acct = Account.objects.create(name='Test Account')
        user1 = User.objects.create(first_name='Test', last_name='User', email='test@user.com',
                                   username='test@user.com', account=acct, role=Roles.INSPECTOR)
        user1.set_password('abadone')
        user1.save()

        user2 = User.objects.create(first_name='Test2', last_name='User2', email='test2@user.com',
                                    username='test2@user.com', account=acct, role=Roles.ACCOUNT_ADMIN)
        user2.set_password('abadone')
        user2.save()

        acct2 = Account.objects.create(name='Test Account 2')
        user3 = User.objects.create(first_name='Test3', last_name='User3', email='test3@user.com',
                                    username='test3@user.com', account=acct2, role=Roles.ACCOUNT_ADMIN)
        user3.set_password('abadone')
        user3.save()

    def test_successful_api_login(self):
        creds = {"email": "test@user.com", "password": "abadone"}
        resp = self.client.post(path='/api/auth/login', data=creds, content_type='application/json')
        self.assertEqual(resp.status_code, 200)

    def test_valid_response_body_on_successful_login(self):
        creds = {"email": "test@user.com", "password": "abadone"}
        resp = self.client.post(path='/api/auth/login', data=creds, content_type='application/json')
        data = json.loads(resp.content)

        self.assertIn('account_uuid', data.keys())
        self.assertIn('auth_token', data.keys())
        self.assertIn('refresh_token', data.keys())
        self.assertIn('expires', data.keys())
        self.assertIn('ROLES', data.keys())

    def test_correct_account_uuid_in_response(self):
        acct = Account.objects.get(name='Test Account 2')
        creds = {"email": "test3@user.com", "password": "abadone"}
        resp = self.client.post(path='/api/auth/login', data=creds, content_type='application/json')
        data = json.loads(resp.content)

        self.assertEqual(str(acct.uuid), data['account_uuid'])

    def test_valid_uuids_in_multiple_logins(self):
        user1 = User.objects.get(email='test@user.com')
        acct1 = user1.account

        user2 = User.objects.get(email='test2@user.com')
        acct2 = user2.account

        user3 = User.objects.get(email='test3@user.com')
        acct3 = user3.account

        # login all 3 and check account_uuids in responses for valid ones.
