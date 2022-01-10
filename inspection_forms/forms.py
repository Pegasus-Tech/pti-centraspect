from django import forms
from django import forms
from .models import InspectionForm

class InspectionFormForm(forms.ModelForm):
    
    class Meta:
        model = InspectionForm
        fields = ("title", "form_json",)
