from django import forms
from django.forms import fields

from authentication.models import User
from inspection_forms.models import InspectionForm

from .models import InspectionInterval, InspectionItem, InspectionType

class InspectionItemForm(forms.ModelForm):    
    
    title = forms.CharField(widget=forms.TextInput(attrs={'class':'uk-input', 'placeholder':'Form Title or Name'}))
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={'class':'uk-textarea', 'rows':'1'}))
    inspection_interval = forms.ChoiceField(choices=[(interval, interval.label) for interval in InspectionInterval], 
                                            widget=forms.Select(attrs={'class':'uk-select'}))
    inspection_type = forms.ChoiceField(choices=[(ins_type, ins_type.label) for ins_type in InspectionType], 
                                            widget=forms.Select(attrs={'class':'uk-select'}))
    serial_number = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'uk-input'}))
    model_number = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'uk-input'}))
    first_inspection_date = forms.DateField(required=False, widget=forms.TextInput(attrs={'class':'uk-input', 'type':'date'}))
    last_inspection_date = forms.DateField(required=False, widget=forms.TextInput(attrs={'class':'uk-input', 'type':'date'}))
    next_inspection_date = forms.DateField(widget=forms.TextInput(attrs={'class':'uk-input', 'type':'date'}))
    expiration_date = forms.DateField(required=False, widget=forms.TextInput(attrs={'class':'uk-input', 'type':'date'}))
    assigned_to = forms.ModelChoiceField(required=False, queryset=User.objects.all(), widget=forms.Select(attrs={'class':'uk-select'}))
    form = forms.ModelChoiceField(required=False, queryset=InspectionForm.objects.all(), widget=forms.Select(attrs={'class':'uk-select'}))
    
    
    class Meta:
        model = InspectionItem
        fields = ['title', 'description', 'inspection_interval', 'inspection_type', 
                  'serial_number', 'model_number','first_inspection_date', 
                  'last_inspection_date','next_inspection_date', 'expiration_date', 
                  'form', 'assigned_to']
         