from django.contrib import admin

# Register your models here.

from . import models

admin.site.register(models.WomenSupportCampaign)
admin.site.register(models.WomenSupportArticle)
admin.site.register(models.WomenSupportQuestion)
