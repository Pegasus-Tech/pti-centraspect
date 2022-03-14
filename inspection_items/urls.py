from django.urls import path
from .views import (InspectionItemListView, InspectionItemCreateView,
                    InspectionItemDetailView, InspectionItemUpdateView,
                    InspectionItemDeleteView, clear_filters, add_form_to_inspection_item)

app_name = 'inspection_items'
urlpatterns = [
    path('', InspectionItemListView.as_view(), name='list'),
    path('new', InspectionItemCreateView.as_view(), name='create'),
    path('<uuid:uuid>', InspectionItemDetailView.as_view(), name="details"),
    path('<uuid:uuid>/edit', InspectionItemUpdateView.as_view(), name="update"),
    path('<uuid:uuid>/delete', InspectionItemDeleteView.as_view(), name="delete"),
    path('<uuid:uuid>/add_form', add_form_to_inspection_item, name='add_form'),
    path('clear_filters', clear_filters, name="clear_filters"),
]
