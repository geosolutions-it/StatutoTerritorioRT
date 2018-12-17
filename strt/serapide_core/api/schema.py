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
from serapide_core.helpers import get_errors, update_create_instance
from serapide_core.modello.models import (
    Piano, Stato, StatoPianoStorico
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
class StatoNode(DjangoObjectType):
    class Meta:
        model = Stato
        filter_fields = ['codice', 'nome', 'descrizione', 'piani_operativi']
        interfaces = (relay.Node, )


class StatoPianoStoricoType(DjangoObjectType):
    class Meta:
        model = StatoPianoStorico
        interfaces = (relay.Node, )


class PianoNode(DjangoObjectType):

    storico_stati = graphene.List(StatoPianoStoricoType)

    def resolve_storico_stati(self, info, **args):
        # Warning this is not currently paginated
        _hist = StatoPianoStorico.objects.filter(piano=self)
        return list(_hist)

    class Meta:
        model = Piano
        # Allow for some more advanced filtering here
        filter_fields = {
            'nome': ['exact', 'icontains', 'istartswith'],
            'codice': ['exact', 'icontains', 'istartswith'],
            'identificativo': ['exact', 'icontains', 'istartswith'],
            'notes': ['exact', 'icontains'],
            'tipologia': ['exact', 'icontains'],
            'stato': ['exact'],
            'stato__nome': ['exact'],
            'stato__codice': ['exact'],
        }
        interfaces = (relay.Node, )


class StatoCreateInput(InputObjectType):
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

    nome = graphene.String(required=True)
    codice = graphene.String(required=True)
    identificativo = graphene.String(required=True)
    tipologia = graphene.String(required=False)
    url = graphene.String(required=False)
    data_creazione = graphene.types.datetime.DateTime(required=False)
    notes = graphene.InputField(graphene.List(graphene.String), required=False)
    stato = graphene.InputField(StatoCreateInput, required=True)


class CreateStato(relay.ClientIDMutation):

    class Input:
        stato = graphene.Argument(StatoCreateInput)

    nuovo_stato = graphene.Field(StatoNode)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        _data = input.get('stato')
        _stato = Stato()
        nuovo_stato = update_create_instance(_stato, _data)
        return cls(nuovo_stato=nuovo_stato)


class UpdateStato(relay.ClientIDMutation):

    class Input:
        stato = graphene.Argument(StatoCreateInput)
        codice = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    stato_aggiornato = graphene.Field(StatoNode)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        try:
            _instance = Stato.objects.get(codice=input['codice'])
            if _instance:
                _data = input.get('stato')
                stato_aggiornato = update_create_instance(_instance, _data)
                return cls(stato_aggiornato=stato_aggiornato)
        except ValidationError as e:
            return cls(stato_aggiornato=None, errors=get_errors(e))


class CreatePiano(relay.ClientIDMutation):

    class Input:
        piano_operativo = graphene.Argument(PianoCreateInput)

    nuovo_piano = graphene.Field(PianoNode)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        _piano_data = input.get('piano_operativo')
        _data = _piano_data.pop('stato')
        _stato = Stato.objects.get(codice=_data['codice'])
        _piano_data['stato'] = _stato
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
                _data = _piano_data.pop('stato')
                _stato = Stato.objects.get(codice=_data['codice'])
                _piano.stato = _stato
                piano_aggiornato = update_create_instance(_piano, _piano_data)
                return cls(piano_aggiornato=piano_aggiornato)
        except ValidationError as e:
            return cls(stato_aggiornato=None, errors=get_errors(e))


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
# QUERIES
# ##############################################################################
class Query(object):
    stato = relay.Node.Field(StatoNode)
    tutti_gli_stati = DjangoFilterConnectionField(StatoNode)

    piano = relay.Node.Field(PianoNode)
    tutti_i_piani = DjangoFilterConnectionField(PianoNode)

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
    create_stato = CreateStato.Field()
    update_stato = UpdateStato.Field()
    create_piano = CreatePiano.Field()
    update_piano = UpdatePiano.Field()
