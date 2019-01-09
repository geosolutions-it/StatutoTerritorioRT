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

import datetime
import graphene
import django_filters
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from graphene import InputObjectType, relay
from graphene_django import DjangoObjectType
from graphene_django.debug import DjangoDebug
from graphene_django.filter import DjangoFilterConnectionField

from strt_users.models import (
    Organization, OrganizationType
)

from serapide_core.helpers import (
    get_errors, update_create_instance, is_RUP
)
from serapide_core.modello.models import (
    Piano, Fase, FasePianoStorico
)
from serapide_core.modello.enums import (
    FASE, TIPOLOGIA_PIANO
)


# Graphene will automatically map the Category model's fields onto the CategoryNode.
# This is configured in the CategoryNode's Meta class (as you can see below)
class FaseNode(DjangoObjectType):

    class Meta:
        model = Fase
        filter_fields = ['codice', 'nome', 'descrizione', 'piani_operativi']
        interfaces = (relay.Node, )


class FasePianoStoricoType(DjangoObjectType):

    class Meta:
        model = FasePianoStorico
        interfaces = (relay.Node, )


class EnteTipoNode(DjangoObjectType):

    class Meta:
        model = OrganizationType
        interfaces = (relay.Node, )


class EnteNode(DjangoObjectType):

    tipologia_ente = graphene.Field(EnteTipoNode)
    role = graphene.List(graphene.String)

    def resolve_role(self, info, **args):
        roles = []
        if info.context.user and info.context.user.is_authenticated:
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


class PianoNode(DjangoObjectType):

    ente = graphene.Field(EnteNode)
    storico_fasi = graphene.List(FasePianoStoricoType)

    def resolve_storico_fasi(self, info, **args):
        # Warning this is not currently paginated
        _hist = FasePianoStorico.objects.filter(piano=self)
        return list(_hist)

    class Meta:
        model = Piano
        # Allow for some more advanced filtering here
        filter_fields = {
            'codice': ['exact', 'icontains', 'istartswith'],
            'ente': ['exact'],
            'descrizione': ['exact', 'icontains'],
            'tipologia': ['exact', 'icontains'],
            'fase': ['exact'],
            'fase__nome': ['exact'],
            'fase__codice': ['exact'],
        }
        interfaces = (relay.Node, )


class FaseCreateInput(InputObjectType):
    """
    Class created to accept input data
    from the interactive graphql console.
    """
    nome = graphene.String(source='nome', required=False)
    codice = graphene.String(required=True)
    descrizione = graphene.String(required=False)


class EnteCreateInput(InputObjectType):
    """
    Class created to accept input data
    from the interactive graphql console.
    """
    name = graphene.String(source='name', required=False)
    code = graphene.String(required=True)


class PianoCreateInput(InputObjectType):
    """
    Class created to accept input data
    from the interactive graphql console.
    """
    ente = graphene.InputField(EnteCreateInput, required=True)
    tipologia = graphene.String(required=True)

    codice = graphene.String(required=False)
    url = graphene.String(required=False)
    data_creazione = graphene.types.datetime.DateTime(required=False)
    descrizione = graphene.InputField(graphene.List(graphene.String), required=False)
    fase = graphene.InputField(FaseCreateInput, required=False)


class CreateFase(relay.ClientIDMutation):

    class Input:
        fase = graphene.Argument(FaseCreateInput)

    nuova_fase = graphene.Field(FaseNode)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        if info.context.user and info.context.user.is_authenticated and info.context.user.is_superuser:
            _data = input.get('fase')
            _fase = Fase()
            nuova_fase = update_create_instance(_fase, _data)
            return cls(nuova_fase=nuova_fase)
        else:
            return cls(nuova_fase=None, errors=[_("Forbidden")])


class UpdateFase(relay.ClientIDMutation):

    class Input:
        fase = graphene.Argument(FaseCreateInput)
        codice = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    fase_aggiornata = graphene.Field(FaseNode)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        if info.context.user and info.context.user.is_authenticated and info.context.user.is_superuser:
            try:
                _instance = Fase.objects.get(codice=input['codice'])
                if _instance:
                    _data = input.get('fase')
                    fase_aggiornata = update_create_instance(_instance, _data)
                    return cls(fase_aggiornata=fase_aggiornata)
            except ValidationError as e:
                return cls(fase_aggiornata=None, errors=get_errors(e))
        else:
            return cls(fase_aggiornata=None, errors=[_("Forbidden")])


class CreatePiano(relay.ClientIDMutation):

    class Input:
        piano_operativo = graphene.Argument(PianoCreateInput)

    nuovo_piano = graphene.Field(PianoNode)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        if is_RUP(info.context.user):
            _piano_data = input.get('piano_operativo')
            # Ente (M)
            _data = _piano_data.pop('ente')
            _ente = Organization.objects.get(usermembership__member=info.context.user, code=_data['code'])
            _piano_data['ente'] = _ente
            # Codice (M)
            if 'codice' in _piano_data:
                _data = _piano_data.pop('codice')
                _codice = _data
            else:
                _year = str(datetime.date.today().year)[2:]
                _month = datetime.date.today().month
                _piano_id = Piano.objects.filter(ente=_ente).count() + 1
                _codice = '%s%02d%02d%05d' % (_ente.code, int(_year), _month, _piano_id)
            _piano_data['codice'] = _codice
            # Fase (O)
            if 'fase' in _piano_data:
                _data = _piano_data.pop('fase')
                _fase = Fase.objects.get(codice=_data['codice'])
            else:
                _fase = Fase.objects.get(codice='FP255')
            _piano_data['fase'] = _fase
            # Descrizione (O)
            if 'descrizione' in _piano_data:
                _data = _piano_data.pop('descrizione')
                _piano_data['descrizione'] = _data[0]
            _piano = Piano()
            nuovo_piano = update_create_instance(_piano, _piano_data)
            return cls(nuovo_piano=nuovo_piano)
        else:
            return cls(nuovo_piano=None, errors=[_("Forbidden")])


class UpdatePiano(relay.ClientIDMutation):

    class Input:
        piano_operativo = graphene.Argument(PianoCreateInput)
        codice = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    piano_aggiornato = graphene.Field(PianoNode)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        if is_RUP(info.context.user):
            try:
                _piano = Piano.objects.get(codice=input['codice'])
                if _piano:
                    _piano_data = input.get('piano_operativo')
                    if 'codice' in _piano_data:
                        _piano_data.pop('codice')
                        # This cannot be changed
                    if 'data_creazione' in _piano_data:
                        _piano_data.pop('data_creazione')
                        # This cannot be changed
                    # Ente (M)
                    if 'ente' in _piano_data:
                        _piano_data.pop('ente')
                        # This cannot be changed
                    # Fase (O)
                    if 'fase' in _piano_data:
                        _piano_data.pop('fase')
                        # This cannot be changed
                    # Descrizione (O)
                    if 'descrizione' in _piano_data:
                        _data = _piano_data.pop('descrizione')
                        _piano.descrizione = _data[0]
                    piano_aggiornato = update_create_instance(_piano, _piano_data)
                    return cls(piano_aggiornato=piano_aggiornato)
            except ValidationError as e:
                return cls(piano_aggiornato=None, errors=get_errors(e))
        else:
            return cls(piano_aggiornato=None, errors=[_("Forbidden")])


"""
# EXAMPLE FILE UPLOAD
class UploadFile(graphene.ClientIDMutation):
     class Input:
         pass
         # nothing needed for uploading file

     # your return fields
     success = graphene.String()

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        # When using it in Django, context will be the request
        files = info.context.FILES
        # Or, if used in Flask, context will be the flask global request
        # files = context.files

        # do something with files

        return UploadFile(success=True)
"""

# ##############################################################################
# ENUMS
# ##############################################################################
class StrtEnumNode(graphene.ObjectType):
    value= graphene.String()
    label = graphene.String()


class FasePiano(StrtEnumNode):
    pass


class TipologiaPiano(StrtEnumNode):
    pass


# ##############################################################################
# FILTERS
# ##############################################################################
class EnteUserMembershipFilter(django_filters.FilterSet):
    # Do case-insensitive lookups on 'name'
    name = django_filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = Organization
        fields = ['name', 'code', 'description', 'usermembership', ]

    @property
    def qs(self):
        # The query context can be found in self.request.
        if self.request.user and self.request.user.is_authenticated:
            return super(EnteUserMembershipFilter, self).qs.filter(usermembership__member=self.request.user)
        else:
            return super(EnteUserMembershipFilter, self).qs.none()


class PianoUserMembershipFilter(django_filters.FilterSet):
    # Do case-insensitive lookups on 'name'
    codice = django_filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = Piano
        fields = '__all__'

    @property
    def qs(self):
        # The query context can be found in self.request.
        _enti = []
        _memberships = None
        if self.request.user and self.request.user.is_authenticated:
            _memberships = self.request.user.memberships
            if _memberships:
                for _m in _memberships.all():
                    if _m.type.code == settings.RESPONSABILE_ISIDE_CODE:
                        # RESPONSABILE_ISIDE_CODE cannot access to Piani at all
                        continue
                    # elif _m.type.code == settings.RUP_CODE:
                    #     # RUP_CODE can access to all Piani
                    #     _enti = Organization.objects.values_list('code', flat=True)
                    #     break
                    else:
                        _enti.append(_m.organization.code)
        return super(PianoUserMembershipFilter, self).qs.filter(ente__code__in=_enti)


# ##############################################################################
# QUERIES
# ##############################################################################
class Query(object):
    # Models
    # ente = relay.Node.Field(EnteNode)
    enti = DjangoFilterConnectionField(EnteNode,
                                       filterset_class=EnteUserMembershipFilter)

    # fase = relay.Node.Field(FaseNode)
    fasi = DjangoFilterConnectionField(FaseNode)

    # piano = relay.Node.Field(PianoNode)
    piani = DjangoFilterConnectionField(PianoNode,
                                        filterset_class=PianoUserMembershipFilter)

    # Enums
    fase_piano = graphene.List(FasePiano)
    tipologia_piano = graphene.List(TipologiaPiano)

    def resolve_fase_piano(self, info):
        l = []
        for f in FASE:
            l.append(FasePiano(f[0], f[1]))
        return l

    def resolve_tipologia_piano(self, info):
        l = []
        for t in TIPOLOGIA_PIANO:
            l.append(TipologiaPiano(t[0], t[1]))
        return l

    # Debug
    debug = graphene.Field(DjangoDebug, name='__debug')


# ##############################################################################
# MUTATIONS
# ##############################################################################
class Mutation(object):
    create_fase = CreateFase.Field()
    update_fase = UpdateFase.Field()
    create_piano = CreatePiano.Field()
    update_piano = UpdatePiano.Field()
