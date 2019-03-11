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

import graphene

from graphene import InputObjectType


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
    assoggettamento = graphene.Boolean(required=False)
    pubblicazione_provvedimento_verifica_ap = graphene.String(required=False)
    pubblicazione_provvedimento_verifica_ac = graphene.String(required=False)


class ConsultazioneVASUpdateInput(InputObjectType):
    """
    Class created to accept input data
    from the interactive graphql console.
    """
    data_scadenza = graphene.types.datetime.DateTime(required=False)
    data_ricezione_pareri = graphene.types.datetime.DateTime(required=False)
    avvio_consultazioni_sca = graphene.Boolean(required=False)
