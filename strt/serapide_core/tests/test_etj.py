import logging

import json
import os
import sys

from graphene_django.utils.testing import GraphQLTestCase
from serapide_core.schema import schema


from .test_data_setup import DataLoader

logger = logging.getLogger(__name__)

class UserLoginTestCase(GraphQLTestCase):
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
        get_profiles_resp = self._client.get(self.GET_PROFILES_URL + "?user_id=" + DataLoader.FC_ACTIVE1)
        self.assertEqual(200, get_profiles_resp.status_code, 'Test GET PROFILES should succeed also without session')

        print("LOGIN  ====================")
        logged = True
        logged = self._client.login(username=DataLoader.FC_ACTIVE1, password='42')

        # get(
        #     self.LOGIN_URL + "?user_id=" + DataLoader.FC_ACTIVE1 + "&password=42",
        #     # json.dumps(body),
        #     # content_type="application/json",
        #     # **headers
        # )

        self.assertTrue(logged, "Error in login")


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

        self.assertEqual(3, len(node['profili']))

        ### Now we should select a profile


        ### Try a CreatePiano
        # this_path = sys.path[0]
        this_path = os.path.dirname(__file__)

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
        self.assertEqual(200, response.status_code, 'CREATE PIANO failed')

        dump_result('CREATE PIANO', response)

        content = json.loads(response.content)
        codice_piano = content['data']['createPiano']['nuovoPiano']['codice']
        print("PIANO CREATO ==================== {}".format(codice_piano))


        print("UPDATE PIANO ====================")
        with open(os.path.join(this_path, 'fixtures', '002_update_piano.query'), 'r') as file:
            query = file.read().replace('\n', '')
        query_bound = query.replace('{codice_piano}', codice_piano)
        response = self._client.post(
            self.GRAPHQL_URL,
            query_bound,
            content_type="application/json",
            # **headers
        )

        dump_result('UPDATE PIANO', response)

        self.assertEqual(200, response.status_code, 'UPDATE PIANO failed')



        # This validates the status code and if you get errors
        self.assertResponseNoErrors(response)

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
