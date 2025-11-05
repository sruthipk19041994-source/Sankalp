from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.LegalAwarenessCamp)
admin.site.register(models.LegalArticle)
admin.site.register(models.LegalQuestion)