#!/usr/bin/env python
# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright 2019, GeoSolutions Sas.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.
#
#########################################################################

from __future__ import unicode_literals
from django.contrib.auth import get_user_model
from django.contrib.sessions.middleware import SessionMiddleware
from serapide_core.schema import schema
from serapide_core.modello.models import Piano, Contatto
from serapide_core.modello.enums import TIPOLOGIA_CONTATTO
from snapshottest.django import TestCase
from graphene.test import Client
from django.test import RequestFactory
import logging


logger = logging.getLogger(__name__)
UserModel = get_user_model()


def _log(msg):
    logger.debug(msg)


class APITestCase(TestCase):

    def setUp(self):
        self.client = Client(schema)
        self.factory = RequestFactory()


class TestPianoGraphQlAPI(APITestCase):

    fixtures = ['serapide_core/tests/fixtures/tests_piano.json']

    FR_RISORSA = """
    fragment Risorsa on RisorsaNode {
        nome
        uuid
        tipo
        dimensione
        downloadUrl
        lastUpdate
        user {
            fiscalCode
            firstName
            lastName
        }
        label
        tooltip
    }
    """
    FR_RISORSE = f"""
    fragment Risorse on RisorsaNodeConnection {{
        edges {{
            node {{
                ...Risorsa
            }}
        }}
    }}
    {FR_RISORSA}
    """
    FR_USER = """
    fragment User on AppUserNode {
        id
        email
        fiscalCode
        firstName
        lastName
        dateJoined
        alertsCount
    }
    """
    FR_CONTATTO = """
    fragment Contatto on ContattoNode{
        nome
        tipologia
        uuid
    }
    """
    FR_AZIONI = """
    fragment Azioni on AzioneNodeConnection {
        edges {
            node {
                order
                tipologia
                stato
                attore
                data
                uuid
                label
                tooltip
                fase
            }
        }
    }
    """
    FR_PIANO = f"""
    fragment Piano on PianoNode {{
        codice
        tipo: tipologia
        descrizione
        lastUpdate
        dataDelibera
        dataCreazione
        dataAccettazione
        dataAvvio
        dataApprovazione
        alertsCount
        numeroProtocolloGenioCivile
        dataProtocolloGenioCivile
        redazioneNormeTecnicheAttuazioneUrl
        compilazioneRapportoAmbientaleUrl
        conformazionePitPprUrl
        monitoraggioUrbanisticoUrl
        azioni {{
            ...Azioni
        }}
        ente {{
            code
            name
            type {{
                tipoente: name
            }}
        }}
        fase {{
            nome
            codice
            descrizione
        }}
        user {{
            ...User
        }}
        risorse(archiviata: false) {{
            ...Risorse
        }}
        autoritaCompetenteVas {{
            edges {{
                node {{
                    ...Contatto
                }}
            }}
        }}
        soggettiSca {{
            edges {{
                node {{
                    ...Contatto
                }}
            }}
        }}
        autoritaIstituzionali {{
            edges {{
                node {{
                    ...Contatto
                }}
            }}
        }}
        altriDestinatari {{
            edges {{
                node {{
                    ...Contatto
                }}
            }}
        }}
        soggettoProponente {{
            ...Contatto
        }}
    }}
    {FR_RISORSE}
    {FR_USER}
    {FR_CONTATTO}
    {FR_AZIONI}
    """

    def _prepare_request_for_test(self, user=None):
        # Request for query execution context
        request = self.factory.post('/')
        request.user = user
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()
        return request

    def test_api_piano_operativo(self):
        """Testing the API for_PIANO OPERATIVO"""
        # Mario Rossi - RUP Firenze
        user = UserModel.objects.get(
            fiscal_code='RSSMRA80A01H501U'
        )
        # ----------------------------------------- #
        # Fase DRAFT
        # ----------------------------------------- #
        # CreatePiano
        create = f"""
        mutation CreatePiano($input: CreatePianoInput!) {{
            createPiano(input: $input) {{
                nuovoPiano {{
                    ...Piano
                }}
            }}
        }}
        {self.FR_PIANO}
        """
        create_input = {
            "input": {
                "pianoOperativo": {
                    "ente": {
                        "code": "FI"
                    },
                    "tipologia": "operativo"
                }
            }
        }
        self.assertMatchSnapshot(
            self.client.execute(
                create,
                variables=create_input,
                context=self._prepare_request_for_test(user)
            )
        )
        # ----------------------------------------- #
        # Fase ANAGRAFICA
        # ----------------------------------------- #
        # UpdatePiano
        update = f"""
        mutation UpdatePiano($input: UpdatePianoInput!) {{
            updatePiano(input: $input) {{
                pianoAggiornato {{
                    ...Piano
                }}
            }}
        }}
        {self.FR_PIANO}
        """
        piano = Piano.objects.order_by('data_creazione').first()
        SP = Contatto.objects.filter(tipologia=TIPOLOGIA_CONTATTO.generico).first()
        AC_VAS = Contatto.objects.filter(tipologia=TIPOLOGIA_CONTATTO.acvas).first()
        update_input = {
            "input": {
                "codice": piano.codice,
                "pianoOperativo": {
                    "dataDelibera": "2019-05-02T22:00:00.000Z",
                    "descrizione": "TEST ATTO PIANO OPERATIVO",
                    "soggettoProponenteUuid": SP.uuid,
                    "autoritaCompetenteVas": AC_VAS.uuid
                }
            }
        }
        self.assertMatchSnapshot(
            self.client.execute(
                update,
                variables=update_input,
                context=self._prepare_request_for_test(user)
            )
        )
        # UploadFile (DELIBERA DI AVVIO DEL PROCEDIMENTO and ALTRI DOCUMENTI)
        # TODO
        # UpdateProceduraVas (PROCEDIMENTO DI VERIFICA SEMPLIFICATA, RICHIESTA VERIFICA DI ASSOGGETTABILITA',
        # PROCEDIMENTO SEMPLIFICATO, PROCEDIMENTO VAS (AVVIO), VAS NON NECESSARIA)
        # TODO
        # VasUploadFile (Relazione motivata per VAS semplificata, Documento preliminare)
        # TODO
        # PromozionePiano
        # TODO
