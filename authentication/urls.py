from django.urls import path
from .views import AccountUsersListView, AccountCreateUserView, AccountUserDeactivateView, user_detail_view

app_name="authentication"
urlpatterns = [
    path("", AccountUsersListView.as_view(), name="all"),
    path('new', AccountCreateUserView.as_view(), name="create"),
    path('<uuid:uuid>', user_detail_view, name="details"),
    path('<uuid:uuid>/deactivate', AccountUserDeactivateView.as_view(), name="deactivate")
]
