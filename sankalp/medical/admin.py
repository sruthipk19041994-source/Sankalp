from django.contrib import admin

from . import models
# Register your models here.

admin.site.register(models.MedicalCampRequest)
admin.site.register(models.Hospital)