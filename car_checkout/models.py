from django.db import models

from charger_management.models import Pool, Charger, Car

class ChargingProcedure(models.Model):
	pool = models.ForeignKey(Pool, on_delete=models.CASCADE, default=1)
	charger = models.ForeignKey(Charger, on_delete=models.CASCADE, null=True)
	car = models.ForeignKey(Car, on_delete=models.CASCADE)
	parked_from = models.DateTimeField(auto_now=True)
	parked_until = models.DateTimeField(default=None, null=True)
	charging_state = models.IntegerField(3)
	needs_relocation = models.BooleanField(default=False)
	is_pickedup = models.BooleanField(default=False)

	def __str__(self):
		return f"{self.id}"