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
from .models import AppUser, MembershipType, Organization
from django.views.generic.base import TemplateView


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
    return render(request, 'registration/registration.html', context)


class UsersManagementView(TemplateView):

    template_name = "strt_users/users_management.html"

def usersManagementView(request):
    users = AppUser.objects.order_by('-name')
    membership_types = MembershipType.objects.order_by('-name')
    organizations = Organization.objects.order_by('-name')
    context = {
        "users_list": users,
        "membership_type_list": membership_types,
        "organizations_list": organizations,
    }
    return render(request, "strt_users/users_management.html", context)