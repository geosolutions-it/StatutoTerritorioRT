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
    TipologiaVAS
)

from .test_data_setup import DataLoader

logger = logging.getLogger(__name__)

this_path = os.path.dirname(__file__)

class AbstractSerapideTest(GraphQLTestCase):
    # injecting test case's schema
    GRAPHQL_SCHEMA = schema
    GRAPHQL_URL = "/serapide/graphql/"

    LOGIN_URL = '/users/login/'
    GET_PROFILES_URL =  '/users/membership-type-api/'

    def setUp(self):
        DataLoader.loadData()

    def create_piano(self, ipa, expected_code=200, extra_title=''):
        print("CREATE PIANO ================================================== {}".format(extra_title))
        with open(os.path.join(this_path, 'fixtures', '001_create_piano.query'), 'r') as file:
            query = file.read().replace('\n', '')
        query_bound = query.replace('{IPA}', ipa)
        response = self._client.post(
            self.GRAPHQL_URL,
            query_bound,
            content_type="application/json",
            # **headers
        )
        dump_result('CREATE PIANO', response)
        self.assertEqual(expected_code, response.status_code, 'CREATE PIANO failed')
        print("CREATE PIANO ({}) ^^^^^^^^^^^^^^^^^^^^".format(response.status_code))
        return response

    def update_piano(self, codice_piano, nome_campo, valore_campo, expected_code=200, extra_title='', kill_quote=False):
        print("UPDATE PIANO ================================================== {} --- {}".format(nome_campo, extra_title))
        with open(os.path.join(this_path, 'fixtures', '002_update_piano.query'), 'r') as file:
            query = file.read().replace('\n', '')
        query = query.replace('{codice_piano}', codice_piano)

        query = query.replace('{nome_campo}', nome_campo)

        val_replace = '"{valore_campo}"' if kill_quote else '{valore_campo}'
        query = query.replace(val_replace,  valore_campo)

        response = self._client.post(
            self.GRAPHQL_URL,
            query,
            content_type="application/json",
            # **headers
        )

        dump_result('UPDATE PIANO', response)
        self.assertEqual(expected_code, response.status_code, 'UPDATE PIANO failed')

        print("UPDATE PIANO ({})^^^^^^^^^^^^^^^^^^^^".format(response.status_code))


    def upload_file(self, codice_piano, file_name):
        print("UPLOAD FILE ==================================================")
        with open(os.path.join(this_path, 'fixtures', file_name), 'r') as file:
            query_upload = file.read().replace('\n', '')
        query_bound = query_upload.replace('{codice_piano}', codice_piano)


        with tempfile.NamedTemporaryFile(mode='w+', suffix=".pdf", delete=False) as f:
            f.write("this is a fake PDF file\n")
            filename = f.name

        with open(filename) as f:
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


    def update_vas(self, codice_vas, tipologia, file_name, expected_code=200):
        print("UPDATE VAS ==================================================")
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

        self.assertEqual(expected_code, response.status_code, 'UPDATE VAS failed')
        print("UPDATE VAS ({}) ^^^^^^^^^^^^^^^^^^^^".format(response.status_code))

        return response

    def vas_upload_file(self, codice_vas, tipo:TipoRisorsa, file_name):
        print("VAS UPLOAD FILE ==================================================")
        with open(os.path.join(this_path, 'fixtures', file_name), 'r') as file:
            query = file.read().replace('\n', '')
        query = query.replace('{codice_vas}', codice_vas)
        query = query.replace('{tipo_risorsa}', tipo.value)

        with tempfile.NamedTemporaryFile(mode='w+', prefix=tipo.name, suffix=".pdf", delete=False) as f:
            f.write("this is a fake PDF file\n")
            filename = f.name

        with open(filename) as f:
            form = {
                "operations": query,
                "map": '{"1":["variables.file"]}',
                "1": f,
            }

            response = self._client.post(self.GRAPHQL_URL,
                                         content_type=MULTIPART_CONTENT,
                                         data=form)
        os.unlink(filename)

        self.assertEqual(response.status_code, 200)

        dump_result('VAS UPLOAD FILE', response)
        print("VAS UPLOAD FILE OK ^^^^^^^^^^^^^^^^^^^^ 1")
        return response

    def promuovi_piano(self, codice_piano, file_name, expected_code=200):
        print("PROMOZIONE PIANO ================================================== ")
        with open(os.path.join(this_path, 'fixtures', file_name), 'r') as file:
            query = file.read().replace('\n', '')

        query = query.replace('{codice_piano}', codice_piano)

        response = self._client.post(
            self.GRAPHQL_URL,
            query,
            content_type="application/json",
            # **headers
        )

        dump_result('PROMOZIONE PIANO', response)

        self.assertEqual(expected_code, response.status_code, 'PROMOZIONE PIANO failed')
        print("PROMOZIONE PIANO ({}) ^^^^^^^^^^^^^^^^^^^^".format(response.status_code))

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
    print(title + " result --------------------------------------------------")

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
