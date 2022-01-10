from django import forms
from authentication.models import Account, User, Roles
        
class AdminCreateUserForm(forms.ModelForm):
    ROLES = [
        ('base_user', 'User'),
        ('inspector', 'Equipment Inspector'),
        ('account_admin', 'Account Administrator')
    ]
    
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class':'uk-input', 'placeholder':'User First Name'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class':'uk-input', 'placeholder':'User Last Name'}))
    email = forms.CharField(widget=forms.EmailInput(attrs={'class':'uk-input', 'placeholder':'User Email'}))
    role = forms.ChoiceField(choices=ROLES, widget=forms.Select(attrs={'class':'uk-select'}))
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'role']