import logging

import json
import os
import datetime

from django.test import TestCase, Client

from serapide_core.modello.enums import (
    TipoRisorsa,
    TipologiaVAS)

from strt_users.enums import Qualifica

from .test_data_setup import DataLoader
from .test_serapide_abs import AbstractSerapideTest

logger = logging.getLogger(__name__)

this_path = os.path.dirname(__file__)

class FullFlowTestCase(AbstractSerapideTest):

    def test_full_piano_procedure_vas_verifica(self):

        query = None

        print("LOGIN  ====================")
        logged = True
        logged = self._client.login(username=DataLoader.FC_RUP_RESP, password='42')

        self.assertTrue(logged, "Error in login")

        client_ac = Client()
        client_sca = Client()
        client_gc = Client()

        self.assertTrue(client_ac.login(username=DataLoader.FC_AC1, password='42'), "Error in login - AC")
        self.assertTrue(client_sca.login(username=DataLoader.FC_SCA1, password='42'), "Error in login - SCA")
        self.assertTrue(client_gc.login(username=DataLoader.FC_GC1, password='42'), "Error in login - GC")

        print("GET_PROFILES ====================")
        response = self._client.get(
            self.GET_PROFILES_URL, #  + "?user_id=" + DataLoader.FC_ACTIVE1,
        )
        self.assertEqual(200, response.status_code, 'GET PROFILES failed')


        ### Now we should select a profile
        # not really needed

        response = self.create_piano(DataLoader.IPA_FI)

        content = json.loads(response.content)
        codice_piano = content['data']['createPiano']['nuovoPiano']['codice']
        codice_vas = content['data']['createPiano']['nuovoPiano']['proceduraVas']['uuid']
        codice_avvio = content['data']['createPiano']['nuovoPiano']['proceduraAvvio']['uuid']

        now = datetime.datetime.now()
        now = now.replace(microsecond=0)

        for nome, val in [
            ("dataDelibera", now.isoformat()),
            ("descrizione", "Piano di test - VAS VERIFICA [{}]".format(now)),
            ("soggettoProponenteUuid", DataLoader.uffici_stored[DataLoader.IPA_FI][DataLoader.UFF1].uuid.__str__())
        ]:
            self.send3('002_update_piano.query', 'UPDATE PIANO', codice_piano, nome, val)

        self.upload(codice_piano, TipoRisorsa.DELIBERA, '003_upload_file.query')

        self.send3('004_update_procedura_vas.query', 'UPDATE VAS', codice_vas, 'tipologia', TipologiaVAS.VERIFICA.value)
        self.upload(codice_vas, TipoRisorsa.VAS_VERIFICA, '005_vas_upload_file.query')

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

        self.send3('002_update_piano.query', 'UPDATE PIANO', codice_piano, "soggettiOperanti", sogg_op)
        self.send3('006_promozione.query', 'PROMUOVI PIANO', codice_piano)


        # Promozione effettuata DRAFT --> ANAGRAFICA

        avvio_scadenza = datetime.datetime.now()
        avvio_scadenza = avvio_scadenza.replace(hour=0, minute=0, second=0, microsecond=0)
        avvio_scadenza = avvio_scadenza + datetime.timedelta(days=10)

        for nome, val in [
            ('dataScadenzaRisposta', avvio_scadenza.isoformat()),
            ('garanteNominativo', 'pippo'),
            ('garantePec', 'pippo@pec.pec'),
            ('conferenzaCopianificazione', 'posticipata'),
        ]:
            self.send3('010_update_procedura_avvio.query', 'UPDATE AVVIO', codice_avvio, nome, val, extra_title=nome)

        for tipo in [
            TipoRisorsa.OBIETTIVI_PIANO,
            TipoRisorsa.QUADRO_CONOSCITIVO,
            TipoRisorsa.PROGRAMMA_ATTIVITA,
            TipoRisorsa.INDIVIDUAZIONE_GARANTE_INFORMAZIONE,
        ]:
            self.upload(codice_avvio, tipo, '011_avvio_upload_file.query')

        # self.update_piano(codice_piano, "numeroProtocolloGenioCivile", "1234567890", expected_code=403)
        # self.update_piano(codice_piano, "numeroProtocolloGenioCivile", "1234567890", client=client_gc)
        self.send3('012_avvio_piano.query', 'AVVIO PIANO', codice_avvio)

        # {"operationName": "UpdateProceduraVas", "variables": {"input": {"proceduraVas": {"assoggettamento": false},
        self.send3('004_update_procedura_vas.query', 'UPDATE VAS', codice_vas, 'assoggettamento', False)


        # SCA
        self.upload(codice_vas, TipoRisorsa.PARERE_VERIFICA_VAS, '005_vas_upload_file.query')
        self.send('013_invio_pareri_verifica.query', 'INVIO PARERE VERIFICA', replace_args={'codice': codice_vas}, expected_code=403)
        self.send('013_invio_pareri_verifica.query', 'INVIO PARERE VERIFICA', replace_args={'codice': codice_vas}, client=client_sca)

        # AC
        # {"operationName":"VasUploadFile","variables":{"file":null,"codice":"a62a4292-bc89-4a54-9361-ba7d0472d317","tipo":"provvedimento_verifica_vas"}
        self.upload(codice_vas, TipoRisorsa.PROVVEDIMENTO_VERIFICA_VAS, '005_vas_upload_file.query')
        self.send('014_provvedimento_verifica_vas.query', 'PROVVEDIMENTO VERIFICA VAS', replace_args={'codice': codice_vas}, expected_code=403)
        self.send('014_provvedimento_verifica_vas.query', 'PROVVEDIMENTO VERIFICA VAS', replace_args={'codice': codice_vas}, client=client_ac)

        self.send3('004_update_procedura_vas.query', 'UPDATE VAS', codice_vas, 'pubblicazioneProvvedimentoVerificaAc', "https://dev.serapide.geo-solutions.it/serapide", expected_code=403)
        self.send3('004_update_procedura_vas.query', 'UPDATE VAS', codice_vas, 'pubblicazioneProvvedimentoVerificaAc', "https://dev.serapide.geo-solutions.it/serapide", client=client_ac)

        self.send3('004_update_procedura_vas.query', 'UPDATE VAS', codice_vas, 'pubblicazioneProvvedimentoVerificaAp', "https://dev.serapide.geo-solutions.it/serapide")

        # VAS COMPLETATO
        response = self.send3('999_get_vas.query', 'GET VAS', codice_piano)
        content = json.loads(response.content)
        vas_conclusa = content['data']['modello']['edges'][0]['node']['conclusa']
        self.assertTrue(vas_conclusa, 'VAS non conclusa')

        # self.send3('006_promozione.query', 'PROMUOVI PIANO', codice_piano)


