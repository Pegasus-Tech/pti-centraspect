from django.urls import path
from .views import (InspectionItemListView, InspectionItemCreateView, InspectionItemDetailView,
                    InspectionItemUpdateView, InspectionItemDeleteView, InspectionSubItemCreateView,
                    clear_filters, add_form_to_inspection_item, add_component_to_kit, edit_component,
                    delete_component, mark_component_failed)

app_name = 'inspection_items'
urlpatterns = [
    path('', InspectionItemListView.as_view(), name='list'),
    path('new', InspectionItemCreateView.as_view(), name='create'),
    path('kit', InspectionSubItemCreateView.as_view(), name="create_sub_item"),
    path('<uuid:uuid>', InspectionItemDetailView.as_view(), name="details"),
    path('<uuid:uuid>/edit', InspectionItemUpdateView.as_view(), name="update"),
    path('<uuid:uuid>/delete', InspectionItemDeleteView.as_view(), name="delete"),
    path('<uuid:uuid>/add_form', add_form_to_inspection_item, name='add_form'),
    path('<uuid:uuid>/add-component', add_component_to_kit, name='add_component_to_kit'),
    path('clear_filters', clear_filters, name="clear_filters"),
    path('edit-component/<uuid:uuid>', edit_component, name='edit_component'),
    path('delete-component/<uuid:uuid>', delete_component, name='delete_sub_item'),
    path('mark-failed/<uuid:uuid>', mark_component_failed, name='mark_sub_item_failed')
]
