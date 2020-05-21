import logging

import json
import os
import datetime

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


class UpdatePianoTest(AbstractSerapideProcsTest):

    def test_piano(self):

        self.do_login()

        # self.create_piano_and_promote(TipologiaVAS.VERIFICA)
        response = self.create_piano(DataLoader.IPA_FI)

        content = json.loads(response.content)
        self.codice_piano = content['data']['createPiano']['nuovoPiano']['codice']
        self.codice_vas = content['data']['createPiano']['nuovoPiano']['proceduraVas']['uuid']
        self.codice_avvio = content['data']['createPiano']['nuovoPiano']['proceduraAvvio']['uuid']

        now = _get_datetime()

        prop = DataLoader.uffici_stored[DataLoader.IPA_FI][DataLoader.UFF1].uuid.__str__()

        for nome, val in [
            ("dataDelibera", now.isoformat()),
            ("descrizione", "Piano di test - Eliminazione Piano"),
            ("soggettoProponenteUuid", prop)
        ]:
            self.sendCNV('002_update_piano.query', 'UPDATE PIANO', self.codice_piano, nome, val)

        self.upload('800_upload_file.query', self.codice_piano, TipoRisorsa.DELIBERA)

        self.sendCNV('004_update_procedura_vas.query', 'UPDATE VAS', self.codice_vas, 'tipologia', TipologiaVAS.VERIFICA.name)
        self.upload('005_vas_upload_file.query', self.codice_vas, TipoRisorsa.DOCUMENTO_PRELIMINARE_VERIFICA_VAS)

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

        # Crea Delega
        client_delega = Client()
        self.assertTrue(client_delega.login(username=DataLoader.FC_DELEGATO, password='42'), "Error in login - DELEGATO")
        key = self.get_delega(self.codice_piano, Qualifica.SCA, 'CREA DELEGA SCA by RESP')
        self.bind_delega(client_delega, key)

        self.assertEqual(1, Token.objects.all().count(), 'Missing token')
        self.assertEqual(1, Delega.objects.all().count(), 'Missing delega')

        self.sendCNV('002_update_piano.query', 'UPDATE PIANO', self.codice_piano, "soggettiOperanti", sogg_op)

        # ===  CONTROLLA LISTA SOGGETTI

        response = self.sendCNV('900_get_piani.query', 'GET PIANO', self.codice_piano)
        content = json.loads(response.content)

        piano = content['data']['piani']['edges'][0]['node']
        so = piano['soggettiOperanti']
        self.assertEqual(4, len(so), 'sos len')

        # ===  AGGIORNA LISTA SOGGETTI

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

        self.sendCNV('002_update_piano.query', 'UPDATE PIANO', self.codice_piano, "soggettiOperanti", sogg_op)

        self.assertEqual(0, Token.objects.all().count(), 'Token non eliminato')
        self.assertEqual(0, Delega.objects.all().count(), 'Delega non eliminata')

        response = self.sendCNV('900_get_piani.query', 'GET PIANO', self.codice_piano)
        content = json.loads(response.content)

        piano = content['data']['piani']['edges'][0]['node']
        so = piano['soggettiOperanti']
        self.assertEqual(3, len(so), 'sos len')

        # === SVUOTA LISTA SOGGETTI

        sogg_op = []

        self.sendCNV('002_update_piano.query', 'UPDATE PIANO', self.codice_piano, "soggettiOperanti", sogg_op)

        response = self.sendCNV('900_get_piani.query', 'GET PIANO', self.codice_piano)
        content = json.loads(response.content)

        piano = content['data']['piani']['edges'][0]['node']
        so = piano['soggettiOperanti']
        self.assertEqual(0, len(so), 'sos len')

        # ===  CHECK PROPONENTE

        proponente_read = piano['soggettoProponente']['ufficio']['uuid']
        self.assertEqual(prop, proponente_read, 'Proponente errato')

        # ===  ELIMINA PROPONENTE

        self.sendCNV('002_update_piano.query', 'UPDATE PIANO', self.codice_piano, "soggettoProponenteUuid", '')

        response = self.sendCNV('900_get_piani.query', 'GET PIANO', self.codice_piano)
        content = json.loads(response.content)

        piano = content['data']['piani']['edges'][0]['node']
        proponente_read = piano['soggettoProponente']
        self.assertIsNone(proponente_read, 'Proponente non vuoto')
