from django.urls import path
from .views import InspectionCalendarView

app_name = 'inspection_calendar'
urlpatterns = [
    path('/calendar', InspectionCalendarView.as_view(), name="calendar")
]
