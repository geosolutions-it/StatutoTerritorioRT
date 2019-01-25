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

import os
import logging
import datetime
import graphene
import traceback
import django_filters

from django.conf import settings

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from django.core.files.storage import default_storage
from django.core.files.uploadedfile import (TemporaryUploadedFile, InMemoryUploadedFile)

from graphene import InputObjectType, relay
from graphene_django import DjangoObjectType
from graphene_django.debug import DjangoDebug
from graphene_django.filter import DjangoFilterConnectionField
from graphene_file_upload.scalars import Upload

from strt_users.models import (
    AppUser, Organization, OrganizationType
)

from serapide_core.helpers import (
    get_errors, update_create_instance, is_RUP
)
from serapide_core.modello.models import (
    Piano, Fase, Risorsa, FasePianoStorico, RisorsePiano
)
from serapide_core.modello.enums import (
    FASE, TIPOLOGIA_PIANO
)

logger = logging.getLogger(__name__)

# ############################################################################ #
# INPUTS                                                                       #
# ############################################################################ #

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


class RisorsaNode(DjangoObjectType):

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


class EnteTipoNode(DjangoObjectType):

    class Meta:
        model = OrganizationType
        interfaces = (relay.Node, )


class AppUserNode(DjangoObjectType):

    class Meta:
        model = AppUser
        # Allow for some more advanced filtering here
        filter_fields = {
            'fiscal_code': ['exact'],
            'first_name': ['exact', 'icontains', 'istartswith'],
            'last_name': ['exact', 'icontains', 'istartswith'],
            'email': ['exact'],
        }
        exclude_fields = ('password', 'is_staff', 'is_active', 'is_superuser', 'last_login' )
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

    user = graphene.Field(AppUserNode)
    ente = graphene.Field(EnteNode)
    storico_fasi = graphene.List(FasePianoStoricoType)
    risorsa = DjangoFilterConnectionField(RisorsePianoType)

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
    fase__codice = django_filters.CharFilter(lookup_expr='iexact')

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
    enti = DjangoFilterConnectionField(EnteNode,
                                       filterset_class=EnteUserMembershipFilter)

    fasi = DjangoFilterConnectionField(FaseNode)

    risorse = DjangoFilterConnectionField(RisorsaNode)

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
            _piano_data['user'] = info.context.user
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
How to use this mutation
- send a POST multi-part form with Content-Type: application/graphql
- params:
  1. operations: {"query":"mutation UploadFile($file: Upload!, $piano: String!,
                                            $file_type: String!) {
                              upload(file: $file, codicePiano: $piano, tipoFile: $file_type) {
                                  resourceId,
                                  success }}",
                        "variables": { "file": null, "piano":"1234","file_type":"****"} }

  2. map: {"0":["variables.file"]}
  3. 0: <binary data>
  4. <other POST params if needed>
"""
class UploadFile(graphene.Mutation):
    class Arguments:
        codice_piano = graphene.String(required=True)
        tipo_file = graphene.String(required=True)
        file = Upload(required=True)

    risorse = graphene.List(RisorsaNode)
    success = graphene.Boolean()

    def mutate(self, info, file, **input):
        if info.context.user and info.context.user.is_authenticated:
            # Fetching input arguments
            _codice_piano = input['codice_piano']
            _tipo_file = input['tipo_file']

            try:
                # Validating 'Piano'
                _piano = Piano.objects.get(codice=_codice_piano)
                # Ensuring Media Folder exists and is writable
                _base_media_folder = os.path.join(settings.MEDIA_ROOT, _codice_piano)
                if not os.path.exists(_base_media_folder):
                    os.makedirs(_base_media_folder)
                if not isinstance(file, list):
                    file = [file]
                resources = []
                for f in file:
                    _dimensione_file = f.size / 1024 # size in KB
                    if os.path.exists(_base_media_folder) and _piano is not None and \
                        type(f) in (TemporaryUploadedFile, InMemoryUploadedFile):
                            _file_name = str(f)
                            _file_path = '{}/{}'.format(_codice_piano, _file_name)
                            _risorsa = None

                            with default_storage.open(_file_path, 'wb+') as _destination:
                                for _chunk in f.chunks():
                                    _destination.write(_chunk)
                                # Attaching uploaded File to Piano
                                _risorsa = Risorsa.create(
                                    _file_name,
                                    _destination,
                                    _tipo_file,
                                    _dimensione_file,
                                    _piano.fase)
                                _risorsa.save()
                                if _risorsa:
                                    RisorsePiano(piano=_piano, risorsa=_risorsa).save()
                                resources.append(_risorsa)
                            _full_path = os.path.join(settings.MEDIA_ROOT, _file_path)
                            # Remove original uploaded/temporary file
                            os.remove(_destination.name)

                return UploadFile(risorse=resources, success=True)
            except:
                tb = traceback.format_exc()
                logger.error(tb)

        # Something went wrong
        return UploadFile(success=False)

class DeleteRisorsa(graphene.Mutation):
    class Arguments:
        risorsa_id = graphene.ID(required=True)

    success = graphene.Boolean()
    uuid =  graphene.ID()
    def mutate(self, info, **input):
        if info.context.user and info.context.user.is_authenticated:
            # Fetching input arguments
            _id = input['risorsa_id']
            # TODO:: Andrebbe controllato se la risorsa in funzione del tipo e della fase del piano è eliminabile o meno
            try:
                _risorse = Risorsa.objects.filter(uuid=_id)
                """
                Deletes file from filesystem
                when corresponding `MediaFile` object is deleted.
                """
                for _risorsa in _risorse:
                    if _risorsa.file:
                        if os.path.isfile(_risorsa.file.path) and os.path.exists(_risorsa.file.path):
                            os.remove(_risorsa.file.path)
                    _risorsa.delete()

                return DeleteRisorsa(success=True, uuid=_id)
            except:
                tb = traceback.format_exc()
                logger.error(tb)

        return DeleteRisorsa(success=False)

# ############################################################################ #
class Mutation(object):
    create_fase = CreateFase.Field()
    update_fase = UpdateFase.Field()
    create_piano = CreatePiano.Field()
    update_piano = UpdatePiano.Field()
    upload = UploadFile.Field()
    delete_risorsa = DeleteRisorsa.Field()
