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
    Fase,
    TipologiaVAS,
    TipologiaPiano,
    # TIPOLOGIA_CONTATTO,
    TipologiaCopianificazione,
)

from serapide_core.api.graphene import (
    enums,
    types,
    filters
)

from serapide_core.api.graphene.mutations import (
    vas,
    core,
    avvio,
    piano,
    uploads,
    adozione,
    approvazione,
    pubblicazione,
)

from strt_users.models import (
    Utente,
    QualificaUfficio)

logger = logging.getLogger(__name__)


# ##############################################################################
# QUERIES
# ##############################################################################
class Query(object):

    # Models
    # fasi = DjangoFilterConnectionField(types.FaseNode)

    utenti = DjangoFilterConnectionField(types.UtenteNode,
                                         filterset_class=filters.UserMembershipFilter)

    enti = DjangoFilterConnectionField(types.EnteNode,
                                       filterset_class=filters.EnteUserMembershipFilter)

    piani = DjangoFilterConnectionField(types.PianoNode,
                                        filterset_class=filters.PianoUserMembershipFilter)

    procedure_vas = DjangoFilterConnectionField(types.ProceduraVASNode,
                                                filterset_class=filters.ProceduraVASMembershipFilter)

    procedure_adozione_vas = DjangoFilterConnectionField(types.ProceduraAdozioneVASNode,
                                                         filterset_class=filters.ProceduraVASMembershipFilter)

    procedure_avvio = DjangoFilterConnectionField(types.ProceduraAvvioNode,
                                                  filterset_class=filters.ProceduraAvvioMembershipFilter)

    procedure_adozione = DjangoFilterConnectionField(types.ProceduraAdozioneNode,
                                                     filterset_class=filters.ProceduraAdozioneMembershipFilter)

    procedure_approvazione = DjangoFilterConnectionField(types.ProceduraApprovazioneNode,
                                                         filterset_class=filters.ProceduraApprovazioneMembershipFilter)

    procedure_pubblicazione = DjangoFilterConnectionField(
        types.ProceduraPubblicazioneNode,
        filterset_class=filters.ProceduraPubblicazioneMembershipFilter)

    consultazione_vas = DjangoFilterConnectionField(types.ConsultazioneVASNode)

    conferenza_copianificazione = DjangoFilterConnectionField(types.ConferenzaCopianificazioneNode)

    piano_controdedotto = DjangoFilterConnectionField(types.PianoControdedottoNode)

    piano_rev_post_cp = DjangoFilterConnectionField(types.PianoRevPostCPNode)

    user_choices = graphene.Field(types.UtenteChoiceNode)

    uffici = DjangoFilterConnectionField(types.QualificaUfficioNode)

    # soggetti_operanti = DjangoFilterConnectionField(types.SoggettoOperanteNode,
    #                                     filterset_class=types.SoggettoOperanteFilter)


    # TODO
    # contatti = DjangoFilterConnectionField(types.ContattoNode,
    #                                        filterset_class=filters.EnteContattoMembershipFilter)

    # Enums
    # fase_piano = graphene.List(enums.FasePiano) # TODO
    tipologia_vas = graphene.List(enums.TipologiaVAS)
    tipologia_piano = graphene.List(enums.TipologiaPiano)
    tipologia_contatto = graphene.List(enums.TipologiaContatto)
    tipologia_conferenza_copianificazione = graphene.List(enums.TipologiaConferenzaCopianificazione)

    def resolve_fase_piano(self, info):
        _l = []
        for _f in Fase:
            _l.append(enums.FasePiano(_f[0], _f[1]))
        return _l

    def resolve_tipologia_vas(self, info):
        _l = []
        for _t in TipologiaVAS:
            _l.append(enums.TipologiaVAS(_t[0], _t[1]))
        return _l

    def resolve_tipologia_piano(self, info):
        return [enums.TipologiaPiano(value=t.name, label=t.value)
                    for t in TipologiaPiano]

    def resolve_user_choices(self, info):
        if info.context.user.is_anonymous:
            return None
        else:
            return info.context.user

    def resolve_tipologia_conferenza_copianificazione(self, info):
        return [enums.TipologiaConferenzaCopianificazione(value=t.name, label=t.value)
                    for t in TipologiaCopianificazione]

    # Debug
    debug = graphene.Field(DjangoDebug, name='__debug')


# ############################################################################ #
# Default Mutation Proxy
# ############################################################################ #
class Mutation(object):

    # create_fase = core.CreateFase.Field()
    # update_fase = core.UpdateFase.Field()

    # TODO
    # create_contatto = core.CreateContatto.Field()
    # delete_contatto = core.DeleteContatto.Field()

    create_piano = piano.CreatePiano.Field()
    update_piano = piano.UpdatePiano.Field()
    delete_piano = piano.DeletePiano.Field()
    promozione_piano = piano.PromozionePiano.Field()

    # create_procedura_vas = vas.CreateProceduraVAS.Field()
    update_procedura_vas = vas.UpdateProceduraVAS.Field()
    invio_pareri_verifica_vas = vas.InvioPareriVerificaVAS.Field()
    assoggettamento_vas = vas.AssoggettamentoVAS.Field()
    create_consultazione_vas = vas.CreateConsultazioneVAS.Field()
    update_consultazione_vas = vas.UpdateConsultazioneVAS.Field()
    avvio_consultazioni_vas = vas.AvvioConsultazioniVAS.Field()
    invio_pareri_vas = vas.InvioPareriVAS.Field()
    avvio_esame_pareri_sca = vas.AvvioEsamePareriSCA.Field()
    upload_elaborati_vas = vas.UploadElaboratiVAS.Field()

    # create_procedura_avvio = avvio.CreateProceduraAvvio.Field()
    update_procedura_avvio = avvio.UpdateProceduraAvvio.Field()
    avvia_piano = avvio.AvvioPiano.Field()
    contributi_tecnici = avvio.ContributiTecnici.Field()
    invio_protocollo_genio_civile = avvio.InvioProtocolloGenioCivile.Field()
    richiesta_integrazioni = avvio.RichiestaIntegrazioni.Field()
    integrazioni_richieste = avvio.IntegrazioniRichieste.Field()
    richiesta_conferenza_copianificazione = avvio.RichiestaConferenzaCopianificazione.Field()
    chiusura_conferenza_copianificazione = avvio.ChiusuraConferenzaCopianificazione.Field()
    formazione_del_piano = avvio.FormazionePiano.Field()

    create_procedura_adozione = adozione.CreateProceduraAdozione.Field()
    update_procedura_adozione = adozione.UpdateProceduraAdozione.Field()
    trasmissione_adozione = adozione.TrasmissioneAdozione.Field()
    trasmissione_osservazioni = adozione.TrasmissioneOsservazioni.Field()
    controdeduzioni = adozione.Controdeduzioni.Field()
    piano_controdedotto = adozione.PianoControdedotto.Field()
    esito_conferenza_paesaggistica = adozione.EsitoConferenzaPaesaggistica.Field()
    revisione_conferenza_paesaggistica = adozione.RevisionePianoPostConfPaesaggistica.Field()

    invio_pareri_adozione_vas = adozione.InvioPareriAdozioneVAS.Field()
    invio_parere_motivato_ac = adozione.InvioParereMotivatoAC.Field()
    upload_elaborati_adozione_vas = adozione.UploadElaboratiAdozioneVAS.Field()

    create_procedura_approvazione = approvazione.CreateProceduraApprovazione.Field()
    update_procedura_approvazione = approvazione.UpdateProceduraApprovazione.Field()
    trasmissione_approvazione = approvazione.TrasmissioneApprovazione.Field()
    esito_conferenza_paesaggistica_ap = approvazione.EsitoConferenzaPaesaggisticaAP.Field()
    pubblicazione_approvazione = approvazione.PubblicazioneApprovazione.Field()
    attribuzione_conformita_pit = approvazione.AttribuzioneConformitaPIT.Field()

    create_procedura_pubblicazione = pubblicazione.CreateProceduraPubblicazione.Field()
    update_procedura_pubblicazione = pubblicazione.UpdateProceduraPubblicazione.Field()
    pubblicazione_piano = pubblicazione.PubblicazionePiano.Field()

    upload = uploads.UploadFile.Field()
    delete_risorsa = uploads.DeleteRisorsa.Field()
    upload_risorsa_vas = uploads.UploadRisorsaVAS.Field()
    delete_risorsa_vas = uploads.DeleteRisorsaVAS.Field()
    upload_risorsa_avvio = uploads.UploadRisorsaAvvio.Field()
    delete_risorsa_avvio = uploads.DeleteRisorsaAvvio.Field()
    upload_risorsa_adozione = uploads.UploadRisorsaAdozione.Field()
    delete_risorsa_adozione = uploads.DeleteRisorsaAdozione.Field()
    upload_risorsa_adozione_vas = uploads.UploadRisorsaAdozioneVAS.Field()
    delete_risorsa_adozione_vas = uploads.DeleteRisorsaAdozioneVAS.Field()
    upload_risorsa_approvazione = uploads.UploadRisorsaApprovazione.Field()
    delete_risorsa_approvazione = uploads.DeleteRisorsaApprovazione.Field()
    upload_risorsa_pubblicazione = uploads.UploadRisorsaPubblicazione.Field()
    delete_risorsa_pubblicazione = uploads.DeleteRisorsaPubblicazione.Field()
    upload_risorsa_copianificazione = uploads.UploadRisorsaCopianificazione.Field()
    delete_risorsa_copianificazione = uploads.DeleteRisorsaCopianificazione.Field()
    upload_risorsa_piano_controdedotto = uploads.UploadRisorsaPianoControdedotto.Field()
    delete_risorsa_piano_controdedotto = uploads.DeleteRisorsaPianoControdedotto.Field()
    upload_risorsa_piano_rev_post_cp = uploads.UploadRisorsaPianoRevPostCP.Field()
    delete_risorsa_piano_rev_post_cp = uploads.DeleteRisorsaPianoRevPostCP.Field()
