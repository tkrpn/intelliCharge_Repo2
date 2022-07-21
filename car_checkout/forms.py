from django import forms
from charger_management.models import Pool, Car

class carCheckoutForm(forms.Form):
    pool = forms.ModelChoiceField(label="Pool", queryset=Pool.objects.all(), widget=forms.Select(attrs={'class': 'form-control formSelectField font-product-sans custom--button'})) #form-control formSelectField dropdown--menu 
    car = forms.ModelChoiceField(label="Car", queryset=Car.objects.all(), widget=forms.Select(attrs={'class': 'form-control formCharField'}))
    charging_state = forms.IntegerField(label="State of Charge (%)", widget=forms.NumberInput(attrs={'class': 'range-input', 'type': 'range', 'min':'0', 'max':'100', 'value':'45', 'steps':'1'}))
    distance_traveled = forms.IntegerField(label="Total Vehicle kilometers after trip (KM)", widget=forms.NumberInput(attrs={'class': 'form-control formIntField'}))

    #dropdown--menu font-product-sans position-absolute w-100 dropdown 