from django.urls import path
from django.conf.urls import include, url
from django.views.generic import RedirectView
from .views import geportale_home

urlpatterns = [
    path('', geportale_home, name='geportale_home'),
    url(r'(static\/extjs\/search\/category\/MAP\/)', RedirectView.as_view(url='/static/MAPS.json', permanent=False)),
    url(r'(static\/extjs\/search\/category\/CONTEXT\/)', RedirectView.as_view(url='/static/EMPTY_RESOURCES.json', permanent=False)),
    url(r'(static\/extjs\/search\/category\/GEOSTORY\/)', RedirectView.as_view(url='/static/EMPTY_RESOURCES.json', permanent=False)),
    url(r'(static\/extjs\/search\/category\/DASHBOARD\/)', RedirectView.as_view(url='/static/EMPTY_RESOURCES.json', permanent=False)),
]