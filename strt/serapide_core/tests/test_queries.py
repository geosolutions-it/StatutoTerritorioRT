#!/usr/bin/env python
# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright 2018, GeoSolutions Sas.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.
#
#########################################################################

from __future__ import unicode_literals

import json
import logging

from django.contrib.auth import get_user_model
from django.test import TestCase
from serapide_core.schema import schema


logger = logging.getLogger(__name__)

UserModel = get_user_model()


def _log(msg):
    logger.debug(msg)


class BaseTest(TestCase):

    def setUp(self):
        self.foo_user = UserModel.objects.create_user("foo_user", "test@example.com", "123456")
        self.bar_user = UserModel.objects.create_user("bar_user", "dev@example.com", "123456")

    def tearDown(self):
        self.foo_user.delete()
        self.bar_user.delete()


class TestGrapheneQueries(BaseTest):

    fixtures = ['test_set_001.json', ]

    def test_select(self):
        query_1 = """query {
          tuttiGliStati{
            edges {
              node {
                nome,
                codice,
                descrizione,
                pianiOperativi {
                  edges {
                    node {
                      identificativo
                    }
                  }
                }
              }
            }
          }
        }"""

        result = schema.execute(query_1)
        self.assertIsNone(result.errors)
        self.assertIsNotNone(result.data)
        _query_result = dict(result.data)
        # _log(json.dumps(_query_result))

        self.assertTrue('tuttiGliStati' in _query_result)
        self.assertEqual(len(_query_result['tuttiGliStati']['edges']), 4)

        # Stato == 'DRAFT'
        self.assertEqual(_query_result['tuttiGliStati']['edges'][0]['node']['nome'], 'DRAFT')
        self.assertEqual(_query_result['tuttiGliStati']['edges'][0]['node']['codice'], '001')
        self.assertTrue('pianiOperativi', _query_result['tuttiGliStati']['edges'][0]['node'])
        _piani_operativi = _query_result['tuttiGliStati']['edges'][0]['node']['pianiOperativi']['edges']
        self.assertEqual(len(_piani_operativi), 1)
        self.assertEqual(_piani_operativi[0]['node']['identificativo'], 'TEST_B_002')

        # Stato == 'INSERITO'
        self.assertEqual(_query_result['tuttiGliStati']['edges'][1]['node']['nome'], 'INSERITO')
        self.assertEqual(_query_result['tuttiGliStati']['edges'][1]['node']['codice'], '002')
        self.assertTrue('pianiOperativi', _query_result['tuttiGliStati']['edges'][1]['node'])
        _piani_operativi = _query_result['tuttiGliStati']['edges'][1]['node']['pianiOperativi']['edges']
        self.assertEqual(len(_piani_operativi), 1)
        self.assertEqual(_piani_operativi[0]['node']['identificativo'], 'TEST_A_001')

        # Stato == 'AVVIO'
        self.assertEqual(_query_result['tuttiGliStati']['edges'][2]['node']['nome'], 'AVVIO')
        self.assertEqual(_query_result['tuttiGliStati']['edges'][2]['node']['codice'], '003')
        self.assertTrue('pianiOperativi', _query_result['tuttiGliStati']['edges'][2]['node'])
        _piani_operativi = _query_result['tuttiGliStati']['edges'][2]['node']['pianiOperativi']['edges']
        self.assertEqual(len(_piani_operativi), 0)

        # Stato == 'UNKNOWN'
        self.assertEqual(_query_result['tuttiGliStati']['edges'][3]['node']['nome'], 'UNKNOWN')
        self.assertEqual(_query_result['tuttiGliStati']['edges'][3]['node']['codice'], '404')
        self.assertTrue('pianiOperativi', _query_result['tuttiGliStati']['edges'][3]['node'])
        _piani_operativi = _query_result['tuttiGliStati']['edges'][3]['node']['pianiOperativi']['edges']
        self.assertEqual(len(_piani_operativi), 0)

        query_2 = """query {
          tuttiGliStati(nome: "draft"){
            edges {
              node {
                nome,
                codice,
                descrizione,
                pianiOperativi {
                  edges {
                    node {
                      nome
                      codice
                      identificativo
                    }
                  }
                }
              }
            }
          }
        }"""

        # Filtered Query
        result = schema.execute(query_2)
        self.assertIsNone(result.errors)
        self.assertIsNotNone(result.data)
        _query_result = dict(result.data)
        # _log(json.dumps(_query_result))

        self.assertTrue('tuttiGliStati' in _query_result)
        self.assertEqual(len(_query_result['tuttiGliStati']['edges']), 1)

        # Stato == 'DRAFT'
        self.assertEqual(_query_result['tuttiGliStati']['edges'][0]['node']['nome'], 'DRAFT')
        self.assertEqual(_query_result['tuttiGliStati']['edges'][0]['node']['codice'], '001')
        self.assertTrue('pianiOperativi', _query_result['tuttiGliStati']['edges'][0]['node'])
        _piani_operativi = _query_result['tuttiGliStati']['edges'][0]['node']['pianiOperativi']['edges']
        self.assertEqual(len(_piani_operativi), 1)
        self.assertEqual(_piani_operativi[0]['node']['nome'], 'TEST_B')
        self.assertEqual(_piani_operativi[0]['node']['codice'], '002')
        self.assertEqual(_piani_operativi[0]['node']['identificativo'], 'TEST_B_002')

        query_3 = """query {
          tuttiGliStati(nome: "bogus"){
            edges {
              node {
                nome,
                codice,
                descrizione,
                pianiOperativi {
                  edges {
                    node {
                      nome
                      codice
                      identificativo
                    }
                  }
                }
              }
            }
          }
        }"""

        # Filtered Query
        result = schema.execute(query_3)
        _query_result = dict(result.data)
        _log(json.dumps(_query_result))
        self.assertIsNone(result.errors)
        self.assertIsNotNone(result.data)

        self.assertTrue('tuttiGliStati' in _query_result)
        self.assertEqual(len(_query_result['tuttiGliStati']['edges']), 4)

        query_4 = """query {
          tuttiIPiani {
            edges {
              node {
                identificativo
                storicoStati {
                  stato {
                    nome
                  }
                  dataApertura
                  dataChiusura
                }
              }
            }
          }
        }"""

        # Filtered Query
        result = schema.execute(query_4)
        self.assertIsNone(result.errors)
        self.assertIsNotNone(result.data)
        _query_result = dict(result.data)
        # _log(json.dumps(_query_result))

        self.assertTrue('tuttiIPiani' in _query_result)
        self.assertEqual(len(_query_result['tuttiIPiani']['edges']), 2)
        _storico_stati = _query_result['tuttiIPiani']['edges'][0]['node']['storicoStati']
        # _log(_storico_stati)
        self.assertEqual(len(_storico_stati), 1)
        self.assertEqual(_storico_stati[0]['stato']['nome'], 'INSERITO')
        self.assertIsNotNone(_storico_stati[0]['dataApertura'])
        self.assertIsNone(_storico_stati[0]['dataChiusura'])

    def test_insert(self):
        from graphene.test import Client
        client = Client(schema)

        # TEST: Creazione Nuovo Stato
        mutation_1 = """mutation CreateStato($input: CreateStatoInput!) {
          createStato(input: $input){
            nuovoStato{
              codice
              nome
              descrizione
            }
            clientMutationId
          }
        }"""

        stato_test_1 = {
          'input': {
            'stato': {
              'codice': '000',
              'nome': 'inserito',
              'descrizione': 'TEST - Creazione nuovo Stato'
            }
          }
        }

        result = client.execute(mutation_1, variables=stato_test_1)
        # _log(result)
        _data = dict(result['data'])
        assert 'errors' not in result
        assert 'nuovoStato' in dict(_data['createStato'])
        _nuovo_stato = dict(dict(_data['createStato'])['nuovoStato'])
        # _log(_nuovo_stato)
        assert _nuovo_stato == {'codice': '000', 'descrizione': 'TEST - Creazione nuovo Stato', 'nome': 'INSERITO'}

        # TEST: Aggiornamen Stato Esistente
        mutation_2 = """
        mutation UpdateStato($input: UpdateStatoInput!) {
          updateStato(input: $input){
            statoAggiornato {
              nome,
              codice,
              descrizione
            }
            clientMutationId
          }
        }"""

        stato_test_2 = {
          'input': {
            'codice': '000',
            'stato': {
              'codice': '000',
              'nome': 'avvio',
              'descrizione': 'AGGIORNATO'
            }
          }
        }

        result = client.execute(mutation_2, variables=stato_test_2)
        # _log(result)
        _data = dict(result['data'])
        assert 'errors' not in result
        assert 'statoAggiornato' in dict(_data['updateStato'])
        _nuovo_stato = dict(dict(_data['updateStato'])['statoAggiornato'])
        # _log(_nuovo_stato)
        assert _nuovo_stato == {'codice': '000', 'descrizione': 'AGGIORNATO', 'nome': 'AVVIO'}

        query_stato = """query {
          tuttiGliStati(codice: "000"){
            edges {
              node {
                nome,
                codice,
                descrizione,
                pianiOperativi {
                  edges {
                    node {
                      nome
                      codice
                      identificativo
                    }
                  }
                }
              }
            }
          }
        }"""

        # Filtered Query
        result = schema.execute(query_stato)
        self.assertIsNone(result.errors)
        self.assertIsNotNone(result.data)
        _query_result = dict(result.data)
        # _log(json.dumps(_query_result))

        self.assertTrue('tuttiGliStati' in _query_result)
        self.assertEqual(len(_query_result['tuttiGliStati']['edges']), 1)

        # Stato == 'TEST_UPDATE'
        self.assertEqual(_query_result['tuttiGliStati']['edges'][0]['node']['nome'], 'AVVIO')
        self.assertEqual(_query_result['tuttiGliStati']['edges'][0]['node']['codice'], '000')
        self.assertTrue('pianiOperativi', _query_result['tuttiGliStati']['edges'][0]['node'])
        _piani_operativi = _query_result['tuttiGliStati']['edges'][0]['node']['pianiOperativi']['edges']
        self.assertEqual(len(_piani_operativi), 0)

        # TEST: Creazione Nuovo Piano Operativo
        mutation_3 = """
        mutation CreatePiano($input: CreatePianoInput!) {
          createPiano(input: $input) {
            nuovoPiano {
              stato {
                codice
              }
              nome
              codice
              identificativo
              dataCreazione
            }
            clientMutationId
          }
        }"""

        piano_test_3 = {
            'input': {
                'pianoOperativo': {
                    'stato': {
                    'nome': 'draft',
                    'codice': '001'
                },
                'nome': 'foo',
                'codice': 'bar',
                'identificativo': 'foo_bar_aa',
                'dataCreazione': '2018-10-10T12:02Z'
            }
          }
        }

        result = client.execute(mutation_3, variables=piano_test_3)
        # _log(result)
        _data = dict(result['data'])
        assert 'errors' not in result
        assert 'nuovoPiano' in dict(_data['createPiano'])
        _nuovo_piano = dict(dict(_data['createPiano'])['nuovoPiano'])
        # _log(_nuovo_piano)
        assert _nuovo_piano == {
            'stato': {
                'codice': '001'
            },
            'nome': 'foo',
            'codice': 'bar',
            'identificativo': 'foo_bar_aa',
            'dataCreazione': '2018-10-10T12:02:00+00:00'
        }

        query_stato = """query {
          tuttiGliStati(codice: "001"){
            edges {
              node {
                nome,
                codice,
                descrizione,
                pianiOperativi {
                  edges {
                    node {
                      nome
                      codice
                      identificativo
                    }
                  }
                }
              }
            }
          }
        }"""

        # Filtered Query
        result = schema.execute(query_stato)
        self.assertIsNone(result.errors)
        self.assertIsNotNone(result.data)
        _query_result = dict(result.data)
        # _log(json.dumps(_query_result))

        self.assertTrue('tuttiGliStati' in _query_result)
        self.assertEqual(len(_query_result['tuttiGliStati']['edges']), 1)

        # Stato == 'DRAFT'
        self.assertEqual(_query_result['tuttiGliStati']['edges'][0]['node']['nome'], 'DRAFT')
        self.assertEqual(_query_result['tuttiGliStati']['edges'][0]['node']['codice'], '001')
        self.assertTrue('pianiOperativi', _query_result['tuttiGliStati']['edges'][0]['node'])
        _piani_operativi = _query_result['tuttiGliStati']['edges'][0]['node']['pianiOperativi']['edges']
        self.assertEqual(len(_piani_operativi), 2)

        self.assertEqual(_piani_operativi[0]['node']['nome'], 'TEST_B')
        self.assertEqual(_piani_operativi[0]['node']['codice'], '002')
        self.assertEqual(_piani_operativi[0]['node']['identificativo'], 'TEST_B_002')

        self.assertEqual(_piani_operativi[1]['node']['nome'], 'foo')
        self.assertEqual(_piani_operativi[1]['node']['codice'], 'bar')
        self.assertEqual(_piani_operativi[1]['node']['identificativo'], 'foo_bar_aa')

        # TEST: Simulate Error
        piano_test_4 = {
            'input': {
                'pianoOperativo': {
                    'stato': {
                    'nome': 'unknown',
                    'codice': 'POCUS'
                },
                'nome': 'foo',
                'codice': 'bar',
                'identificativo': 'foo_bar_aa',
                'dataCreazione': '2018-10-10T12:02Z'
            }
          }
        }

        result = client.execute(mutation_3, variables=piano_test_4)
        # _log(result)
        _data = dict(result['data'])
        assert 'errors' in result
        assert _data == {'createPiano': None}

        # TEST: Update Piano Operativo
        mutation_4 = """mutation UpdatePiano($input: UpdatePianoInput!) {
          updatePiano(input: $input) {
            pianoAggiornato {
              codice
              identificativo
              nome
              stato {
                codice
                nome
              }
            }
            clientMutationId
          }
        }"""

        piano_update_test = {
          'input': {
            'pianoOperativo': {
              'nome': '001',
              'codice': '001',
              'identificativo': 'PIANO_001',
              'stato': {
                'nome': 'draft',
                'codice': '001'
              }
            },
            'codice': '001'
          }
        }

        # Updating multiple times without changing the 'Stato', does not impact the history
        for i in range(0, 2):
            # _log(" ----------------------------------------------------------- %s " % i)
            result = client.execute(mutation_4, variables=piano_update_test)
            # _log(result)
            _data = dict(result['data'])
            assert 'errors' not in result
            assert 'pianoAggiornato' in dict(_data['updatePiano'])
            _nuovo_piano = dict(dict(_data['updatePiano'])['pianoAggiornato'])
            # _log(_nuovo_piano)
            assert _nuovo_piano == {
                'codice': '001',
                'identificativo': 'PIANO_001',
                'nome': '001',
                'stato': {
                    'codice': '001',
                    'nome': 'DRAFT'
                },
            }

            query_4 = """query {
              tuttiIPiani {
                edges {
                  node {
                    identificativo
                    storicoStati {
                      stato {
                        nome
                      }
                      dataApertura
                      dataChiusura
                    }
                  }
                }
              }
            }"""

            # Filtered Query
            result = schema.execute(query_4)
            self.assertIsNone(result.errors)
            self.assertIsNotNone(result.data)
            _query_result = dict(result.data)
            # _log(json.dumps(_query_result))

            self.assertTrue('tuttiIPiani' in _query_result)
            self.assertEqual(len(_query_result['tuttiIPiani']['edges']), 3)
            _storico_stati = _query_result['tuttiIPiani']['edges'][0]['node']['storicoStati']
            # _log(_storico_stati)
            self.assertEqual(len(_storico_stati), 2)
            self.assertEqual(_storico_stati[0]['stato']['nome'], 'INSERITO')
            self.assertIsNotNone(_storico_stati[0]['dataApertura'])
            self.assertIsNotNone(_storico_stati[0]['dataChiusura'])
            self.assertEqual(_storico_stati[1]['stato']['nome'], 'DRAFT')
            self.assertIsNotNone(_storico_stati[1]['dataApertura'])
            self.assertIsNone(_storico_stati[1]['dataChiusura'])
