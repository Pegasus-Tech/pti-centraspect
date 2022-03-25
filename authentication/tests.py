from django.test import Client, TestCase

from .models import Account, Roles, User
from centraspect import messages
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
        resp, data = self.__get_login_response("test@user.com", "abadone")
        self.assertEqual(resp.status_code, 200)

    def test_valid_response_body_on_successful_login(self):
        resp, data = self.__get_login_response("test@user.com", "abadone")

        self.assertIn('account_uuid', data.keys())
        self.assertIn('auth_token', data.keys())
        self.assertIn('refresh_token', data.keys())
        self.assertIn('expires', data.keys())
        self.assertIn('ROLES', data.keys())

    def test_correct_account_uuid_in_response(self):
        acct = Account.objects.get(name='Test Account 2')
        resp, data = self.__get_login_response("test3@user.com", "abadone")
        self.assertEqual(str(acct.uuid), data['account_uuid'])

    def test_valid_uuids_in_multiple_logins(self):
        user1 = User.objects.get(email='test@user.com')
        resp, data = self.__get_login_response(user1.email, "abadone")

        user2 = User.objects.get(email='test2@user.com')
        resp2, data2 = self.__get_login_response(user2.email, "abadone")

        user3 = User.objects.get(email='test3@user.com')
        resp3, data3 = self.__get_login_response(user3.email, "abadone")

        self.assertEqual(str(user1.account.uuid), data['account_uuid'])
        self.assertEqual(str(user2.account.uuid), data2['account_uuid'])
        self.assertEqual(str(user3.account.uuid), data3['account_uuid'])
        self.assertEqual(data['account_uuid'], data2['account_uuid'])
        self.assertNotEqual(data['account_uuid'], data3['account_uuid'])

    def test_response_for_invalid_email(self):
        resp, data = self.__get_login_response("bad@email.com", "abadone")

        self.assertEqual(resp.status_code, 400)
        self.assertIn("Credential Error", data.keys())
        self.assertEqual(data['Credential Error'], messages.INVALID_USER_CREDENTIAL_ERROR)

    def test_response_for_invalid_password(self):
        resp, data = self.__get_login_response("test@user.com", "wrongPassword")

        self.assertEqual(resp.status_code, 400)
        self.assertIn("Credential Error", data.keys())
        self.assertEqual(data['Credential Error'], messages.INVALID_USER_CREDENTIAL_ERROR)

    def test_refresh_token_success(self):
        resp, data = self.__get_login_response("test@user.com", "abadone")
        auth_token = data['auth_token']
        ref_token = data['refresh_token']

        ref_resp = self.client.post(path='/api/auth/refresh_token',
                                    data={"refresh_token": ref_token},
                                    content_type='application/json')

        self.assertEqual(ref_resp.status_code, 200)
        self.assertNotEqual(auth_token, json.loads(ref_resp.content)['auth_token'])

    def test_no_refresh_token_provided(self):
        ref_resp = self.client.post(path='/api/auth/refresh_token',
                                    data={},
                                    content_type='application/json')
        data = json.loads(ref_resp.content)
        self.assertEqual(ref_resp.status_code, 400)
        self.assertEqual(data['error_message'], messages.NO_REFRESH_TOKEN_PROVIDED_ERROR)

    def test_invalid_refresh_token_provided(self):
        ref_resp = self.client.post(path='/api/auth/refresh_token',
                                    data={"refresh_token": "this-doesnt-exist"},
                                    content_type='application/json')

        data = json.loads(ref_resp.content)
        self.assertEqual(ref_resp.status_code, 400)
        self.assertEqual(data['error_message'], messages.INVALID_REFRESH_TOKEN_ERROR)

    def __get_login_response(self, email, password):
        creds = {"email": email, "password": password}
        resp = self.client.post(path='/api/auth/login', data=creds, content_type='application/json')
        data = json.loads(resp.content)
        return resp, data
