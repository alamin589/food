from django import forms
from .models import Customer, MealOff

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'lunch_category', 'dinner_category', 'plan_days']

class MealOffForm(forms.ModelForm):
    class Meta:
        model = MealOff
        fields = ['lunch_off', 'dinner_off']
