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

from django import forms
from django.core.validators import RegexValidator
from strt_users.models import Organization


class UserAuthenticationForm(forms.Form):

    first_name = forms.CharField(
        label='Nome',
        required=False,
    )
    last_name = forms.CharField(
        label='Cognome',
        required=False,
    )
    fiscal_code = forms.CharField(
        label='Codice Fiscale',
        required=False,
        validators=[
            RegexValidator(
                regex='^(?i)(?:(?:[B-DF-HJ-NP-TV-Z]|[AEIOU])[AEIOU][AEIOUX]|'
                      '[B-DF-HJ-NP-TV-Z]{2}[A-Z]){2}[\dLMNP-V]{2}(?:[A-EHLMPR-T]'
                      '(?:[04LQ][1-9MNP-V]|[1256LMRS][\dLMNP-V])|[DHPS][37PT][0L]|'
                      '[ACELMRT][37PT][01LM])(?:[A-MZ][1-9MNP-V][\dLMNP-V]{2}|[A-M][0L]'
                      '(?:[1-9MNP-V][\dLMNP-V]|[0L][1-9MNP-V]))[A-Z]$',
                message='Codice fiscale errato.',
            ),
        ]
    )
    membership_type = forms.CharField(
        label='Ruolo',
        required=False,
    )
    hidden_orgs = forms.CharField(
        widget=forms.HiddenInput(),
        required=False
    )
    organizations = forms.ModelChoiceField(
        label='Enti',
        queryset=Organization.objects.all(),
        required=False
    )
