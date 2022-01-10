from rest_framework import serializers
from inspection_forms.models import InspectionForm

class InspectionFormSerializer(serializers.ModelSerializer):
    class Meta:
        model=InspectionForm
        fields=['title', 'form_json']

class FormSerializer(serializers.Serializer):
    item_uuid = serializers.UUIDField()
    form_uuid = serializers.UUIDField()
    assigned_to_uuid = serializers.UUIDField(required=False, allow_null=True)
    form_json = serializers.JSONField()