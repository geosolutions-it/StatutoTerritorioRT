# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright 2019, GeoSolutions Sas.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.
#
#########################################################################

import rules
import logging
import django_filters
from django_filters import (CharFilter)
from django.db.models import Q
from django.conf import settings

from strt_users.models import (
    Utente,
    Ente,
)

from serapide_core.helpers import is_RUP

from serapide_core.modello.models import (
    Piano,
    SoggettoOperante,
    ProceduraVAS,
    ProceduraAvvio,
    ProceduraAdozione,
    ProceduraApprovazione,
    ProceduraPubblicazione,
    PianoAuthTokens,
)


logger = logging.getLogger(__name__)


class UserMembershipFilter(django_filters.FilterSet):

    # Do case-insensitive lookups on 'name'
    name = django_filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = Utente
        exclude = ['password', 'is_staff', 'is_active', 'is_superuser', 'last_login']

    @property
    def qs(self):
        # The query context can be found in self.request.
        if rules.test_rule('strt_core.api.can_access_private_area', self.request.user):
            return super(UserMembershipFilter, self).qs.filter(id=self.request.user.id).distinct()
            # if is_RUP(self.request.user):
            #  return super(UserMembershipFilter, self).qs.filter(usermembership__member=self.request.user).distinct()
            #  return super(UserMembershipFilter, self).qs.all()
            # else:
            #  return super(UserMembershipFilter, self).qs.filter(id=self.request.user.id).distinct()
        else:
            return super(UserMembershipFilter, self).qs.none()


class EnteUserMembershipFilter(django_filters.FilterSet):

    # Do case-insensitive lookups on 'name'
    name = django_filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = Ente
#        fields = ['nome', 'id', 'descrizione', 'qualifica', ]
        fields = ['nome', 'id', 'descrizione']

    @property
    def qs(self):
        # The query context can be found in self.request.
        if rules.test_rule('strt_core.api.can_access_private_area', self.request.user):
            if is_RUP(self.request.user):
                return super(EnteUserMembershipFilter, self).qs.all()
            else:
                return super(EnteUserMembershipFilter, self).qs.filter(usermembership__member=self.request.user)
        else:
            return super(EnteUserMembershipFilter, self).qs.none()


class CharInFilter(django_filters.BaseInFilter, django_filters.CharFilter):
    pass


# class EnteContattoMembershipFilter(django_filters.FilterSet):
#
#     # Do case-insensitive lookups on 'name'
#     name = django_filters.CharFilter(lookup_expr='iexact')
#     tipologiain = CharInFilter(field_name='tipologia', lookup_expr='in')
#
#     class Meta:
#         model = Referente
#         fields = ['name', 'email', 'ente', 'tipologia', 'tipologiain']
#
#     @property
#     def qs(self):
#         # The query context can be found in self.request.
#         if rules.test_rule('strt_core.api.can_access_private_area', self.request.user):
#             if is_RUP(self.request.user):
#                 return super(EnteContattoMembershipFilter, self).qs.all()
#             else:
#                 return super(EnteContattoMembershipFilter, self).qs.filter(
#                     ente__ruolo__utente=self.request.user)
#         else:
#             return super(EnteContattoMembershipFilter, self).qs.none()


class SoggettoOperanteFilter(django_filters.FilterSet):

    qualifica = CharFilter(method='qualifica_filter')

    class Meta:
        model = SoggettoOperante
        fields = ['piano', 'qualifica']

    def qualifica_filter(self, queryset, piano, qualifica):
        return queryset.filter(piano=piano, ruolo__qualifica=qualifica) | \
               queryset.filter(piano=piano, ufficio__qualifica=qualifica)


class PianoUserMembershipFilter(django_filters.FilterSet):

    # Do case-insensitive lookups on 'name'
    codice = django_filters.CharFilter(lookup_expr='iexact')
    fase__codice = django_filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = Piano
        fields = '__all__'

    @property
    def qs(self):
        # The query context can be found in self.request.
        _enti = []
        _memberships = None
        if rules.test_rule('strt_core.api.can_access_private_area', self.request.user):
            _memberships = self.request.user.memberships
            if _memberships:
                _is_iside = self.request.user.memberships.filter(type__code=settings.RESPONSABILE_ISIDE_CODE)
                _is_regione = self.request.user.memberships.filter(type__organization_type__code='R')
                if _is_regione and not _is_iside:
                    for _o in Ente.objects.filter(type__code='C'):
                        _enti.append(_o.code)
                else:
                    for _m in _memberships.all():
                        if _m.type.code == settings.RESPONSABILE_ISIDE_CODE:
                            # RESPONSABILE_ISIDE_CODE cannot access to Piani at all
                            continue
                        else:
                            _enti.append(_m.organization.code)

        token = self.request.session.get('token', None)
        if token:
            _allowed_pianos = [_pt.piano.codice for _pt in PianoAuthTokens.objects.filter(token__key=token)]
            return super(PianoUserMembershipFilter, self).qs.filter(
                codice__in=_allowed_pianos).order_by('-last_update', '-codice')
        else:
            return super(PianoUserMembershipFilter, self).qs.filter(
                ente__code__in=_enti).order_by('-last_update', '-codice')


class ProceduraMembershipFilterBase(django_filters.FilterSet):

    piano__codice = django_filters.CharFilter(lookup_expr='iexact')

    @property
    def qs(self):
        # The query context can be found in self.request.
        _enti = []
        _memberships = None
        if rules.test_rule('strt_core.api.can_access_private_area', self.request.user):
            _memberships = self.request.user.memberships
            if _memberships:
                _is_iside = self.request.user.memberships.filter(type__code=settings.RESPONSABILE_ISIDE_CODE)
                _is_regione = self.request.user.memberships.filter(type__organization_type__code='R')
                if _is_regione and not _is_iside:
                    for _o in Ente.objects.filter(type__code='C'):
                        _enti.append(_o.code)
                else:
                    for _m in _memberships.all():
                        if _m.type.code == settings.RESPONSABILE_ISIDE_CODE:
                            # RESPONSABILE_ISIDE_CODE cannot access to Piani at all
                            continue
                        else:
                            _enti.append(_m.organization.code)
                # _enti = [_m.organization.code for _m in _memberships.all()]

        token = self.request.session.get('token', None)
        if token:
            _allowed_pianos = [_pt.piano.codice for _pt in PianoAuthTokens.objects.filter(token__key=token)]
            _pianos = [_p for _p in Piano.objects.filter(codice__in=_allowed_pianos)]
            for _p in _pianos:
                _enti.append(_p.ente.code)

        return super(ProceduraMembershipFilterBase, self).qs.filter(ente__code__in=_enti)


class ProceduraVASMembershipFilter(ProceduraMembershipFilterBase):

    class Meta:
        model = ProceduraVAS
        fields = '__all__'


class ProceduraAvvioMembershipFilter(ProceduraMembershipFilterBase):

    class Meta:
        model = ProceduraAvvio
        fields = '__all__'


class ProceduraAdozioneMembershipFilter(ProceduraMembershipFilterBase):

    class Meta:
        model = ProceduraAdozione
        fields = '__all__'


class ProceduraApprovazioneMembershipFilter(ProceduraMembershipFilterBase):

    class Meta:
        model = ProceduraApprovazione
        fields = '__all__'


class ProceduraPubblicazioneMembershipFilter(ProceduraMembershipFilterBase):

    class Meta:
        model = ProceduraPubblicazione
        fields = '__all__'
