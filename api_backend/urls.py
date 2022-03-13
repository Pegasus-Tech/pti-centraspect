from django.urls import path, re_path
from .views import get_form_from_item, FormItemAPIView, attach_photos_to_inspection

app_name = 'api_backend'
urlpatterns = [
    path('forms/<uuid:uuid>', FormItemAPIView.as_view(), name="get_form_json"),
    path('upload/<uuid:uuid>', attach_photos_to_inspection, name="upload_inspection_photos")
]
