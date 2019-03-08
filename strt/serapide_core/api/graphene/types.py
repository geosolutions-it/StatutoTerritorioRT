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
import graphene

from urllib.parse import urljoin

from django.conf import settings

from pinax.messages.models import Thread, Message

from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from strt_users.models import (
    AppUser,
    Organization,
    OrganizationType,
    UserMembership,
)

from serapide_core.modello.models import (
    Fase,
    Piano,
    Azione,
    Risorsa,
    Contatto,
    ProceduraVAS,
    ConsultazioneVAS,
    PianoAuthTokens,
    FasePianoStorico,
    RisorsePiano,
    RisorseVas,
)

from serapide_core.modello.enums import (
    STATO_AZIONE,
    TIPOLOGIA_VAS,
)

logger = logging.getLogger(__name__)


# Graphene will automatically map the Category model's fields onto the CategoryNode.
# This is configured in the CategoryNode's Meta class (as you can see below)
class RoleNode(DjangoObjectType):

    type = graphene.String()

    def resolve_type(self, info, **args):
        return self.type.code

    class Meta:
        model = UserMembership
        filter_fields = '__all__'
        interfaces = (relay.Node, )


class FaseNode(DjangoObjectType):

    class Meta:
        model = Fase
        filter_fields = ['codice', 'nome', 'descrizione', 'piani_operativi']
        interfaces = (relay.Node, )


class FasePianoStoricoType(DjangoObjectType):

    class Meta:
        model = FasePianoStorico
        interfaces = (relay.Node, )


class UserThreadType(DjangoObjectType):

    absolute_url = graphene.String()

    def resolve_absolute_url(self, info, **args):
        return self.get_absolute_url()

    class Meta:
        model = Thread
        filter_fields = ['subject', 'users', ]
        interfaces = (relay.Node, )


class UserMessageType(DjangoObjectType):

    thread = graphene.Field(UserThreadType)

    class Meta:
        model = Message
        interfaces = (relay.Node, )


class AzioneNode(DjangoObjectType):

    class Meta:
        model = Azione
        filter_fields = ['uuid',
                         'tipologia',
                         'attore',
                         'stato',
                         'data']
        interfaces = (relay.Node, )


class RisorsaNode(DjangoObjectType):

    download_url = graphene.String()

    def resolve_download_url(self, info, **args):
        _url = str(self.file)
        return urljoin(settings.SITE_URL, _url[_url.index('media/'):])

    class Meta:
        model = Risorsa
        filter_fields = ['uuid',
                         'nome',
                         'tipo',
                         'dimensione',
                         'descrizione',
                         'data_creazione',
                         'last_update',
                         'fase__codice',
                         'piano__codice']
        interfaces = (relay.Node, )


class RisorsePianoType(DjangoObjectType):

    risorsa = DjangoFilterConnectionField(RisorsaNode)

    class Meta:
        model = RisorsePiano
        filter_fields = ['risorsa__fase__codice',
                         'piano__codice']
        interfaces = (relay.Node, )


class RisorseVASType(DjangoObjectType):

    risorsa = DjangoFilterConnectionField(RisorsaNode)

    class Meta:
        model = RisorseVas
        filter_fields = ['risorsa__fase__codice']
        interfaces = (relay.Node, )


class EnteTipoNode(DjangoObjectType):

    class Meta:
        model = OrganizationType
        interfaces = (relay.Node, )


class AppUserNode(DjangoObjectType):

    role = graphene.Field(RoleNode)
    attore = graphene.String()
    alerts_count = graphene.String()
    unread_threads_count = graphene.String()
    unread_messages = graphene.List(UserMessageType)
    contact_type = graphene.String()

    def resolve_role(self, info, **args):
        _org = info.context.session.get('organization', None)
        token = info.context.session.get('token', None)
        if token:
            return self.memberships.all().first()
        else:
            return self.memberships.get(organization__code=_org)

    def resolve_alerts_count(self, info, **args):
        _alerts_count = 0

        _pianos = []
        _enti = []
        _memberships = None
        _memberships = self.memberships
        if _memberships:
            for _m in _memberships.all():
                if _m.type.code == settings.RESPONSABILE_ISIDE_CODE:
                    # RESPONSABILE_ISIDE_CODE cannot access to Piani at all
                    continue
                else:
                    _enti.append(_m.organization.code)

        token = info.context.session.get('token', None)
        if token:
            _allowed_pianos = [_pt.piano.codice for _pt in PianoAuthTokens.objects.filter(token__key=token)]
            _pianos = [_p for _p in Piano.objects.filter(codice__in=_allowed_pianos)]
        else:
            _pianos = [_p for _p in Piano.objects.filter(ente__code__in=_enti)]

        _alert_states = [STATO_AZIONE.attesa, STATO_AZIONE.necessaria]
        for _p in _pianos:
            _alerts_count += _p.azioni.filter(stato__in=_alert_states).count()

        return _alerts_count

    def resolve_unread_threads_count(self, info, **args):
        return Thread.unread(self).count()

    def resolve_unread_messages(self, info, **args):
        unread_messages = []
        for _t in Thread.unread(self).order_by('subject'):
            unread_messages.append(_t.latest_message)
        return unread_messages

    def resolve_contact_type(self, info, **args):
        return Contatto.tipologia_contatto(self)

    def resolve_attore(self, info, **args):
        organization = info.context.session.get('organization', None)
        token = info.context.session.get('token', None)
        return Contatto.attore(self, organization, token)

    class Meta:
        model = AppUser
        # Allow for some more advanced filtering here
        filter_fields = {
            'fiscal_code': ['exact'],
            'first_name': ['exact', 'icontains', 'istartswith'],
            'last_name': ['exact', 'icontains', 'istartswith'],
            'email': ['exact'],
        }
        exclude_fields = ('password', 'is_staff', 'is_active', 'is_superuser', 'last_login')
        interfaces = (relay.Node, )


class EnteNode(DjangoObjectType):

    tipologia_ente = graphene.Field(EnteTipoNode)
    role = graphene.List(graphene.String)

    def resolve_role(self, info, **args):
        roles = []
        if rules.test_rule('strt_core.api.can_access_private_area', info.context.user):
            _memberships = info.context.user.memberships
            if _memberships:
                for _m in _memberships:
                    if _m.organization.code == self.code:
                        roles.append(_m.type.code)
        return roles

    class Meta:
        model = Organization
        # Allow for some more advanced filtering here
        filter_fields = {
            'code': ['exact'],
            'name': ['exact', 'icontains', 'istartswith'],
            'description': ['exact', 'icontains'],
        }
        interfaces = (relay.Node, )


class ProceduraVASNode(DjangoObjectType):

    ente = graphene.Field(EnteNode)
    risorsa = DjangoFilterConnectionField(RisorseVASType)
    documento_preliminare_verifica = graphene.Field(RisorsaNode)
    relazione_motivata_vas_semplificata = graphene.Field(RisorsaNode)

    def resolve_documento_preliminare_verifica(self, info, **args):
        _risorsa = None
        if self.tipologia == TIPOLOGIA_VAS.verifica:
            _risorsa = self.risorse.filter(tipo='vas_verifica').first()
        return _risorsa

    def resolve_relazione_motivata_vas_semplificata(self, info, **args):
        _risorsa = None
        if self.tipologia == TIPOLOGIA_VAS.semplificata:
            _risorsa = self.risorse.filter(tipo='vas_semplificata').first()
        return _risorsa

    class Meta:
        model = ProceduraVAS
        # Allow for some more advanced filtering here
        filter_fields = {
            'ente': ['exact'],
            'piano__codice': ['exact'],
            'note': ['exact', 'icontains'],
            'tipologia': ['exact', 'icontains'],
        }
        interfaces = (relay.Node, )


class ContattoNode(DjangoObjectType):

    ente = graphene.Field(EnteNode)

    class Meta:
        model = Contatto
        # Allow for some more advanced filtering here
        filter_fields = {
            'nome': ['exact', 'icontains'],
            'email': ['exact'],
            'tipologia': ['exact'],
            'ente': ['exact'],
            'piano__codice': ['exact'],
        }
        interfaces = (relay.Node, )


class ConsultazioneVASNode(DjangoObjectType):

    user = graphene.Field(AppUserNode)
    contatto = graphene.Field(ContattoNode)
    procedura_vas = graphene.Field(ProceduraVASNode)

    def resolve_contatto(self, info, **args):
        _contatto = None
        if self.user:
            _contatto = Contatto.objects.filter(user=self.user).first()
        return _contatto

    class Meta:
        model = ConsultazioneVAS
        # Allow for some more advanced filtering here
        filter_fields = {
            'procedura_vas__piano__codice': ['exact'],
        }
        interfaces = (relay.Node, )


class PianoNode(DjangoObjectType):

    user = graphene.Field(AppUserNode)
    ente = graphene.Field(EnteNode)
    storico_fasi = graphene.List(FasePianoStoricoType)
    risorsa = DjangoFilterConnectionField(RisorsePianoType)
    procedura_vas = graphene.Field(ProceduraVASNode)
    soggetto_proponente = graphene.Field(ContattoNode)
    alerts_count = graphene.String()

    def resolve_alerts_count(self, info, **args):
        _alert_states = [STATO_AZIONE.attesa, STATO_AZIONE.necessaria]
        return self.azioni.filter(stato__in=_alert_states).count()

    def resolve_storico_fasi(self, info, **args):
        # Warning this is not currently paginated
        _hist = FasePianoStorico.objects.filter(piano=self)
        return list(_hist)

    def resolve_procedura_vas(self, info, **args):
        _vas = None
        try:
            _vas = ProceduraVAS.objects.get(piano=self)
        except BaseException:
            pass
        return _vas

    class Meta:
        model = Piano
        # Allow for some more advanced filtering here
        filter_fields = {
            'codice': ['exact', 'icontains', 'istartswith'],
            'ente': ['exact'],
            'descrizione': ['exact', 'icontains'],
            'tipologia': ['exact', 'icontains'],
        }
        interfaces = (relay.Node, )
