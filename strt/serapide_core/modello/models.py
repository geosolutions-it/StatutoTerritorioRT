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

import uuid
import rules
import logging
from datetime import datetime

import pytz
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import pre_delete, post_delete
from django.utils.translation import ugettext_lazy as _

from strt_users.models import (
    AppUser,
    Organization,
    Token,
)

from .enums import (FASE,
                    FASE_NEXT,
                    STATO_AZIONE,
                    TIPOLOGIA_VAS,
                    TIPOLOGIA_PIANO,
                    TIPOLOGIA_ATTORE,
                    TIPOLOGIA_AZIONE,
                    TIPOLOGIA_CONTATTO,
                    TIPOLOGIA_CONF_COPIANIFIZAZIONE
                    )


log = logging.getLogger(__name__)


class Fase(models.Model):

    codice = models.CharField(max_length=255, primary_key=True)

    nome = models.CharField(
        choices=FASE,
        default=FASE.draft,
        max_length=20
    )

    descrizione = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "strt_core_fase"
        verbose_name_plural = 'Fasi'

    def __str__(self):
        return '{} [{}]'.format(self.codice, self.nome)


class Risorsa(models.Model):
    """
    Model storing *ptrs to every Piano resource (File) uploaded by users...
    """

    """
    Every "Piano" in the serapide_core application has a unique uuid
    """
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        null=True
    )

    nome = models.TextField(null=False, blank=False)
    file = models.FileField(max_length=500, upload_to='uploads/%Y/%m/%d/')
    tipo = models.TextField(null=False, blank=False)

    dimensione = models.DecimalField(
        null=False,
        blank=False,
        max_digits=19,
        decimal_places=10,
        default=0.0
    )

    descrizione = models.TextField(null=True, blank=True)
    data_creazione = models.DateTimeField(auto_now_add=True, blank=True)
    last_update = models.DateTimeField(auto_now=True, blank=True)

    fase = models.ForeignKey(Fase, on_delete=models.CASCADE)

    user = models.ForeignKey(
        to=AppUser,
        on_delete=models.CASCADE,
        verbose_name=_('user'),
        default=None,
        blank=True,
        null=True
    )

    archiviata = models.BooleanField(null=False, blank=False, default=False)

    @classmethod
    def create(cls, nome, file, tipo, dimensione, fase):
        _file = cls(nome=nome, file=file, tipo=tipo, dimensione=dimensione, fase=fase)
        # do something with the book
        return _file

    class Meta:
        db_table = "strt_core_risorsa"
        verbose_name_plural = 'Risorse'

    def __str__(self):
        return '{} [{}]'.format(self.nome, self.uuid)


class Contatto(models.Model):

    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        null=True
    )

    nome = models.CharField(
        max_length=255,
        null=False,
        blank=False
    )

    tipologia = models.CharField(
        choices=TIPOLOGIA_CONTATTO,
        default=TIPOLOGIA_CONTATTO.unknown,
        max_length=20
    )

    email = models.EmailField(null=False, blank=False)

    ente = models.ForeignKey(
        to=Organization,
        on_delete=models.CASCADE,
        verbose_name=_('ente'),
        null=False,
        blank=False
    )

    user = models.ForeignKey(
        to=AppUser,
        on_delete=models.CASCADE,
        verbose_name=_('user'),
        default=None,
        blank=True,
        null=True
    )

    @classmethod
    def tipologia_contatto(cls, user):
        contact_type = ""
        if user:
            contact = Contatto.objects.filter(user=user).first()
            if contact:
                contact_type = TIPOLOGIA_CONTATTO[contact.tipologia]
        return contact_type

    @classmethod
    def attore(cls, user, organization=None, token=None, tipologia=None):
        attore = ""
        if user:
            if tipologia:
                membership = user.memberships.filter(organization__type__name=tipologia).first()
                if membership and membership.organization:
                    attore = membership.organization.type.name
                else:
                    attore = TIPOLOGIA_ATTORE[TIPOLOGIA_ATTORE.unknown]
            else:
                attore = TIPOLOGIA_ATTORE[TIPOLOGIA_ATTORE.unknown]

            if attore in \
            (TIPOLOGIA_ATTORE[TIPOLOGIA_ATTORE.unknown],
             TIPOLOGIA_ATTORE[TIPOLOGIA_ATTORE.comune],
             TIPOLOGIA_ATTORE[TIPOLOGIA_ATTORE.regione]):
                membership = None
                if token:
                    membership = user.memberships.all().first()
                elif organization:
                    membership = user.memberships.get(organization__code=organization)
                if attore == TIPOLOGIA_ATTORE[TIPOLOGIA_ATTORE.unknown] and \
                membership and membership.organization and membership.organization.type:
                    attore = membership.organization.type.name

                for contact in Contatto.objects.filter(user=user):
                    if contact.tipologia == 'acvas':
                        attore = TIPOLOGIA_ATTORE[TIPOLOGIA_ATTORE.ac]
                    elif contact.tipologia == 'sca':
                        attore = TIPOLOGIA_ATTORE[TIPOLOGIA_ATTORE.sca]
                    elif contact.tipologia == 'generico' and \
                    attore == TIPOLOGIA_ATTORE[TIPOLOGIA_ATTORE.unknown]:
                        attore = TIPOLOGIA_ATTORE[TIPOLOGIA_ATTORE.unknown]
                    elif contact.tipologia == 'ente' and \
                    (attore == TIPOLOGIA_ATTORE[TIPOLOGIA_ATTORE.unknown] or
                     attore != TIPOLOGIA_ATTORE[TIPOLOGIA_ATTORE.regione]):
                        attore = TIPOLOGIA_ATTORE[TIPOLOGIA_ATTORE.enti]
                    elif contact.tipologia == 'genio_civile':
                        attore = TIPOLOGIA_ATTORE[TIPOLOGIA_ATTORE.genio_civile]

        return attore

    class Meta:
        db_table = "strt_core_contatto"
        verbose_name_plural = 'Contatti'

    def __str__(self):
        return '{} <{}> - {} [{}] - {}'.format(
            self.nome, self.email, self.ente, self.uuid, TIPOLOGIA_CONTATTO[self.tipologia])


class Azione(models.Model):

    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        null=True
    )

    tipologia = models.CharField(
        choices=TIPOLOGIA_AZIONE,
        default=TIPOLOGIA_AZIONE.unknown,
        max_length=80
    )

    attore = models.CharField(
        choices=TIPOLOGIA_ATTORE,
        default=TIPOLOGIA_ATTORE.unknown,
        max_length=80
    )

    stato = models.CharField(
        choices=STATO_AZIONE,
        default=STATO_AZIONE.unknown,
        max_length=20
    )

    data = models.DateTimeField(null=True, blank=True)

    order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "strt_core_azione"
        verbose_name_plural = 'Azioni'

    def __str__(self):
        return '{} - {} [{}]'.format(self.attore, TIPOLOGIA_AZIONE[self.tipologia], self.uuid)


# ############################################################################ #
# - Piano
# ############################################################################ #
class Piano(models.Model):
    """
    Every "Piano" in the serapide_core application has a unique uuid
    """
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        null=True
    )

    codice = models.CharField(
        max_length=255,
        null=False,
        blank=False,
        unique=True
    )

    tipologia = models.CharField(
        choices=TIPOLOGIA_PIANO,
        default=TIPOLOGIA_PIANO.unknown,
        max_length=80
    )

    descrizione = models.TextField(null=True, blank=True)
    url = models.URLField(null=True, blank=True, default='')
    data_delibera = models.DateTimeField(null=True, blank=True)
    data_creazione = models.DateTimeField(auto_now_add=True, blank=True)
    data_accettazione = models.DateTimeField(null=True, blank=True)
    data_avvio = models.DateTimeField(null=True, blank=True)
    data_approvazione = models.DateTimeField(null=True, blank=True)
    last_update = models.DateTimeField(auto_now=True, blank=True)

    data_protocollo_genio_civile = models.DateTimeField(null=True, blank=True)
    numero_protocollo_genio_civile = models.TextField(null=True, blank=True)

    fase = models.ForeignKey(Fase, related_name='piani_operativi', on_delete=models.CASCADE)
    storico_fasi = models.ManyToManyField(Fase, through='FasePianoStorico')
    risorse = models.ManyToManyField(Risorsa, through='RisorsePiano')
    azioni = models.ManyToManyField(Azione, through='AzioniPiano')

    redazione_norme_tecniche_attuazione_url = models.URLField(null=True, blank=True, default='')
    compilazione_rapporto_ambientale_url = models.URLField(null=True, blank=True, default='')
    conformazione_pit_ppr_url = models.URLField(null=True, blank=True, default='')
    monitoraggio_urbanistico_url = models.URLField(null=True, blank=True, default='')

    procedura_vas = models.ForeignKey(
        'ProceduraVAS',
        null=True,
        blank=True,
        on_delete=models.DO_NOTHING,
        related_name='vas')

    autorita_competente_vas = models.ManyToManyField(
        Contatto,
        related_name='autorita_competente_vas',
        through='AutoritaCompetenteVAS'
    )

    autorita_istituzionali = models.ManyToManyField(
        Contatto,
        related_name='autorita_istituzionali',
        through='AutoritaIstituzionali'
    )

    altri_destinatari = models.ManyToManyField(
        Contatto,
        related_name='altri_destinatari',
        through='AltriDestinatari'
    )

    soggetti_sca = models.ManyToManyField(
        Contatto,
        related_name='soggetti_sca',
        through='SoggettiSCA'
    )

    soggetto_proponente = models.ForeignKey(
        to=Contatto,
        on_delete=models.DO_NOTHING,
        verbose_name=_('soggetto proponente'),
        default=None,
        blank=True,
        null=True
    )

    ente = models.ForeignKey(
        to=Organization,
        on_delete=models.CASCADE,
        verbose_name=_('ente'),
        default=None,
        blank=True,
        null=True
    )

    user = models.ForeignKey(
        to=AppUser,
        on_delete=models.CASCADE,
        verbose_name=_('user'),
        default=None,
        blank=True,
        null=True
    )

    @property
    def next_phase(self):
        return FASE_NEXT[self.fase.nome]

    @property
    def is_eligible_for_promotion(self):
        _res = rules.test_rule('strt_core.api.fase_{next}_completa'.format(
                               next=self.next_phase),
                               self,
                               self.procedura_vas)
        return _res

    class Meta:
        db_table = "strt_core_piano"
        verbose_name_plural = 'Piani'
        # unique_together = (('nome', 'codice',),)

    def __str__(self):
        return '{} - {} [{}]'.format(self.codice, TIPOLOGIA_PIANO[self.tipologia], self.uuid)

    def post_save(self):
        _now = datetime.utcnow().replace(tzinfo=pytz.utc)
        _full_hist = list(self.storico_fasi.all())
        _prev_state = _full_hist[len(_full_hist) - 1] if len(_full_hist) > 0 else None
        if self.fase:
            if not _prev_state or _prev_state.codice != self.fase.codice:
                _state_hist = FasePianoStorico()
                _state_hist.piano = self
                _state_hist.fase = self.fase
                _state_hist.data_apertura = _now
                _state_hist.save()

                if _prev_state:
                    _state_hist = FasePianoStorico.objects.filter(piano=self, fase=_prev_state).first()
                    _state_hist.data_chiusura = _now
                    _state_hist.save()


class FasePianoStorico(models.Model):
    piano = models.ForeignKey(Piano, on_delete=models.CASCADE)
    fase = models.ForeignKey(Fase, on_delete=models.CASCADE)
    data_apertura = models.DateTimeField()
    data_chiusura = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "strt_core_piano_storico_fasi"


class RisorsePiano(models.Model):
    piano = models.ForeignKey(Piano, on_delete=models.CASCADE)
    risorsa = models.ForeignKey(Risorsa, on_delete=models.CASCADE)

    class Meta:
        db_table = "strt_core_piano_risorse"


class AzioniPiano(models.Model):
    piano = models.ForeignKey(Piano, on_delete=models.CASCADE)
    azione = models.ForeignKey(Azione, on_delete=models.CASCADE)

    class Meta:
        db_table = "strt_core_piano_azioni"


# ############################################################################ #
# - VAS
# ############################################################################ #
class ProceduraVAS(models.Model):

    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        null=True
    )

    tipologia = models.CharField(
        choices=TIPOLOGIA_VAS,
        default=TIPOLOGIA_VAS.unknown,
        max_length=50
    )

    note = models.TextField(null=True, blank=True)
    data_creazione = models.DateTimeField(auto_now_add=True, blank=True)
    data_verifica = models.DateTimeField(null=True, blank=True)
    data_procedimento = models.DateTimeField(null=True, blank=True)
    data_assoggettamento = models.DateTimeField(null=True, blank=True)
    data_approvazione = models.DateTimeField(null=True, blank=True)
    last_update = models.DateTimeField(auto_now=True, blank=True)

    verifica_effettuata = models.BooleanField(null=False, blank=False, default=False)
    procedimento_effettuato = models.BooleanField(null=False, blank=False, default=False)
    non_necessaria = models.BooleanField(null=False, blank=False, default=False)
    assoggettamento = models.BooleanField(null=False, blank=False, default=True)

    pubblicazione_provvedimento_verifica_ap = models.URLField(null=True, blank=True)
    pubblicazione_provvedimento_verifica_ac = models.URLField(null=True, blank=True)

    conclusa = models.BooleanField(null=False, blank=False, default=False)

    risorse = models.ManyToManyField(Risorsa, through='RisorseVas')

    ente = models.ForeignKey(
        to=Organization,
        on_delete=models.CASCADE,
        verbose_name=_('ente'),
        default=None,
        blank=True,
        null=True
    )

    piano = models.ForeignKey(Piano, on_delete=models.CASCADE)

    class Meta:
        db_table = "strt_core_vas"
        verbose_name_plural = 'Procedure VAS'

    def __str__(self):
        return '{} - {} [{}]'.format(self.piano.codice, TIPOLOGIA_VAS[self.tipologia], self.uuid)


class RisorseVas(models.Model):
    procedura_vas = models.ForeignKey(ProceduraVAS, on_delete=models.CASCADE)
    risorsa = models.ForeignKey(Risorsa, on_delete=models.CASCADE)

    class Meta:
        db_table = "strt_core_vas_risorse"


class ParereVerificaVAS(models.Model):

    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        null=True
    )

    data_creazione = models.DateTimeField(auto_now_add=True, blank=True)
    data_invio_parere = models.DateTimeField(null=True, blank=True)
    data_ricezione_parere = models.DateTimeField(null=True, blank=True)

    procedura_vas = models.ForeignKey(ProceduraVAS, on_delete=models.CASCADE)

    inviata = models.BooleanField(null=False, blank=False, default=False)

    user = models.ForeignKey(
        to=AppUser,
        on_delete=models.CASCADE,
        verbose_name=_('user'),
        default=None,
        blank=True,
        null=True
    )

    class Meta:
        db_table = "strt_core_pareri_verifica_vas"
        verbose_name_plural = 'Pareri Verifica VAS'

    def __str__(self):
        return '{} - [{}]'.format(self.procedura_vas, self.uuid)


class ConsultazioneVAS(models.Model):

    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        null=True
    )

    data_creazione = models.DateTimeField(auto_now_add=True, blank=True)
    data_scadenza = models.DateTimeField(null=True, blank=True)
    data_ricezione_pareri = models.DateTimeField(null=True, blank=True)

    data_avvio_consultazioni_sca = models.DateTimeField(null=True, blank=True)
    avvio_consultazioni_sca = models.BooleanField(null=False, blank=False, default=False)

    procedura_vas = models.ForeignKey(ProceduraVAS, on_delete=models.CASCADE)

    user = models.ForeignKey(
        to=AppUser,
        on_delete=models.CASCADE,
        verbose_name=_('user'),
        default=None,
        blank=True,
        null=True
    )

    class Meta:
        db_table = "strt_core_consultazioni_vas"
        verbose_name_plural = 'Consultazioni VAS'

    def __str__(self):
        return '{} - [{}]'.format(self.procedura_vas, self.uuid)


class ParereVAS(models.Model):

    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        null=True
    )

    data_creazione = models.DateTimeField(auto_now_add=True, blank=True)
    data_invio_parere = models.DateTimeField(null=True, blank=True)
    data_ricezione_parere = models.DateTimeField(null=True, blank=True)

    procedura_vas = models.ForeignKey(ProceduraVAS, on_delete=models.CASCADE)
    consultazione_vas = models.ForeignKey(ConsultazioneVAS, on_delete=models.CASCADE)

    inviata = models.BooleanField(null=False, blank=False, default=False)

    user = models.ForeignKey(
        to=AppUser,
        on_delete=models.CASCADE,
        verbose_name=_('user'),
        default=None,
        blank=True,
        null=True
    )

    class Meta:
        db_table = "strt_core_pareri_vas"
        verbose_name_plural = 'Pareri VAS'

    def __str__(self):
        return '{} - [{}]'.format(self.procedura_vas, self.uuid)


class AutoritaCompetenteVAS(models.Model):
    autorita_competente = models.ForeignKey(Contatto, on_delete=models.DO_NOTHING)
    piano = models.ForeignKey(Piano, on_delete=models.DO_NOTHING)

    class Meta:
        db_table = "strt_core_autorita_competente"

    def __str__(self):
        return '{} <---> {}'.format(self.piano.codice, self.autorita_competente.email)


class SoggettiSCA(models.Model):
    soggetto_sca = models.ForeignKey(Contatto, on_delete=models.DO_NOTHING)
    piano = models.ForeignKey(Piano, on_delete=models.DO_NOTHING)

    class Meta:
        db_table = "strt_core_soggetti_sca"

    def __str__(self):
        return '{} <---> {}'.format(self.piano.codice, self.soggetto_sca.email)


class AutoritaIstituzionali(models.Model):
    autorita_istituzionale = models.ForeignKey(Contatto, on_delete=models.DO_NOTHING)
    piano = models.ForeignKey(Piano, on_delete=models.DO_NOTHING)

    class Meta:
        db_table = "strt_core_autorita_istituzionale"

    def __str__(self):
        return '{} <---> {}'.format(self.piano.codice, self.autorita_istituzionale.email)


class AltriDestinatari(models.Model):
    altro_destinatario = models.ForeignKey(Contatto, on_delete=models.DO_NOTHING)
    piano = models.ForeignKey(Piano, on_delete=models.DO_NOTHING)

    class Meta:
        db_table = "strt_core_altri_destinatari"

    def __str__(self):
        return '{} <---> {}'.format(self.piano.codice, self.altro_destinatario.email)


class PianoAuthTokens(models.Model):
    piano = models.ForeignKey(Piano, on_delete=models.CASCADE)
    token = models.ForeignKey(Token, on_delete=models.CASCADE)

    class Meta:
        db_table = "strt_core_piano_auth_tokens"
        unique_together = ('piano', 'token')

    def __str__(self):
        return '{} <---> {}'.format(self.piano.codice, self.token.key)


# ############################################################################ #
# - Avvio
# ############################################################################ #
class ProceduraAvvio(models.Model):

    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        null=True
    )

    conferenza_copianificazione = models.CharField(
        choices=TIPOLOGIA_CONF_COPIANIFIZAZIONE,
        default=TIPOLOGIA_CONF_COPIANIFIZAZIONE.necessaria,
        max_length=20
    )

    data_creazione = models.DateTimeField(auto_now_add=True, blank=True)
    data_scadenza_risposta = models.DateTimeField(null=True, blank=True)

    garante_nominativo = models.TextField(null=True, blank=True)
    garante_pec = models.EmailField(null=True, blank=True)

    notifica_genio_civile = models.BooleanField(null=False, blank=False, default=False)
    richiesta_integrazioni = models.BooleanField(null=False, blank=False, default=False)
    messaggio_integrazione = models.TextField(null=True, blank=True)

    conclusa = models.BooleanField(null=False, blank=False, default=False)

    risorse = models.ManyToManyField(Risorsa, through='RisorseAvvio')

    ente = models.ForeignKey(
        to=Organization,
        on_delete=models.CASCADE,
        verbose_name=_('ente'),
        default=None,
        blank=True,
        null=True
    )

    piano = models.ForeignKey(Piano, on_delete=models.CASCADE)

    class Meta:
        db_table = "strt_core_avvio"
        verbose_name_plural = 'Procedure Avvio'

    def __str__(self):
        return '{} - {} [{}]'.format(self.piano.codice, self.ente, self.uuid)


class RisorseAvvio(models.Model):
    procedura_avvio = models.ForeignKey(ProceduraAvvio, on_delete=models.CASCADE)
    risorsa = models.ForeignKey(Risorsa, on_delete=models.CASCADE)

    class Meta:
        db_table = "strt_core_avvio_risorse"


class ConferenzaCopianificazione(models.Model):

    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        null=True
    )

    id_pratica = models.TextField(null=True, blank=True)

    data_richiesta_conferenza = models.DateTimeField(null=True, blank=True)
    data_scadenza_risposta = models.DateTimeField(null=True, blank=True)
    data_chiusura_conferenza = models.DateTimeField(null=True, blank=True)

    piano = models.ForeignKey(Piano, on_delete=models.CASCADE)

    risorse = models.ManyToManyField(Risorsa, through='RisorseCopianificazione')

    class Meta:
        db_table = "strt_core_conferenza_copianificazione"
        verbose_name_plural = 'Conferenze di Copianificazione'

    def __str__(self):
        return '{} - {} [{}]'.format(self.piano.codice, self.piano.ente, self.uuid)


class RisorseCopianificazione(models.Model):
    conferenza_copianificazione = models.ForeignKey(ConferenzaCopianificazione, on_delete=models.CASCADE)
    risorsa = models.ForeignKey(Risorsa, on_delete=models.CASCADE)

    class Meta:
        db_table = "strt_core_risorse_copianificazione"


# ############################################################################ #
# Model Signals
# ############################################################################ #
@receiver(post_delete, sender=Contatto)
def delete_roles_and_users(sender, instance, **kwargs):
    if instance.user is not None:
        try:
            instance.user.delete()
        except BaseException:
            pass


@receiver(pre_delete, sender=Piano)
def delete_piano_associations(sender, instance, **kwargs):
    AutoritaCompetenteVAS.objects.filter(piano=instance).delete()
    AutoritaIstituzionali.objects.filter(piano=instance).delete()
    AltriDestinatari.objects.filter(piano=instance).delete()
    SoggettiSCA.objects.filter(piano=instance).delete()
    instance.risorse.all().delete()
    RisorsePiano.objects.filter(piano=instance).delete()
    for _vas in ProceduraVAS.objects.filter(piano=instance):
        _vas.risorse.all().delete()
        RisorseVas.objects.filter(procedura_vas=_vas).delete()
    for _avvio in ProceduraAvvio.objects.filter(piano=instance):
        _avvio.risorse.all().delete()
        RisorseAvvio.objects.filter(procedura_avvio=_avvio).delete()
    for _cc in ConferenzaCopianificazione.objects.filter(piano=instance):
        _cc.risorse.all().delete()
        RisorseCopianificazione.objects.filter(conferenza_copianificazione=_cc).delete()
    for _a in AzioniPiano.objects.filter(piano=instance):
        _a.azione.delete()
    for _t in PianoAuthTokens.objects.filter(piano=instance):
        _t.token.delete()
