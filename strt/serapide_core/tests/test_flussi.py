import logging

from serapide_core.modello.enums import (
    TipoRisorsa,
    TipologiaVAS,
    TipologiaCopianificazione,
    Fase,
)

from .test_serapide_proc import AbstractSerapideProcsTest

logger = logging.getLogger(__name__)


class FlussiTest(AbstractSerapideProcsTest):

    def test_flow_vasverificanoass_ccposticipatanoint_form(self):

        self.do_login()
        self.create_piano_and_promote(TipologiaVAS.VERIFICA) # Promozione effettuata DRAFT --> ANAGRAFICA
        self.avvio_piano(TipologiaCopianificazione.POSTICIPATA)

        self.vas_verifica_no_assoggettamento()

        self.contributi_tecnici()
        self.confcop_no_int()

        self.genio_civile()

        self.check_fase(Fase.ANAGRAFICA)

        self.formazione_piano()

        self.check_fase(Fase.AVVIO)

    def test_flow_ccposticipatanoint_form_vasverificanoass(self):

        self.do_login()
        self.create_piano_and_promote(TipologiaVAS.VERIFICA) # Promozione effettuata DRAFT --> ANAGRAFICA
        self.avvio_piano(TipologiaCopianificazione.POSTICIPATA)

        self.contributi_tecnici()
        self.confcop_no_int()

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
        self.confcop_IR()

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

        self.genio_civile()

        self.check_fase(Fase.ANAGRAFICA)

        self.formazione_piano()

        self.check_fase(Fase.AVVIO)
