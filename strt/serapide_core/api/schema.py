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

import graphene
from django.core.exceptions import ValidationError
from graphene import InputObjectType, relay
from graphene_django import DjangoObjectType
from graphene_django.debug import DjangoDebug
from graphene_django.filter import DjangoFilterConnectionField

from strt_users.models import (
    Organization, OrganizationType
)

from serapide_core.helpers import get_errors, update_create_instance
from serapide_core.modello.models import (
    Piano, Fase, FasePianoStorico
)
from serapide_core.modello.enums import (
    FASE, TIPOLOGIA_PIANO
)


"""
# Custom Filter Set example
class AnimalNode(DjangoObjectType):
    class Meta:
        # Assume you have an Animal model defined with the following fields
        model = Animal
        filter_fields = ['name', 'genus', 'is_domesticated']
        interfaces = (relay.Node, )


class AnimalFilter(django_filters.FilterSet):
    # Do case-insensitive lookups on 'name'
    name = django_filters.CharFilter(lookup_expr=['iexact'])

    class Meta:
        model = Animal
        fields = ['name', 'genus', 'is_domesticated']

    @property
    def qs(self):
        # The query context can be found in self.request.
        # The context argument is passed on as the request argument in a django_filters.FilterSet instance.
        # You can use this to customize your filters to be context-dependent.
        # We could modify the AnimalFilter above to pre-filter animals owned by
        # the authenticated user (set in context.user)
        return super(AnimalFilter, self).qs.filter(owner=self.request.user)


class Query(ObjectType):
    animal = relay.Node.Field(AnimalNode)
    # We specify our custom AnimalFilter using the filterset_class param
    all_animals = DjangoFilterConnectionField(AnimalNode,
                                              filterset_class=AnimalFilter)
"""


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

    nome = graphene.String(source='nome', required=True)
    codice = graphene.String(required=True)
    descrizione = graphene.String(required=False)


class PianoCreateInput(InputObjectType):
    """
    Class created to accept input data
    from the interactive graphql console.
    """

    codice = graphene.String(required=True)
    tipologia = graphene.String(required=False)
    url = graphene.String(required=False)
    data_creazione = graphene.types.datetime.DateTime(required=False)
    descrizione = graphene.InputField(graphene.List(graphene.String), required=False)
    fase = graphene.InputField(FaseCreateInput, required=True)


class CreateFase(relay.ClientIDMutation):

    class Input:
        fase = graphene.Argument(FaseCreateInput)

    nuova_fase = graphene.Field(FaseNode)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        _data = input.get('fase')
        _fase = Fase()
        nuova_fase = update_create_instance(_fase, _data)
        return cls(nuova_fase=nuova_fase)


class UpdateFase(relay.ClientIDMutation):

    class Input:
        fase = graphene.Argument(FaseCreateInput)
        codice = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    fase_aggiornata = graphene.Field(FaseNode)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        try:
            _instance = Fase.objects.get(codice=input['codice'])
            if _instance:
                _data = input.get('fase')
                fase_aggiornata = update_create_instance(_instance, _data)
                return cls(fase_aggiornata=fase_aggiornata)
        except ValidationError as e:
            return cls(fase_aggiornata=None, errors=get_errors(e))


class CreatePiano(relay.ClientIDMutation):

    class Input:
        piano_operativo = graphene.Argument(PianoCreateInput)

    nuovo_piano = graphene.Field(PianoNode)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        _piano_data = input.get('piano_operativo')
        _data = _piano_data.pop('fase')
        _fase = Fase.objects.get(codice=_data['codice'])
        _piano_data['fase'] = _fase
        _piano = Piano()
        nuovo_piano = update_create_instance(_piano, _piano_data)

        return cls(nuovo_piano=nuovo_piano)


class UpdatePiano(relay.ClientIDMutation):

    class Input:
        piano_operativo = graphene.Argument(PianoCreateInput)
        codice = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    piano_aggiornato = graphene.Field(PianoNode)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        try:
            _piano = Piano.objects.get(codice=input['codice'])
            if _piano:
                _piano_data = input.get('piano_operativo')
                _data = _piano_data.pop('fase')
                _fase = Fase.objects.get(codice=_data['codice'])
                _piano.fase = _fase
                piano_aggiornato = update_create_instance(_piano, _piano_data)
                return cls(piano_aggiornato=piano_aggiornato)
        except ValidationError as e:
            return cls(piano_aggiornato=None, errors=get_errors(e))


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
# QUERIES
# ##############################################################################
class Query(object):
    # Models
    ente = relay.Node.Field(EnteNode)
    tutti_gli_enti = DjangoFilterConnectionField(EnteNode)

    fase = relay.Node.Field(FaseNode)
    tutte_le_fasi = DjangoFilterConnectionField(FaseNode)

    piano = relay.Node.Field(PianoNode)
    tutti_i_piani = DjangoFilterConnectionField(PianoNode)

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

    """
    # Example Auth
    my_posts = DjangoFilterConnectionField(PostNode)

    def resolve_my_posts(self, info):
        # context will reference to the Django request
        if not info.context.user.is_authenticated():
            return Post.objects.none()
        else:
            return Post.objects.filter(owner=info.context.user)
    """


# ##############################################################################
# MUTATIONS
# ##############################################################################
class Mutation(object):
    create_fase = CreateFase.Field()
    update_fase = UpdateFase.Field()
    create_piano = CreatePiano.Field()
    update_piano = UpdatePiano.Field()
