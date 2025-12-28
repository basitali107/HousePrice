# floor_map/forms.py
from django import forms

class FloorMapForm(forms.Form):
    total_area = forms.IntegerField(
        label='Total Area (sq ft)',
        min_value=100,
        max_value=10000,
        initial=1000,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter total area'
        })
    )
    bedrooms = forms.IntegerField(
        label='Number of Bedrooms',
        min_value=1,
        max_value=10,
        initial=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Number of bedrooms'
        })
    )
    bathrooms = forms.IntegerField(
        label='Number of Bathrooms',
        min_value=1,
        max_value=5,
        initial=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Number of bathrooms'
        })
    )