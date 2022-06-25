from django.urls import path

from .views import SitesListView

app_name = "sites"

urlpatterns = [
    path("", SitesListView.as_view(), name="all"),
]
