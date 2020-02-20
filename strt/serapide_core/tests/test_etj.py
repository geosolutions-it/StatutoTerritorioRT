import logging

import json
import os
import datetime
import tempfile

from django.test.client import MULTIPART_CONTENT
from django.test import TestCase, Client
from graphene_django.utils.testing import GraphQLTestCase

from serapide_core.schema import schema

from serapide_core.modello.enums import TipoRisorsa

from .test_data_setup import DataLoader

logger = logging.getLogger(__name__)

this_path = os.path.dirname(__file__)

class FullFlowTestCase(GraphQLTestCase):
    # injecting test case's schema
    GRAPHQL_SCHEMA = schema
    GRAPHQL_URL = "/serapide/graphql/"
    LOGIN_URL = '/users/login/'

    GET_PROFILES_URL =  '/users/membership-type-api/'

    def setUp(self):
        DataLoader.loadData()

    def test_full_piano_procedure(self):

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
            # json.dumps(body),
            # content_type="application/json",
            # **headers
        )
        print(response)
        print(response.content)

        self.assertEqual(200, response.status_code, 'GET PROFILES failed')

        content = json.loads(response.content)
        self.assertIn('userChoices', content)
        self.assertIn('edges', content['userChoices'])
        self.assertEqual(1, len(content['userChoices']['edges']))
        self.assertIn('node', content['userChoices']['edges'][0])

        node = content['userChoices']['edges'][0]['node']
        print(node.keys())

        self.assertEqual(2, len(node['profili']))

        ### Now we should select a profile


        ### Try a CreatePiano
        # this_path = sys.path[0]


        with open(os.path.join(this_path, 'fixtures', '001_create_piano.query'), 'r') as file:
            query = file.read().replace('\n', '')

        print("CREATE PIANO on Regione ====================")
        query_bound = query.replace('{IPA}', DataLoader.IPA_RT)

        print('QUERY_RT: ' + query_bound)

        response = self._client.post(
            self.GRAPHQL_URL,
            query_bound,
            content_type="application/json",
            # **headers
        )

        self.assertEqual(400, response.status_code, 'CREATE PIANO on RT should fail')


        print("CREATE PIANO ====================")
        query_bound = query.replace('{IPA}', DataLoader.IPA_FI)

        response = self._client.post(
            self.GRAPHQL_URL,
            query_bound,
            content_type="application/json",
            # **headers
        )

        dump_result('CREATE PIANO', response)
        self.assertEqual(200, response.status_code, 'CREATE PIANO failed')

        content = json.loads(response.content)
        codice_piano = content['data']['createPiano']['nuovoPiano']['codice']
        codice_vas = content['data']['createPiano']['nuovoPiano']['proceduraVas']['uuid']
        print("PIANO CREATO ^^^^^^^^^^^^^^^^^^^^ {}".format(codice_piano))

        print("UPDATE PIANO ==================== 1")
        with open(os.path.join(this_path, 'fixtures', '002_update_piano.query'), 'r') as file:
            query_update = file.read().replace('\n', '')
        query_bound = query_update.replace('{codice_piano}', codice_piano)

        now = datetime.datetime.now()
        now = now.replace(microsecond=0)

        query_bound = query_bound.replace('{nome_campo}', "dataDelibera")
        query_bound = query_bound.replace('{valore_campo}',  now.isoformat())

        response = self._client.post(
            self.GRAPHQL_URL,
            query_bound,
            content_type="application/json",
            # **headers
        )

        dump_result('UPDATE PIANO', response)
        self.assertEqual(200, response.status_code, 'UPDATE PIANO failed')

        print("UPDATE PIANO OK ^^^^^^^^^^^^^^^^^^^^ 1")

        print("UPDATE PIANO ==================== 2")
        query_bound = query_update.replace('{codice_piano}', codice_piano)

        query_bound = query_bound.replace('{nome_campo}', "descrizione")
        query_bound = query_bound.replace('{valore_campo}', "Piano di test [{}]".format(now))

        response = self._client.post(
            self.GRAPHQL_URL,
            query_bound,
            content_type="application/json",
            # **headers
        )

        dump_result('UPDATE PIANO', response)

        self.assertEqual(200, response.status_code, 'UPDATE PIANO failed')
        print("UPDATE PIANO OK ^^^^^^^^^^^^^^^^^^^^ 2")

        response = self.upload_file(codice_piano, '003_upload_file.query')

        response = self.update_vas(codice_vas, 'semplificata', '004_update_procedura_vas.query')

        response = self.vas_upload_file(codice_vas, TipoRisorsa.VAS_SEMPLIFICATA, '005_vas_upload_file.query')


    def upload_file(self, codice_piano, file_name):
        print("UPLOAD FILE ==================== 1")
        with open(os.path.join(this_path, 'fixtures', file_name), 'r') as file:
            query_upload = file.read().replace('\n', '')
        query_bound = query_upload.replace('{codice_piano}', codice_piano)

        with tempfile.NamedTemporaryFile(suffix=".pdf") as f:
            form = {
                "operations": query_bound,
                "map": '{"1":["variables.file"]}',
                "1": f,
            }

            response = self._client.post(self.GRAPHQL_URL,
                                         content_type=MULTIPART_CONTENT,
                                         data=form)

            self.assertEqual(response.status_code, 200)
        dump_result('UPLOAD FILE', response)
        print("UPLOAD FILE OK ^^^^^^^^^^^^^^^^^^^^ 1")
        return response


    def update_vas(self, codice_vas, tipologia, file_name):
        print("UPDATE VAS ==================== 1")
        with open(os.path.join(this_path, 'fixtures', file_name), 'r') as file:
            query = file.read().replace('\n', '')

        query = query.replace('{codice_vas}', codice_vas)
        query = query.replace('{tipologia_vas}', tipologia)

        response = self._client.post(
            self.GRAPHQL_URL,
            query,
            content_type="application/json",
            # **headers
        )

        dump_result('UPDATE VAS', response)

        self.assertEqual(200, response.status_code, 'UPDATE VAS failed')
        print("UPDATE VAS OK ^^^^^^^^^^^^^^^^^^^^ 1")

        return response

    def vas_upload_file(self, codice_vas, tipo:TipoRisorsa, file_name):
        print("VAS UPLOAD FILE ==================== 1")
        with open(os.path.join(this_path, 'fixtures', file_name), 'r') as file:
            query = file.read().replace('\n', '')
        query = query.replace('{codice_vas}', codice_vas)
        query = query.replace('{tipo_risorsa}', tipo.value)


        with tempfile.NamedTemporaryFile(prefix=tipo.name, suffix=".pdf") as f:
            form = {
                "operations": query,
                "map": '{"1":["variables.file"]}',
                "1": f,
            }

            response = self._client.post(self.GRAPHQL_URL,
                                         content_type=MULTIPART_CONTENT,
                                         data=form)

            self.assertEqual(response.status_code, 200)
        dump_result('VAS UPLOAD FILE', response)
        print("VAS UPLOAD FILE OK ^^^^^^^^^^^^^^^^^^^^ 1")
        return response


    @classmethod
    def tearDownClass(cls):
        # Check https://github.com/graphql-python/graphene-django/issues/828
        # for the error: AttributeError: 'function' object has no attribute 'wrapped'
        try:
            super().tearDownClass()
        except AttributeError as e:
            logging.getLogger(__name__).warning('Trapped AttributeError')


def dump_result(title, result):
    print(title + "==============================")

    print(result)
    print(result.content)
    content = json.dumps(json.loads(result.content), indent=4)
    print(content.replace('\\n', '\n'))

    # result = schema.execute(q)
    # if result.errors:
    #     logger.warning("ERRORS:::::::::::::::::::")
    #     for error in result.errors:
    #         logger.warning(error);
    # else:
    #     logger.warning("RESULT::::::::::::::::::")
    #     logger.warning(result)
    #     logger.warning("RESULT DATA::::::::::::::::::.")
    #     try:
    #         logger.warning(json.dumps(result.data, indent=4))
    #     except:
    #         logger.warning(result.data)
    logger.warning("-------------------------")
    return result
