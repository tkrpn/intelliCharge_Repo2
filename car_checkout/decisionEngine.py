from email.policy import default
from car_checkout.models import ChargingProcedure
import numpy as np
from datetime import datetime, timedelta, timezone
import pytz
tz = pytz.timezone('Europe/Berlin')

from charger_management.models import Pool, Charger

TARGET_SOC=99
CRITICAL_CHARGING_CUTOFF = 50
CV_END=75

def makeParkingDecision(pool, car, soc, distance):
    if soc < CRITICAL_CHARGING_CUTOFF:
        chargers_in_pool = Charger.objects.filter(pool=pool)

        available_chargers = []
        for charger in chargers_in_pool:
            if charger.is_available:
                available_chargers.append(charger)
        
        if len(available_chargers) >= 2:
            charger = available_chargers[0]

            saveChargingToDB(pool=pool, charger=charger, car=car, soc=soc)
            return ({"head": f"Charger {charger.name}", "sub": "Car nearly empty"}, charger)

        elif len(available_chargers) < 2:
            if soc < 20:
                if len(available_chargers) > 0: 
                    charger = available_chargers[0]
                    saveChargingToDB(pool=pool, charger=charger, car=car, soc=soc)
                    return ({"head": f"Charger {charger.name}", "sub": "Car nearly empty"}, charger)
                else:
                    saveParkingToDB(pool=pool, car=car, soc=soc, needs_relocation=True)
                    return ({"head": "Regular Lot", "sub": "Maintenance Crew was notified (nearly empty car without charger)!"}, None)
            else:
                saveParkingToDB(pool=pool, car=car, soc=soc, needs_relocation=True)
                return ({"head": "Regular Lot", "sub": "Maintenance Crew was notified (medium full car without charger)!"}, None)
    else:
        saveParkingToDB(pool=pool, car=car, soc=soc)
        return ({"head": "Regular Lot", "sub":""}, None)

def refreshCurrentSoC(querySet):
    for i in querySet:
        if i.charger is not None:
            curr_soc = chargingStateApprox(i.car.battery_capacity, i.charger.charger_type.kw, i.parked_from, i.charging_state)
            if curr_soc > 70:
                i.needs_relocation = True
                ChargingProcedure.objects.filter(id=i.id).update(needs_relocation=True)
                if curr_soc > 100:
                    curr_soc = 100
        else:
            curr_soc = i.charging_state
        
        i.current_charging_state = curr_soc
    return querySet
        
def chargingTimeApprox(car_kwh, charger_kw, initial_datetime, soc, type="cv"):
    if type=="linear":
        return linearTimeApprox(initial_datetime, soc)
    elif type=="cv":
        return cvTimeApprox(car_kwh, charger_kw, initial_datetime, soc)
    else:
        return linearTimeApprox(initial_datetime, soc)

def linearTimeApprox(initial_datetime, initial_soc):
    charging_duration = initial_datetime + timedelta(minutes=(TARGET_SOC-initial_soc)*10)
    return charging_duration

def cvTimeApprox(car_kwh, charger_kw, initial_datetime, initial_soc):
    socCurve = approxCVCurve(car_kwh, charger_kw)
    mStart = np.where(socCurve > initial_soc)[0][0]
    mEnd = np.where(socCurve > TARGET_SOC)[0][0]
    charging_duration_minutes = mEnd - mStart
    charging_duration = initial_datetime + timedelta(minutes=int(charging_duration_minutes))
    #print(f"Car will be charged from {initial_soc}% to {target_soc}% in {charging_duration / 60} hours")
    return charging_duration

def chargingStateApprox(car_kwh, charger_kw, initial_datetime, initial_soc, type="cv"):
    charging_duration = datetime.now(tz) - initial_datetime
    if type=="linear":
        state = linearStateApprox(charging_duration, initial_soc)
        return state
    elif type=="cv":
        return cvStateApprox(car_kwh, charger_kw, charging_duration, initial_soc)
    else:
        return linearStateApprox(charging_duration, initial_soc)

def linearStateApprox(charging_duration, initial_soc):
    socEnd = initial_soc+int(charging_duration.total_seconds()/60/10)
    if socEnd > 100:
        socEnd = 100
    return socEnd

def cvStateApprox(car_kwh, charger_kw, charging_duration, initial_soc):
    socCurve = approxCVCurve(car_kwh, charger_kw)
    socEnd = 0
    try:
        relative_time_passed = charging_duration.total_seconds()/60 - np.where(socCurve > initial_soc)[0][0]
    except IndexError as e:
        # This needs to be fixed... Can happen when initial_soc is > 100 but after relocation from not having a charger to having a charger BUT WHYYYYYY? (no time for debug... tomorrow is presentation time ;) )
        print(e)
        print(f"initial_soc: {initial_soc}")
        print(f"socCurve: {socCurve}")
        relative_time_passed = -1 

    if relative_time_passed < 0:
        relative_time_passed = int(np.where(socCurve > initial_soc)[0][0])
    if relative_time_passed > len(socCurve):
        socEnd = 100
    else:
        socEnd = round(socCurve[round(relative_time_passed)])
    return socEnd

    #print(f"Car will be charged from {initial_soc}% to {socEnd}% when charged for {round(time_passed/60,2)} hours")

def approxCVCurve(car_kwh, charger_kw):
    onePercentOfMaxCapacity = float(car_kwh)*0.01
    minutesForOnePercent = (onePercentOfMaxCapacity/float(charger_kw))*60
    percentAfterOneMinute = 1/minutesForOnePercent

    y = [0] # SoC
    i = 1
    while y[-1] < 99 :
        last_soc = y[-1]
        if last_soc >= CV_END:
            curr_soc = last_soc + (percentAfterOneMinute * (1-((last_soc-CV_END)/(100-CV_END))))
            i += 1

            if curr_soc > 100:
                curr_soc = 100
            y.append(curr_soc)
        else:
            y.append(last_soc + percentAfterOneMinute)
    
    return np.array(y)

import plotly.graph_objects as go
def chargingPlot(car_kwh, charger_kw, initial_soc, current_charging_state=None):    
    socCurve = approxCVCurve(car_kwh, charger_kw)
    #plot = chargingPlot(socCurve=socCurve, initial_soc=initial_soc, charging_duration=charging_duration, socEnd=socEnd)
    #plt.plot(y)
    #plt.hlines(CRITICAL_CHARGING_CUTOFF, xmin=0, xmax=len(y), color="red")
    #plt.hlines(cv_end, xmin=0, xmax=len(y), color="red")
    x = np.arange(len(socCurve))
    y = socCurve
    trace1 = go.Scatter(x=x, y=y, marker={'color': 'blue', 'symbol': 104, 'size': 10},
                        mode="lines",  name='1st Trace')

    layout= go.Layout(title="Charging Curve", yaxis={'title':'State of Charge', 'linecolor':'lightblue'}, xaxis={'title':'Charging Duration (Minutes)', 'linecolor':'lightblue'}, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    figure= go.Figure(data=trace1, layout=layout)

    figure.add_hline(y=initial_soc, line_width=1, line_dash="dash", line_color="blue")
    #figure.add_annotation(go.layout.Annotation(x=100, y = initial_soc, text = f"Initial SoC ({initial_soc}%)", align='center', showarrow=False, yanchor='bottom', textangle=0))
    if current_charging_state is not None:
        figure.add_vline(x=current_charging_state, line_width=1, line_dash="dash", line_color="blue")
        figure.add_annotation(go.layout.Annotation(x = current_charging_state+3, y = 50, text = "Current State of Charge", align='center', showarrow=False, yanchor='bottom', textangle=-90))

    return figure.to_html()

def saveChargingToDB(pool, charger, car, soc):
    parked_until = chargingTimeApprox(car.battery_capacity, charger.charger_type.kw, datetime.now(tz), soc)
    
    p = ChargingProcedure(pool=pool, charger=charger, car=car, charging_state=soc, parked_until=parked_until)
    p.save()
    
    Charger.objects.filter(id=charger.id).update(is_available=False)

def saveParkingToDB(pool, car, soc, needs_relocation=False): 

    p = ChargingProcedure(pool=pool, charger=None, car=car, charging_state=soc, parked_until=None, needs_relocation=needs_relocation)
    p.save()