from django import forms
from charger_management.models import Pool, Charger, ChargerTypes
from car_checkout.models import ChargingProcedure

class addPoolForm(forms.Form):
    name = forms.CharField(label="Pool Name", max_length=128, widget=forms.TextInput(attrs={'class': 'form-control formCharField'}))
    longitude = forms.IntegerField(label="longitude", widget=forms.NumberInput(attrs={'class': 'form-control formIntField'}))
    latitude = forms.IntegerField(label="latitude", widget=forms.NumberInput(attrs={'class': 'form-control formIntField'}))

class removePoolForm(forms.Form):
    name = forms.ModelChoiceField(label="Pool Name", queryset=Pool.objects.all(), widget=forms.Select(attrs={'class': 'form-control formSelectField'}))

class addChargerForm(forms.Form):
    name = forms.CharField(label="Charger Name", max_length=128, widget=forms.TextInput(attrs={'class': 'form-control formCharField'}))
    pool = forms.ModelChoiceField(label="Pool", queryset=Pool.objects.all(), widget=forms.Select(attrs={'class': 'form-control formSelectField'}))
    longitude = forms.IntegerField(label="longitude", widget=forms.NumberInput(attrs={'class': 'form-control formIntField'}))
    latitude = forms.IntegerField(label="latitude", widget=forms.NumberInput(attrs={'class': 'form-control formIntField'}))

    charger_type = forms.ModelChoiceField(label="Types", queryset=ChargerTypes.objects.all(), widget=forms.Select(attrs={'class': 'form-control formSelectField'}))

class removeChargerForm(forms.Form):
    name = forms.ModelChoiceField(label="Charger Name", queryset=Charger.objects.all(), widget=forms.Select(attrs={'class': 'form-control formSelectField'}))

class addChargerTypeForm(forms.Form):
    name = forms.CharField(label="Charger Type", max_length=128, widget=forms.TextInput(attrs={'class': 'form-control formCharField'}))
    kw = forms.DecimalField(label="KW", widget=forms.NumberInput(attrs={'class': 'form-control formIntField'}))

class removeChargerTypeForm(forms.Form):
    name = forms.ModelChoiceField(label="Charger Type", queryset=ChargerTypes.objects.all(), widget=forms.Select(attrs={'class': 'form-control formSelectField'}))

class relocateCarForm(forms.Form):
    cpid = forms.ModelChoiceField(label="Id", queryset=ChargingProcedure.objects.filter(needs_relocation=True), widget=forms.Select(attrs={'class': 'form-control formSelectField font-product-sans custom--button'}))
    pool = forms.ModelChoiceField(label="Pool", queryset=Pool.objects.all(), widget=forms.Select(attrs={'class': 'form-control formSelectField'}))
    charger = forms.ModelChoiceField(label="Charger", queryset=Charger.objects.filter(is_available=True), required=False, widget=forms.Select(attrs={'class': 'form-control formSelectField'}))

from functools import partial
DateTimeInput = partial(forms.DateTimeInput, {'class': 'datepicker'})

class manipulateTransaction(forms.Form):
    car = forms.ModelChoiceField(label="Id", queryset=ChargingProcedure.objects.all(), widget=forms.Select(attrs={'class': 'form-control formSelectField'}))
    parked_from = forms.DateTimeField(label="New Parked From", widget=forms.Select(attrs={'class': 'form-control'}))#widget=DateTimeInput())

class uploadCarInfoForm(forms.Form):
    file = forms.FileField(widget=forms.FileInput(attrs={'class': 'form-control'}))