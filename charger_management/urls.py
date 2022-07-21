from django.urls import path

from . import views

urlpatterns = [
    path('', views.pools, name='index'),
    path('pools/', views.pools, name='pools'),
    path('chargers/', views.chargers, name='chargers'),
    path('fleet/', views.fleet, name='fleet'),
    path('poolAdded/', views.poolAdded, name='poolAdded'),
    path('removedPool/', views.removedPool, name='removedPool'),
    path('chargerAdded/', views.chargerAdded, name='chargerAdded'),
    path('removedCharger/', views.removedCharger, name='removedPool'),
    path('chargerTypeAdded/', views.chargerTypeAdded, name='chargerTypeAdded'),
    path('removeChargerType/', views.removedChargerType, name='removeChargerType'),
    path('uploadCarInfo/', views.uploadCarInfo, name='uploadCarInfo'),
    path('maintenance/', views.maintenanceView, name='maintenanceView'),
    path('maintenance/relocate/', views.relocateCar, name='relocate Car'),
    path('transactions/', views.transactionOverview, name='transactions'),
    path('manipulateTransaction/', views.manipulateTransactionView, name='manipulate transactions'),
    path('removeTransactions/', views.removeTransactions, name='remove transactions')
]