import logging

import json
import os
import datetime
from collections import Counter

from django.test import Client

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
    ElaboratoCartografico, LottoCartografico,
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


class CartoTest(AbstractSerapideProcsTest):

    def test_carto_errori_shape(self):

        descr = "Piano per test cartografia [{dt}]".format(dt=_get_datetime())

        self.do_login()
        self.create_piano_and_promote(TipologiaVAS.VERIFICA, descr=descr)
        self.avvio_piano(TipologiaCopianificazione.NECESSARIA)

        self.vas_verifica_no_assoggettamento()

        self.contributi_tecnici()
        self.copianificazione(TipologiaCopianificazione.NECESSARIA, False)

        self.genio_civile()

        self.check_fase(Fase.ANAGRAFICA)

        self.formazione_piano()

        self.check_fase(Fase.AVVIO)

        # carto check here!
        self.trasmissione_adozione_carto_errori_shape()

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

    def trasmissione_adozione_carto_errori_shape(self):
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
        self.assertEqual(az_carto.stato, StatoAzione.FALLITA)

        az_ado: Azione = piano.azioni(TipologiaAzione.trasmissione_adozione).get()
        self.assertEqual(az_ado.stato, StatoAzione.NECESSARIA)

        report = AzioneReport.objects.filter(azione=az_carto, tipo=TipoReportAzione.ERR).get()
        self.assertTrue('CRS non consentito' in report.messaggio)

        # cleanup
        for uuid in [u1]:
            self.sendCXX('003d_delete_risorsa.query', 'DELETE RISORSA', self.codice_piano, 'codice_risorsa', uuid)

        # zip with bad shape names
        u1,_,_ = self.upload('804_adozione_upload_file.query', self.codice_adozione,
                    TipoRisorsa.DISCIPLINA_INSEDIAMENTI,
                    datafile='assetti_3003.zip')

        self.sendCNV('052_trasmissione_adozione.query', 'TRASMISSIONE ADOZIONE', self.codice_adozione)

        az_carto: Azione = piano.azioni(TipologiaAzione.validazione_cartografia_adozione).get()
        self.assertEqual(az_carto.stato, StatoAzione.FALLITA)

        az_ado: Azione = piano.azioni(TipologiaAzione.trasmissione_adozione).get()
        self.assertEqual(az_ado.stato, StatoAzione.NECESSARIA)

        report = AzioneReport.objects.filter(azione=az_carto, tipo=TipoReportAzione.ERR).first()
        self.assertTrue('Shapefile inaspettato' in report.messaggio)

        # cleanup
        for uuid in [u1]:
            self.sendCXX('003d_delete_risorsa.query', 'DELETE RISORSA', self.codice_piano, 'codice_risorsa', uuid)

        # good shapefile
        u1,_,_ = self.upload('804_adozione_upload_file.query', self.codice_adozione,
                    TipoRisorsa.ASSETTI_INSEDIATIVI,
                    datafile='assetti_3003.zip')

        self.sendCNV('052_trasmissione_adozione.query', 'TRASMISSIONE ADOZIONE', self.codice_adozione)

        az_carto: Azione = piano.azioni(TipologiaAzione.validazione_cartografia_adozione).get()
        self.assertEqual(az_carto.stato, StatoAzione.ESEGUITA)

        az_ado: Azione = piano.azioni(TipologiaAzione.trasmissione_adozione).get()
        self.assertEqual(az_ado.stato, StatoAzione.ESEGUITA)

        az_ingest: Azione = piano.azioni(TipologiaAzione.ingestione_cartografia_adozione).get()
        self.assertTrue(az_ingest.stato in [StatoAzione.NECESSARIA, StatoAzione.FALLITA])

        report = AzioneReport.objects.filter(azione=az_carto, tipo=TipoReportAzione.ERR).first()
        self.assertIsNone(report)

        self.assertEqual(1, Piano.objects.count())
        self.assertEqual(1, LottoCartografico.objects.count())
        self.assertEqual(2, ElaboratoCartografico.objects.count())

        logger.warning('===== GEO SEARCH ALL -- anonymous')
        anon_client = Client()
        response = anon_client.get("/serapide/geo/map/search",content_type = "application/json")
        content = json.loads(response.content)
        self.assertEqual(0, content['totalCount'])

        logger.warning('===== GEO SEARCH ALL')
        response = self._client.get("/serapide/geo/map/search", content_type = "application/json")
        content = json.loads(response.content)
        print(json.dumps(content, indent=4))
        self.assertEqual(1, content['totalCount'])

        search_by = "test carto"

        logger.warning('===== GEO SEARCH BY {} -- anonymous'.format(search_by))
        response = anon_client.get("/serapide/geo/map/search?q={}".format(search_by),content_type = "application/json")
        content = json.loads(response.content)
        self.assertEqual(0, content['totalCount'])

        logger.warning('===== GEO SEARCH BY {}'.format(search_by))
        response = self._client.get(
                                    # "/serapide/geo/map/search",
                                    "/serapide/geo/map/search?q={}".format(search_by),
                                    content_type = "application/json"
                                    )
        content = json.loads(response.content)
        print(json.dumps(content, indent=4))
        self.assertEqual(1, content['totalCount'])

        logger.warning('===== GEO GET MAP')
        response = self._client.get("/serapide/geo/map/{}".format(self.codice_piano),content_type = "application/json")
        logger.warning('GEO GET {} {}'.format(response, response.content))
        content = json.dumps(json.loads(response.content), indent=4)
        print(content)

        logger.warning('===== GEO GET MAP -- anonymous')
        response = anon_client.get("/serapide/geo/map/{}".format(self.codice_piano),content_type = "application/json")
        logger.warning('GEO GET {} {}'.format(response, response.content))
        content = json.loads(response.content)
        print(json.dumps(content, indent=4))
        self.assertTrue(content['err'])

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

    def test_map_search(self):

        self.do_login()

        for d in ('AAAZ', 'aaaZ', 'ABBB', 'BBB', 'ZZZ' ):
            self.create_piano_and_promote(TipologiaVAS.VERIFICA, descr=d)

        response = self._client.get(
                                    "/serapide/geo/map/search?q={}&include_empty=1".format('A'),
                                    content_type = "application/json"
                                    )
        logger.warning('GEO SEARCH {} {}'.format(response, response.content))
        content = json.loads(response.content)
        print(json.dumps(content, indent=4))
        self.assertEqual(3, content['totalCount'])

        response = self._client.get(
                                    "/serapide/geo/map/search?page=2&limit=2&include_empty=1",
                                    content_type = "application/json"
                                    )
        logger.warning('GEO SEARCH {} {}'.format(response, response.content))
        content = json.loads(response.content)
        print(json.dumps(content, indent=4))
        self.assertEqual(5, content['totalCount'])
        self.assertEqual(2, len(content['results']))

    def test_flow_vasno_ccsiirno_form(self):

        self.do_login()
        self.create_piano_and_promote(TipologiaVAS.NON_NECESSARIA)
        self.avvio_piano(TipologiaCopianificazione.NECESSARIA)

        # self.vas_verifica_no_assoggettamento()

        self.contributi_tecnici()
        self.copianificazione(TipologiaCopianificazione.NECESSARIA, False)

        self.genio_civile()

        self.check_fase(Fase.ANAGRAFICA)

        self.formazione_piano()

        self.check_fase(Fase.AVVIO)

        self.trasmissione_adozione()
        self.adozione_osservazione(richiesta_cp=True)

        lotti = LottoCartografico.objects.count()
        self.assertEqual(3, lotti)

        response = self._client.get("/serapide/geo/map/search", content_type = "application/json")
        logger.warning('GEO SEARCH {} {}'.format(response, response.content))
        content = json.loads(response.content)
        print(json.dumps(content, indent=4))
        self.assertEqual(1, content['totalCount'])

        #
        # self.check_fase(Fase.ADOZIONE)
        #
        # self.approvazione()
        # self.check_fase(Fase.APPROVAZIONE)
        #
        # self.pubblicazione()
        #
        # self.check_fase(Fase.APPROVAZIONE)
