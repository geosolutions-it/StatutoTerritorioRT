# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright 2019, GeoSolutions SAS.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.
#
#########################################################################

import jwt

from django.conf import settings

from django import forms
from django.forms import ValidationError
from django.views.generic.base import TemplateView
from django.contrib.auth import authenticate, login
from django.utils.translation import ugettext_lazy as _
from django.utils.text import slugify
# from django.contrib.auth import logout

from strt_tests.forms import UserAuthenticationForm
from rules.contrib.views import permission_required

from django_currentuser.middleware import (
    get_current_authenticated_user
)
from django.shortcuts import (
    render, redirect
)
from strt_users.models import Organization, UserMembership
from .glossario import glossario


def privateAreaView(request):
    current_user = get_current_authenticated_user()
    if current_user:
        if 'role' in request.session and request.session['role']:
            current_role = current_user.memberships.filter(pk=request.session['role']).first()
            if current_role:
                if current_role.type.code == settings.RESPONSABILE_ISIDE_CODE:
                    return redirect('users_list')
        if current_user.has_perm('strt_users.can_access_serapide'):
            return redirect('serapide')
        else:
            return redirect('/')
        #    logout(request)
        #    return redirect('user_registration')
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
                # TODO: MembershipType Check
                _role = form_cleaned_data.pop('membership_type')
                if not _role:
                    ve = forms.ValidationError(
                        _("Ruolo non valido.")
                    )
                    form.add_error(None, ve)
                else:
                    encoded_jwt = jwt.encode(
                        payload=form_cleaned_data,
                        key=settings.SECRET_KEY,
                        algorithm='HS256'
                    )

                    try:
                        user = authenticate(encoded_jwt)
                        _organization = orgs.pop()['organization'].strip()
                        organization = None
                        try:
                            # Organizations must be already registered
                            organization = Organization._default_manager.get(
                                code=_organization
                            )
                        except Organization.DoesNotExist:
                            ve = forms.ValidationError(
                                _("L'ente {} non risulta censito.".format(_organization))
                            )
                            form.add_error(None, ve)

                        if user and organization:
                            try:
                                membership = UserMembership._default_manager.get(code=_role)

                                login(request, user)
                                request.session['role'] = membership.pk
                                request.session['organization'] = organization.code
                                request.session['attore'] = membership.organization.type.name
                                if membership.type.code == settings.RESPONSABILE_ISIDE_CODE:
                                    return redirect('users_list')
                                return redirect('serapide')
                            except UserMembership.DoesNotExist:
                                ve = forms.ValidationError(
                                    _("Utente {} non valido.".format(user))
                                )
                                form.add_error(None, ve)
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
    template_name = "strt_portal/glossario/glossario.html"
    unique_char = []
    index = []

    for termine in glossario:
        denominazione = termine['denominazione']
        termine['slug'] = denominazione
        first_char = denominazione[0]
        if not first_char in unique_char:
            unique_char.append(first_char)
            index.append({
                'lettera': first_char,
                'slug': termine['slug']
            })

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['indice'] = GlossaryView.index
        context['glossario'] = glossario
        return context