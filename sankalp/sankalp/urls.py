from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('education/', include('education.urls')),
    path('medical/', include('medical.urls')),
    path('legal/', include('legal.urls')),
    path('women-support/', include('women_support.urls')),
]
