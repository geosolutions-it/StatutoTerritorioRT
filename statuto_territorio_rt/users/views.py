#########################################################################
#
# Copyright 2018, GeoSolutions Sas.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.
#
#########################################################################


from django.shortcuts import render, HttpResponseRedirect
from django.contrib.auth import authenticate, login
from .forms import AppUserCreationForm
from .models import AppUser


def registrazionView(request):
    if request.method == "POST":
        form = AppUserCreationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password1"]
            fiscal_code = form.cleaned_data["fiscal_code"]
            AppUser.objects.create_user(
                username=username,
                password=password,
                fiscal_code=fiscal_code,
                email=email
            )
            user = authenticate(username=username, password=password)
            login(request, user)
            return HttpResponseRedirect("/")
    else:
        form = AppUserCreationForm()
    context = {"form": form}
    return render(request, 'users/registration.html', context)