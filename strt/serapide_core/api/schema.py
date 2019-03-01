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

import logging
import graphene

from graphene_django.debug import DjangoDebug
from graphene_django.filter import DjangoFilterConnectionField

from serapide_core.modello.enums import (
    FASE,
    TIPOLOGIA_VAS,
    TIPOLOGIA_PIANO,
    TIPOLOGIA_CONTATTO,
)

from serapide_core.api.graphene import (
    enums,
    types,
    filters
)

from serapide_core.api.graphene.mutations import (
    vas,
    core,
    piano,
    uploads,
)

logger = logging.getLogger(__name__)


# ##############################################################################
# QUERIES
# ##############################################################################
class Query(object):

    # Models
    fasi = DjangoFilterConnectionField(types.FaseNode)

    utenti = DjangoFilterConnectionField(types.AppUserNode,
                                         filterset_class=filters.UserMembershipFilter)

    enti = DjangoFilterConnectionField(types.EnteNode,
                                       filterset_class=filters.EnteUserMembershipFilter)

    piani = DjangoFilterConnectionField(types.PianoNode,
                                        filterset_class=filters.PianoUserMembershipFilter)

    procedure_vas = DjangoFilterConnectionField(types.ProceduraVASNode,
                                                filterset_class=filters.ProceduraVASMembershipFilter)

    contatti = DjangoFilterConnectionField(types.ContattoNode,
                                           filterset_class=filters.EnteContattoMembershipFilter)

    # Enums
    fase_piano = graphene.List(enums.FasePiano)
    tipologia_vas = graphene.List(enums.TipologiaVAS)
    tipologia_piano = graphene.List(enums.TipologiaPiano)
    tipologia_contatto = graphene.List(enums.TipologiaContatto)

    def resolve_fase_piano(self, info):
        _l = []
        for _f in FASE:
            _l.append(enums.FasePiano(_f[0], _f[1]))
        return _l

    def resolve_tipologia_vas(self, info):
        _l = []
        for _t in TIPOLOGIA_VAS:
            _l.append(enums.TipologiaVAS(_t[0], _t[1]))
        return _l

    def resolve_tipologia_piano(self, info):
        _l = []
        for _t in TIPOLOGIA_PIANO:
            _l.append(enums.TipologiaPiano(_t[0], _t[1]))
        return _l

    def resolve_tipologia_contatto(self, info):
        _l = []
        for _t in TIPOLOGIA_CONTATTO:
            _l.append(enums.TipologiaContatto(_t[0], _t[1]))
        return _l

    # Debug
    debug = graphene.Field(DjangoDebug, name='__debug')


# ############################################################################ #
# Default Mutation Proxy
# ############################################################################ #
class Mutation(object):

    create_fase = core.CreateFase.Field()
    update_fase = core.UpdateFase.Field()

    create_contatto = core.CreateContatto.Field()
    delete_contatto = core.DeleteContatto.Field()

    create_piano = piano.CreatePiano.Field()
    update_piano = piano.UpdatePiano.Field()
    delete_piano = piano.DeletePiano.Field()
    promozione_piano = piano.PromozionePiano.Field()

    create_procedura_vas = vas.CreateProceduraVAS.Field()
    update_procedura_vas = vas.UpdateProceduraVAS.Field()

    upload = uploads.UploadFile.Field()
    delete_risorsa = uploads.DeleteRisorsa.Field()
    upload_risorsa_vas = uploads.UploadRisorsaVAS.Field()
    delete_risorsa_vas = uploads.DeleteRisorsaVAS.Field()
