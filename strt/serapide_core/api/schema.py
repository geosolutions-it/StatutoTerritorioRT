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
import rules
import logging
import datetime
import graphene
import traceback
import django_filters

from urllib.parse import urljoin
from codicefiscale import codicefiscale

from django.conf import settings

from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from django.core.files.storage import default_storage
from django.core.files.uploadedfile import (
    TemporaryUploadedFile,
    InMemoryUploadedFile
)

from pinax.messages.models import Thread, Message

from graphene import InputObjectType, relay
from graphene_django import DjangoObjectType
from graphene_django.debug import DjangoDebug
from graphene_django.filter import DjangoFilterConnectionField
from graphene_file_upload.scalars import Upload

from graphql_extensions.exceptions import GraphQLError

from strt_users.models import (
    AppUser,
    Organization,
    OrganizationType,
    MembershipType,
    UserMembership,
    Token,
)

from serapide_core.helpers import (
    is_RUP,
    get_errors,
    update_create_instance,
)
from serapide_core.signals import (
    piano_phase_changed,
)
from serapide_core.modello.models import (
    Fase,
    Piano,
    Azione,
    Risorsa,
    Contatto,
    AzioniPiano,
    ProceduraVAS,
    PianoAuthTokens,
    FasePianoStorico,
    RisorsePiano, RisorseVas,
    AutoritaCompetenteVAS, SoggettiSCA,
)
from serapide_core.modello.enums import (
    FASE,
    AZIONI,
    FASE_NEXT,
    STATO_AZIONE,
    TIPOLOGIA_VAS,
    TIPOLOGIA_PIANO,
    TIPOLOGIA_AZIONE,
    TIPOLOGIA_CONTATTO,
)

logger = logging.getLogger(__name__)


# ##############################################################################
# ENUMS
# ##############################################################################
class StrtEnumNode(graphene.ObjectType):

    value = graphene.String()
    label = graphene.String()


class FasePiano(StrtEnumNode):
    pass


class TipologiaVAS(StrtEnumNode):
    pass


class TipologiaPiano(StrtEnumNode):
    pass


class TipologiaContatto(StrtEnumNode):
    pass


# ############################################################################ #
# INPUTS                                                                       #
# ############################################################################ #

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


class ContattoCreateInput(InputObjectType):
    """
    Class created to accept input data
    from the interactive graphql console.
    """
    nome = graphene.String(source='nome', required=True)
    email = graphene.String(source='email', required=True)
    tipologia = graphene.String(required=True)
    ente = graphene.InputField(EnteCreateInput, required=True)


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
    data_delibera = graphene.types.datetime.DateTime(required=False)
    descrizione = graphene.InputField(graphene.List(graphene.String), required=False)
    fase = graphene.InputField(FaseCreateInput, required=False)


class PianoUpdateInput(InputObjectType):
    """
    Class created to accept input data
    from the interactive graphql console.
    """
    url = graphene.String(required=False)
    data_delibera = graphene.types.datetime.DateTime(required=False)
    data_accettazione = graphene.types.datetime.DateTime(required=False)
    data_avvio = graphene.types.datetime.DateTime(required=False)
    data_approvazione = graphene.types.datetime.DateTime(required=False)
    descrizione = graphene.InputField(graphene.List(graphene.String), required=False)
    soggetto_proponente_uuid = graphene.String(required=False)
    autorita_competente_vas = graphene.List(graphene.String, required=False)
    soggetti_sca = graphene.List(graphene.String, required=False)


class ProceduraVASCreateInput(InputObjectType):
    """
    Class created to accept input data
    from the interactive graphql console.
    """
    tipologia = graphene.String(required=True)

    piano = graphene.InputField(PianoUpdateInput, required=False)
    note = graphene.InputField(graphene.List(graphene.String), required=False)
    data_creazione = graphene.types.datetime.DateTime(required=False)


class ProceduraVASUpdateInput(InputObjectType):
    """
    Class created to accept input data
    from the interactive graphql console.
    """
    tipologia = graphene.String(required=False)
    note = graphene.InputField(graphene.List(graphene.String), required=False)
    data_creazione = graphene.types.datetime.DateTime(required=False)
    data_verifica = graphene.types.datetime.DateTime(required=False)
    data_procedimento = graphene.types.datetime.DateTime(required=False)
    data_approvazione = graphene.types.datetime.DateTime(required=False)
    verifica_effettuata = graphene.Boolean(required=False)
    procedimento_effettuato = graphene.Boolean(required=False)
    non_necessaria = graphene.Boolean(required=False)


# ##############################################################################
# FILTERS
# ##############################################################################
class UserMembershipFilter(django_filters.FilterSet):

    # Do case-insensitive lookups on 'name'
    name = django_filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = AppUser
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
        model = Organization
        fields = ['name', 'code', 'description', 'usermembership', ]

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


class EnteContattoMembershipFilter(django_filters.FilterSet):

    # Do case-insensitive lookups on 'name'
    name = django_filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = Contatto
        fields = ['name', 'email', 'ente', 'tipologia', ]

    @property
    def qs(self):
        # The query context can be found in self.request.
        if rules.test_rule('strt_core.api.can_access_private_area', self.request.user):
            if is_RUP(self.request.user):
                return super(EnteContattoMembershipFilter, self).qs.all()
            else:
                return super(EnteContattoMembershipFilter, self).qs.filter(
                    ente__usermembership__member=self.request.user)
        else:
            return super(EnteContattoMembershipFilter, self).qs.none()


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
                for _m in _memberships.all():
                    if _m.type.code == settings.RESPONSABILE_ISIDE_CODE:
                        # RESPONSABILE_ISIDE_CODE cannot access to Piani at all
                        continue
                    else:
                        _enti.append(_m.organization.code)

        token = self.request.session.get('token', None)
        if token:
            _allowed_pianos = [_pt.piano.codice for _pt in PianoAuthTokens.objects.filter(token__key=token)]
            return super(PianoUserMembershipFilter, self).qs.filter(codice__in=_allowed_pianos).order_by('-last_update')
        else:
            return super(PianoUserMembershipFilter, self).qs.filter(ente__code__in=_enti).order_by('-last_update')


class ProceduraVASMembershipFilter(django_filters.FilterSet):

    piano__codice = django_filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = ProceduraVAS
        fields = '__all__'

    @property
    def qs(self):
        # The query context can be found in self.request.
        _enti = []
        _memberships = None
        if rules.test_rule('strt_core.api.can_access_private_area', self.request.user):
            _memberships = self.request.user.memberships
            if _memberships:
                _enti = [_m.organization.code for _m in _memberships.all()]

        token = self.request.session.get('token', None)
        if token:
            _allowed_pianos = [_pt.piano.codice for _pt in PianoAuthTokens.objects.filter(token__key=token)]
            _pianos = [_p for _p in Piano.objects.filter(codice__in=_allowed_pianos)]
            for _p in _pianos:
                _enti.append(_p.ente.code)

        return super(ProceduraVASMembershipFilter, self).qs.filter(ente__code__in=_enti)


# ##############################################################################
# QUERIES
# ##############################################################################
class Query(object):

    # Models
    fasi = DjangoFilterConnectionField(FaseNode)

    utenti = DjangoFilterConnectionField(AppUserNode,
                                         filterset_class=UserMembershipFilter)

    enti = DjangoFilterConnectionField(EnteNode,
                                       filterset_class=EnteUserMembershipFilter)

    piani = DjangoFilterConnectionField(PianoNode,
                                        filterset_class=PianoUserMembershipFilter)

    procedure_vas = DjangoFilterConnectionField(ProceduraVASNode,
                                                filterset_class=ProceduraVASMembershipFilter)

    contatti = DjangoFilterConnectionField(ContattoNode,
                                           filterset_class=EnteContattoMembershipFilter)

    # Enums
    fase_piano = graphene.List(FasePiano)
    tipologia_vas = graphene.List(TipologiaVAS)
    tipologia_piano = graphene.List(TipologiaPiano)
    tipologia_contatto = graphene.List(TipologiaContatto)

    def resolve_fase_piano(self, info):
        _l = []
        for _f in FASE:
            _l.append(FasePiano(_f[0], _f[1]))
        return _l

    def resolve_tipologia_vas(self, info):
        _l = []
        for _t in TIPOLOGIA_VAS:
            _l.append(TipologiaVAS(_t[0], _t[1]))
        return _l

    def resolve_tipologia_piano(self, info):
        _l = []
        for _t in TIPOLOGIA_PIANO:
            _l.append(TipologiaPiano(_t[0], _t[1]))
        return _l

    def resolve_tipologia_contatto(self, info):
        _l = []
        for _t in TIPOLOGIA_CONTATTO:
            _l.append(TipologiaContatto(_t[0], _t[1]))
        return _l

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
        try:
            if info.context.user and \
            rules.test_rule('strt_users.is_superuser', info.context.user):
                _data = input.get('fase')
                _fase = Fase()
                nuova_fase = update_create_instance(_fase, _data)
                return cls(nuova_fase=nuova_fase)
            else:
                return GraphQLError(_("Forbidden"), code=403)
        except BaseException as e:
            tb = traceback.format_exc()
            logger.error(tb)
            return GraphQLError(e, code=500)


class UpdateFase(relay.ClientIDMutation):

    class Input:
        fase = graphene.Argument(FaseCreateInput)
        codice = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    fase_aggiornata = graphene.Field(FaseNode)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        try:
            if info.context.user and \
            rules.test_rule('strt_users.is_superuser', info.context.user):
                try:
                    _instance = Fase.objects.get(codice=input['codice'])
                    if _instance:
                        _data = input.get('fase')
                        fase_aggiornata = update_create_instance(_instance, _data)
                        return cls(fase_aggiornata=fase_aggiornata)
                except ValidationError as e:
                    return cls(fase_aggiornata=None, errors=get_errors(e))
            else:
                return GraphQLError(_("Forbidden"), code=403)
        except BaseException as e:
            tb = traceback.format_exc()
            logger.error(tb)
            return GraphQLError(e, code=500)


class CreateContatto(relay.ClientIDMutation):

    class Input:
        contatto = graphene.Argument(ContattoCreateInput)

    nuovo_contatto = graphene.Field(ContattoNode)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        try:
            _data = input.get('contatto')
            # Ente (M)
            if 'ente' in _data:
                _ente = _data.pop('ente')
                if is_RUP(info.context.user):
                    _ente = Organization.objects.get(code=_ente['code'])
                else:
                    _ente = Organization.objects.get(usermembership__member=info.context.user, code=_ente['code'])
                _data['ente'] = _ente

            if info.context.user and not info.context.user.is_anonymous:

                # Tipologia (M)
                if 'tipologia' in _data:
                    _tipologia = _data.pop('tipologia')
                    if _tipologia and _tipologia in TIPOLOGIA_CONTATTO:
                        _data['tipologia'] = _tipologia
                _contatto = Contatto()
                nuovo_contatto = update_create_instance(_contatto, _data)

                if nuovo_contatto.user is None:
                    # ####
                    # Creating a Temporary User to be associate to this 'Contatto'
                    # ###
                    first_name = nuovo_contatto.nome.split(' ')[0] if len(nuovo_contatto.nome.split(' ')) > 0 \
                        else nuovo_contatto.nome
                    last_name = nuovo_contatto.nome.split(' ')[1] if len(nuovo_contatto.nome.split(' ')) > 1 \
                        else nuovo_contatto.nome
                    fiscal_code = codicefiscale.encode(
                        surname=last_name,
                        name=first_name,
                        sex='M',
                        birthdate=datetime.datetime.now(timezone.get_current_timezone()).strftime('%m/%d/%Y'),
                        birthplace=nuovo_contatto.ente.name if nuovo_contatto.ente.type.code == 'C'
                            else settings.DEFAULT_MUNICIPALITY
                    )

                    nuovo_contatto.user, created = AppUser.objects.get_or_create(
                        fiscal_code=fiscal_code,
                        defaults={
                            'first_name': nuovo_contatto.nome,
                            'last_name': None,
                            'email': nuovo_contatto.email,
                            'is_staff': False,
                            'is_active': True
                        }
                    )

                    _new_role_type = MembershipType.objects.get(
                        code=settings.TEMP_USER_CODE,
                        organization_type=nuovo_contatto.ente.type
                    )
                    _new_role_name = '%s-%s-membership' % (fiscal_code, nuovo_contatto.ente.code)
                    _new_role, created = UserMembership.objects.get_or_create(
                        name=_new_role_name,
                        defaults={
                            'member': nuovo_contatto.user,
                            'organization': nuovo_contatto.ente,
                            'type': _new_role_type
                        }
                    )

                    _new_role.save()
                    nuovo_contatto.save()
                return cls(nuovo_contatto=nuovo_contatto)
            else:
                return GraphQLError(_("Forbidden"), code=403)
        except BaseException as e:
            tb = traceback.format_exc()
            logger.error(tb)
            return GraphQLError(e, code=500)


class DeleteContatto(graphene.Mutation):

    class Arguments:
        uuid = graphene.ID(required=True)

    success = graphene.Boolean()
    uuid = graphene.ID()

    def mutate(self, info, **input):
        if info.context.user and rules.test_rule('strt_users.can_access_private_area', info.context.user) and \
        is_RUP(info.context.user):

            # Fetching input arguments
            _id = input['uuid']
            try:
                _contatto = Contatto.objects.get(uuid=_id)
                _contatto.delete()

                return DeleteContatto(success=True, uuid=_id)
            except BaseException as e:
                tb = traceback.format_exc()
                logger.error(tb)
                return GraphQLError(e, code=500)

        return DeleteContatto(success=False)


class CreatePiano(relay.ClientIDMutation):

    class Input:
        piano_operativo = graphene.Argument(PianoCreateInput)

    nuovo_piano = graphene.Field(PianoNode)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        try:
            _piano_data = input.get('piano_operativo')
            # Ente (M)
            _data = _piano_data.pop('ente')
            _ente = Organization.objects.get(usermembership__member=info.context.user, code=_data['code'])
            _piano_data['ente'] = _ente
            if info.context.user and rules.test_rule('strt_users.is_RUP_of', info.context.user, _ente):

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

                # Inizializzazione Azioni del Piano
                _order = 0
                _azioni_piano = []
                for _a in AZIONI[_fase.nome]:
                    _azione = Azione(
                        tipologia=_a["tipologia"],
                        attore=_a["attore"],
                        order=_order
                    )
                    _azioni_piano.append(_azione)
                    _order += 1

                # Inizializzazione Procedura VAS
                _procedura_vas = ProceduraVAS()
                _procedura_vas.tipologia = TIPOLOGIA_VAS.semplificata

                nuovo_piano = update_create_instance(_piano, _piano_data)
                _procedura_vas.piano = nuovo_piano
                _procedura_vas.ente = nuovo_piano.ente
                _procedura_vas.save()

                for _ap in _azioni_piano:
                    _ap.save()
                    AzioniPiano.objects.get_or_create(azione=_ap, piano=nuovo_piano)

                _creato = nuovo_piano.azioni.filter(tipologia=TIPOLOGIA_AZIONE.creato_piano).first()
                if _creato:
                    _creato.stato = STATO_AZIONE.necessaria
                    _creato.save()

                return cls(nuovo_piano=nuovo_piano)
            else:
                return GraphQLError(_("Forbidden"), code=403)
        except BaseException as e:
            tb = traceback.format_exc()
            logger.error(tb)
            return GraphQLError(e, code=500)


class UpdatePiano(relay.ClientIDMutation):

    class Input:
        piano_operativo = graphene.Argument(PianoUpdateInput)
        codice = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    piano_aggiornato = graphene.Field(PianoNode)

    @staticmethod
    def make_token_expiration(days=365):
        _expire_days = getattr(settings, 'TOKEN_EXPIRE_DAYS', days)
        _expire_time = datetime.datetime.now(timezone.get_current_timezone())
        _expire_delta = datetime.timedelta(days=_expire_days)
        return _expire_time + _expire_delta

    @staticmethod
    def get_or_create_token(user, piano):
        _allowed_tokens = Token.objects.filter(user=user)
        _auth_token = PianoAuthTokens.objects.filter(piano=piano, token__in=_allowed_tokens)
        if not _auth_token:
            _token_key = Token.generate_key()
            _new_token, created = Token.objects.get_or_create(
                key=_token_key,
                defaults={
                    'user': user,
                    'expires': UpdatePiano.make_token_expiration()
                }
            )

            _auth_token, created = PianoAuthTokens.objects.get_or_create(
                piano=piano,
                token=_new_token
            )

            _new_token.save()
            _auth_token.save()

    @staticmethod
    def delete_token(user, piano):
        _allowed_tokens = Token.objects.filter(user=user)
        _auth_tokens = PianoAuthTokens.objects.filter(piano=piano, token__in=_allowed_tokens)
        for _at in _auth_tokens:
            _at.token.delete()
        _auth_tokens.delete()

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        _piano = Piano.objects.get(codice=input['codice'])
        _piano_data = input.get('piano_operativo')
        if info.context.user and \
        rules.test_rule('strt_core.api.can_edit_piano', info.context.user, _piano) and \
        rules.test_rule('strt_core.api.can_update_piano', info.context.user, _piano):
            try:
                # Codice Piano (M)
                if 'codice' in _piano_data:
                    _piano_data.pop('codice')
                    # This cannot be changed

                # Data Accettazione (M)
                if 'data_creazione' in _piano_data:
                    _piano_data.pop('data_creazione')
                    # This cannot be changed

                # Data Accettazione (O)
                if 'data_accettazione' in _piano_data:
                    _piano_data.pop('data_accettazione')
                    # This cannot be changed

                # Data Avvio (O)
                if 'data_avvio' in _piano_data:
                    _piano_data.pop('data_avvio')
                    # This cannot be changed

                # Data Approvazione (O)
                if 'data_approvazione' in _piano_data:
                    _piano_data.pop('data_approvazione')
                    # This cannot be changed

                # Ente (M)
                if 'ente' in _piano_data:
                    _piano_data.pop('ente')
                    # This cannot be changed

                # Fase (O)
                if 'fase' in _piano_data:
                    _piano_data.pop('fase')
                    # This cannot be changed

                # Tipologia (O)
                if 'tipologia' in _piano_data:
                    _piano_data.pop('tipologia')
                    # This cannot be changed

                # ############################################################ #
                # Editable fields - consistency checks
                # ############################################################ #
                # Descrizione (O)
                if 'descrizione' in _piano_data:
                    _data = _piano_data.pop('descrizione')
                    if rules.test_rule('strt_core.api.can_update_piano', info.context.user, _piano):
                        _piano.descrizione = _data[0]

                # Data Delibera (O)
                if 'data_delibera' in _piano_data:
                    if not rules.test_rule('strt_core.api.can_update_piano', info.context.user, _piano):
                        _piano_data.pop('data_delibera')
                        # This cannot be changed

                # Soggetto Proponente (O)
                if 'soggetto_proponente_uuid' in _piano_data:
                    _soggetto_proponente_uuid = _piano_data.pop('soggetto_proponente_uuid')
                    if rules.test_rule('strt_core.api.can_update_piano', info.context.user, _piano):
                        if _piano.soggetto_proponente:
                            UpdatePiano.delete_token(_piano.soggetto_proponente.user, _piano)
                            _piano.soggetto_proponente = None

                        if _soggetto_proponente_uuid and len(_soggetto_proponente_uuid) > 0:
                            _soggetto_proponente = Contatto.objects.get(uuid=_soggetto_proponente_uuid)
                            UpdatePiano.get_or_create_token(_soggetto_proponente.user, _piano)
                            _piano.soggetto_proponente = _soggetto_proponente

                # Autorità Competente VAS (O)
                if 'autorita_competente_vas' in _piano_data:
                    _autorita_competente_vas = _piano_data.pop('autorita_competente_vas')
                    if rules.test_rule('strt_core.api.can_update_piano', info.context.user, _piano):
                        _piano.autorita_competente_vas.clear()
                        if _autorita_competente_vas:
                            for _ac in _piano.autorita_competente_vas.all():
                                UpdatePiano.delete_token(_ac.user, _piano)

                            if len(_autorita_competente_vas) > 0:
                                _autorita_competenti = []
                                for _contatto_uuid in _autorita_competente_vas:
                                    _autorita_competenti.append(AutoritaCompetenteVAS(
                                        piano=_piano,
                                        autorita_competente=Contatto.objects.get(uuid=_contatto_uuid))
                                    )

                                for _ac in _autorita_competenti:
                                    UpdatePiano.get_or_create_token(_ac.autorita_competente.user, _piano)
                                    _ac.save()

                # Soggetti SCA (O)
                if 'soggetti_sca' in _piano_data:
                    _soggetti_sca_uuid = _piano_data.pop('soggetti_sca')
                    if rules.test_rule('strt_core.api.can_update_piano', info.context.user, _piano):
                        _piano.soggetti_sca.clear()
                        if _soggetti_sca_uuid:
                            for _sca in _piano.soggetti_sca.all():
                                UpdatePiano.delete_token(_sca.user, _piano)

                            if len(_soggetti_sca_uuid) > 0:
                                _soggetti_sca = []
                                for _contatto_uuid in _soggetti_sca_uuid:
                                    _soggetti_sca.append(SoggettiSCA(
                                        piano=_piano,
                                        soggetto_sca=Contatto.objects.get(uuid=_contatto_uuid))
                                    )

                                for _sca in _soggetti_sca:
                                    UpdatePiano.get_or_create_token(_sca.soggetto_sca.user, _piano)
                                    _sca.save()

                piano_aggiornato = update_create_instance(_piano, _piano_data)
                return cls(piano_aggiornato=piano_aggiornato)
            except BaseException as e:
                tb = traceback.format_exc()
                logger.error(tb)
                return GraphQLError(e, code=500)
        else:
            return GraphQLError(_("Forbidden"), code=403)


class DeletePiano(graphene.Mutation):

    class Arguments:
        codice_piano = graphene.String(required=True)

    success = graphene.Boolean()
    codice_piano = graphene.String()

    def mutate(self, info, **input):
        if info.context.user and is_RUP(info.context.user):

            # Fetching input arguments
            _id = input['codice_piano']
            try:
                _piano = Piano.objects.get(codice=_id)
                if rules.test_rule('strt_core.api.can_edit_piano', info.context.user, _piano) and \
                rules.test_rule('strt_core.api.can_update_piano', info.context.user, _piano):
                    _piano.delete()

                    return DeletePiano(success=True, codice_piano=_id)
            except BaseException as e:
                tb = traceback.format_exc()
                logger.error(tb)
                return GraphQLError(e, code=500)

        return DeletePiano(success=False)


class CreateProceduraVAS(relay.ClientIDMutation):

    class Input:
        procedura_vas = graphene.Argument(ProceduraVASCreateInput)
        codice_piano = graphene.String(required=True)

    nuova_procedura_vas = graphene.Field(ProceduraVASNode)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        _piano = Piano.objects.get(codice=input['codice_piano'])
        _procedura_vas_data = input.get('procedura_vas')
        if info.context.user and \
        rules.test_rule('strt_core.api.can_edit_piano', info.context.user, _piano) and \
        rules.test_rule('strt_core.api.can_update_piano', info.context.user, _piano):
            try:
                # ProceduraVAS (M)
                _procedura_vas_data['piano'] = _piano
                # Ente (M)
                _procedura_vas_data['ente'] = _piano.ente
                # Note (O)
                if 'note' in _procedura_vas_data:
                    _data = _procedura_vas_data.pop('note')
                    _procedura_vas_data['note'] = _data[0]
                _procedura_vas = ProceduraVAS()
                _procedura_vas.piano = _piano
                _procedura_vas_data['id'] = _procedura_vas.id
                _procedura_vas_data['uuid'] = _procedura_vas.uuid
                nuova_procedura_vas = update_create_instance(_procedura_vas, _procedura_vas_data)
                return cls(nuova_procedura_vas=nuova_procedura_vas)
            except BaseException as e:
                tb = traceback.format_exc()
                logger.error(tb)
                return GraphQLError(e, code=500)
        else:
            return GraphQLError(_("Forbidden"), code=403)


class UpdateProceduraVAS(relay.ClientIDMutation):

    class Input:
        procedura_vas = graphene.Argument(ProceduraVASUpdateInput)
        uuid = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    procedura_vas_aggiornata = graphene.Field(ProceduraVASNode)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        _procedura_vas = ProceduraVAS.objects.get(uuid=input['uuid'])
        _procedura_vas_data = input.get('procedura_vas')
        if 'piano' in _procedura_vas_data:
            # This cannot be changed
            _procedura_vas_data.pop('piano')
        _piano = _procedura_vas.piano
        if info.context.user and \
        rules.test_rule('strt_core.api.can_edit_piano', info.context.user, _piano) and \
        rules.test_rule('strt_core.api.can_update_piano', info.context.user, _piano):
            try:
                if 'uuid' in _procedura_vas_data:
                    _procedura_vas_data.pop('uuid')
                    # This cannot be changed

                if 'data_creazione' in _procedura_vas_data:
                    _procedura_vas_data.pop('data_creazione')
                    # This cannot be changed

                # Ente (M)
                if 'ente' in _procedura_vas_data:
                    _procedura_vas_data.pop('ente')
                    # This cannot be changed

                # Tipologia (O)
                if 'tipologia' in _procedura_vas_data:
                    _tipologia = _procedura_vas_data.pop('tipologia')
                    if _tipologia and _tipologia in TIPOLOGIA_VAS:
                        _procedura_vas_data['tipologia'] = _tipologia

                # Note (O)
                if 'note' in _procedura_vas_data:
                    _data = _procedura_vas_data.pop('note')
                    _procedura_vas.note = _data[0]
                procedura_vas_aggiornata = update_create_instance(_procedura_vas, _procedura_vas_data)
                return cls(procedura_vas_aggiornata=procedura_vas_aggiornata)
            except BaseException as e:
                tb = traceback.format_exc()
                logger.error(tb)
                return GraphQLError(e, code=500)
        else:
            return GraphQLError(_("Forbidden"), code=403)


# ############################################################################ #
# Upload 'Risorse' Mutations
# ############################################################################ #
class UploadBaseBase(graphene.Mutation):

    class Arguments:
        codice = graphene.String(required=True)
        tipo_file = graphene.String(required=True)
        file = Upload(required=True)

    @classmethod
    def handle_uploaded_data(cls, file, media_prefix, fase, tipo_file=None):
        # Ensuring Media Folder exists and is writable
        _base_media_folder = os.path.join(settings.MEDIA_ROOT, media_prefix)
        if not os.path.exists(_base_media_folder):
            os.makedirs(_base_media_folder)
        if not isinstance(file, list):
            file = [file]
        resources = []
        for f in file:
            _dimensione_file = f.size / 1024  # size in KB
            if os.path.exists(_base_media_folder) and \
            type(f) in (TemporaryUploadedFile, InMemoryUploadedFile):
                _file_name = str(f)
                _file_path = '{}/{}'.format(media_prefix, _file_name)
                _risorsa = None

                with default_storage.open(_file_path, 'wb+') as _destination:
                    for _chunk in f.chunks():
                        _destination.write(_chunk)
                    _risorsa = Risorsa.create(
                        _file_name,
                        _destination,
                        tipo_file,
                        _dimensione_file,
                        fase)
                    _risorsa.save()
                    resources.append(_risorsa)
                    # _full_path = os.path.join(settings.MEDIA_ROOT, _file_path)
                    # Remove original uploaded/temporary file
                    os.remove(_destination.name)
        return resources

    @classmethod
    def mutate(cls, root, info, file, **input):
        pass


class UploadFile(UploadBaseBase):

    piano_aggiornato = graphene.Field(PianoNode)
    success = graphene.Boolean()
    file_name = graphene.String()

    @classmethod
    def mutate(cls, root, info, file, **input):
        if info.context.user and rules.test_rule('strt_core.api.can_access_private_area', info.context.user):
            # Fetching input arguments
            _codice_piano = input['codice']
            _tipo_file = input['tipo_file']

            try:
                # Validating 'Piano'
                _piano = Piano.objects.get(codice=_codice_piano)
                if rules.test_rule('strt_core.api.can_edit_piano', info.context.user, _piano) and \
                rules.test_rule('strt_core.api.can_update_piano', info.context.user, _piano):
                    _resources = UploadBaseBase.handle_uploaded_data(
                        file,
                        _codice_piano,
                        _piano.fase,
                        _tipo_file
                    )
                    _success = False
                    if _resources and len(_resources) > 0:
                        _success = True
                        for _risorsa in _resources:
                            RisorsePiano(piano=_piano, risorsa=_risorsa).save()
                    return UploadFile(piano_aggiornato=_piano, success=_success, file_name=_resources[0].nome)
                else:
                    return GraphQLError(_("Forbidden"), code=403)
            except BaseException as e:
                tb = traceback.format_exc()
                logger.error(tb)
                return GraphQLError(e, code=500)

        # Something went wrong
        return GraphQLError(_("Not Allowed"), code=405)


class UploadRisorsaVAS(UploadBaseBase):

    success = graphene.Boolean()
    procedura_vas_aggiornata = graphene.Field(ProceduraVASNode)

    @classmethod
    def mutate(cls, root, info, file, **input):
        if info.context.user and rules.test_rule('strt_core.api.can_access_private_area', info.context.user):
            # Fetching input arguments
            _uuid_vas = input['codice']
            _tipo_file = input['tipo_file']

            try:
                # Validating 'Procedura VAS'
                _procedura_vas = ProceduraVAS.objects.get(uuid=_uuid_vas)
                if rules.test_rule('strt_core.api.can_edit_piano', info.context.user, _procedura_vas.piano) and \
                rules.test_rule('strt_core.api.can_update_piano', info.context.user, _procedura_vas.piano):
                    _resources = UploadBaseBase.handle_uploaded_data(
                        file,
                        _uuid_vas,
                        _procedura_vas.piano.fase,
                        _tipo_file
                    )
                    _success = False
                    if _resources and len(_resources) > 0:
                        _success = True
                        for _risorsa in _resources:
                            RisorseVas(procedura_vas=_procedura_vas, risorsa=_risorsa).save()
                    return UploadRisorsaVAS(procedura_vas_aggiornata=_procedura_vas, success=_success)
                else:
                    return GraphQLError(_("Forbidden"), code=403)
            except BaseException as e:
                tb = traceback.format_exc()
                logger.error(tb)
                return GraphQLError(e, code=500)

        # Something went wrong
        return GraphQLError(_("Not Allowed"), code=405)


class DeleteRisorsaBase(graphene.Mutation):

    class Arguments:
        risorsa_id = graphene.ID(required=True)
        codice = graphene.String(required=True)

    @classmethod
    def handle_downloaded_data(cls, risorsa):
        """
        Deletes file from filesystem
        when corresponding `MediaFile` object is deleted.
        """
        try:
            if risorsa.file:
                if os.path.isfile(risorsa.file.path) and os.path.exists(risorsa.file.path):
                    os.remove(risorsa.file.path)
            risorsa.delete()
            return True
        except BaseException:
            tb = traceback.format_exc()
            logger.error(tb)
            return False

    @classmethod
    def mutate(cls, root, info, **input):
        pass


class DeleteRisorsa(DeleteRisorsaBase):

    success = graphene.Boolean()
    piano_aggiornato = graphene.Field(PianoNode)

    @classmethod
    def mutate(cls, root, info, **input):
        if info.context.user and rules.test_rule('strt_core.api.can_access_private_area', info.context.user):
            # Fetching input arguments
            _id = input['risorsa_id']
            _codice_piano = input['codice']
            # TODO: Andrebbe controllato se la risorsa in funzione del tipo e della fase del piano è eliminabile o meno
            try:
                _piano = Piano.objects.get(codice=_codice_piano)
                if rules.test_rule('strt_core.api.can_edit_piano', info.context.user, _piano) and \
                rules.test_rule('strt_core.api.can_update_piano', info.context.user, _piano):
                    _risorsa = Risorsa.objects.get(uuid=_id)
                    _success = DeleteRisorsaBase.handle_downloaded_data(_risorsa)
                    return DeleteRisorsa(piano_aggiornato=_piano, success=_success)
                else:
                    return GraphQLError(_("Forbidden"), code=403)
            except BaseException as e:
                tb = traceback.format_exc()
                logger.error(tb)
                return GraphQLError(e, code=500)

        # Something went wrong
        return GraphQLError(_("Not Allowed"), code=405)


class DeleteRisorsaVAS(DeleteRisorsaBase):

    success = graphene.Boolean()
    procedura_vas_aggiornata = graphene.Field(ProceduraVASNode)

    @classmethod
    def mutate(cls, root, info, **input):
        if info.context.user and rules.test_rule('strt_core.api.can_access_private_area', info.context.user):
            # Fetching input arguments
            _id = input['risorsa_id']
            _uuid_vas = input['codice']
            # TODO: Andrebbe controllato se la risorsa in funzione del tipo e della fase del piano è eliminabile o meno
            try:
                _procedura_vas = ProceduraVAS.objects.get(uuid=_uuid_vas)
                if rules.test_rule('strt_core.api.can_edit_piano', info.context.user, _procedura_vas.piano) and \
                rules.test_rule('strt_core.api.can_update_piano', info.context.user, _procedura_vas.piano):
                    _risorsa = Risorsa.objects.get(uuid=_id)
                    _success = DeleteRisorsaBase.handle_downloaded_data(_risorsa)
                    return DeleteRisorsaVAS(procedura_vas_aggiornata=_procedura_vas, success=_success)
                else:
                    return GraphQLError(_("Forbidden"), code=403)
            except BaseException as e:
                tb = traceback.format_exc()
                logger.error(tb)
                return GraphQLError(e, code=500)

        # Something went wrong
        return GraphQLError(_("Not Allowed"), code=405)


# ############################################################################ #
# Management Passaggio di Stato Piano
# ############################################################################ #
class PromozionePiano(graphene.Mutation):

    class Arguments:
        codice_piano = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    piano_aggiornato = graphene.Field(PianoNode)

    @classmethod
    def get_next_phase(cls, fase):
        return FASE_NEXT[fase.nome]

    @classmethod
    def update_actions_for_phase(cls, fase, piano, procedura_vas):

        # Update Azioni Piano
        # - Complete Current Actions
        _order = 0
        for _a in piano.azioni.all():
            # _a.stato = STATO_AZIONE.nessuna
            _a.data = datetime.datetime.now(timezone.get_current_timezone())
            _a.save()
            _order += 1

        # - Attach Actions Templates for the Next "Fase"
        for _a in AZIONI[fase.nome]:
            _azione = Azione(
                tipologia=_a["tipologia"],
                attore=_a["attore"],
                order=_order,
                stato=STATO_AZIONE.necessaria
            )
            _azione.save()
            _order += 1
            AzioniPiano.objects.get_or_create(azione=_azione, piano=piano)

        # - Update Action state accordingly
        if fase.nome == FASE.anagrafica:

            _creato = piano.azioni.filter(tipologia=TIPOLOGIA_AZIONE.creato_piano).first()
            if _creato.stato != STATO_AZIONE.necessaria:
                raise Exception("Stato Inconsistente!")

            if _creato:
                _creato.stato = STATO_AZIONE.nessuna
                _creato.data = datetime.datetime.now(timezone.get_current_timezone())
                _creato.save()

            _verifica_vas = piano.azioni.filter(tipologia=TIPOLOGIA_AZIONE.parere_verifica_vas).first()
            if _verifica_vas:
                if procedura_vas.tipologia == TIPOLOGIA_VAS.non_necessaria:
                    _verifica_vas.stato = STATO_AZIONE.nessuna
                else:
                    _verifica_vas.stato = STATO_AZIONE.attesa
                    _verifica_vas_expire_days = getattr(settings, 'VERIFICA_VAS_EXPIRE_DAYS', 60)
                    _verifica_vas.data = datetime.datetime.now(timezone.get_current_timezone()) + \
                    datetime.timedelta(days=_verifica_vas_expire_days)
                _verifica_vas.save()

            _consultazioni_sca = piano.azioni.filter(tipologia=TIPOLOGIA_AZIONE.avvio_consultazioni_sca).first()
            if _consultazioni_sca:
                _consultazioni_sca.stato = STATO_AZIONE.attesa
                _consultazioni_sca_expire_days = getattr(settings, 'CONSULTAZIONI_SCA_EXPIRE_DAYS', 10)
                _consultazioni_sca.data = datetime.datetime.now(timezone.get_current_timezone()) + \
                datetime.timedelta(days=_consultazioni_sca_expire_days)
                _consultazioni_sca.save()

        elif fase.nome == FASE.avvio:

            _genio_civile = piano.azioni.filter(tipologia=TIPOLOGIA_AZIONE.protocollo_genio_civile).first()
            if _genio_civile:
                _genio_civile.stato = STATO_AZIONE.attesa
                _genio_civile.save()

    @classmethod
    def mutate(cls, root, info, **input):
        _piano = Piano.objects.get(codice=input['codice_piano'])
        _procedura_vas = ProceduraVAS.objects.get(piano=_piano)
        if info.context.user and rules.test_rule('strt_core.api.can_edit_piano', info.context.user, _piano):
            try:
                _next_fase = cls.get_next_phase(_piano.fase)
                if rules.test_rule('strt_core.api.fase_{next}_completa'.format(
                                   next=_next_fase),
                                   _piano,
                                   _procedura_vas):
                    _piano.fase = _fase = Fase.objects.get(nome=_next_fase)
                    piano_phase_changed.send(sender=Piano, user=info.context.user, piano=_piano)
                    _piano.save()

                    cls.update_actions_for_phase(_fase, _piano, _procedura_vas)

                    return PromozionePiano(
                        piano_aggiornato=_piano,
                        errors=[]
                    )
                else:
                    return GraphQLError(_("Not Allowed"), code=405)
            except BaseException as e:
                    tb = traceback.format_exc()
                    logger.error(tb)
                    return GraphQLError(e, code=500)
        else:
            return GraphQLError(_("Forbidden"), code=403)


# ############################################################################ #
# Default Mutation Proxy
# ############################################################################ #
class Mutation(object):

    create_fase = CreateFase.Field()
    update_fase = UpdateFase.Field()

    create_piano = CreatePiano.Field()
    update_piano = UpdatePiano.Field()
    delete_piano = DeletePiano.Field()

    create_procedura_vas = CreateProceduraVAS.Field()
    update_procedura_vas = UpdateProceduraVAS.Field()

    create_contatto = CreateContatto.Field()
    delete_contatto = DeleteContatto.Field()

    upload = UploadFile.Field()
    delete_risorsa = DeleteRisorsa.Field()

    upload_risorsa_vas = UploadRisorsaVAS.Field()
    delete_risorsa_vas = DeleteRisorsaVAS.Field()

    promozione_piano = PromozionePiano.Field()
