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


class EnteCreateInput(InputObjectType):
    """
    Class created to accept input data
    from the interactive graphql console.
    """
    nome = graphene.String(source='nome', required=False)
    ipa = graphene.String(required=True)


# class ContattoCreateInput(InputObjectType):
#     """
#     Class created to accept input data
#     from the interactive graphql console.
#     """
#     nome = graphene.String(source='nome', required=True)
#     email = graphene.String(source='email', required=True)
#     tipologia = graphene.String(required=True)
#     ente = graphene.InputField(EnteCreateInput, required=True)

# class SoggettoOperanteCreateInput(InputObjectType):
#     """
#     Class created to accept input data
#     from the interactive graphql console.
#     """
#     ufficio_id = graphene.ID(source='ufficio_id', required=True)
#     qualifica = graphene.ID(source='qualifica', required=True)
#     piano = graphene.String(source='piano', required=True)


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
    fase = graphene.String(required=False)


class SoggettoOperanteInput(InputObjectType):
    ufficio_uuid = graphene.String(required=True)
    qualifica = graphene.String(required=True)


class PianoUpdateInput(InputObjectType):
    """
    Class created to accept input data
    from the interactive graphql console.
    """
    url = graphene.String(required=False)
    numero_delibera = graphene.String(required=False)
    data_delibera = graphene.types.datetime.DateTime(required=False)
    data_accettazione = graphene.types.datetime.DateTime(required=False)
    data_avvio = graphene.types.datetime.DateTime(required=False)
    data_approvazione = graphene.types.datetime.DateTime(required=False)
    descrizione = graphene.InputField(graphene.List(graphene.String), required=False)

    soggetto_proponente_uuid = graphene.String(required=False)

    soggetti_operanti = graphene.List(SoggettoOperanteInput, required=False)

    redazione_norme_tecniche_attuazione_url = graphene.String(required=False)
    compilazione_rapporto_ambientale_url = graphene.String(required=False)
    conformazione_pit_ppr_url = graphene.String(required=False)
    monitoraggio_urbanistico_url = graphene.String(required=False)


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


class ProceduraAvvioCreateInput(InputObjectType):
    """
    Class created to accept input data
    from the interactive graphql console.
    """
    piano = graphene.InputField(PianoUpdateInput, required=False)
    data_creazione = graphene.types.datetime.DateTime(required=False)


class ProceduraAvvioUpdateInput(InputObjectType):
    """
    Class created to accept input data
    from the interactive graphql console.
    """
    conferenza_copianificazione = graphene.String(required=False)
    data_creazione = graphene.types.datetime.DateTime(required=False)
    data_scadenza_risposta = graphene.types.datetime.DateTime(required=False)
    garante_nominativo = graphene.String(required=False)
    garante_pec = graphene.String(required=False)
    notifica_genio_civile = graphene.Boolean(required=False)
    richiesta_integrazioni = graphene.Boolean(required=False)
    messaggio_integrazione = graphene.String(required=False)


class ProceduraAdozioneCreateInput(InputObjectType):
    """
    Class created to accept input data
    from the interactive graphql console.
    """
    piano = graphene.InputField(PianoUpdateInput, required=False)
    data_creazione = graphene.types.datetime.DateTime(required=False)


class ProceduraAdozioneUpdateInput(InputObjectType):
    """
    Class created to accept input data
    from the interactive graphql console.
    """
    data_delibera_adozione = graphene.types.datetime.DateTime(required=False)
    data_ricezione_osservazioni = graphene.types.datetime.DateTime(required=False)
    data_ricezione_pareri = graphene.types.datetime.DateTime(required=False)
    pubblicazione_burt_url = graphene.String(required=False)
    pubblicazione_burt_data = graphene.types.datetime.DateTime(required=False)
    pubblicazione_burt_bollettino = graphene.String(required=False)
    pubblicazione_sito_url = graphene.String(required=False)
    osservazioni_concluse = graphene.Boolean(required=False)
    richiesta_conferenza_paesaggistica = graphene.Boolean(required=False)
    url_piano_controdedotto = graphene.String(required=False)
    url_rev_piano_post_cp = graphene.String(required=False)


class ProceduraApprovazioneCreateInput(InputObjectType):
    """
    Class created to accept input data
    from the interactive graphql console.
    """
    piano = graphene.InputField(PianoUpdateInput, required=False)
    data_creazione = graphene.types.datetime.DateTime(required=False)


class ProceduraApprovazioneUpdateInput(InputObjectType):
    """
    Class created to accept input data
    from the interactive graphql console.
    """
    data_delibera_approvazione = graphene.types.datetime.DateTime(required=False)
    pubblicazione_url = graphene.String(required=False)
    pubblicazione_url_data = graphene.types.datetime.DateTime(required=False)
    richiesta_conferenza_paesaggistica = graphene.Boolean(required=False)
    url_piano_pubblicato = graphene.String(required=False)
    url_rev_piano_post_cp = graphene.String(required=False)


class ProceduraPubblicazioneCreateInput(InputObjectType):
    """
    Class created to accept input data
    from the interactive graphql console.
    """
    piano = graphene.InputField(PianoUpdateInput, required=False)
    data_creazione = graphene.types.datetime.DateTime(required=False)


class ProceduraPubblicazioneUpdateInput(InputObjectType):
    """
    Class created to accept input data
    from the interactive graphql console.
    """
    data_pubblicazione = graphene.types.datetime.DateTime(required=False)
    pubblicazione_url = graphene.String(required=False)
    pubblicazione_url_data = graphene.types.datetime.DateTime(required=False)
