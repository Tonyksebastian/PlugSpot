from django import forms
from .models import  Subscription

class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = ['sub_type', 'price', 'validity', 'features']
        widgets = {
            'sub_type': forms.TextInput(attrs={
                "class": "form-control ",
                'id':'sub_type'
            }),
            'price': forms.TextInput(attrs={
                "class": "form-control ",
                'id':"price",
               
            }),
           'validity': forms.Select(attrs={
                "class": "form-control ",
                'id':'validity'
            }),
            'features': forms.TextInput(attrs={
                "class": "form-control ",
                'id':"features",
                'placeholder': 'Enter the Features',
                'required':False
            }),
            
         }