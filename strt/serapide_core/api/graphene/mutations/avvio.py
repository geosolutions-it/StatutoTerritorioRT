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
    ProceduraAvvio,
)

from serapide_core.modello.enums import (
    TIPOLOGIA_CONF_COPIANIFIZAZIONE,
)

from .. import types
from .. import inputs

logger = logging.getLogger(__name__)


class CreateProceduraAvvio(relay.ClientIDMutation):

    class Input:
        procedura_avvio = graphene.Argument(inputs.ProceduraAvvioCreateInput)
        codice_piano = graphene.String(required=True)

    nuova_procedura_avvio = graphene.Field(types.ProceduraAvvioNode)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        _piano = Piano.objects.get(codice=input['codice_piano'])
        _procedura_avvio_data = input.get('procedura_avvio')
        if info.context.user and \
        rules.test_rule('strt_core.api.can_edit_piano', info.context.user, _piano) and \
        rules.test_rule('strt_core.api.can_update_piano', info.context.user, _piano):
            try:
                # ProceduraAvvio (M)
                _procedura_avvio_data['piano'] = _piano
                # Ente (M)
                _procedura_avvio_data['ente'] = _piano.ente

                _procedura_avvio = ProceduraAvvio()
                _procedura_avvio.piano = _piano
                _procedura_avvio_data['id'] = _procedura_avvio.id
                _procedura_avvio_data['uuid'] = _procedura_avvio.uuid
                nuova_procedura_avvio = update_create_instance(_procedura_avvio, _procedura_avvio_data)
                return cls(nuova_procedura_avvio=nuova_procedura_avvio)
            except BaseException as e:
                tb = traceback.format_exc()
                logger.error(tb)
                return GraphQLError(e, code=500)
        else:
            return GraphQLError(_("Forbidden"), code=403)


class UpdateProceduraAvvio(relay.ClientIDMutation):

    class Input:
        procedura_avvio = graphene.Argument(inputs.ProceduraAvvioUpdateInput)
        uuid = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    procedura_avvio_aggiornata = graphene.Field(types.ProceduraAvvioNode)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        _procedura_avvio = ProceduraAvvio.objects.get(uuid=input['uuid'])
        _procedura_avvio_data = input.get('procedura_avvio')
        if 'piano' in _procedura_avvio_data:
            # This cannot be changed
            _procedura_avvio_data.pop('piano')
        _piano = _procedura_avvio.piano
        if info.context.user and \
        rules.test_rule('strt_core.api.can_edit_piano', info.context.user, _piano):
            try:
                if 'uuid' in _procedura_avvio_data:
                    _procedura_avvio_data.pop('uuid')
                    # This cannot be changed

                if 'data_creazione' in _procedura_avvio_data:
                    _procedura_avvio_data.pop('data_creazione')
                    # This cannot be changed

                # Ente (M)
                if 'ente' in _procedura_avvio_data:
                    _procedura_avvio_data.pop('ente')
                    # This cannot be changed

                # Tipologia (O)
                if 'conferenza_copianificazione' in _procedura_avvio_data:
                    _conferenza_copianificazione = _procedura_avvio_data.pop('conferenza_copianificazione')
                    if _conferenza_copianificazione and _conferenza_copianificazione in TIPOLOGIA_CONF_COPIANIFIZAZIONE:
                        _procedura_avvio_data['conferenza_copianificazione'] = _conferenza_copianificazione

                procedura_avvio_aggiornata = update_create_instance(_procedura_avvio, _procedura_avvio_data)

                return cls(procedura_avvio_aggiornata=procedura_avvio_aggiornata)
            except BaseException as e:
                tb = traceback.format_exc()
                logger.error(tb)
                return GraphQLError(e, code=500)
        else:
            return GraphQLError(_("Forbidden"), code=403)
