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
    def attore(cls, user, organization=None, token=None):
        attore = ""
        if user:
            contact = Contatto.objects.filter(user=user).first()
            if contact:
                if contact.tipologia == 'acvas':
                    attore = TIPOLOGIA_ATTORE[TIPOLOGIA_ATTORE.ac]
                elif contact.tipologia == 'sca':
                    attore = TIPOLOGIA_ATTORE[TIPOLOGIA_ATTORE.sca]
                else:
                    attore = TIPOLOGIA_ATTORE[TIPOLOGIA_ATTORE.unknown]
            if not contact or attore == TIPOLOGIA_ATTORE[TIPOLOGIA_ATTORE.unknown]:
                if token:
                    membership = user.memberships.all().first()
                else:
                    membership = user.memberships.get(organization__code=organization)
                if membership and membership.organization and membership.organization.type:
                    attore = membership.organization.type.name
                else:
                    attore = TIPOLOGIA_ATTORE[TIPOLOGIA_ATTORE.unknown]
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

    fase = models.ForeignKey(Fase, related_name='piani_operativi', on_delete=models.CASCADE)
    storico_fasi = models.ManyToManyField(Fase, through='FasePianoStorico')
    risorse = models.ManyToManyField(Risorsa, through='RisorsePiano')
    azioni = models.ManyToManyField(Azione, through='AzioniPiano')

    autorita_competente_vas = models.ManyToManyField(
        Contatto,
        related_name='autorita_competente_vas',
        through='AutoritaCompetenteVAS'
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
        max_length=20
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


# ############################################################################ #
# Model Signals
# ############################################################################ #
@receiver(post_delete, sender=Contatto)
def delete_roles_and_users(sender, instance, **kwargs):
    if instance.user is not None:
        instance.user.delete()


@receiver(pre_delete, sender=Piano)
def delete_piano_associations(sender, instance, **kwargs):
    AutoritaCompetenteVAS.objects.filter(piano=instance).delete()
    SoggettiSCA.objects.filter(piano=instance).delete()
    instance.risorse.all().delete()
    RisorsePiano.objects.filter(piano=instance).delete()
    for _vas in ProceduraVAS.objects.filter(piano=instance):
        _vas.risorse.all().delete()
        RisorseVas.objects.filter(procedura_vas=_vas).delete()
    for _a in AzioniPiano.objects.filter(piano=instance):
        _a.azione.delete()
    for _t in PianoAuthTokens.objects.filter(piano=instance):
        _t.token.delete()
