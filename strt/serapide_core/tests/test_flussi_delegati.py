import logging
import json

from django.test import TestCase, Client

from .test_data_setup import DataLoader

from serapide_core.modello.enums import (
    TipoRisorsa,
    TipologiaVAS,
    TipologiaCopianificazione,
    Fase,
)
from strt_users.enums import Qualifica

from .test_flussi import FlussiTest

logger = logging.getLogger(__name__)


class FlussiDelegatiTest(FlussiTest):

    BASE_URL = "/serapide/"

    def create_piano_and_promote(self, tipovas: TipologiaVAS):
        super(FlussiDelegatiTest, self).create_piano_and_promote(tipovas)

        client = Client()
        self.assertTrue(client.login(username=DataLoader.FC_DELEGATO, password='42'), "Error in login - DELEGATO")

        key = self.get_delega(self.codice_piano, Qualifica.GC, 'CREA DELEGA GC by RESP')
        self.bind_delega(client, key)

        key = self.get_delega(self.codice_piano, Qualifica.PIAN, 'CREA DELEGA PIAN by RESP')
        self.bind_delega(client, key)

        key = self.get_delega(self.codice_piano, Qualifica.AC, 'CREA DELEGA AC', client=self.client_ac)
        self.bind_delega(client, key)

        key = self.get_delega(self.codice_piano, Qualifica.SCA, 'CREA DELEGA SCA', client=self.client_sca)
        self.bind_delega(client, key)

        self.client_gc = client
        self.client_pian = client
        self.client_ac = client
        self.client_sca = client

    def get_delega(self, codice_piano, qualifica: Qualifica, msg, client=None):
        response = self.send('100_crea_delega.query', msg,
                             replace_args={'codice': codice_piano, 'qualifica': qualifica.name, 'mail': 'fkame@mail'},
                             client=client)

        content = json.loads(response.content)
        key = content['data']['creaDelega']['token']
        return key

    def bind_delega(self, client, key):

        response = client.post("/serapide/?token="+key)

        self.assertEqual(302, response.status_code, 'Delega binding failed')


