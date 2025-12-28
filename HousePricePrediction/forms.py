from django import forms
from .models import UserProfile

class UserProfileForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = UserProfile
        fields = ['full_name', 'email', 'phone', 'address', 'profile_pic', 'password']
