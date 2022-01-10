from django.urls import path
from .views import (FormBuilderTemplateView, 
                    create_form_ajax_view, 
                    InspectionFormDetailView, 
                    InspectionFormListView, 
                    InspectionFormUpdateView,
                    InspectionFormDeleteView)

app_name = "inspection_forms"
urlpatterns= [
    path('', FormBuilderTemplateView.as_view(), name='form_builder'),
    path('/create', create_form_ajax_view, name='create'),
    path('/<uuid:uuid>', InspectionFormDetailView.as_view(), name='details'),
    path('/all', InspectionFormListView.as_view(), name='list'),
    path('/<uuid:uuid>/edit', InspectionFormUpdateView.as_view(), name="edit"),
    path('/<uuid:uuid>/delete', InspectionFormDeleteView.as_view(), name="delete")
]