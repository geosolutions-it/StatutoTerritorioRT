import logging

import json
import os
import datetime
from collections import Counter

from serapide_core.modello.enums import (
    TipoRisorsa,
    TipologiaVAS,
    TipologiaCopianificazione,
    Fase,
    TipologiaAzione,
    StatoAzione,
    TipoReportAzione,
)

from serapide_core.modello.models import (
    Piano,
    Delega,
    Azione,
    AzioneReport,
    ElaboratoCartografico,
)

from strt_users.enums import (
    Qualifica,
)

from .test_data_setup import DataLoader
from .test_serapide_abs import AbstractSerapideTest, dump_result
from .test_serapide_proc import AbstractSerapideProcsTest
from ..api.auth.user import get_UffAssTok

logger = logging.getLogger(__name__)

this_path = os.path.dirname(__file__)


def _get_datetime(**argw_delta):
    date = datetime.datetime.now()
    date = date.replace(microsecond=0)
    if argw_delta:
        date = date + datetime.timedelta(**argw_delta)
    return date


def _get_date(**argw_delta):
    date = _get_datetime(**argw_delta)
    date = date.replace(hour=0, minute=0, second=0, microsecond=0)
    return date


class MiscTest(AbstractSerapideProcsTest):

    def test_delete_piano(self):

        self.do_login()

        # self.create_piano_and_promote(TipologiaVAS.VERIFICA)
        response = self.create_piano(DataLoader.IPA_FI)

        content = json.loads(response.content)
        self.codice_piano = content['data']['createPiano']['nuovoPiano']['codice']
        self.codice_vas = content['data']['createPiano']['nuovoPiano']['proceduraVas']['uuid']
        self.codice_avvio = content['data']['createPiano']['nuovoPiano']['proceduraAvvio']['uuid']

        now = _get_datetime()

        for nome, val in [
            ("dataDelibera", now.isoformat()),
            ("descrizione", "Piano di test - Eliminazione Piano"),
            ("soggettoProponenteUuid", DataLoader.uffici_stored[DataLoader.IPA_FI][DataLoader.UFF1].uuid.__str__())
        ]:
            self.sendCNV('002_update_piano.query', 'UPDATE PIANO', self.codice_piano, nome, val)

        self.upload('800_upload_file.query', self.codice_piano, TipoRisorsa.DELIBERA)

        self.sendCNV('004_update_procedura_vas.query', 'UPDATE VAS', self.codice_vas, 'tipologia', TipologiaVAS.VERIFICA.name)
        self.upload('005_vas_upload_file.query', self.codice_vas, TipoRisorsa.DOCUMENTO_PRELIMINARE_VERIFICA_VAS)

        sogg_op = []
        for ente, uff, q in [
            (DataLoader.IPA_RT, DataLoader.UFF_GC_TN, Qualifica.GC),
            (DataLoader.IPA_RT, DataLoader.UFF_PIAN, Qualifica.PIAN),
            (DataLoader.IPA_PI, DataLoader.UFF1, Qualifica.AC),
            (DataLoader.IPA_LU, DataLoader.UFF1, Qualifica.SCA),
        ]:
            sogg_op.append({
                'ufficioUuid': DataLoader.uffici_stored[ente][uff].uuid.__str__(),
                'qualifica': q.name})

        self.sendCNV('002_update_piano.query', 'UPDATE PIANO', self.codice_piano, "soggettiOperanti", sogg_op)

        piano = Piano.objects.get(codice=self.codice_piano)
        self.assertIsNotNone(piano)

        for req, uff_expected, ass_expected in [
            ([Qualifica.AC,],
                [DataLoader.uffici_stored[DataLoader.IPA_PI][DataLoader.UFF1],],
                [DataLoader.utenti_stored[DataLoader.FC_AC1],]),
            ([Qualifica.SCA,],
                [DataLoader.uffici_stored[DataLoader.IPA_LU][DataLoader.UFF1],],
                [DataLoader.utenti_stored[DataLoader.FC_ACTIVE2],
                 DataLoader.utenti_stored[DataLoader.FC_SCA1],
                ]),
            ([Qualifica.AC, Qualifica.SCA,],
                [DataLoader.uffici_stored[DataLoader.IPA_PI][DataLoader.UFF1],
                 DataLoader.uffici_stored[DataLoader.IPA_LU][DataLoader.UFF1],],
                [DataLoader.utenti_stored[DataLoader.FC_AC1],
                 DataLoader.utenti_stored[DataLoader.FC_ACTIVE2],
                 DataLoader.utenti_stored[DataLoader.FC_SCA1],
                ]),
            ([Qualifica.OPCOM, ],
             [DataLoader.uffici_stored[DataLoader.IPA_FI][DataLoader.UFF1], ],
             [DataLoader.utenti_stored[DataLoader.FC_RUP_RESP], ]),
        ]:
            uff, ass, tok = get_UffAssTok(piano, req)
            self.assertEqual(len(uff_expected), len(uff), 'Numero uffici non corretto per qualifiche {}'.format(req))
            self.assertEqual(len(ass_expected), len(ass), 'Numero assegnatari non corretto')

            self.assertEqual(uff_expected, uff, 'Lista Uffici non corretta')
            self.assertEqual(Counter(ass_expected), Counter(ass), 'Lista assegnatari non corretta')

        # # Crea Delega
        # client = Client()
        # self.assertTrue(client.login(username=DataLoader.FC_DELEGATO, password='42'), "Error in login - DELEGATO")
        # key = self.get_delega(self.codice_piano, Qualifica.GC, 'CREA DELEGA GC by RESP')
        # self.bind_delega(client, key)
        # self.assertEqual(1, Token.objects.all().count(), 'Token non creato')
        # self.assertEqual(1, Delega.objects.all().count(), 'Delega non creata')
        #
        # self.sendCNV('001d_delete_piano.query', 'DELETE PIANO', self.codice_piano,
        #              client=self.client_sca, expected_code=403)
        # self.sendCNV('001d_delete_piano.query', 'DELETE PIANO', self.codice_piano)
        #
        # self.assertEqual(0, Token.objects.all().count(), 'Token non eliminato')
        # self.assertEqual(0, Delega.objects.all().count(), 'Delega non eliminata')

    def test_carto(self):

        self.do_login()
        self.create_piano_and_promote(TipologiaVAS.VERIFICA)
        self.avvio_piano(TipologiaCopianificazione.NECESSARIA)

        self.vas_verifica_no_assoggettamento()

        self.contributi_tecnici()
        self.copianificazione(TipologiaCopianificazione.NECESSARIA, False)

        self.genio_civile()

        self.check_fase(Fase.ANAGRAFICA)

        self.formazione_piano()

        self.check_fase(Fase.AVVIO)

        # carto check here!
        self.trasmissione_adozione_carto()

        # self.adozione_osservazione(richiesta_cp=False)
        #
        # self.check_fase(Fase.AVVIO)
        # self.adozione_vas()
        # self.check_fase(Fase.ADOZIONE)
        #
        # self.approvazione()
        # self.check_fase(Fase.APPROVAZIONE)
        #
        # self.pubblicazione()

    def trasmissione_adozione_carto(self):
        response = self.sendCNV('903_get_adozione.query', 'GET ADOZIONE', self.codice_piano)
        content = json.loads(response.content)
        self.codice_adozione = content['data']['modello']['edges'][0]['node']['uuid']

        for nome, val in [
                ("compilazioneRapportoAmbientaleUrl", 'http://compilazioneRapportoAmbientaleUrl'),
                ("conformazionePitPprUrl", 'http://conformazionePitPprUrl'),
                ("monitoraggioUrbanisticoUrl", 'http://monitoraggioUrbanisticoUrl')]:
            self.sendCNV('002_update_piano.query', 'UPDATE PIANO', self.codice_piano, nome, val)

        self.upload('804_adozione_upload_file.query', self.codice_adozione, TipoRisorsa.DELIBERA_ADOZIONE)

        self.sendCNV('051_update_procedura_adozione.query', 'UPDATE ADOZIONE', self.codice_adozione, 'dataDeliberaAdozione', _get_date().isoformat())
        self.sendCNV('051_update_procedura_adozione.query', 'UPDATE ADOZIONE', self.codice_adozione, 'pubblicazioneBurtData', _get_date().isoformat())

        uploads = {}

        for tipo in [
                TipoRisorsa.RELAZIONE_GENERALE,
                TipoRisorsa.DISCIPLINA_PIANO,
                TipoRisorsa.RELAZIONE_RESPONSABILE,
                TipoRisorsa.RELAZIONE_GARANTE_INFORMAZIONE_PARTECIPAZIONE,
                TipoRisorsa.VALUTAZIONE,
                TipoRisorsa.ELABORATI_CONFORMAZIONE,
                TipoRisorsa.PIANI_ATTUATIVI_BP,
                TipoRisorsa.INDAGINI_G_I_S]:
            self.upload('804_adozione_upload_file.query', self.codice_adozione, tipo)

        for tipo in [
                TipoRisorsa.SUPPORTO_PREVISIONI_P_C,
                TipoRisorsa.DISCIPLINA_INSEDIAMENTI,
                TipoRisorsa.ASSETTI_INSEDIATIVI,]:
            uuid,_,_ = self.upload('804_adozione_upload_file.query', self.codice_adozione, tipo, suffix='.zip')
            uploads[tipo] = uuid

        self.sendCNV('052_trasmissione_adozione.query', 'TRASMISSIONE ADOZIONE', self.codice_adozione)

        # we sent invalid zip files:
        piano = Piano.objects.filter(codice=self.codice_piano).get()
        az_carto: Azione = piano.azioni(TipologiaAzione.validazione_cartografia_adozione).get()
        self.assertIsNotNone(az_carto)
        self.assertIsNotNone(az_carto.data)
        self.assertEqual(az_carto.stato, StatoAzione.FALLITA)

        az_ado: Azione = piano.azioni(TipologiaAzione.trasmissione_adozione).get()
        self.assertIsNotNone(az_ado)
        self.assertEqual(az_ado.stato, StatoAzione.NECESSARIA)

        reports = AzioneReport.objects.filter(azione=az_carto)
        for report in reports:
            self.assertTrue("Errore nell'estrazione" in report.messaggio)

        # cleanup
        for tipo in [
                TipoRisorsa.SUPPORTO_PREVISIONI_P_C,
                TipoRisorsa.DISCIPLINA_INSEDIAMENTI,
                TipoRisorsa.ASSETTI_INSEDIATIVI,]:
            self.sendCXX('003d_delete_risorsa.query', 'DELETE RISORSA', self.codice_piano,
                         'codice_risorsa', uploads[tipo],
                         extra_title=uploads[tipo])

        # risorsa doppia
        u1,_,_ = self.upload('804_adozione_upload_file.query', self.codice_adozione, TipoRisorsa.ASSETTI_INSEDIATIVI, suffix='.zip')
        u2,_,_ = self.upload('804_adozione_upload_file.query', self.codice_adozione, TipoRisorsa.ASSETTI_INSEDIATIVI, suffix='.zip')
        self.sendCNV('052_trasmissione_adozione.query', 'TRASMISSIONE ADOZIONE', self.codice_adozione)

        az_ado: Azione = piano.azioni(TipologiaAzione.trasmissione_adozione).get()
        self.assertIsNotNone(az_ado)
        self.assertEqual(az_ado.stato, StatoAzione.NECESSARIA)

        report = AzioneReport.objects.filter(azione=az_carto, tipo=TipoReportAzione.ERR).get()
        self.assertTrue('Troppe risorse' in report.messaggio)

        # cleanup
        for uuid in [u1, u2,]:
            self.sendCXX('003d_delete_risorsa.query', 'DELETE RISORSA', self.codice_piano, 'codice_risorsa', uuid)

        # zip with proper file names but bad shp
        u1,_,_ = self.upload('804_adozione_upload_file.query', self.codice_adozione,
                    TipoRisorsa.ASSETTI_INSEDIATIVI,
                    datafile='bad_content.zip')

        self.sendCNV('052_trasmissione_adozione.query', 'TRASMISSIONE ADOZIONE', self.codice_adozione)

        az_ado: Azione = piano.azioni(TipologiaAzione.trasmissione_adozione).get()
        self.assertIsNotNone(az_ado)
        self.assertEqual(az_ado.stato, StatoAzione.NECESSARIA)

        report = AzioneReport.objects.filter(azione=az_carto, tipo=TipoReportAzione.ERR).get()
        self.assertTrue('rrore lettura shp' in report.messaggio)

        # cleanup
        for uuid in [u1]:
            self.sendCXX('003d_delete_risorsa.query', 'DELETE RISORSA', self.codice_piano, 'codice_risorsa', uuid)

        # shapefile with wrong CRS
        u1,_,_ = self.upload('804_adozione_upload_file.query', self.codice_adozione,
                    TipoRisorsa.ASSETTI_INSEDIATIVI,
                    datafile='RT_sempl_4326.zip')

        self.sendCNV('052_trasmissione_adozione.query', 'TRASMISSIONE ADOZIONE', self.codice_adozione)

        az_carto: Azione = piano.azioni(TipologiaAzione.validazione_cartografia_adozione).get()
        self.assertIsNotNone(az_carto.data)
        self.assertEqual(az_carto.stato, StatoAzione.FALLITA)

        az_ado: Azione = piano.azioni(TipologiaAzione.trasmissione_adozione).get()
        self.assertIsNotNone(az_ado)
        self.assertEqual(az_ado.stato, StatoAzione.NECESSARIA)

        report = AzioneReport.objects.filter(azione=az_carto, tipo=TipoReportAzione.ERR).get()
        self.assertTrue('CRS non consentito' in report.messaggio)

        # cleanup
        for uuid in [u1]:
            self.sendCXX('003d_delete_risorsa.query', 'DELETE RISORSA', self.codice_piano, 'codice_risorsa', uuid)

        # good shapefile
        u1,_,_ = self.upload('804_adozione_upload_file.query', self.codice_adozione,
                    TipoRisorsa.ASSETTI_INSEDIATIVI,
                    datafile='RT_sempl_3003.zip')

        self.sendCNV('052_trasmissione_adozione.query', 'TRASMISSIONE ADOZIONE', self.codice_adozione)

        az_carto: Azione = piano.azioni(TipologiaAzione.validazione_cartografia_adozione).get()
        self.assertIsNotNone(az_carto.data)
        self.assertEqual(az_carto.stato, StatoAzione.ESEGUITA)

        az_ado: Azione = piano.azioni(TipologiaAzione.trasmissione_adozione).get()
        self.assertIsNotNone(az_ado)
        self.assertEqual(az_ado.stato, StatoAzione.ESEGUITA)

        report = AzioneReport.objects.filter(azione=az_carto, tipo=TipoReportAzione.ERR).first()
        self.assertIsNone(report)

        elaborati = ElaboratoCartografico.objects.all()
        self.assertEqual(2, len(elaborati))

        response = self._client.get(
                                    "/serapide/geo/map/search?q={}".format(self.codice_piano[0:3]),
                                    content_type = "application/json"
                                    )
        logger.warning('GEO SEARCH {} {}'.format(response, response.content))

        content = json.dumps(json.loads(response.content), indent=4)
        print(content)


        response = self._client.get(
                                    "/serapide/geo/map/{}".format(self.codice_piano),
                                    content_type = "application/json"
                                    )
        logger.warning('GEO GET {} {}'.format(response, response.content))

        content = json.dumps(json.loads(response.content), indent=4)
        print(content)


        #
        # response = self.client.post(
        #     self.GRAPHQL_URL,
        #     query,
        #     content_type="application/json",
        #     # **headers
        # )

        # for nome, val in [
        #         ("pubblicazioneBurtUrl", 'http://pubblicazioneBurtUrl'),
        #         ("pubblicazioneSitoUrl", 'http://pubblicazioneSitoUrl'),
        #         ("pubblicazioneBurtBollettino", 'test di numero bollettino burt'),
        # ]:
        #     self.sendCNV('051_update_procedura_adozione.query', 'UPDATE ADOZIONE', self.codice_adozione, nome, val)
        #
        # self.sendCNV('201_pubblicazione_burt.query', 'PUBBLICAZIONE BURT', self.codice_adozione)