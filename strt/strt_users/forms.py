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
from django.utils.translation import ugettext_lazy as _
from wagtail.users.forms import UserEditForm, UserCreationForm


class AppUserEditForm(UserEditForm):

    fiscal_code = forms.CharField(required=True,
                              label=_('Codice Fiscale'))


class AppUserCreationForm(UserCreationForm):

    fiscal_code = forms.CharField(required=True,
                              label=_('Codice Fiscale'))