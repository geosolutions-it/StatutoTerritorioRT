import logging

import json
import os
import datetime


from django.test import TestCase, Client

from serapide_core.modello.enums import (
    TipoRisorsa,
    TipologiaVAS,
    TipologiaCopianificazione,
    Fase,
)

from strt_users.enums import (
    Qualifica,
)

from .test_data_setup import DataLoader
from .test_serapide_abs import AbstractSerapideTest, dump_result

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


class AbstractSerapideProcsTest(AbstractSerapideTest):

    def do_login(self):
        print("LOGIN  ====================")
        logged = True
        logged = self._client.login(username=DataLoader.FC_RUP_RESP, password='42')

        self.assertTrue(logged, "Error in login")

        self.client_ac = Client()
        self.client_sca = Client()
        self.client_gc = Client()
        self.client_pian = Client()

        self.assertTrue(self.client_ac.login(username=DataLoader.FC_AC1, password='42'), "Error in login - AC")
        self.assertTrue(self.client_sca.login(username=DataLoader.FC_SCA1, password='42'), "Error in login - SCA")
        self.assertTrue(self.client_gc.login(username=DataLoader.FC_GC1, password='42'), "Error in login - GC")
        self.assertTrue(self.client_pian.login(username=DataLoader.FC_PIAN, password='42'), "Error in login - PIAN")

        print("GET_PROFILES ====================")
        response = self._client.get(self.GET_PROFILES_URL)
        self.assertEqual(200, response.status_code, 'GET PROFILES failed')

    def create_piano_and_promote(self, tipovas:TipologiaVAS):
        response = self.create_piano(DataLoader.IPA_FI)

        content = json.loads(response.content)
        self.codice_piano = content['data']['createPiano']['nuovoPiano']['codice']
        self.codice_vas = content['data']['createPiano']['nuovoPiano']['proceduraVas']['uuid']
        self.codice_avvio = content['data']['createPiano']['nuovoPiano']['proceduraAvvio']['uuid']

        now = _get_datetime()

        for nome, val in [
            ("dataDelibera", now.isoformat()),
            ("descrizione", "Piano di test - VAS {vas} [{dt}]".format(dt=now, vas=tipovas.name)),
            ("soggettoProponenteUuid", DataLoader.uffici_stored[DataLoader.IPA_FI][DataLoader.UFF1].uuid.__str__())
        ]:
            self.sendCNV('002_update_piano.query', 'UPDATE PIANO', self.codice_piano, nome, val)

        self.upload('003_upload_file.query', self.codice_piano, TipoRisorsa.DELIBERA)

        self.sendCNV('004_update_procedura_vas.query', 'UPDATE VAS', self.codice_vas, 'tipologia', tipovas.value)
        self.upload('005_vas_upload_file.query', self.codice_vas, TipoRisorsa.VAS_VERIFICA)

        sogg_op = []
        sogg_op.append({
            'ufficioUuid': DataLoader.uffici_stored[DataLoader.IPA_RT][DataLoader.UFF_GC_TN].uuid.__str__(),
            'qualifica': Qualifica.GC.name})
        sogg_op.append({
            'ufficioUuid': DataLoader.uffici_stored[DataLoader.IPA_RT][DataLoader.UFF_PIAN].uuid.__str__(),
            'qualifica': Qualifica.PIAN.name})
        sogg_op.append({
            'ufficioUuid': DataLoader.uffici_stored[DataLoader.IPA_PI][DataLoader.UFF1].uuid.__str__(),
            'qualifica': Qualifica.AC.name})
        sogg_op.append({
            'ufficioUuid': DataLoader.uffici_stored[DataLoader.IPA_LU][DataLoader.UFF1].uuid.__str__(),
            'qualifica': Qualifica.SCA.name})

        self.sendCNV('002_update_piano.query', 'UPDATE PIANO', self.codice_piano, "soggettiOperanti", sogg_op)
        self.sendCNV('006_promozione.query', 'PROMUOVI PIANO', self.codice_piano)

    def avvio_piano(self, copianificazione:TipologiaCopianificazione):
        avvio_scadenza = _get_date(days=10)

        for nome, val in [
            ('dataScadenzaRisposta', avvio_scadenza.isoformat()),
            ('garanteNominativo', 'pippo'),
            ('garantePec', 'pippo@pec.pec'),
            ('conferenzaCopianificazione', copianificazione.name), # questo modifica la sequenza in CC
        ]:
            self.sendCNV('010_update_procedura_avvio.query', 'UPDATE AVVIO', self.codice_avvio, nome, val, extra_title=nome)

        for tipo in [
            TipoRisorsa.OBIETTIVI_PIANO,
            TipoRisorsa.QUADRO_CONOSCITIVO,
            TipoRisorsa.PROGRAMMA_ATTIVITA,
            TipoRisorsa.INDIVIDUAZIONE_GARANTE_INFORMAZIONE,
        ]:
            self.upload('011_avvio_upload_file.query', self.codice_avvio, tipo)

        # self.update_piano(codice_piano, "numeroProtocolloGenioCivile", "1234567890", expected_code=403)
        # self.update_piano(codice_piano, "numeroProtocolloGenioCivile", "1234567890", client=client_gc)
        self.sendCNV('012_avvio_piano.query', 'AVVIO PIANO', self.codice_avvio)

    def vas_verifica_no_assoggettamento(self):
        # {"operationName": "UpdateProceduraVas", "variables": {"input": {"proceduraVas": {"assoggettamento": false},
        self.sendCNV('004_update_procedura_vas.query', 'UPDATE VAS', self.codice_vas, 'assoggettamento', False)

        # SCA
        self.upload('005_vas_upload_file.query', self.codice_vas, TipoRisorsa.PARERE_VERIFICA_VAS)
        self.send('013_invio_pareri_verifica.query', 'INVIO PARERE VERIFICA', replace_args={'codice': self.codice_vas}, expected_code=403)
        self.send('013_invio_pareri_verifica.query', 'INVIO PARERE VERIFICA', replace_args={'codice': self.codice_vas}, client=self.client_sca)

        # AC
        self.upload('005_vas_upload_file.query', self.codice_vas, TipoRisorsa.PROVVEDIMENTO_VERIFICA_VAS)
        self.send('014_provvedimento_verifica_vas.query', 'PROVVEDIMENTO VERIFICA VAS', replace_args={'codice': self.codice_vas}, expected_code=403)
        self.send('014_provvedimento_verifica_vas.query', 'PROVVEDIMENTO VERIFICA VAS', replace_args={'codice': self.codice_vas}, client=self.client_ac)

        # self.sendCNV('004_update_procedura_vas.query', 'UPDATE VAS', self.codice_vas, 'pubblicazioneProvvedimentoVerificaAc', "https://dev.serapide.geo-solutions.it/serapide", expected_code=403)
        self.sendCNV('004_update_procedura_vas.query', 'UPDATE VAS', self.codice_vas, 'pubblicazioneProvvedimentoVerificaAc', "https://dev.serapide.geo-solutions.it/serapide", client=self.client_ac)

        self.sendCNV('004_update_procedura_vas.query', 'UPDATE VAS', self.codice_vas, 'pubblicazioneProvvedimentoVerificaAp', "https://dev.serapide.geo-solutions.it/serapide")

        # VAS COMPLETATO
        response = self.sendCNV('901_get_vas.query', 'GET VAS', self.codice_piano)
        content = json.loads(response.content)
        vas_conclusa = content['data']['modello']['edges'][0]['node']['conclusa']
        self.assertTrue(vas_conclusa, 'VAS non conclusa')

    def contributi_tecnici(self):
        self.sendCNV('902_get_avvio.query', 'GET AVVIO', self.codice_piano)
        self.upload('011_avvio_upload_file.query', self.codice_avvio, TipoRisorsa.CONTRIBUTI_TECNICI)
        self.sendCNV('015_contributi_tecnici.query', 'CONTRIBUTI TECNICI', self.codice_avvio, expected_code=403)
        self.sendCNV('015_contributi_tecnici.query', 'CONTRIBUTI TECNICI', self.codice_avvio, client=self.client_pian) # questo crea le azioni di CC

    def copianificazione(self, tipo:TipologiaCopianificazione, richiedi_integrazioni:bool):

        if tipo == TipologiaCopianificazione.NON_NECESSARIA:
            return

        response = self.sendCNV('021_get_cc.query', 'GET CONF COP', self.codice_piano)
        content = json.loads(response.content)
        codice_cc = content['data']['modello']['edges'][0]['node']['uuid']

        if tipo == TipologiaCopianificazione.POSTICIPATA:
            self.sendCNV('020_richiesta_cc.query', 'RICHIESTA CONF COP', self.codice_avvio)

        self.upload('022_conferenza_upload_file.query', codice_cc, TipoRisorsa.ELABORATI_CONFERENZA)
        self.sendCNV('023_chiusura_cc.query', 'CHIUSURA CONF COP', self.codice_avvio, expected_code=403)
        self.sendCNV('023_chiusura_cc.query', 'CHIUSURA CONF COP', self.codice_avvio, client=self.client_pian)

        self.sendCNV('024_richiesta_integrazioni.query', 'RICHIESTA INT NO', self.codice_avvio, expected_code=403)

        # richiediamo integrazioni!
        self.sendCNV('010_update_procedura_avvio.query', 'UPDATE AVVIO', self.codice_avvio, 'messaggioIntegrazione', 'msg integr', extra_title='integrazioni')
        self.sendCNV('010_update_procedura_avvio.query', 'UPDATE AVVIO', self.codice_avvio, 'richiestaIntegrazioni', richiedi_integrazioni, extra_title='richiestaIntegrazioni')
        self.sendCNV('024_richiesta_integrazioni.query', 'RICHIESTA INT', self.codice_avvio, client=self.client_pian)

        if richiedi_integrazioni:
            # le integrazioni sono state richieste, quindi serve chiudere "integrazioni richieste"
            # inviamo integrazioni
            self.upload('011_avvio_upload_file.query', self.codice_avvio, TipoRisorsa.INTEGRAZIONI)
            self.sendCNV('010_update_procedura_avvio.query', 'UPDATE AVVIO', self.codice_avvio, 'dataScadenzaRisposta',
                         _get_date(days=20).isoformat(), extra_title='dataScadenzaRisposta')
            self.sendCNV('025_integrazioni_richieste.query', 'INTEGRAZIONI RICH', self.codice_avvio)

    def genio_civile(self):
        self.sendCNV('002_update_piano.query', 'UPDATE PIANO', self.codice_piano, 'numeroProtocolloGenioCivile', 'prot_g_c', expected_code=403)
        self.sendCNV('002_update_piano.query', 'UPDATE PIANO', self.codice_piano, 'numeroProtocolloGenioCivile', 'prot_g_c', client=self.client_gc)
        self.sendCNV('030_invio_protocollo_genio_civile.query', 'INVIO PROT GC', self.codice_avvio, expected_code=403)
        self.sendCNV('030_invio_protocollo_genio_civile.query', 'INVIO PROT GC', self.codice_avvio, client=self.client_gc)

    def formazione_piano(self):
        self.upload('003_upload_file.query', self.codice_piano, TipoRisorsa.NORME_TECNICHE_ATTUAZIONE)
        self.sendCNV('040_formazione_piano.query', 'FORMAZIONE PIANO', self.codice_piano)

    ### ADOZIONE
    def trasmissione_adozione(self):
        response = self.sendCNV('903_get_adozione.query', 'GET ADOZIONE', self.codice_piano)
        content = json.loads(response.content)
        self.codice_adozione = content['data']['modello']['edges'][0]['node']['uuid']

        for nome, val in [
                ("compilazioneRapportoAmbientaleUrl", 'http://compilazioneRapportoAmbientaleUrl'),
                ("conformazionePitPprUrl", 'http://conformazionePitPprUrl'),
                ("monitoraggioUrbanisticoUrl", 'http://monitoraggioUrbanisticoUrl')]:
            self.sendCNV('002_update_piano.query', 'UPDATE PIANO', self.codice_piano, nome, val)

        self.upload('050_adozione_upload_file.query', self.codice_adozione, TipoRisorsa.DELIBERA_ADOZIONE)

        self.sendCNV('051_update_procedura_adozione.query', 'UPDATE ADOZIONE', self.codice_adozione, 'dataDeliberaAdozione', _get_date().isoformat())
        self.sendCNV('051_update_procedura_adozione.query', 'UPDATE ADOZIONE', self.codice_adozione, 'pubblicazioneBurtData', _get_date().isoformat())

        for tipo in [
                TipoRisorsa.RELAZIONE_GENERALE,
                TipoRisorsa.DISCIPLINA_PIANO,
                TipoRisorsa.RELAZIONE_RESPONSABILE,
                TipoRisorsa.RELAZIONE_GARANTE_INFORMAZIONE_PARTECIPAZIONE,
                TipoRisorsa.VALUTAZIONE,
                TipoRisorsa.ELABORATI_CONFORMAZIONE,
                TipoRisorsa.PIANI_ATTUATIVI_BP,
                TipoRisorsa.INDAGINI_G_I_S]:
            self.upload('050_adozione_upload_file.query', self.codice_adozione, tipo)

        for tipo in [
                TipoRisorsa.SUPPORTO_PREVISIONI_P_C,
                TipoRisorsa.DISCIPLINA_INSEDIAMENTI,
                TipoRisorsa.ASSETTI_INSEDIATIVI,]:
            self.upload('050_adozione_upload_file.query', self.codice_adozione, tipo, suffix='.zip')

        self.sendCNV('052_trasmissione_adozione.query', 'TRASMISSIONE ADOZIONE', self.codice_adozione)

    def adozione_osservazione(self, richiesta_cp: bool = True):
        self.upload('050_adozione_upload_file.query', self.codice_adozione, TipoRisorsa.OSSERVAZIONI_PRIVATI)
        self.sendCNV('053_trasmissione_osservazioni.query', 'TRASMISSIONE OSSERVAZIONI', self.codice_adozione)

        self.upload('050_adozione_upload_file.query', self.codice_adozione, TipoRisorsa.OSSERVAZIONI_ENTI)

        self.sendCNV('054_controdeduzioni.query', 'CONTRODEDUZIONI', self.codice_adozione)
        response = self.sendCNV('055_get_risorse_pcd.query', 'GET RISORSE PIANO CD', self.codice_piano)
        content = json.loads(response.content)
        self.codice_pcd = content['data']['modello']['edges'][0]['node']['uuid']

        for tipo in [
                TipoRisorsa.RELAZIONE_GENERALE,
                # TipoRisorsa.DISCIPLINA_PIANO,
                TipoRisorsa.RELAZIONE_RESPONSABILE,
                # TipoRisorsa.RELAZIONE_GARANTE_INFORMAZIONE_PARTECIPAZIONE,
                TipoRisorsa.VALUTAZIONE,
                # TipoRisorsa.ELABORATI_CONFORMAZIONE,
                # TipoRisorsa.PIANI_ATTUATIVI_BP,
                TipoRisorsa.INDAGINI_G_I_S]:
            self.upload('056_controdedotto_upload_file.query', self.codice_pcd, tipo)

        for tipo in [
                # TipoRisorsa.SUPPORTO_PREVISIONI_P_C,
                # TipoRisorsa.DISCIPLINA_INSEDIAMENTI,
                TipoRisorsa.ASSETTI_INSEDIATIVI, ]:
            self.upload('056_controdedotto_upload_file.query', self.codice_pcd, tipo, suffix='.zip')

        self.sendCNV('051_update_procedura_adozione.query', 'UPDATE ADOZIONE', self.codice_adozione, 'richiestaConferenzaPaesaggistica', richiesta_cp)
        self.sendCNV('057_piano_controdedotto.query', 'PIANO CONTRODEDOTTO', self.codice_adozione)

        if richiesta_cp:
            self.upload('050_adozione_upload_file.query', self.codice_adozione, TipoRisorsa.ELABORATI_CONF_P)
            self.sendCNV('058_esito_cp.query', 'ESITO CONF PAESGG', self.codice_adozione, expected_code=403)
            self.sendCNV('058_esito_cp.query', 'ESITO CONF PAESGG', self.codice_adozione, client=self.client_pian)

            response = self.sendCNV('059_piano_rev_post_cp.query', 'PIANO REV POST CP', self.codice_piano)
            content = json.loads(response.content)
            self.codice_rpcp = content['data']['modello']['edges'][0]['node']['uuid']
            for tipo in [
                    # TipoRisorsa.RELAZIONE_GENERALE,
                    TipoRisorsa.DISCIPLINA_PIANO,
                    # TipoRisorsa.RELAZIONE_RESPONSABILE,
                    TipoRisorsa.RELAZIONE_GARANTE_INFORMAZIONE_PARTECIPAZIONE,
                    # TipoRisorsa.VALUTAZIONE,
                    TipoRisorsa.ELABORATI_CONFORMAZIONE,
                    # TipoRisorsa.PIANI_ATTUATIVI_BP,
                    TipoRisorsa.INDAGINI_G_I_S]:
                self.upload('060_prcp_upload_file.query', self.codice_rpcp, tipo)

            for tipo in [
                    TipoRisorsa.SUPPORTO_PREVISIONI_P_C,
                    # TipoRisorsa.DISCIPLINA_INSEDIAMENTI,
                    TipoRisorsa.ASSETTI_INSEDIATIVI, ]:
                self.upload('060_prcp_upload_file.query', self.codice_rpcp, tipo, suffix='.zip')

        self.sendCNV('061_revisione_cp.query', 'REVISIONE CONF PAESGG', self.codice_adozione)

    def adozione_vas(self):
        response = self.sendCNV('062_adozione_vas.query', 'GET ADOZIONE VAS', self.codice_piano)
        content = json.loads(response.content)
        self.codice_adozione_vas = content['data']['modello']['edges'][0]['node']['uuid']

        self.upload('064_adozionevas_file_upload.query', self.codice_adozione_vas, TipoRisorsa.PARERE_ADOZIONE_SCA, client=self.client_sca)
        self.sendCNV('065_invio_pareri_adozione.query', 'INVIO_PARERI AD VAS', self.codice_adozione_vas, client=self.client_sca)

        self.upload('064_adozionevas_file_upload.query', self.codice_adozione_vas, TipoRisorsa.PARERE_MOTIVATO,
                    client=self.client_ac)
        self.sendCNV('066_invio_parere_m_ac.query', 'INVIO_PARERI AD AC', self.codice_adozione_vas, client=self.client_ac)

        self.upload('064_adozionevas_file_upload.query', self.codice_adozione_vas, TipoRisorsa.DOCUMENTO_SINTESI)
        self.upload('064_adozionevas_file_upload.query', self.codice_adozione_vas, TipoRisorsa.RAPPORTO_AMBIENTALE)
        self.sendCNV('067_up_elabo_adozione_vas.query', 'UP ELABORATO ADOZ VAS', self.codice_adozione_vas)

    def approvazione(self):
        response = self.sendCNV('904_get_approvazione.query', 'GET APPROVAZIONE', self.codice_piano)
        content = json.loads(response.content)
        self.codice_approvazione = content['data']['modello']['edges'][0]['node']['uuid']

        self.upload('070_approvazione_file_upload.query', self.codice_approvazione, TipoRisorsa.DELIBERA_APPROVAZIONE)
        self.sendCNV('071_update_approvazione.query', 'UPDATE APPROVAZIONE', self.codice_approvazione,
                     'dataDeliberaApprovazione', _get_datetime().isoformat())

        for tipo in [
                # TipoRisorsa.RELAZIONE_GENERALE,
                TipoRisorsa.DISCIPLINA_PIANO,
                # TipoRisorsa.RELAZIONE_RESPONSABILE,
                TipoRisorsa.RELAZIONE_GARANTE_INFORMAZIONE_PARTECIPAZIONE,
                # TipoRisorsa.VALUTAZIONE,
                TipoRisorsa.ELABORATI_CONFORMAZIONE,
                # TipoRisorsa.PIANI_ATTUATIVI_BP,
                TipoRisorsa.INDAGINI_G_I_S]:
            self.upload('070_approvazione_file_upload.query', self.codice_approvazione, tipo)

        for tipo in [
                TipoRisorsa.SUPPORTO_PREVISIONI_P_C,
                # TipoRisorsa.DISCIPLINA_INSEDIAMENTI,
                TipoRisorsa.ASSETTI_INSEDIATIVI, ]:
            self.upload('070_approvazione_file_upload.query', self.codice_approvazione, tipo, suffix='.zip')

        self.sendCNV('071_update_approvazione.query', 'UPDATE APPROVAZIONE', self.codice_approvazione,
                     'urlPianoPubblicato', 'http://approvazione.serapide')
        self.sendCNV('072_trasmissione_approvazione.query', 'TRASMISSIONE APPROVAZIONE', self.codice_approvazione)

        for nome, val in [
                ("pubblicazioneUrl", 'http://compilazioneRapportoAmbientaleUrl'),
                ("pubblicazioneUrlData", _get_datetime().isoformat())]:
            self.sendCNV('071_update_approvazione.query', 'UPDATE APPROVAZIONE', self.codice_approvazione, nome, val)

        self.sendCNV('073_pubblicazione_approvazione.query', 'PUBBLICAZIONE APPROVAZIONE', self.codice_approvazione)

        self.upload('070_approvazione_file_upload.query', self.codice_approvazione, TipoRisorsa.CONFORMITA_PIT)
        self.sendCNV('074_attrib_conformita_pit.query', 'CONFORMITA PIT', self.codice_approvazione, client=self.client_pian)

    def pubblicazione(self):
        response = self.sendCNV('905_get_pubblicazione.query', 'GET PUBBLICAZIONE', self.codice_piano)
        content = json.loads(response.content)
        self.codice_pubblicazione = content['data']['modello']['edges'][0]['node']['uuid']

        for nome, val in [
                ("pubblicazioneUrl", 'http://compilazioneRapportoAmbientaleUrl'),
                ("pubblicazioneUrlData", _get_datetime().isoformat())]:
            self.sendCNV('080_update_pubblicazione.query', 'UPDATE PUBBLICAZIONE', self.codice_pubblicazione, nome, val)
        self.sendCNV('081_pubblicazione_piano.query', 'PUBBLICAZIONE PIANO', self.codice_pubblicazione)

    def check_fase(self, fase_expected:Fase):
        # l'azione precedente promuove automaticamente alla fase AVVIO
        response = self.sendCNV('900_get_piani.query', 'GET PIANI', self.codice_piano)
        content = json.loads(response.content)
        fase = content['data']['piani']['edges'][0]['node']['fase']
        self.assertEqual(fase_expected, Fase.fix_enum(fase), "Fase errata")
