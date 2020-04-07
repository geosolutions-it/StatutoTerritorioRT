import logging

import json
import os
import datetime

from django.test import TestCase, Client

from serapide_core.modello.enums import (
    TipoRisorsa,
    TipologiaVAS,
    TipologiaCopianificazione,
    Fase,
)

from serapide_core.modello.models import (
    Delega,
)

from strt_users.enums import (
    Qualifica,
)

from strt_users.models import (
    Token
)

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


class DeletePianoTest(AbstractSerapideProcsTest):

    def test_delete_piano(self):

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

        # Crea Delega
        client = Client()
        self.assertTrue(client.login(username=DataLoader.FC_DELEGATO, password='42'), "Error in login - DELEGATO")
        key = self.get_delega(self.codice_piano, Qualifica.GC, 'CREA DELEGA GC by RESP')
        self.bind_delega(client, key)
        self.assertEqual(1, Token.objects.all().count(), 'Token non creato')
        self.assertEqual(1, Delega.objects.all().count(), 'Delega non creata')

        self.sendCNV('001d_delete_piano.query', 'DELETE PIANO', self.codice_piano,
                     client=self.client_sca, expected_code=403)
        self.sendCNV('001d_delete_piano.query', 'DELETE PIANO', self.codice_piano)

        self.assertEqual(0, Token.objects.all().count(), 'Token non eliminato')
        self.assertEqual(0, Delega.objects.all().count(), 'Delega non eliminata')
