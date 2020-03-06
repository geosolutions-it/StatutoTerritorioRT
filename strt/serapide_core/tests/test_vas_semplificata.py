import logging

import json
import os
import datetime
import tempfile
import uuid

from django.test.client import MULTIPART_CONTENT
from django.test import TestCase, Client
from graphene_django.utils.testing import GraphQLTestCase

from serapide_core.schema import schema

from serapide_core.modello.enums import (
    TipoRisorsa,
    TipologiaVAS)

from .test_data_setup import DataLoader
from .test_serapide_abs import AbstractSerapideTest

logger = logging.getLogger(__name__)

this_path = os.path.dirname(__file__)

class FullFlowTestCase(AbstractSerapideTest):

    def test_full_piano_procedure_vas_semplificata(self):

        query = None

        print("GET_PROFILES (should fail) ====================")
        get_profiles_resp = self._client.get(self.GET_PROFILES_URL)
        self.assertEqual(401, get_profiles_resp.status_code, 'Unauthenticated GET PROFILES should fail')

        print("Test GET_PROFILES ====================")
        get_profiles_resp = self._client.get(self.GET_PROFILES_URL + "?user_id=" + DataLoader.FC_RUP_RESP)
        self.assertEqual(200, get_profiles_resp.status_code, 'Test GET PROFILES should succeed also without session')

        print("LOGIN  ====================")
        logged = True
        logged = self._client.login(username=DataLoader.FC_RUP_RESP, password='42')

        # get(
        #     self.LOGIN_URL + "?user_id=" + DataLoader.FC_ACTIVE1 + "&password=42",
        #     # json.dumps(body),
        #     # content_type="application/json",
        #     # **headers
        # )

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
        print(response)
        print(response.content)

        self.assertEqual(200, response.status_code, 'GET PROFILES failed')

        content = json.loads(response.content)

        node = content['userChoices']


        self.assertEqual(2, len(node['profili']))

        ### Now we should select a profile
        # not really needed

        ### Try a CreatePiano
        response = self.create_piano(DataLoader.IPA_RT, expected_code=400, extra_title=" on Regione (should fail)")
        response = self.create_piano(DataLoader.IPA_FI)

        content = json.loads(response.content)
        codice_piano = content['data']['createPiano']['nuovoPiano']['codice']
        codice_vas = content['data']['createPiano']['nuovoPiano']['proceduraVas']['uuid']

        now = datetime.datetime.now()
        now = now.replace(microsecond=0)

        for nome, val in [
            ("dataDelibera", now.isoformat()),
            ("descrizione", "Piano di test - VAS SEMPLIFICATA [{}]".format(now)),
            ("soggettoProponenteUuid", DataLoader.uffici_stored[DataLoader.IPA_FI][DataLoader.UFF1].uuid.__str__())
        ]:
            self.sendCNV('002_update_piano.query', 'UPDATE PIANO', codice_piano, nome, val)

        self.sendCNV('002_update_piano.query', 'UPDATE PIANO', codice_piano, "soggettoProponenteUuid", uuid.uuid4().__str__(), expected_code=404)


        response = self.upload(codice_piano, TipoRisorsa.DELIBERA, '003_upload_file.query')

        self.sendCNV('004_update_procedura_vas.query', 'UPDATE VAS', codice_vas, 'tipologia', "fake_vas_type", expected_code=400)
        self.sendCNV('004_update_procedura_vas.query', 'UPDATE VAS', codice_vas, 'tipologia', TipologiaVAS.SEMPLIFICATA.name)

        response = self.upload(codice_vas, TipoRisorsa.VAS_SEMPLIFICATA, '005_vas_upload_file.query')

        # response = self.promuovi_piano(codice_piano, '006_promozione.query')


