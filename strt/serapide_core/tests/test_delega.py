import logging

import json
import os
import datetime
from ast import dump
from contextlib import redirect_stderr
from functools import partial

from django.test import TestCase, Client


from serapide_core.modello.enums import (
    TipoRisorsa,
    TipologiaVAS,
)
from serapide_core.modello.models import (
    Delega,
)

from strt_users.enums import (
    Qualifica,
)
from strt_users.models import Token

from .test_data_setup import DataLoader
from .test_serapide_abs import AbstractSerapideTest, dump_result
from .test_serapide_proc import AbstractSerapideProcsTest

logger = logging.getLogger(__name__)

this_path = os.path.dirname(__file__)


def _get_datetime(**argw_delta):
    date = datetime.datetime.now()
    date = date.replace(microsecond=0)
    if argw_delta:
        date = date + datetime.timedelta(**argw_delta)
    return date


def _get_date(**argw_delta):
    date = _get_datetime(**argw_delta)
    date = date.replace(hour=0, minute=0, second=0, microsecond=0)
    return date


class DelegaTest(AbstractSerapideProcsTest):

    def test_crea_delega(self):

        self.do_login()

        # self.create_piano_and_promote(TipologiaVAS.VERIFICA)
        response = self.create_piano(DataLoader.IPA_FI)

        content = json.loads(response.content)
        self.codice_piano = content['data']['createPiano']['nuovoPiano']['codice']
        self.codice_vas = content['data']['createPiano']['nuovoPiano']['proceduraVas']['uuid']
        self.codice_avvio = content['data']['createPiano']['nuovoPiano']['proceduraAvvio']['uuid']

        now = _get_datetime()

        for nome, val in [
            ("dataDelibera", now.isoformat()),
            ("descrizione", "Piano di test - Eliminazione Piano"),
            ("soggettoProponenteUuid", DataLoader.uffici_stored[DataLoader.IPA_FI][DataLoader.UFF1].uuid.__str__())
        ]:
            self.sendCNV('002_update_piano.query', 'UPDATE PIANO', self.codice_piano, nome, val)

        self.upload('003_upload_file.query', self.codice_piano, TipoRisorsa.DELIBERA)

        self.sendCNV('004_update_procedura_vas.query', 'UPDATE VAS', self.codice_vas, 'tipologia', TipologiaVAS.VERIFICA.name)
        self.upload('005_vas_upload_file.query', self.codice_vas, TipoRisorsa.VAS_VERIFICA)

        sogg_op = []
        sogg_op.append({
            'ufficioUuid': DataLoader.uffici_stored[DataLoader.IPA_RT][DataLoader.UFF_GC_TN].uuid.__str__(),
            'qualifica': Qualifica.GC.name})
        sogg_op.append({
            'ufficioUuid': DataLoader.uffici_stored[DataLoader.IPA_RT][DataLoader.UFF_PIAN].uuid.__str__(),
            'qualifica': Qualifica.PIAN.name})
        sogg_op.append({
            'ufficioUuid': DataLoader.uffici_stored[DataLoader.IPA_PI][DataLoader.UFF1].uuid.__str__(),
            'qualifica': Qualifica.AC.name})
        sogg_op.append({
            'ufficioUuid': DataLoader.uffici_stored[DataLoader.IPA_LU][DataLoader.UFF1].uuid.__str__(),
            'qualifica': Qualifica.SCA.name})

        self.sendCNV('002_update_piano.query', 'UPDATE PIANO', self.codice_piano, "soggettiOperanti", sogg_op)
        # self.sendCNV('006_promozione.query', 'PROMUOVI PIANO', self.codice_piano)

        # --------------------------------------------------------------------------------------------------------------
        # Crea Delega - by RESPONSABILE
        client = Client()
        self.assertTrue(client.login(username=DataLoader.FC_DELEGATO, password='42'), "Error in login - DELEGATO")
        key_ac = self.get_delega(self.codice_piano, Qualifica.AC, 'CREA DELEGA AC by RESP')
        self.bind_delega(client, key_ac)
        self.assertEqual(1, Token.objects.all().count(), 'Token non creato')
        self.assertEqual(1, Delega.objects.all().count(), 'Delega non creata')

        # GET deleghe da responsabile:
        # check: esiste solo la delega creata dal responsabile
        # check: key è popolato
        response = self.sendCNV('906_get_deleghe.query', 'GET DELEGHE', self.codice_piano)
        content = json.loads(response.content)
        piano = content['data']['piani']['edges'][0]['node']
        for so in piano['soggettiOperanti']:
            q = so['qualificaUfficio']['qualifica']
            deleghe = so['deleghe']
            if q == Qualifica.RESP.name:
                self.assertEqual(1, len(deleghe))
                self.assertEqual(key_ac, deleghe[0]['key'])
                self.assertIsNotNone(deleghe[0]['utente'])
            else:
                self.assertEqual(0, len(deleghe))

        # GET deleghe da altro soggetto operante:
        # check: esiste solo la delega creata dal responsabile
        # check: key NON è popolato
        response = self.sendCNV('906_get_deleghe.query', 'GET DELEGHE', self.codice_piano, client=self.client_sca)
        content = json.loads(response.content)
        piano = content['data']['piani']['edges'][0]['node']
        for so in piano['soggettiOperanti']:
            q = so['qualificaUfficio']['qualifica']
            deleghe = so['deleghe']
            if q == Qualifica.RESP.name:
                self.assertEqual(1, len(deleghe))
                self.assertIsNone(deleghe[0]['key'])  # key non visibile
                self.assertIsNotNone(deleghe[0]['utente'])
            else:
                self.assertEqual(0, len(deleghe))

        # --------------------------------------------------------------------------------------------------------------
        # Crea Delega - by SCA
        # client = Client()
        # self.assertTrue(client.login(username=DataLoader.FC_DELEGATO, password='42'), "Error in login - DELEGATO")
        key_sca = self.get_delega(self.codice_piano, Qualifica.SCA, 'CREA DELEGA SCA', client=self.client_sca)
        self.bind_delega(client, key_sca)
        self.assertEqual(2, Token.objects.all().count(), 'Token non creato')
        self.assertEqual(2, Delega.objects.all().count(), 'Delega non creata')

        # GET deleghe da responsabile:
        # check: esistono 2 deleghe
        # check: key è popolato per tutte le deleghe
        response = self.sendCNV('906_get_deleghe.query', 'GET DELEGHE', self.codice_piano)
        content = json.loads(response.content)
        piano = content['data']['piani']['edges'][0]['node']
        for so in piano['soggettiOperanti']:
            q = so['qualificaUfficio']['qualifica']
            deleghe = so['deleghe']
            if q == Qualifica.RESP.name:
                self.assertEqual(1, len(deleghe))
                self.assertEqual(key_ac, deleghe[0]['key'])
                self.assertIsNotNone(deleghe[0]['utente'])
            elif q == Qualifica.SCA.name:
                self.assertEqual(1, len(deleghe))
                self.assertEqual(key_sca, deleghe[0]['key'])
                self.assertIsNotNone(deleghe[0]['utente'])
            else:
                self.assertEqual(0, len(deleghe))

        # GET deleghe da soggetto operante creatore della delega:
        # check: esistono 2 deleghe
        # check: key è popolato per la delega creata da SCA, none per quella creata da RESP
        response = self.sendCNV('906_get_deleghe.query', 'GET DELEGHE', self.codice_piano, client=self.client_sca)
        content = json.loads(response.content)
        piano = content['data']['piani']['edges'][0]['node']
        for so in piano['soggettiOperanti']:
            q = so['qualificaUfficio']['qualifica']
            deleghe = so['deleghe']
            if q == Qualifica.RESP.name:
                self.assertEqual(1, len(deleghe))
                self.assertIsNone(deleghe[0]['key'])  # key non visibile
                self.assertIsNotNone(deleghe[0]['utente'])
            elif q == Qualifica.SCA.name:
                self.assertEqual(1, len(deleghe))
                self.assertEqual(key_sca, deleghe[0]['key'])
                self.assertIsNotNone(deleghe[0]['utente'])
            else:
                self.assertEqual(0, len(deleghe))

        # GET deleghe da altro soggetto operante:
        # check: esistono 2 deleghe
        # check: key NON è popolato
        response = self.sendCNV('906_get_deleghe.query', 'GET DELEGHE', self.codice_piano, client=self.client_gc)
        content = json.loads(response.content)
        piano = content['data']['piani']['edges'][0]['node']
        for so in piano['soggettiOperanti']:
            q = so['qualificaUfficio']['qualifica']
            deleghe = so['deleghe']
            if q == Qualifica.RESP.name:
                self.assertEqual(1, len(deleghe))
                self.assertIsNone(deleghe[0]['key'])  # key non visibile
                self.assertIsNotNone(deleghe[0]['utente'])
            elif q == Qualifica.SCA.name:
                self.assertEqual(1, len(deleghe))
                self.assertIsNone(deleghe[0]['key'])  # key non visibile
                self.assertIsNotNone(deleghe[0]['utente'])
            else:
                self.assertEqual(0, len(deleghe))

        self.sendCNV('101_delete_delega.query', 'DELETE_DELEGA', key_sca, client=self.client_pian, expected_code=403)
        self.sendCNV('101_delete_delega.query', 'DELETE_DELEGA', 'xxx', expected_code=404)

        self.sendCNV('101_delete_delega.query', 'DELETE_DELEGA', key_sca)
        self.assertEqual(1, Token.objects.all().count(), 'Token non eliminato')
        self.assertEqual(1, Delega.objects.all().count(), 'Delega non eliminato')
