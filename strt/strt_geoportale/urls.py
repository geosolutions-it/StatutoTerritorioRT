from django.urls import path
from .views import geportale_home

urlpatterns = [
    path('', geportale_home, name='membership_type_data'),
]