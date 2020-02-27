import logging

import json
import os
import datetime

from django.test import TestCase, Client

from serapide_core.modello.enums import (
    TipoRisorsa,
    TipologiaVAS)

from strt_users.enums import (
    Qualifica)

from .test_data_setup import DataLoader
from .test_serapide_abs import AbstractSerapideTest

logger = logging.getLogger(__name__)

this_path = os.path.dirname(__file__)

class FullFlowTestCase(AbstractSerapideTest):

    def test_full_piano_procedure_vas_procedimento(self):

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

        now = datetime.datetime.now()
        now = now.replace(microsecond=0)

        for nome, val in [
            ("dataDelibera", now.isoformat()),
            ("descrizione", "Piano di test - VAS PROCEDIMENTO [{}]".format(now)),
            ("soggettoProponenteUuid", DataLoader.uffici_stored[DataLoader.IPA_FI][DataLoader.UFF1].uuid.__str__())
        ]:
            self.send3('002_update_piano.query', 'UPDATE PIANO', codice_piano, nome, val)

        response = self.upload(codice_piano, TipoRisorsa.DELIBERA, '003_upload_file.query')

        self.send3('004_update_procedura_vas.query', 'UPDATE VAS', codice_vas, 'tipologia', TipologiaVAS.PROCEDIMENTO.name)

        response = self.send3('006_promozione.query', 'PROMUOVI PIANO', codice_piano, expected_code=409)
        content = json.loads(response.content)
        errors = content['errors'][0]['data']['errors']
        self.assertEqual(2, len(errors))
        for err in errors:
            self.assertIn("Soggetto", err)
            self.assertIn("mancante", err)

        # test error in soggetto operante
        # PI::uff1 non è SCA
        so_err = [{
            'ufficioUuid': DataLoader.uffici_stored[DataLoader.IPA_PI][DataLoader.UFF1].uuid.__str__(),
            'qualifica': Qualifica.SCA.name}]
        self.send3('002_update_piano.query', 'UPDATE PIANO', codice_piano, "soggettiOperanti", so_err, expected_code=404)

        # add soggetto operante AC
        sogg_op = []

        sogg_op.append({
            'ufficioUuid': DataLoader.uffici_stored[DataLoader.IPA_PI][DataLoader.UFF1].uuid.__str__(),
            'qualifica': Qualifica.AC.name})
        sogg_op.append({
            'ufficioUuid': DataLoader.uffici_stored[DataLoader.IPA_LU][DataLoader.UFF1].uuid.__str__(),
            'qualifica': Qualifica.SCA.name})

        self.send3('002_update_piano.query', 'UPDATE PIANO', codice_piano, "soggettiOperanti", sogg_op)

        # response = self.send3('006_promozione.query', 'PROMUOVI PIANO', codice_piano)
