import logging
import json

from serapide_core.modello.enums import (
    TipoRisorsa,
    TipologiaVAS,
    TipologiaCopianificazione,
    Fase,
)

from .test_serapide_proc import AbstractSerapideProcsTest, _get_date

logger = logging.getLogger(__name__)


class FlussiTest(AbstractSerapideProcsTest):

    def test_flow_vasverificanoass_ccposticipatanoint_form(self):

        self.do_login()
        self.create_piano_and_promote(TipologiaVAS.VERIFICA) # Promozione effettuata DRAFT --> ANAGRAFICA
        self.avvio_piano(TipologiaCopianificazione.POSTICIPATA)

        self.vas_verifica_no_assoggettamento()

        self.contributi_tecnici()
        self.copianificazione(TipologiaCopianificazione.POSTICIPATA, False)

        self.genio_civile()

        self.check_fase(Fase.ANAGRAFICA)

        self.formazione_piano()

        self.check_fase(Fase.AVVIO)

    def test_flow_ccposticipatanoint_form_vasverificanoass(self):

        self.do_login()
        self.create_piano_and_promote(TipologiaVAS.VERIFICA) # Promozione effettuata DRAFT --> ANAGRAFICA
        self.avvio_piano(TipologiaCopianificazione.POSTICIPATA)

        self.contributi_tecnici()
        self.copianificazione(TipologiaCopianificazione.POSTICIPATA, False)

        self.genio_civile()

        self.formazione_piano()

        self.check_fase(Fase.ANAGRAFICA)

        self.vas_verifica_no_assoggettamento()

        self.check_fase(Fase.AVVIO)

    def test_flow_vasverificanoass_ccposticipataIR_form(self):

        self.do_login()
        self.create_piano_and_promote(TipologiaVAS.VERIFICA) # Promozione effettuata DRAFT --> ANAGRAFICA
        self.avvio_piano(TipologiaCopianificazione.POSTICIPATA)

        self.vas_verifica_no_assoggettamento()

        self.contributi_tecnici()
        self.copianificazione(TipologiaCopianificazione.POSTICIPATA, True)

        self.genio_civile()

        self.check_fase(Fase.ANAGRAFICA)

        self.formazione_piano()

        self.check_fase(Fase.AVVIO)


    def test_flow_vasverificanoass_ccno_form(self):

        self.do_login()
        self.create_piano_and_promote(TipologiaVAS.VERIFICA)
        self.avvio_piano(TipologiaCopianificazione.NON_NECESSARIA)

        self.vas_verifica_no_assoggettamento()

        self.contributi_tecnici()
        self.copianificazione(TipologiaCopianificazione.NON_NECESSARIA, True)

        self.genio_civile()

        self.check_fase(Fase.ANAGRAFICA)

        self.formazione_piano()

        self.check_fase(Fase.AVVIO)

    def test_flow_vasno_ccsiirno_form(self):

        self.do_login()
        self.create_piano_and_promote(TipologiaVAS.NON_NECESSARIA)
        self.avvio_piano(TipologiaCopianificazione.NECESSARIA)

        # self.vas_verifica_no_assoggettamento()

        self.contributi_tecnici()
        self.copianificazione(TipologiaCopianificazione.NECESSARIA, False)

        self.genio_civile()

        self.check_fase(Fase.ANAGRAFICA)

        self.formazione_piano()

        self.check_fase(Fase.AVVIO)

        self.trasmissione_adozione()
        self.adozione_osservazione(richiesta_cp=True)

        self.check_fase(Fase.ADOZIONE)

        self.approvazione()
        self.check_fase(Fase.APPROVAZIONE)

        self.pubblicazione()

        self.check_fase(Fase.APPROVAZIONE)

    def test_flow_vasverificanoass_ccsiirno_form(self):

        self.do_login()
        self.create_piano_and_promote(TipologiaVAS.VERIFICA)
        self.avvio_piano(TipologiaCopianificazione.NECESSARIA)

        self.vas_verifica_no_assoggettamento()

        self.contributi_tecnici()
        self.copianificazione(TipologiaCopianificazione.NECESSARIA, False)

        self.genio_civile()

        self.check_fase(Fase.ANAGRAFICA)

        self.formazione_piano()

        self.check_fase(Fase.AVVIO)

        self.trasmissione_adozione()
        self.adozione_osservazione(richiesta_cp=False)

        self.check_fase(Fase.AVVIO)
        self.adozione_vas()
        self.check_fase(Fase.ADOZIONE)

        self.approvazione()
        self.check_fase(Fase.APPROVAZIONE)

        self.pubblicazione()

        # {"operationName":"AdozioneUploadFile","variables":{"file":null,"codice":"865c0650-1f35-436f-ae00-3995a1128a97","tipo":"osservazioni_privati"}

    def test_flow_vasprocedimento(self):

        self.do_login()
        self.create_piano_and_promote(TipologiaVAS.PROCEDURA_ORDINARIA)  # Promozione effettuata DRAFT --> ANAGRAFICA
        self.avvio_piano(TipologiaCopianificazione.NON_NECESSARIA)

        self.vas_procedimento()

        self.contributi_tecnici()
        self.copianificazione(TipologiaCopianificazione.NON_NECESSARIA, False)

        self.genio_civile()

        self.check_fase(Fase.ANAGRAFICA)

        self.formazione_piano()

        self.check_fase(Fase.AVVIO)

    def test_flow_vasprocedimento_autoclose(self):

        self.do_login()
        self.create_piano_and_promote(TipologiaVAS.PROCEDURA_ORDINARIA)  # Promozione effettuata DRAFT --> ANAGRAFICA
        self.avvio_piano(TipologiaCopianificazione.NON_NECESSARIA)

        self.contributi_tecnici()
        self.copianificazione(TipologiaCopianificazione.NON_NECESSARIA, False)

        self.genio_civile()

        self.formazione_piano()

        self.check_fase(Fase.ANAGRAFICA)

        self.vas_procedimento()

        self.check_fase(Fase.AVVIO)

