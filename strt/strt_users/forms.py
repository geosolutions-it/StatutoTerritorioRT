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

from django import forms
from django.contrib.auth.forms import UsernameField
from .models import Utente


# class RuoloForm(forms.ModelForm):
#
#     class Meta:
#         model = Ruolo
#         fields = '__all__'
#         exclude = ('id', 'name', 'permissions',)


class UtenteForm(forms.ModelForm):
    """
    A form that creates a user, with no privileges, from the given fiscal code
    """

    class Meta:
        model = Utente
        fields = (
            'first_name', 'last_name', 'fiscal_code', 'email'
        )
        field_classes = {'fiscal_code': UsernameField}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self._meta.model.USERNAME_FIELD in self.fields:
            self.fields[self._meta.model.USERNAME_FIELD].widget.attrs.update({'autofocus': True})

    def _post_clean(self):
        super()._post_clean()

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        return user
