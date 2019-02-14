# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright 2018, GeoSolutions Sas.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.
#
#########################################################################

from django.views.generic.base import TemplateView
from django_currentuser.middleware import (
    get_current_authenticated_user
)
from django.shortcuts import (
    render, redirect
)
from django.contrib.auth import authenticate, login
from django.forms import ValidationError
from django.conf import settings
from strt_tests.forms import UserAuthenticationForm
from rules.contrib.views import permission_required
import jwt


def privateAreaView(request):
    current_user = get_current_authenticated_user()
    if current_user:
        if current_user.has_perm('strt_users.can_access_serapide'):
            return redirect('serapide')
        elif current_user.has_perm('strt_users.can_manage_users'):
            return redirect('users_list')
        else:
            return redirect('')
    else:
        # TODO: redirect to RT SSO service endpoint
        if request.method == "POST":
            form = UserAuthenticationForm(request.POST)
            if form.is_valid():
                form_cleaned_data = form.cleaned_data
                orgs = [
                    {
                        'organization': org
                    }
                    for org
                    in form_cleaned_data['hidden_orgs'].split('-')
                    if org
                ]
                form_cleaned_data.pop('hidden_orgs')
                form_cleaned_data['organizations'] = orgs
                encoded_jwt = jwt.encode(
                    payload=form_cleaned_data,
                    key=settings.SECRET_KEY,
                    algorithm='HS256'
                )
                try:
                    user = authenticate(encoded_jwt)
                    if user:
                        login(request, user)
                        return redirect('serapide')
                except ValidationError as ve:
                    form.add_error(None, ve)
        else:
            form = UserAuthenticationForm()
    context = {'form': form}
    return render(request, 'strt_tests/user_authentication_test.html', context)


@permission_required('strt_users.can_access_serapide')
def serapideView(request):
    return render(request, 'index.html')  # serapide-client


class GeoportalView(TemplateView):

    template_name = "strt_portal/geoportal/geoportal.html"


class OpendataView(TemplateView):

    template_name = "strt_portal/opendata/opendata.html"


class GlossaryView(TemplateView):

    template_name = "strt_portal/glossary/glossary.html"
