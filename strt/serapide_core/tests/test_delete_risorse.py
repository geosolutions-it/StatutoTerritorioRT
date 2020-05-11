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

        # CREATE and DELETE
        nome,response = self.upload('003_upload_file.query', self.codice_piano, TipoRisorsa.DELIBERA)
        content = json.loads(response.content)
        risorse = content['data']['upload']['pianoAggiornato']['risorse']['edges']
        logger.warning("LOOK FOR FILE %s"%nome)
        res_code = [edge['node']['uuid'] for edge in risorse if edge['node']['nome']==nome][0]
        logger.warning("CODICE RISORSA %s"% res_code)
        response = self.sendCXX('003d_delete_risorsa.query', 'DELETE RISORSA', self.codice_piano, 'codice_risorsa', res_code)

        self.upload('003_upload_file.query', self.codice_piano, TipoRisorsa.DELIBERA)
        self.sendCNV('004_update_procedura_vas.query', 'UPDATE VAS', self.codice_vas, 'tipologia', tipovas.value)

        # CREATE and DELETE
        nome,response = self.upload('005_vas_upload_file.query', self.codice_vas, TipoRisorsa.DOCUMENTO_PRELIMINARE_VERIFICA_VAS)
        content = json.loads(response.content)
        risorse = content['data']['upload']['proceduraVasAggiornata']['risorse']['edges']
        logger.warning("LOOK FOR FILE %s"%nome)
        res_code = [edge['node']['uuid'] for edge in risorse if edge['node']['nome']==nome][0]
        logger.warning("CODICE RISORSA %s"% res_code)
        response = self.sendCXX('003d_delete_risorsa.query', 'DELETE RISORSA', self.codice_piano, 'codice_risorsa', res_code)

        self.upload('005_vas_upload_file.query', self.codice_vas, TipoRisorsa.DOCUMENTO_PRELIMINARE_VERIFICA_VAS)


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
        self.sendCNV('013_invio_pareri_verifica.query', 'INVIO PARERE VERIFICA', self.codice_vas, expected_code=403)
        self.sendCNV('013_invio_pareri_verifica.query', 'INVIO PARERE VERIFICA', self.codice_vas, client=self.client_sca)

        # AC
        # {"operationName":"VasUploadFile","variables":{"file":null,"codice":"a62a4292-bc89-4a54-9361-ba7d0472d317","tipo":"provvedimento_verifica_vas"}
        self.upload('005_vas_upload_file.query', self.codice_vas, TipoRisorsa.PROVVEDIMENTO_VERIFICA_VAS)
        self.sendCNV('014_provvedimento_verifica_vas.query', 'PROVVEDIMENTO VERIFICA VAS', self.codice_vas, expected_code=403)
        self.sendCNV('014_provvedimento_verifica_vas.query', 'PROVVEDIMENTO VERIFICA VAS', self.codice_vas, client=self.client_ac)

        self.sendCNV('004_update_procedura_vas.query', 'UPDATE VAS', self.codice_vas,
                     'pubblicazioneProvvedimentoVerificaAc', "https://dev.serapide.geo-solutions.it/serapide",
                     client=self.client_ac)

        self.sendCNV('004_update_procedura_vas.query', 'UPDATE VAS', self.codice_vas,
                     'pubblicazioneProvvedimentoVerificaAp', "https://dev.serapide.geo-solutions.it/serapide")

        # VAS COMPLETATO
        response = self.sendCNV('901_get_vas.query', 'GET VAS', self.codice_piano)
        content = json.loads(response.content)
        vas_conclusa = content['data']['modello']['edges'][0]['node']['conclusa']
        self.assertTrue(vas_conclusa, 'VAS non conclusa')

    def contributi_tecnici(self):
        self.sendCNV('902_get_avvio.query', 'GET AVVIO', self.codice_piano)

        nome,response = self.upload('011_avvio_upload_file.query', self.codice_avvio, TipoRisorsa.CONTRIBUTI_TECNICI)
        content = json.loads(response.content)
        risorse = content['data']['upload']['proceduraAvvioAggiornata']['risorse']['edges']
        logger.warning("LOOK FOR FILE %s"%nome)
        res_code = [edge['node']['uuid'] for edge in risorse if edge['node']['nome']==nome][0]
        logger.warning("CODICE RISORSA %s"% res_code)
        response = self.sendCXX('003d_delete_risorsa.query', 'DELETE RISORSA', self.codice_piano, 'codice_risorsa', res_code)

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

        nome,response =  self.upload('022_conferenza_upload_file.query', codice_cc, TipoRisorsa.ELABORATI_CONFERENZA)
        content = json.loads(response.content)
        risorse = content['data']['upload']['conferenzaCopianificazioneAggiornata']['risorse']['edges']
        logger.warning("LOOK FOR FILE %s"%nome)
        res_code = [edge['node']['uuid'] for edge in risorse if edge['node']['nome']==nome][0]
        logger.warning("CODICE RISORSA %s"% res_code)
        response = self.sendCXX('003d_delete_risorsa.query', 'DELETE RISORSA', self.codice_piano, 'codice_risorsa', res_code)

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
        #{"operationName":"UploadFile","variables":{"file":null,"codice":"SCND_FI200200017","tipo":"norme_tecniche_attuazione"}
        self.upload('003_upload_file.query', self.codice_piano, TipoRisorsa.NORME_TECNICHE_ATTUAZIONE)
        self.sendCNV('040_formazione_piano.query', 'FORMAZIONE PIANO', self.codice_piano)

    def check_fase(self, fase_expected:Fase):
        # l'azione precedente promuove automaticamente alla fase AVVIO
        response = self.sendCNV('900_get_piani.query', 'GET PIANI', self.codice_piano)
        content = json.loads(response.content)
        fase = content['data']['piani']['edges'][0]['node']['fase']
        self.assertEqual(fase_expected, Fase.fix_enum(fase), "Fase errata")

    def test_flow_vasverificanoass_ccsiirno_form(self):

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
