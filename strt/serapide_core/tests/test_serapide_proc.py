import logging

import json
import os
import datetime
from ast import dump
from contextlib import redirect_stderr
from functools import partial

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

        now = datetime.datetime.now()
        now = now.replace(microsecond=0)

        for nome, val in [
            ("dataDelibera", now.isoformat()),
            ("descrizione", "Piano di test - VAS {vas} [{dt}]".format(dt=now, vas=tipovas.name)),
            ("soggettoProponenteUuid", DataLoader.uffici_stored[DataLoader.IPA_FI][DataLoader.UFF1].uuid.__str__())
        ]:
            self.send3('002_update_piano.query', 'UPDATE PIANO', self.codice_piano, nome, val)

        self.upload(self.codice_piano, TipoRisorsa.DELIBERA, '003_upload_file.query')

        self.send3('004_update_procedura_vas.query', 'UPDATE VAS', self.codice_vas, 'tipologia', tipovas.value)
        self.upload(self.codice_vas, TipoRisorsa.VAS_VERIFICA, '005_vas_upload_file.query')

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

        self.send3('002_update_piano.query', 'UPDATE PIANO', self.codice_piano, "soggettiOperanti", sogg_op)
        self.send3('006_promozione.query', 'PROMUOVI PIANO', self.codice_piano)


    def avvio_piano(self, copianificazione:TipologiaCopianificazione):
        avvio_scadenza = datetime.datetime.now()
        avvio_scadenza = avvio_scadenza.replace(hour=0, minute=0, second=0, microsecond=0)
        avvio_scadenza = avvio_scadenza + datetime.timedelta(days=10)

        for nome, val in [
            ('dataScadenzaRisposta', avvio_scadenza.isoformat()),
            ('garanteNominativo', 'pippo'),
            ('garantePec', 'pippo@pec.pec'),
            ('conferenzaCopianificazione', copianificazione.name), # questo modifica la sequenza in CC
        ]:
            self.send3('010_update_procedura_avvio.query', 'UPDATE AVVIO', self.codice_avvio, nome, val, extra_title=nome)

        for tipo in [
            TipoRisorsa.OBIETTIVI_PIANO,
            TipoRisorsa.QUADRO_CONOSCITIVO,
            TipoRisorsa.PROGRAMMA_ATTIVITA,
            TipoRisorsa.INDIVIDUAZIONE_GARANTE_INFORMAZIONE,
        ]:
            self.upload(self.codice_avvio, tipo, '011_avvio_upload_file.query')

        # self.update_piano(codice_piano, "numeroProtocolloGenioCivile", "1234567890", expected_code=403)
        # self.update_piano(codice_piano, "numeroProtocolloGenioCivile", "1234567890", client=client_gc)
        self.send3('012_avvio_piano.query', 'AVVIO PIANO', self.codice_avvio)

    def vas_verifica_no_assoggettamento(self):
        # {"operationName": "UpdateProceduraVas", "variables": {"input": {"proceduraVas": {"assoggettamento": false},
        self.send3('004_update_procedura_vas.query', 'UPDATE VAS', self.codice_vas, 'assoggettamento', False)


        # SCA
        self.upload(self.codice_vas, TipoRisorsa.PARERE_VERIFICA_VAS, '005_vas_upload_file.query')
        self.send('013_invio_pareri_verifica.query', 'INVIO PARERE VERIFICA', replace_args={'codice': self.codice_vas}, expected_code=403)
        self.send('013_invio_pareri_verifica.query', 'INVIO PARERE VERIFICA', replace_args={'codice': self.codice_vas}, client=self.client_sca)

        # AC
        # {"operationName":"VasUploadFile","variables":{"file":null,"codice":"a62a4292-bc89-4a54-9361-ba7d0472d317","tipo":"provvedimento_verifica_vas"}
        self.upload(self.codice_vas, TipoRisorsa.PROVVEDIMENTO_VERIFICA_VAS, '005_vas_upload_file.query')
        self.send('014_provvedimento_verifica_vas.query', 'PROVVEDIMENTO VERIFICA VAS', replace_args={'codice': self.codice_vas}, expected_code=403)
        self.send('014_provvedimento_verifica_vas.query', 'PROVVEDIMENTO VERIFICA VAS', replace_args={'codice': self.codice_vas}, client=self.client_ac)

        self.send3('004_update_procedura_vas.query', 'UPDATE VAS', self.codice_vas, 'pubblicazioneProvvedimentoVerificaAc', "https://dev.serapide.geo-solutions.it/serapide", expected_code=403)
        self.send3('004_update_procedura_vas.query', 'UPDATE VAS', self.codice_vas, 'pubblicazioneProvvedimentoVerificaAc', "https://dev.serapide.geo-solutions.it/serapide", client=self.client_ac)

        self.send3('004_update_procedura_vas.query', 'UPDATE VAS', self.codice_vas, 'pubblicazioneProvvedimentoVerificaAp', "https://dev.serapide.geo-solutions.it/serapide")

        # VAS COMPLETATO
        response = self.send3('999_get_vas.query', 'GET VAS', self.codice_piano)
        content = json.loads(response.content)
        vas_conclusa = content['data']['modello']['edges'][0]['node']['conclusa']
        self.assertTrue(vas_conclusa, 'VAS non conclusa')

    def contributi_tecnici(self):
        self.send3('999_get_avvio.query', 'GET AVVIO', self.codice_piano)
        self.upload(self.codice_avvio, TipoRisorsa.CONTRIBUTI_TECNICI, '011_avvio_upload_file.query')
        self.send3('015_contributi_tecnici.query', 'CONTRIBUTI TECNICI', self.codice_avvio, expected_code=403)
        self.send3('015_contributi_tecnici.query', 'CONTRIBUTI TECNICI', self.codice_avvio, client=self.client_pian) # questo crea le azioni di CC

    def confcop_no_int(self):
        self.send3('016_richiesta_conferenza_copianificazione.query', 'RICHIESTA CONF COP', self.codice_avvio)

        response = self.send3('017_get_conferenza_copianificazione.query', 'GET CONF COP', self.codice_piano)
        content = json.loads(response.content)
        codice_cc = content['data']['modello']['edges'][0]['node']['uuid']

        self.upload(codice_cc, TipoRisorsa.ELABORATI_CONFERENZA, '018_conferenza_upload_file.query')
        self.send3('019_chiusura_conferenza_copianificazione.query', 'CHIUSURA CONF COP', self.codice_avvio,
                   expected_code=403)
        self.send3('019_chiusura_conferenza_copianificazione.query', 'CHIUSURA CONF COP', self.codice_avvio,
                   client=self.client_pian)

        #   update procedura avvia
        #    "uuid" : "7fc7c9ad-9064-47a9-9cc0-1162c0907ab7",
        #    "proceduraAvvio" : {
        #       "messaggioIntegrazione" : "Nessuna richiesta"
        #    }
        # }

        # {"operationName":"UpdateProceduraAvvio","variables":{"input":{"proceduraAvvio":{"richiestaIntegrazioni":true},"uuid":"7fc7c9ad-9064-47a9-9cc0-1162c0907ab7"}}
        # richiesta int può creare ultriori azioni

        self.send3('020_richiesta_integrazioni.query', 'CHIUSURA CONF COP', self.codice_avvio, expected_code=403)
        self.send3('020_richiesta_integrazioni.query', 'CHIUSURA CONF COP', self.codice_avvio, client=self.client_pian)

    def genio_civile(self):
        self.send3('002_update_piano.query', 'UPDATE PIANO', self.codice_piano, 'numeroProtocolloGenioCivile', 'prot_g_c', expected_code=403)
        self.send3('002_update_piano.query', 'UPDATE PIANO', self.codice_piano, 'numeroProtocolloGenioCivile', 'prot_g_c', client=self.client_gc)
        self.send3('021_invio_protocollo_genio_civile.query', 'INVIO PROT GC', self.codice_avvio, expected_code=403)
        self.send3('021_invio_protocollo_genio_civile.query', 'INVIO PROT GC', self.codice_avvio, client=self.client_gc)

    def formazione_piano(self):
        #{"operationName":"UploadFile","variables":{"file":null,"codice":"SCND_FI200200017","tipo":"norme_tecniche_attuazione"}
        self.upload(self.codice_piano, TipoRisorsa.NORME_TECNICHE_ATTUAZIONE, '003_upload_file.query')
        self.send3('022_formazione_piano.query', 'FORMAZIONE PIANO', self.codice_piano)

    def check_fase(self, fase_expected:Fase):
        # l'azione precedente promuove automaticamente alla fase AVVIO
        response = self.send3('999_get_piani.query', 'GET PIANI', self.codice_piano)
        content = json.loads(response.content)
        fase = content['data']['piani']['edges'][0]['node']['fase']
        self.assertEqual(fase_expected, Fase.fix_enum(fase), "Fase errata")


    def test_flow_verifica_noass_posticipata_noint(self):

        query = None

        self.do_login()
        self.create_piano_and_promote(TipologiaVAS.VERIFICA) # Promozione effettuata DRAFT --> ANAGRAFICA
        self.avvio_piano(TipologiaCopianificazione.POSTICIPATA)
        self.vas_verifica_no_assoggettamento()

        self.contributi_tecnici()
        self.confcop_no_int()

        self.genio_civile()

        self.check_fase(Fase.ANAGRAFICA)

        self.formazione_piano()

        self.check_fase(Fase.AVVIO)

