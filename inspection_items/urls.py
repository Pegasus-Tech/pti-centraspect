from django.urls import path
from .views import (InspectionItemListView, InspectionItemCreateView, 
                    InspectionItemDetailView, InspectionItemUpdateView, 
                    InspectionItemDeleteView)

app_name = 'inspection_items'
urlpatterns = [
   path('/', InspectionItemListView.as_view(), name='list'),
   path('/new', InspectionItemCreateView.as_view(), name='create'),
   path('/<uuid:uuid>', InspectionItemDetailView.as_view(), name="details"),
   path('/<uuid:uuid>/edit', InspectionItemUpdateView.as_view(), name="update"),
   path('/<uuid:uuid>/delete', InspectionItemDeleteView.as_view(), name="delete")
]