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
import traceback

from django.utils.translation import ugettext_lazy as _

from graphene import relay

from graphql_extensions.exceptions import GraphQLError

from serapide_core.helpers import update_create_instance

from serapide_core.modello.models import (
    Piano,
    ProceduraVAS,
)

from serapide_core.modello.enums import TIPOLOGIA_VAS

from .. import types
from .. import inputs

logger = logging.getLogger(__name__)


class CreateProceduraVAS(relay.ClientIDMutation):

    class Input:
        procedura_vas = graphene.Argument(inputs.ProceduraVASCreateInput)
        codice_piano = graphene.String(required=True)

    nuova_procedura_vas = graphene.Field(types.ProceduraVASNode)

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
        procedura_vas = graphene.Argument(inputs.ProceduraVASUpdateInput)
        uuid = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    procedura_vas_aggiornata = graphene.Field(types.ProceduraVASNode)

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
