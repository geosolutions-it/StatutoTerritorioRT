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
from strt_users.models import Utente

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
        if Utente.objects.count() == 0:
            DataLoader.loadData()

    def sendCNV(self, file, title, codice, nome_campo='', valore_campo=None, extra_title='', expected_code=200, client=None):
        return self.send(file,
                         title + ' ' + nome_campo,
                         extra_title=extra_title,
                         expected_code=expected_code,
                         client=client,
                         replace_args={
                            'codice': codice,
                            'nome_campo': nome_campo,
                            'valore_campo': valore_campo
                         })

    def sendCXX(self, file, title, codice, nome_codice2, codice2, extra_title='', expected_code=200, client=None):
        return self.send(file,
                         title + ' ' + nome_codice2,
                         extra_title=extra_title,
                         expected_code=expected_code,
                         client=client,
                         replace_args={
                            'codice': codice,
                            nome_codice2: codice2,
                         })

    def send(self, file, title, extra_title='', expected_code=200, replace_args={}, client=None):
        _client = client if client else self._client

        print("{title} ================================================== {extra_title}".format(title=title, extra_title=extra_title))
        with open(os.path.join(this_path, 'fixtures', file), 'r') as file:
            query = file.read().replace('\n', '')

        for token,repl in replace_args.items():
            if type(repl) in [str]:
                query = query.replace('{'+token+'}', repl)
            elif type(repl) in [dict, list, bool]:
                query = query.replace('"{'+token+'}"', json.dumps(repl))
            elif repl is None:
                pass
            else:
                raise Exception("Can't encode {}, {}".format(token, repl))

        response = _client.post(
            self.GRAPHQL_URL,
            query,
            content_type="application/json",
            # **headers
        )
        dump_result(title, response)
        self.assertEqual(expected_code, response.status_code, title + ' failed')
        print("{title} ({code}) ^^^^^^^^^^^^^^^^^^^^".format(title=title, code=response.status_code))
        return response

    def upload(self, file:str, codice:str, tipo:TipoRisorsa, extra_title='', expected_code=200, client=None, suffix='.pdf'):
        _client = client if client else self._client
        print("UPLOAD {tipo} ================================================== {extra_title}".format(tipo=tipo.name, extra_title=extra_title))
        with open(os.path.join(this_path, 'fixtures', file), 'r') as file:
            query = file.read().replace('\n', '').replace('__typename', '')

        query = query.replace('{codice}', codice)
        query = query.replace('{tipo_risorsa}', tipo.value)

        with tempfile.NamedTemporaryFile(mode='w+', prefix=tipo.name, suffix=suffix, delete=False) as f:
            f.write("this is a fake PDF file\n")
            tmp_filename = f.name

        with open(tmp_filename) as f:
            form = {
                "operations": query,
                "map": '{"1":["variables.file"]}',
                "1": f,
            }

            response = _client.post(self.GRAPHQL_URL,
                                         content_type=MULTIPART_CONTENT,
                                         data=form)
        os.unlink(tmp_filename)

        dump_result('UPLOAD FILE', response)
        self.assertEqual(expected_code, response.status_code, "upload " + tipo.name  + ' failed')
        print("UPLOAD {tipo}: ({code}) ^^^^^^^^^^^^^^^^^^^^".format(tipo=tipo.name, code=response.status_code))
        return os.path.basename(tmp_filename),response

    def create_piano(self, ipa, expected_code=200, extra_title=''):
        return self.send('001_create_piano.query', 'CREATE PIANO', extra_title, expected_code, {'IPA': ipa})

    def update_piano(self, codice_piano, nome_campo, valore_campo, expected_code=200, extra_title='', client=None):
        _client = client if client else self._client
        return self.send('002_update_piano.query', 'UPDATE PIANO', extra_title, expected_code,
                         {'codice_piano': codice_piano,
                          'nome_campo': nome_campo,
                          'valore_campo': valore_campo
                          }, client=_client)

    def upload_file(self, codice_piano, file_name):
        print("UPLOAD FILE ==================================================")
        with open(os.path.join(this_path, 'fixtures', file_name), 'r') as file:
            query_upload = file.read().replace('\n', '')
        query_bound = query_upload.replace('{codice_piano}', codice_piano)


        with tempfile.NamedTemporaryFile(mode='w+', suffix=".pdf", delete=False) as f:
            f.write("this is a fake PDF file\n")
            tmp_filename = f.name

        with open(tmp_filename) as f:
            form = {
                "operations": query_bound,
                "map": '{"1":["variables.file"]}',
                "1": f,
            }

            response = self._client.post(self.GRAPHQL_URL,
                                         content_type=MULTIPART_CONTENT,
                                         data=form)
            os.unlink(tmp_filename)

            self.assertEqual(response.status_code, 200)

        dump_result('UPLOAD FILE', response)
        print("UPLOAD FILE OK ^^^^^^^^^^^^^^^^^^^^ 1")
        return response


    def update_vas(self, codice_vas, tipologia, file_name, expected_code=200):
        return self.send(file_name, 'UPDATE VAS', '', expected_code,
                         {'codice_vas': codice_vas,
                          'tipologia_vas': tipologia,
                          })

    def vas_upload_file(self, codice_vas, tipo:TipoRisorsa, file_name):
        print("VAS UPLOAD FILE ==================================================")
        with open(os.path.join(this_path, 'fixtures', file_name), 'r') as file:
            query = file.read().replace('\n', '')
        query = query.replace('{codice_vas}', codice_vas)
        query = query.replace('{tipo_risorsa}', tipo.value)

        with tempfile.NamedTemporaryFile(mode='w+', prefix=tipo.name, suffix=".pdf", delete=False) as f:
            f.write("this is a fake PDF file\n")
            tmp_filename = f.name

        with open(tmp_filename) as f:
            form = {
                "operations": query,
                "map": '{"1":["variables.file"]}',
                "1": f,
            }

            response = self._client.post(self.GRAPHQL_URL,
                                         content_type=MULTIPART_CONTENT,
                                         data=form)
        os.unlink(tmp_filename)

        self.assertEqual(response.status_code, 200)

        dump_result('VAS UPLOAD FILE', response)
        print("VAS UPLOAD FILE OK ^^^^^^^^^^^^^^^^^^^^ 1")
        return response

    def promuovi_piano(self, codice_piano, file_name, expected_code=200):
        return self.send(file_name, 'PROMOZIONE PIANO', '', expected_code, {'codice': codice_piano,})

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
