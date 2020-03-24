import logging

import json
import os

from django.test import TestCase, Client

from strt_users.enums import Qualifica

from .test_data_setup import DataLoader
from .test_serapide_abs import AbstractSerapideTest, dump_result

logger = logging.getLogger(__name__)

class UserTestCase(AbstractSerapideTest):

    def test_user_choices(self):

        print("GET_PROFILES unauth ====================")
        response = self._client.get(self.GET_PROFILES_URL)
        self.assertEqual(401, response.status_code, 'GET PROFILES failed')


        print("LOGIN  ====================")
        self.assertTrue(self._client.login(username=DataLoader.FC_RUP_RESP, password='42'), "Error in login")

        client_ac = Client()
        self.assertTrue(client_ac.login(username=DataLoader.FC_AC1, password='42'), "Error in login - AC")

        print("GET_PROFILES ====================")
        response = self._client.get(self.GET_PROFILES_URL)
        self.assertEqual(200, response.status_code, 'GET PROFILES failed')

        dump_result("GET PROFILES", response)

        content = json.loads(response.content)
        fc = content['userChoices']['fiscalCode']
        self.assertEqual(DataLoader.FC_RUP_RESP, fc, 'Bad user returned')

        print("CALL GRAPHQL userchoices ====================")

        query= """
            query {
                userChoices {
                    fiscalCode
                    firstName
                    lastName
    
                    profili {
                        profilo
                        ente       { ipa nome}
                        qualifiche { qualifica ufficio}
                    }
                }
            }"""

        ### QUERY RUP
        query_rup = query.replace('{cf}', DataLoader.FC_RUP_RESP)

        response = self._client.post(
            self.GRAPHQL_URL,
            format_query(query_rup),
            content_type="application/json",
        )
        dump_result('user choices rup', response)
        self.assertEqual(200, response.status_code, 'user_choices failed')
        content = json.loads(response.content)
        fc = content['data']['userChoices']['fiscalCode']
        self.assertEqual(DataLoader.FC_RUP_RESP, fc, 'Bad user returned')


def format_query(query):
    main_query = {'query':query}
    return json.dumps(main_query)