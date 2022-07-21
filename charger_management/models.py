from unicodedata import name
from django.db import models

class Pool(models.Model):
	name = models.CharField(max_length=128)
	longitude = models.DecimalField(decimal_places=6,max_digits=9)
	latitude = models.DecimalField(decimal_places=6,max_digits=9)

	def __str__(self):
		return self.name

class ChargerTypes(models.Model):
	name = models.CharField(max_length=128, default="Charger Type Name Undefined")
	kw = models.DecimalField(decimal_places=2, max_digits=6)

	def __str__(self):
		return self.name

class Charger(models.Model):
	name = models.CharField(max_length=128, default="Charger Name Undefined")
	pool = models.ForeignKey(Pool, on_delete=models.CASCADE)

	longitude = models.DecimalField(decimal_places=6,max_digits=9)
	latitude = models.DecimalField(decimal_places=6,max_digits=9)

	charger_type = models.ForeignKey(ChargerTypes, on_delete=models.CASCADE)

	is_available = models.BooleanField(default=True)

	def __str__(self):
		return f"Pool: {self.pool.name}, Charger: {self.name}"

class Car(models.Model):
	licence_plate = models.CharField(max_length=128)
	brand = models.CharField(max_length=128)
	model = models.CharField(max_length=128)
	battery_capacity = models.DecimalField(decimal_places=6,max_digits=9)

	def __str__(self):
		return f"{self.brand} {self.model} ({self.licence_plate})"
