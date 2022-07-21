from itertools import chain
from django.http import HttpResponse
import json

from django.shortcuts import render, redirect

from charger_management.forms import addChargerForm, addPoolForm, removeChargerForm, removePoolForm, addChargerTypeForm, removeChargerTypeForm, uploadCarInfoForm
from charger_management.models import ChargerTypes, Pool, Charger, Car
from car_checkout.models import ChargingProcedure

from charger_management.forms import relocateCarForm, manipulateTransaction

from datetime import datetime, timedelta
import pytz
tz = pytz.timezone('Europe/Berlin')

from car_checkout.decisionEngine import chargingTimeApprox, refreshCurrentSoC, chargingStateApprox, chargingPlot

from django.contrib.auth.decorators import login_required
from .decorators import group_required

#@login_required
#@group_required('Fleet Manager')
#UNUSED
def index(request):
    context = {
        'pools': Pool.objects.all().order_by('id'),  
        'chargers': Charger.objects.all().order_by('pool__id', 'name'), 
        'chargerTypes': ChargerTypes.objects.all(), 
        'addPoolForm': addPoolForm(), 
        'removePoolForm': removePoolForm(), 
        'addChargerForm': addChargerForm(), 
        'removeChargerForm': removeChargerForm(), 
        'addChargerType': addChargerTypeForm(), 
        'removeChargerType': removeChargerTypeForm(),
        'uploadCarInfoForm': uploadCarInfoForm()}
    return render(request, 'manage.html', context=context)

def chargers(request):
    context = {
        'chargers': Charger.objects.all().order_by('pool__id', 'name'), 
        'chargerTypes': ChargerTypes.objects.all(), 
        'addChargerForm': addChargerForm(), 
        'removeChargerForm': removeChargerForm(), 
        'addChargerType': addChargerTypeForm(), 
        'removeChargerType': removeChargerTypeForm()}
    return render(request, 'chargers.html', context=context)

def pools(request):
    context = {
        'pools': Pool.objects.all().order_by('id'),  
        'addPoolForm': addPoolForm(), 
        'removePoolForm': removePoolForm()}
    return render(request, 'pools.html', context=context)

def fleet(request):
    context = {'uploadCarInfoForm': uploadCarInfoForm()}
    return render(request, 'fleet.html', context=context)

#@login_required
#@group_required('Fleet Manager', 'Maintenance Crew')
def poolAdded(request):
    if request.method == 'POST':
        form = addPoolForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            longitude = form.cleaned_data['longitude']
            latitude = form.cleaned_data['latitude']
            
            p = Pool(name=name, longitude=longitude, latitude=latitude)
            p.save()

            return redirect('/management/pools/')#, permanent=True)
            #return HttpResponse(f"<h1>addPool {form.cleaned_data['name']}</h1>")

#@login_required
#@group_required('Fleet Manager', 'Maintenance Crew')
def removedPool(request):
    if request.method == 'POST':
        form = removePoolForm(request.POST)
        if form.is_valid():
            obj = form.cleaned_data['name']
            Pool.objects.filter(id=obj.id).delete()

            return redirect('/management/pools/')
            #return HttpResponse(f"<h1>removedPool {form.cleaned_data['name']}</h1>")

#@login_required
#@group_required('Fleet Manager', 'Maintenance Crew')
def chargerAdded(request):
    if request.method == 'POST':
        form = addChargerForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            pool = form.cleaned_data['pool']
            longitude = form.cleaned_data['longitude']
            latitude = form.cleaned_data['latitude']

            charger_type = form.cleaned_data['charger_type']
            
            p = Charger(name=name, pool=pool, charger_type=charger_type, longitude=longitude, latitude=latitude)
            p.save()

            return redirect('/management/chargers/')
            #return HttpResponse(f"<h1>addCharger {form.cleaned_data['name']}</h1>")

#@login_required
#@group_required('Fleet Manager', 'Maintenance Crew')
def removedCharger(request):
    if request.method == 'POST':
        form = removeChargerForm(request.POST)
        if form.is_valid():
            obj = form.cleaned_data['name']
            Charger.objects.filter(id=obj.id).delete()

            return redirect('/management/chargers/')

#@login_required
#@group_required('Fleet Manager')
def chargerTypeAdded(request):
    if request.method == 'POST':
        form = addChargerTypeForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            kw = form.cleaned_data['kw']
            
            p = ChargerTypes(name=name, kw=kw)
            p.save()

            return redirect('/management/chargers/')

#@login_required
#@group_required('Fleet Manager')
def removedChargerType(request):
    if request.method == 'POST':
        form = removeChargerTypeForm(request.POST)
        if form.is_valid():
            obj = form.cleaned_data['name']
            Charger.objects.filter(id=obj.id).delete()

            return redirect('/management/chargers/')

#@login_required
#@group_required('Fleet Manager')
def removedChargerType(request):
    if request.method == 'POST':
        form = removeChargerTypeForm(request.POST)
        if form.is_valid():
            obj = form.cleaned_data['name']
            ChargerTypes.objects.filter(id=obj.id).delete()

            return redirect('/management/chargers/')

#@login_required
#@group_required('Fleet Manager')
def uploadCarInfo(request):
    if request.method == 'POST':
        form = uploadCarInfoForm(request.POST, request.FILES)
        if form.is_valid():
            obj = request.FILES['file']

            cars = json.loads(obj.read())

            Car.objects.all().delete()
            for car in cars:
                p = Car(licence_plate=car["licence_plate"], brand=car["brand"], model=car["model"], battery_capacity=car["battery_capacity"])
                p.save()
            return redirect('/management/fleet/')

#@login_required
#@group_required('Maintenance Crew')
def transactionOverview(request):
    queryset_charging = ChargingProcedure.objects.all()
    updated_queryset = refreshCurrentSoC(queryset_charging)

    graph = None
    for i in updated_queryset:
        if i.parked_until:
            duration = (i.parked_until - i.parked_from).seconds
            h, rem = divmod(duration, 3600)
            m, _ = divmod(rem, 60)
            i.duration = f"{h} hours and {m} minutes"
            #graph = chargingPlot(i.car.battery_capacity, i.charger.charger_type.kw, initial_soc=i.charging_state, current_charging_state=i.current_charging_state)

    form = manipulateTransaction()
    return render(request, "transactions.html", {'transactions': updated_queryset, 'form': form, 'graph': graph})


#@login_required
#@group_required('Maintenance Crew')
def manipulateTransactionView(request):
    if request.method == "POST":
        form = manipulateTransaction(request.POST)
        if form.is_valid():
            cp = form.cleaned_data['car']
            parked_from = form.cleaned_data['parked_from']

            ChargingProcedure.objects.filter(id=cp.id).update(parked_from=parked_from)
            return redirect('/management/transactions/')

#@login_required
#@group_required('Fleet Manager')
def removeTransactions(request):
    ChargingProcedure.objects.all().delete()
    Charger.objects.all().update(is_available=True)

    return HttpResponse("Transactions removed!")


#@login_required
#@group_required('Maintenance Crew')
def maintenanceView(request):
    queryset = ChargingProcedure.objects.all()
    
    updated_queryset = refreshCurrentSoC(queryset)

    updated_queryset = sorted(updated_queryset, key=lambda instance: instance.current_charging_state)

    taken_free_chargers = []
    filtered_data = []
    for i in updated_queryset:
        if i.needs_relocation:
            free_chargers = Charger.objects.filter(is_available=True).exclude(id__in=taken_free_chargers)
            if len(free_chargers) > 0 and i.charger is None:
                relocate_to = free_chargers[0]
                taken_free_chargers.append(relocate_to.id)
            else:
                # No free chargers to relocate to
                if i.charger is None:
                    relocate_to = "No charger available. Please wait."
                else:
                    relocate_to = "Unplug and park at regular lot."

            i.relocate_to = relocate_to
            filtered_data.append(i)

    form = relocateCarForm()

    return render(request, 'maintenance.html', {'maintenance': filtered_data, 'form': form})


#@login_required
#@group_required('Maintenance Crew')
#TODO Write functions for Charging Approx new
def relocateCar(request):
    if request.method == 'POST':
        form = relocateCarForm(request.POST)
        if form.is_valid():
            cpid = form.cleaned_data['cpid']
            pool = form.cleaned_data['pool']
            charger = form.cleaned_data['charger']
            old_charger = cpid.charger

            if old_charger is not None:
                # implies that car was charged and is now being unplugged
                # Free old charger
                Charger.objects.filter(id=old_charger.id).update(is_available=True)

                soc_after_charging = chargingStateApprox(cpid.car.battery_capacity, cpid.charger.charger_type.kw, cpid.parked_from, cpid.charging_state) #cpid.parked_from, cpid.charging_state) #car_kwh, charger_kw, initial_datetime, initial_soc
                ChargingProcedure.objects.filter(id=cpid.id).update(charging_state=soc_after_charging)
                parked_until = None

            else:
                #car.battery_capacity, charger.charger_type.kw, datetime.now(), soc
                parked_until = chargingTimeApprox(cpid.car.battery_capacity, charger.charger_type.kw, datetime.now(tz), cpid.charging_state)
                Charger.objects.filter(id=charger.id).update(is_available=False)
            
            # capacity for regular parking lots in pools
            # update parked_from after relocation
            ChargingProcedure.objects.filter(id=cpid.id, needs_relocation=True).update(pool=pool, charger=charger, needs_relocation=False, parked_from=datetime.now(tz), parked_until=parked_until)

            # Change status of chargers (is_available)
            return redirect('/management/maintenance/')