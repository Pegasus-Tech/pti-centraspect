from django import forms
from authentication.models import User


class AdminCreateUserForm(forms.ModelForm):
    GROUPS = [
        ('Viewer', 'Viewer'),
        ('User', 'User'),
        ('Inspector', 'Inspector'),
        ('Account Admin', 'Account Admin')
    ]

    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'uk-input', 'placeholder': 'User First Name'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'uk-input', 'placeholder': 'User Last Name'}))
    email = forms.CharField(widget=forms.EmailInput(attrs={'class': 'uk-input', 'placeholder': 'User Email'}))
    group = forms.ChoiceField(choices=GROUPS, widget=forms.Select(attrs={'class': 'uk-select'}))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'group']
