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
import datetime
import graphene
import traceback

from codicefiscale import codicefiscale

from django.conf import settings
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from graphene import relay

from graphql_extensions.exceptions import GraphQLError

from strt_users.models import (
    AppUser,
    Organization,
    MembershipType,
    UserMembership,
)

from serapide_core.helpers import (
    is_RUP,
    get_errors,
    update_create_instance,
)

from serapide_core.modello.models import (
    Fase,
    Contatto,
)

from serapide_core.modello.enums import TIPOLOGIA_CONTATTO

from .. import types
from .. import inputs

logger = logging.getLogger(__name__)


class CreateFase(relay.ClientIDMutation):

    class Input:
        fase = graphene.Argument(inputs.FaseCreateInput)

    nuova_fase = graphene.Field(types.FaseNode)

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
        fase = graphene.Argument(inputs.FaseCreateInput)
        codice = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    fase_aggiornata = graphene.Field(types.FaseNode)

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
        contatto = graphene.Argument(inputs.ContattoCreateInput)

    nuovo_contatto = graphene.Field(types.ContattoNode)

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
            _token = info.context.session['token'] if 'token' in info.context.session else None

            if info.context.user and not info.context.user.is_anonymous and \
            (rules.test_rule('strt_users.is_superuser', info.context.user) or is_RUP(info.context.user) or
             rules.test_rule('strt_core.api.is_actor', _token or (info.context.user, _ente), 'Comune')):

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

                    user = AppUser.objects.filter(
                        Q(fiscal_code=fiscal_code) |
                        Q(first_name=first_name) |
                        Q(last_name=last_name)).last()
                    if not user:
                        user = AppUser.objects.filter(email=nuovo_contatto.email).last()

                    if user:
                        nuovo_contatto.user = user
                    else:
                        nuovo_contatto.user, created = AppUser.objects.get_or_create(
                            fiscal_code=fiscal_code,
                            defaults={
                                'first_name': first_name,
                                'last_name': last_name,
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
        (rules.test_rule('strt_users.is_superuser', info.context.user) or is_RUP(info.context.user)):

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
