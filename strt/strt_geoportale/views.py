from django.shortcuts import render

def geportale_home(request):
    return render(request, "geoportale/geoportale.html")
