import logging

import json
import os
import datetime
from collections import Counter

from django.test import TestCase, Client

from serapide_core.modello.enums import (
    TipoRisorsa,
    TipologiaVAS,
    TipologiaCopianificazione,
    Fase,
)

from serapide_core.modello.models import (
    Piano,
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
from ..api.auth.user import get_UffAssTok

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


class MiscTest(AbstractSerapideProcsTest):

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

        self.upload('800_upload_file.query', self.codice_piano, TipoRisorsa.DELIBERA)

        self.sendCNV('004_update_procedura_vas.query', 'UPDATE VAS', self.codice_vas, 'tipologia', TipologiaVAS.VERIFICA.name)
        self.upload('005_vas_upload_file.query', self.codice_vas, TipoRisorsa.DOCUMENTO_PRELIMINARE_VERIFICA_VAS)

        sogg_op = []
        for ente, uff, q in [
            (DataLoader.IPA_RT, DataLoader.UFF_GC_TN, Qualifica.GC),
            (DataLoader.IPA_RT, DataLoader.UFF_PIAN, Qualifica.PIAN),
            (DataLoader.IPA_PI, DataLoader.UFF1, Qualifica.AC),
            (DataLoader.IPA_LU, DataLoader.UFF1, Qualifica.SCA),
        ]:
            sogg_op.append({
                'ufficioUuid': DataLoader.uffici_stored[ente][uff].uuid.__str__(),
                'qualifica': q.name})

        self.sendCNV('002_update_piano.query', 'UPDATE PIANO', self.codice_piano, "soggettiOperanti", sogg_op)

        piano = Piano.objects.get(codice=self.codice_piano)
        self.assertIsNotNone(piano)

        for req, uff_expected, ass_expected in [
            ([Qualifica.AC,],
                [DataLoader.uffici_stored[DataLoader.IPA_PI][DataLoader.UFF1],],
                [DataLoader.utenti_stored[DataLoader.FC_AC1],]),
            ([Qualifica.SCA,],
                [DataLoader.uffici_stored[DataLoader.IPA_LU][DataLoader.UFF1],],
                [DataLoader.utenti_stored[DataLoader.FC_ACTIVE2],
                 DataLoader.utenti_stored[DataLoader.FC_SCA1],
                ]),
            ([Qualifica.AC, Qualifica.SCA,],
                [DataLoader.uffici_stored[DataLoader.IPA_PI][DataLoader.UFF1],
                 DataLoader.uffici_stored[DataLoader.IPA_LU][DataLoader.UFF1],],
                [DataLoader.utenti_stored[DataLoader.FC_AC1],
                 DataLoader.utenti_stored[DataLoader.FC_ACTIVE2],
                 DataLoader.utenti_stored[DataLoader.FC_SCA1],
                ]),
            ([Qualifica.OPCOM, ],
             [DataLoader.uffici_stored[DataLoader.IPA_FI][DataLoader.UFF1], ],
             [DataLoader.utenti_stored[DataLoader.FC_RUP_RESP], ]),
        ]:
            uff, ass, tok = get_UffAssTok(piano, req)
            self.assertEqual(len(uff_expected), len(uff), 'Numero uffici non corretto per qualifiche {}'.format(req))
            self.assertEqual(len(ass_expected), len(ass), 'Numero assegnatari non corretto')

            self.assertEqual(uff_expected, uff, 'Lista Uffici non corretta')
            self.assertEqual(Counter(ass_expected), Counter(ass), 'Lista assegnatari non corretta')

        # # Crea Delega
        # client = Client()
        # self.assertTrue(client.login(username=DataLoader.FC_DELEGATO, password='42'), "Error in login - DELEGATO")
        # key = self.get_delega(self.codice_piano, Qualifica.GC, 'CREA DELEGA GC by RESP')
        # self.bind_delega(client, key)
        # self.assertEqual(1, Token.objects.all().count(), 'Token non creato')
        # self.assertEqual(1, Delega.objects.all().count(), 'Delega non creata')
        #
        # self.sendCNV('001d_delete_piano.query', 'DELETE PIANO', self.codice_piano,
        #              client=self.client_sca, expected_code=403)
        # self.sendCNV('001d_delete_piano.query', 'DELETE PIANO', self.codice_piano)
        #
        # self.assertEqual(0, Token.objects.all().count(), 'Token non eliminato')
        # self.assertEqual(0, Delega.objects.all().count(), 'Delega non eliminata')

