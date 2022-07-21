from turtle import distance
from django.shortcuts import render

from django.http import HttpResponse

from car_checkout.forms import carCheckoutForm
from car_checkout.models import ChargingProcedure
from charger_management.models import Charger

from car_checkout.decisionEngine import makeParkingDecision, refreshCurrentSoC, chargingPlot

import os
import sys

#path = os.path.abspath('') + "/car_checkout/"
#sys.path.insert(1, path)

def index(request):
    
    if request.method == 'POST':
    
        checkout = carCheckoutForm(request.POST)

        if checkout.is_valid():
            pool = checkout.cleaned_data['pool']
            car = checkout.cleaned_data['car']
            charging_state = checkout.cleaned_data['charging_state']
            distance = checkout.cleaned_data['distance_traveled']
            
            decision, charger = makeParkingDecision(pool=pool, car=car, soc=charging_state, distance=distance)
            
            graph = None
            if charger is not None:
                graph = chargingPlot(car.battery_capacity, charger.charger_type.kw, initial_soc=charging_state)

            car_str = str(car).split("(")
            car = car_str[0]
            lplate = car_str[1][:-1]
            
            return render(request, 'directions.html', {'decision': decision, 'soc': charging_state, 'car': car, 'plate': lplate, 'graph': graph})
    else:
        checkout = carCheckoutForm()

    return render(request, 'checkout.html', {'form': checkout})