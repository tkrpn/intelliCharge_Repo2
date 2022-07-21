from django.contrib import admin

# Register your models here.
from .models import Users
from .models import maintenanceCrew
from .models import FleetAdmin

admin.site.register(Users)
admin.site.register(FleetAdmin)
admin.site.register(maintenanceCrew)
