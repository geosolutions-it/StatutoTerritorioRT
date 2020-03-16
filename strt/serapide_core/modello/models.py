# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright 2019, GeoSolutions SAS.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.
#
#########################################################################

import os
import pytz
import uuid

from django.core.exceptions import ValidationError

import rules
import logging
from datetime import datetime

from django.db import models
from django.db.models import Q
from django.core import checks
from django.utils import timezone
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import pre_delete  # , post_delete
from model_utils import Choices

from strt_users.models import (
    Ente,
    Ufficio,
    QualificaUfficio,
    Utente,
    Token,
    Assegnatario
)

from strt_users.enums import (
    Qualifica,
    Profilo,
    QualificaRichiesta,
    TipoEnte,
)

from .enums import (Fase,
                    STATO_AZIONE,
                    TipologiaVAS,
                    TipologiaPiano,
                    TIPOLOGIA_AZIONE,
                    # TIPOLOGIA_CONTATTO,
                    TipologiaCopianificazione,
                    # TIPOLOGIA_CONF_COPIANIFIZAZIONE
                    )


log = logging.getLogger(__name__)


class Risorsa(models.Model):
    """
    Model storing *ptrs to every Piano resource (File) uploaded by users...
    """

    """
    Every "Risorsa" in the serapide_core application has a unique uuid
    """
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        null=True
    )

    nome = models.TextField(null=False, blank=False)
    file = models.FileField(max_length=500, upload_to='uploads/%Y/%m/%d/')
    tipo = models.TextField(null=False, blank=False) # TODO usare enum

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

    # fase = models.ForeignKey(Fase, on_delete=models.CASCADE)
    fase = models.CharField(
        choices=Fase.create_choices(),
        default=Fase.UNKNOWN,
        max_length=Fase.get_max_len()
    )

    user = models.ForeignKey(
        to=Utente,
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

    @classmethod
    def from_db(cls, db, field_names, values):
        instance = super(Risorsa, cls).from_db(db, field_names, values)
        instance.fase = Fase.fix_enum(instance.fase)
        return instance



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
        choices=TipologiaPiano.create_choices(),
        default=TipologiaPiano.UNKNOWN,
        max_length=TipologiaPiano.get_max_len()
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

    # fase = models.ForeignKey(Fase, related_name='piani_operativi', on_delete=models.CASCADE)
    fase = models.CharField(
        choices=Fase.create_choices(),
        default=Fase.UNKNOWN,
        max_length=Fase.get_max_len()
    )
    #¯storico_fasi = models.ManyToManyField(Fase, through='FasePianoStorico')
    risorse = models.ManyToManyField(Risorsa, through='RisorsePiano')
    # azioni = models.ManyToManyField(Azione, through='AzioniPiano')

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

    procedura_avvio = models.ForeignKey(
        'ProceduraAvvio',
        null=True,
        blank=True,
        on_delete=models.DO_NOTHING,
        related_name='avvio')

    procedura_adozione = models.ForeignKey(
        'ProceduraAdozione',
        null=True,
        blank=True,
        on_delete=models.DO_NOTHING,
        related_name='adozione')

    procedura_approvazione = models.ForeignKey(
        'ProceduraApprovazione',
        null=True,
        blank=True,
        on_delete=models.DO_NOTHING,
        related_name='approvazione')

    procedura_pubblicazione = models.ForeignKey(
        'ProceduraPubblicazione',
        null=True,
        blank=True,
        on_delete=models.DO_NOTHING,
        related_name='pubblicazione')

    soggetto_proponente = models.ForeignKey(
        to=QualificaUfficio,
        on_delete=models.DO_NOTHING,
        verbose_name=_('soggetto proponente'),
        default=None,
        blank=True,
        null=True
    )

    ente = models.ForeignKey(
        to=Ente,
        on_delete=models.CASCADE,
        verbose_name=_('ente'),
        # default=None,
        # blank=True,
        # null=True
    )

    responsabile = models.ForeignKey(
        to=Utente,
        on_delete=models.CASCADE,
        verbose_name=_('user'),
        default=None,
        blank=True,
        null=True
    )

    def chiudi_pendenti(self, attesa=True, necessaria=True):
        # - Complete Current Actions
        _now = datetime.now(timezone.get_current_timezone())
        stati = []
        if attesa:
            stati.append(STATO_AZIONE.attesa)
        if necessaria:
            stati.append(STATO_AZIONE.necessaria)

        for azione in Azione.objects.filter(piano=self, stato__in=stati):
            log.warning('Chiusura forzata azione pendente {n}:{q}[{s}]'.format(n=azione.tipologia, q=azione.qualifica_richiesta.name, s=azione.stato))
            chiudi_azione(azione, data=_now)

    # @property
    # def next_phase(self):
    #     # return FASE_NEXT[self.fase.nome]
    #     return self.fase.get_next()

    # @property
    # def is_eligible_for_promotion(self):
    #     _res = rules.test_rule('strt_core.api.fase_{next}_completa'.format(
    #                            next=self.next_phase),
    #                            self,
    #                            self.procedura_vas)
    #     return _res

    class Meta:
        db_table = "strt_core_piano"
        verbose_name_plural = 'Piani'
        # unique_together = (('nome', 'codice',),)

        # Next constr would generate a "django.core.exceptions.FieldError: Joined field references are not permitted in this query"
        # constraints = [
        #     models.CheckConstraint(
        #         name='Ente deve essere un comune',
        #         check= Q(ente__tipo = TipoEnte.COMUNE))
        # ]

    # OVERRIDE
    def clean_fields(self, exclude=None):
        super().clean_fields(exclude=exclude)
        self._check_ente_comune()

    def _check_ente_comune(self):
        if self.ente.tipo != TipoEnte.COMUNE:
            raise ValidationError('Ente deve essere un Comune')

    def __str__(self):
        return '{} - {} [{}]'.format(self.codice, self.tipologia, self.uuid)

    def save(self, *args, **kwargs):
        self._check_ente_comune()
        super().save(*args, **kwargs)  # Call the "real" save() method.

    # OVERRIDE
    def post_save(self):
        if self.fase:

            # _full_hist = list(self.storico_fasi.all())
            _full_hist = FasePianoStorico.get_all_by_piano(self)
            _prev_state = _full_hist[len(_full_hist) - 1] if len(_full_hist) > 0 else None  # TODO CHECK: senza ordinamento?!?!?

            if not _prev_state or _prev_state.fase != self.fase:
                _now = datetime.utcnow().replace(tzinfo=pytz.utc)

                _state_hist = FasePianoStorico()
                _state_hist.piano = self
                _state_hist.fase = self.fase
                _state_hist.data_apertura = _now
                _state_hist.save()

                if _prev_state:
                    _state_hist = FasePianoStorico.objects.filter(piano=self, fase=_prev_state.fase).first()
                    _state_hist.data_chiusura = _now
                    _state_hist.save()

    @classmethod
    def from_db(cls, db, field_names, values):
        instance = super(Piano, cls).from_db(db, field_names, values)
        instance.fase = Fase.fix_enum(instance.fase)
        instance.tipologia = TipologiaPiano.fix_enum(instance.tipologia)
        return instance

    def getFirstAction(self, tipologia_azione:TIPOLOGIA_AZIONE, qualifica_richiesta:QualificaRichiesta=None):
        qs = Azione.objects.filter(piano=self, tipologia=tipologia_azione)
        if qualifica_richiesta:
            qs = qs.filter(qualifica_richiesta=qualifica_richiesta)
        return qs.first()

    def azioni(self, tipologia_azione:TIPOLOGIA_AZIONE=None, qualifica_richiesta:QualificaRichiesta=None):
        qs = Azione.objects.filter(piano=self)
        if tipologia_azione:
            qs = qs.filter(tipologia=tipologia_azione)
        if qualifica_richiesta:
            qs = qs.filter(qualifica_richiesta=qualifica_richiesta)
        return qs


class Azione(models.Model):

    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        null=False
    )

    piano = models.ForeignKey(Piano, on_delete=models.CASCADE)

    tipologia = models.CharField(
        choices=TIPOLOGIA_AZIONE,
        default=TIPOLOGIA_AZIONE.unknown,
        max_length=80
    )

    qualifica_richiesta = models.CharField(
        choices=QualificaRichiesta.create_choices(),
        null=False,
        max_length=QualificaRichiesta.get_max_len()
    )

    stato = models.CharField(
        choices=STATO_AZIONE,
        default=STATO_AZIONE.unknown,
        max_length=20
    )

    data = models.DateTimeField(null=True, blank=True)

    order = models.PositiveIntegerField(null=False)

    class Meta:
        db_table = "strt_core_azione"
        verbose_name_plural = 'Azioni'

    def __str__(self):
        return '{} - {} [{}]'.format(self.qualifica_richiesta.name, TIPOLOGIA_AZIONE[self.tipologia], self.uuid)

    def count_by_piano(piano, tipo=None):
        qs = Azione.objects.filter(piano=piano)
        if tipo:
            qs = qs.filter(tipologia=tipo)
        return qs.count()

    @classmethod
    def from_db(cls, db, field_names, values):
        instance = super(Azione, cls).from_db(db, field_names, values)
        instance.qualifica_richiesta = QualificaRichiesta.fix_enum(instance.qualifica_richiesta)
        return instance


class FasePianoStorico(models.Model):
    piano = models.ForeignKey(Piano, on_delete=models.CASCADE)
    # fase = models.ForeignKey(Fase, on_delete=models.CASCADE)
    fase = models.CharField(
        choices=Fase.create_choices(),
        default=Fase.UNKNOWN,
        max_length=Fase.get_max_len()
    )

    data_apertura = models.DateTimeField()
    data_chiusura = models.DateTimeField(null=True, blank=True)

    @classmethod
    def get_all_by_piano(cls, piano):
        return list(FasePianoStorico.objects.filter(piano=piano).all())

    class Meta:
        db_table = "strt_core_piano_storico_fasi"

    @classmethod
    def from_db(cls, db, field_names, values):
        instance = super(FasePianoStorico, cls).from_db(db, field_names, values)
        instance.fase = Fase.fix_enum(instance.fase)
        return instance



class RisorsePiano(models.Model):
    piano = models.ForeignKey(Piano, on_delete=models.CASCADE)
    risorsa = models.ForeignKey(Risorsa, on_delete=models.CASCADE)

    class Meta:
        db_table = "strt_core_piano_risorse"


###########

class SoggettoOperante(models.Model):
    """
OLD    Puo' essere un utente o un ufficio.
OLD    Rende disponibili: mail, ente, qualifica
    """
    # TIPO_VAS =  'vas'
    # TIPO_ISTITUZ = 'autorita'
    # TIPO_ALTRI = 'altri'
    # TIPO_SCA = 'sca'
    # TIPO_PROPONENTE = 'proponente'

    # TIPOLOGIA_REFERENTE = Choices(
    #     (TIPO_VAS, _('autorita_competente_vas utenti')),
    #     (TIPO_ISTITUZ, _('autorita_istituzionali piani')),
    #     (TIPO_ALTRI, _('altri_destinatari piani')),
    #     (TIPO_SCA, _('soggetti_sca piani')),
    #     (TIPO_PROPONENTE, _('proponente piani')),
    # )

    id = models.AutoField(
        auto_created=True, primary_key=True, serialize=False, verbose_name=_('id')
    )

    qualifica_ufficio = models.ForeignKey(QualificaUfficio, related_name="+", on_delete=models.CASCADE, null=True)
    # ufficio = models.ForeignKey(Ufficio, related_name="ufficio+", on_delete=models.CASCADE, null=True)
    piano = models.ForeignKey(Piano, related_name="so+", on_delete=models.CASCADE, null=False)

    # tipo = models.CharField(max_length=10, choices=TIPOLOGIA_REFERENTE, null=False)

    class Meta:
        db_table = "strt_core_soggettooperante"

    def __unicode__(self):
        return "P:{piano} {ufficio} T:{qualifica} <mail>".format(
            piano = self.piano,
            ufficio = self.qualifica_ufficio.ufficio,
            qualifica= self.qualifica_ufficio.qualifica,
            mail=self.qualifica_ufficio.ufficio.mail,
        )

    def get_ente(self):
            return self.qualifica_ufficio.ufficio.ente

    def get_qualifica(self):
        return self.qualifica_ufficio.qualifica

    @classmethod
    def get_by_qualifica(cls, piano, qualifica):
        return SoggettoOperante.objects.filter(piano=piano, qualifica_ufficio__qualifica=qualifica)


class Delega(models.Model):
    """
    An access token that is associated with a user.
    This is essentially the same as the token model from Django REST Framework
    """
    # key = models.CharField(max_length=40, primary_key=True)

    delegante = models.ForeignKey(SoggettoOperante, related_name="+", on_delete=models.CASCADE, null=False)
    token = models.ForeignKey(Token, related_name="delega+", on_delete=models.CASCADE, null=False)

    # can be READONLY or the Qualifica related to SoggettoOperante
    qualifica = models.CharField(
        choices=Qualifica.create_choices(),
        max_length=Qualifica.get_max_len(),
        null=False)

    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(Utente, related_name="+", on_delete=models.CASCADE)

    class Meta:
        db_table = "strt_core_delega"


    def is_expired(self):
        """
        Check token expiration with timezone awareness
        """
        if not self.expires:
            return True

        return timezone.now() >= self.expires

    def __unicode__(self):
        return self.key


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
        choices=TipologiaVAS.create_choices(),
        default=TipologiaVAS.UNKNOWN,
        max_length=TipologiaVAS.get_max_len()
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
    assoggettamento = models.NullBooleanField(null=True, blank=False, default=None)

    pubblicazione_provvedimento_verifica_ap = models.URLField(null=True, blank=True)
    pubblicazione_provvedimento_verifica_ac = models.URLField(null=True, blank=True)

    conclusa = models.BooleanField(null=False, blank=False, default=False)

    risorse = models.ManyToManyField(Risorsa, through='RisorseVas')

    ente = models.ForeignKey(
        to=Ente,
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
        return '{} - {} [{}]'.format(self.piano.codice, self.tipologia, self.uuid)

    @classmethod
    def from_db(cls, db, field_names, values):
        instance = super(ProceduraVAS, cls).from_db(db, field_names, values)
        instance.tipologia = TipologiaVAS.fix_enum(instance.tipologia)
        return instance


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
        to=Utente,
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
        to=Utente,
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
        to=Utente,
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


# class AutoritaCompetenteVAS(models.Model):
#     autorita_competente = models.ForeignKey(Contatto, on_delete=models.DO_NOTHING)
#     piano = models.ForeignKey(Piano, on_delete=models.DO_NOTHING)
#
#     class Meta:
#         db_table = "strt_core_autorita_competente"
#
#     def __str__(self):
#         return '{} <---> {}'.format(self.piano.codice, self.autorita_competente.email)
#
#
# class SoggettiSCA(models.Model):
#     soggetto_sca = models.ForeignKey(Contatto, on_delete=models.DO_NOTHING)
#     piano = models.ForeignKey(Piano, on_delete=models.DO_NOTHING)
#
#     class Meta:
#         db_table = "strt_core_soggetti_sca"
#
#     def __str__(self):
#         return '{} <---> {}'.format(self.piano.codice, self.soggetto_sca.email)
#
#
# class AutoritaIstituzionali(models.Model):
#     autorita_istituzionale = models.ForeignKey(Contatto, on_delete=models.DO_NOTHING)
#     piano = models.ForeignKey(Piano, on_delete=models.DO_NOTHING)
#
#     class Meta:
#         db_table = "strt_core_autorita_istituzionale"
#
#     def __str__(self):
#         return '{} <---> {}'.format(self.piano.codice, self.autorita_istituzionale.email)
#
#
# class AltriDestinatari(models.Model):
#     altro_destinatario = models.ForeignKey(Contatto, on_delete=models.DO_NOTHING)
#     piano = models.ForeignKey(Piano, on_delete=models.DO_NOTHING)
#
#     class Meta:
#         db_table = "strt_core_altri_destinatari"
#
#     def __str__(self):
#         return '{} <---> {}'.format(self.piano.codice, self.altro_destinatario.email)


# class PianoAuthTokens(models.Model):
#     soggetto_operante = models.ForeignKey(SoggettoOperante, on_delete=models.CASCADE)
#     # token = models.ForeignKey(Delega, on_delete=models.CASCADE)
#
#     class Meta:
#         db_table = "strt_core_piano_auth_tokens"
#         # TODO unique_together = ('soggetto_operante', 'token')
#
#     def __str__(self):
# #        return '{} <---> {}'.format(self.piano.codice, self.token.key)
#         return '{} <---> ???'.format(self.soggetto_operante.id)


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
        choices=TipologiaCopianificazione.create_choices(),
        null=True, blank=True,
        default=None,
        max_length=TipologiaCopianificazione.get_max_len()
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
        to=Ente,
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

    @classmethod
    def from_db(cls, db, field_names, values):
        instance = super(ProceduraAvvio, cls).from_db(db, field_names, values)
        instance.conferenza_copianificazione = TipologiaCopianificazione.fix_enum(instance.conferenza_copianificazione)
        return instance


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
# - Adozione
# ############################################################################ #
class ProceduraAdozione(models.Model):

    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        null=True
    )

    data_creazione = models.DateTimeField(auto_now_add=True, blank=True)
    data_delibera_adozione = models.DateTimeField(null=True, blank=True)
    data_ricezione_osservazioni = models.DateTimeField(null=True, blank=True)
    data_ricezione_pareri = models.DateTimeField(null=True, blank=True)

    pubblicazione_burt_url = models.URLField(null=True, blank=True, default='')
    pubblicazione_burt_data = models.DateTimeField(null=True, blank=True)
    pubblicazione_sito_url = models.URLField(null=True, blank=True, default='')
    pubblicazione_sito_data = models.DateTimeField(null=True, blank=True)

    osservazioni_concluse = models.BooleanField(null=False, blank=False, default=False)

    richiesta_conferenza_paesaggistica = models.BooleanField(null=False, blank=False, default=False)
    url_piano_controdedotto = models.URLField(null=True, blank=True, default='')
    url_rev_piano_post_cp = models.URLField(null=True, blank=True, default='')

    conclusa = models.BooleanField(null=False, blank=False, default=False)

    risorse = models.ManyToManyField(Risorsa, through='RisorseAdozione')

    # ente = models.ForeignKey(
    #     to=Ente,
    #     on_delete=models.CASCADE,
    #     verbose_name=_('ente'),
    #     default=None,
    #     blank=True,
    #     null=True
    # )

    piano = models.ForeignKey(Piano, on_delete=models.CASCADE)

    class Meta:
        db_table = "strt_core_adozione"
        verbose_name_plural = 'Procedure Adozione'

    def __str__(self):
        return '{} [{}]'.format(self.piano.codice, self.uuid)


class RisorseAdozione(models.Model):
    procedura_adozione = models.ForeignKey(ProceduraAdozione, on_delete=models.CASCADE)
    risorsa = models.ForeignKey(Risorsa, on_delete=models.CASCADE)

    class Meta:
        db_table = "strt_core_adozione_risorse"


class PianoControdedotto(models.Model):

    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        null=True
    )

    piano = models.ForeignKey(Piano, on_delete=models.CASCADE)

    risorse = models.ManyToManyField(Risorsa, through='RisorsePianoControdedotto')

    class Meta:
        db_table = "strt_core_piano_controdedotto"
        verbose_name_plural = 'Piani Controdedotti'

    def __str__(self):
        return '{} - {} [{}]'.format(self.piano.codice, self.piano.ente, self.uuid)


class RisorsePianoControdedotto(models.Model):
    piano_controdedotto = models.ForeignKey(PianoControdedotto, on_delete=models.CASCADE)
    risorsa = models.ForeignKey(Risorsa, on_delete=models.CASCADE)

    class Meta:
        db_table = "strt_core_risorse_piano_controdedotto"


class PianoRevPostCP(models.Model):

    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        null=True
    )

    piano = models.ForeignKey(Piano, on_delete=models.CASCADE)

    risorse = models.ManyToManyField(Risorsa, through='RisorsePianoRevPostCP')

    class Meta:
        db_table = "strt_core_piano_rev_post_cp"
        verbose_name_plural = 'Piani Rev. post CP'

    def __str__(self):
        return '{} - {} [{}]'.format(self.piano.codice, self.piano.ente, self.uuid)


class RisorsePianoRevPostCP(models.Model):
    piano_rev_post_cp = models.ForeignKey(PianoRevPostCP, on_delete=models.CASCADE)
    risorsa = models.ForeignKey(Risorsa, on_delete=models.CASCADE)

    class Meta:
        db_table = "strt_core_risorse_piano_rev_post_cp"


# ############################################################################ #
# - Adozione VAS
# ############################################################################ #
class ParereAdozioneVAS(models.Model):

    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        null=True
    )

    data_creazione = models.DateTimeField(auto_now_add=True, blank=True)
    data_invio_parere = models.DateTimeField(null=True, blank=True)
    data_ricezione_parere = models.DateTimeField(null=True, blank=True)

    procedura_adozione = models.ForeignKey(ProceduraAdozione, on_delete=models.CASCADE)

    inviata = models.BooleanField(null=False, blank=False, default=False)

    user = models.ForeignKey(
        to=Utente,
        on_delete=models.CASCADE,
        verbose_name=_('user'),
        default=None,
        blank=True,
        null=True
    )

    class Meta:
        db_table = "strt_core_pareri_adozione_vas"
        verbose_name_plural = 'Pareri Adozione VAS'

    def __str__(self):
        return '{} - [{}]'.format(self.procedura_adozione, self.uuid)


class ProceduraAdozioneVAS(models.Model):

    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        null=True
    )

    data_creazione = models.DateTimeField(auto_now_add=True, blank=True)
    last_update = models.DateTimeField(auto_now=True, blank=True)

    conclusa = models.BooleanField(null=False, blank=False, default=False)

    risorse = models.ManyToManyField(Risorsa, through='RisorseAdozioneVas')

    # ente = models.ForeignKey(
    #     to=Ente,
    #     on_delete=models.CASCADE,
    #     verbose_name=_('ente'),
    #     default=None,
    #     blank=True,
    #     null=True
    # )

    piano = models.ForeignKey(Piano, on_delete=models.CASCADE)

    class Meta:
        db_table = "strt_core_adozione_vas"
        verbose_name_plural = 'Procedure Adozione VAS'

    def __str__(self):
        return 'ProceduraAdozioneVAS {} [{}]'.format(self.piano.codice, self.uuid)

    # @classmethod
    # def from_db(cls, db, field_names, values):
    #     instance = super(ProceduraVAS, cls).from_db(db, field_names, values)
    #     instance.tipologia = TipologiaVAS.fix_enum(instance.tipologia)
    #     return instance


class RisorseAdozioneVas(models.Model):
    procedura_adozione_vas = models.ForeignKey(ProceduraAdozioneVAS, on_delete=models.CASCADE)
    risorsa = models.ForeignKey(Risorsa, on_delete=models.CASCADE)

    class Meta:
        db_table = "strt_core_adozione_vas_risorse"


# ############################################################################ #
# - Approvazione
# ############################################################################ #
class ProceduraApprovazione(models.Model):

    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        null=True
    )

    data_creazione = models.DateTimeField(auto_now_add=True, blank=True)
    data_delibera_approvazione = models.DateTimeField(null=True, blank=True)

    pubblicazione_url = models.URLField(null=True, blank=True, default='')
    pubblicazione_url_data = models.DateTimeField(null=True, blank=True)

    richiesta_conferenza_paesaggistica = models.BooleanField(null=False, blank=False, default=False)
    url_piano_pubblicato = models.URLField(null=True, blank=True, default='')
    url_rev_piano_post_cp = models.URLField(null=True, blank=True, default='')

    conclusa = models.BooleanField(null=False, blank=False, default=False)

    risorse = models.ManyToManyField(Risorsa, through='RisorseApprovazione')

    ente = models.ForeignKey(
        to=Ente,
        on_delete=models.CASCADE,
        verbose_name=_('ente'),
        default=None,
        blank=True,
        null=True
    )

    piano = models.ForeignKey(Piano, on_delete=models.CASCADE)

    class Meta:
        db_table = "strt_core_approvazione"
        verbose_name_plural = 'Procedure Approvazione'

    def __str__(self):
        return '{} - {} [{}]'.format(self.piano.codice, self.ente, self.uuid)


class RisorseApprovazione(models.Model):
    procedura_approvazione = models.ForeignKey(ProceduraApprovazione, on_delete=models.CASCADE)
    risorsa = models.ForeignKey(Risorsa, on_delete=models.CASCADE)

    class Meta:
        db_table = "strt_core_approvazione_risorse"


# ############################################################################ #
# - Pubblicazione
# ############################################################################ #
class ProceduraPubblicazione(models.Model):

    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        null=True
    )

    data_creazione = models.DateTimeField(auto_now_add=True, blank=True)
    data_pubblicazione = models.DateTimeField(null=True, blank=True)

    pubblicazione_url = models.URLField(null=True, blank=True, default='')
    pubblicazione_url_data = models.DateTimeField(null=True, blank=True)

    conclusa = models.BooleanField(null=False, blank=False, default=False)

    risorse = models.ManyToManyField(Risorsa, through='RisorsePubblicazione')

    ente = models.ForeignKey(
        to=Ente,
        on_delete=models.CASCADE,
        verbose_name=_('ente'),
        default=None,
        blank=True,
        null=True
    )

    piano = models.ForeignKey(Piano, on_delete=models.CASCADE)

    class Meta:
        db_table = "strt_core_pubblicazione"
        verbose_name_plural = 'Procedure Pubblicazione'

    def __str__(self):
        return '{} - {} [{}]'.format(self.piano.codice, self.ente, self.uuid)


class RisorsePubblicazione(models.Model):
    procedura_pubblicazione = models.ForeignKey(ProceduraPubblicazione, on_delete=models.CASCADE)
    risorsa = models.ForeignKey(Risorsa, on_delete=models.CASCADE)

    class Meta:
        db_table = "strt_core_pubblicazione_risorse"


# ############################################################################ #
# Model Signals
# ############################################################################ #
# @receiver(post_delete, sender=Contatto)
# def delete_roles_and_users(sender, instance, **kwargs):
#     try:
#         if instance.user is not None:
#             instance.user.delete()
#     except BaseException:
#         pass


@receiver(pre_delete, sender=Piano)
def delete_piano_associations(sender, instance, **kwargs):
    SoggettoOperante.objects.filter(piano=instance).delete()
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

    for _vas in ProceduraAdozioneVAS.objects.filter(piano=instance):
        _vas.risorse.all().delete()
        RisorseAdozioneVas.objects.filter(procedura_adozione_vas=_vas).delete()

    for _adozione in ProceduraAdozione.objects.filter(piano=instance):
        _adozione.risorse.all().delete()
        RisorseAdozione.objects.filter(procedura_adozione=_adozione).delete()

    for _pubblicazione in ProceduraPubblicazione.objects.filter(piano=instance):
        _pubblicazione.risorse.all().delete()
        RisorsePubblicazione.objects.filter(procedura_pubblicazione=_pubblicazione).delete()

    for _pc in PianoControdedotto.objects.filter(piano=instance):
        _pc.risorse.all().delete()
        RisorsePianoControdedotto.objects.filter(piano_controdedotto=_pc).delete()

    for _pc in PianoRevPostCP.objects.filter(piano=instance):
        _pc.risorse.all().delete()
        RisorsePianoRevPostCP.objects.filter(piano_rev_post_cp=_pc).delete()

    for _approvazione in ProceduraApprovazione.objects.filter(piano=instance):
        _approvazione.risorse.all().delete()
        RisorseApprovazione.objects.filter(procedura_approvazione=_approvazione).delete()

    for _a in Azione.objects.filter(piano=instance):
        _a.delete()

    # for _t in Token.objects.filter(piano=instance): # TODO
    #     _t.token.delete()


def needsExecution(action:Azione):
    return action and action.stato != STATO_AZIONE.nessuna


def isExecuted(action:Azione):
    return action and action.stato == STATO_AZIONE.nessuna


def ensure_fase(check:Fase, expected:Fase):
    if check !=expected:
        raise Exception(_("Fase Piano incongruente con l'azione richiesta") + " -- " + _(check.name))


def chiudi_azione(azione:Azione, data=None, set_data=True):
    log.warning('Chiusura azione [{a}]:{qr} in piano [{p}]'.format(a=azione.tipologia, qr=azione.qualifica_richiesta, p=azione.piano))
    azione.stato = STATO_AZIONE.nessuna
    if set_data:
        azione.data = data if data else datetime.now(timezone.get_current_timezone())
    azione.save()


def crea_azione(azione:Azione):
    log.warning('Creazione azione [{a}]:{qr} in piano [{p}]'.format(a=azione.tipologia, qr=azione.qualifica_richiesta, p=azione.piano))
    if azione.order == None:
        _order = Azione.count_by_piano(azione.piano)
        azione.order = _order

    azione.save()

