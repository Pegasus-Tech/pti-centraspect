from django.urls import path
from .views import AccountUsersListView, AccountCreateUserView, AccountUserDeactivateView, user_detail_view
from .api_view import get_auth_token, refresh_auth_token, access_this

app_name="authentication"
urlpatterns = [
    path("", AccountUsersListView.as_view(), name="all"),
    path('new', AccountCreateUserView.as_view(), name="create"),
    path('<uuid:uuid>', user_detail_view, name="details"),
    path('<uuid:uuid>/deactivate', AccountUserDeactivateView.as_view(), name="deactivate"),

    path('login', get_auth_token, name='api_login'),
    path('refresh_token', refresh_auth_token, name="refresh_token"),
    path('test', access_this, name='access_this')
]
