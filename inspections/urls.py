from django.urls import path
from.views import LogNewInspectionView

app_name="inpsections"
urlpatterns = [
    path('/new/<uuid:uuid>', LogNewInspectionView.as_view(), name='create')
]
