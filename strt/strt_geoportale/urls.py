from django.urls import path
from django.conf.urls import include, url
from django.views.generic import RedirectView
from .views import geportale_home

urlpatterns = [
    path('', geportale_home, name='geportale_home'),
]