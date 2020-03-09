# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright 2019, GeoSolutions Sas.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.
#
#########################################################################

import rules
import logging
import graphene

from urllib.parse import urljoin

from django.conf import settings
import django_filters

from pinax.messages.models import Thread, Message

from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from serapide_core.api.auth.user import is_soggetto_operante, has_qualifica
from strt_users.enums import (
    Qualifica,
    Profilo,
    QualificaRichiesta)

from strt_users.models import (
    Ente,
    Ufficio, QualificaUfficio,
    Utente, Assegnatario,
    Token,
    ProfiloUtente,
)

from serapide_core.modello.enums import (
    STATO_AZIONE,
    TIPOLOGIA_RISORSA,
    TipologiaVAS,
    FASE_AZIONE,
    TIPOLOGIA_AZIONE,
    TOOLTIP_AZIONE
)

from serapide_core.modello.models import (
    Fase,
    Piano,
    Azione,
    Risorsa,
    SoggettoOperante,
    Delega,
    ProceduraVAS,
    ConsultazioneVAS,
    # PianoAuthTokens,
    FasePianoStorico,
    ProceduraAvvio,
    ProceduraAdozione,
    ProceduraAdozioneVAS,
    ProceduraApprovazione,
    ProceduraPubblicazione,
    PianoControdedotto,
    PianoRevPostCP,
    ConferenzaCopianificazione,
    RisorsePiano,
    RisorseVas,
    RisorseAvvio,
    RisorseAdozione,
    RisorseCopianificazione,
    RisorsePianoControdedotto,
    RisorsePianoRevPostCP,
    RisorseAdozioneVas,
    RisorseApprovazione,
    RisorsePubblicazione,
)

logger = logging.getLogger(__name__)


# Graphene will automatically map the Category model's fields onto the CategoryNode.
# This is configured in the CategoryNode's Meta class (as you can see below)
# class RoleNode(DjangoObjectType):
#
#     type = graphene.String()
#
#     def resolve_type(self, info, **args):
#         return self.type.code
#
#     class Meta:
#         model = Qualifica
#         filter_fields = '__all__'
#         interfaces = (relay.Node, )


# class FaseNode(DjangoObjectType):
#
#     class Meta:
#         model = Fase
#         filter_fields = ['codice', 'nome', 'descrizione', 'piani_operativi']
#         interfaces = (relay.Node, )


class FasePianoStoricoType(DjangoObjectType):

    class Meta:
        model = FasePianoStorico
        interfaces = (relay.Node, )


class UserThreadType(DjangoObjectType):

    absolute_url = graphene.String()

    def resolve_absolute_url(self, info, **args):
        return self.get_absolute_url()

    class Meta:
        model = Thread
        filter_fields = ['subject', 'users', ]
        interfaces = (relay.Node, )


class UserMessageType(DjangoObjectType):

    thread = graphene.Field(UserThreadType)

    class Meta:
        model = Message
        interfaces = (relay.Node, )


class AzioneNode(DjangoObjectType):

    fase = graphene.String()
    label = graphene.String()
    tooltip = graphene.String()
    eseguibile = graphene.Boolean()

    def resolve_fase(self, info, **args):
        return FASE_AZIONE[self.tipologia] if self.tipologia in FASE_AZIONE else None

    def resolve_label(self, info, **args):
        return TIPOLOGIA_AZIONE[self.tipologia] if self.tipologia in TIPOLOGIA_AZIONE else None

    def resolve_tooltip(self, info, **args):
        return TOOLTIP_AZIONE[self.tipologia] if self.tipologia in TOOLTIP_AZIONE else None

    def resolve_qualifica_richiesta(self, info, **args):
        return self.qualifica_richiesta.name

    def resolve_eseguibile(self, info, **args):
        qreq = self.qualifica_richiesta
        user = info.context.user
        piano = self.piano

        if is_soggetto_operante(user, piano, qualifica_richiesta=qreq):
            return True

        if qreq == QualificaRichiesta.COMUNE:
            if has_qualifica(user, piano.ente, Qualifica.RESP):
                return True

        return False

    class Meta:
        model = Azione
        filter_fields = ['uuid',
                         'tipologia',
                         'stato',
                         'data']
        interfaces = (relay.Node, )
        convert_choices_to_enum = False


class RisorsaNode(DjangoObjectType):

    download_url = graphene.String()
    label = graphene.String()
    tooltip = graphene.String()

    def resolve_download_url(self, info, **args):
        _url = str(self.file)
        return urljoin(settings.SITE_URL, _url[_url.index('media/'):])

    def resolve_label(self, info, **args):
        _type = TIPOLOGIA_RISORSA[self.tipo] if self.tipo in TIPOLOGIA_RISORSA else None
        if _type:
            return _type['label']
        return None

    def resolve_tooltip(self, info, **args):
        _type = TIPOLOGIA_RISORSA[self.tipo] if self.tipo in TIPOLOGIA_RISORSA else None
        if _type:
            return _type['tooltip']
        return None

    class Meta:
        model = Risorsa
        filter_fields = ['uuid',
                         'nome',
                         'tipo',
                         'archiviata',
                         'dimensione',
                         'descrizione',
                         'data_creazione',
                         'last_update',
                         'fase',
                         # 'piano__codice' #TODO
                         ]
        interfaces = (relay.Node, )


class RisorsePianoType(DjangoObjectType):

    risorsa = DjangoFilterConnectionField(RisorsaNode)

    class Meta:
        model = RisorsePiano
        filter_fields = ['risorsa__fase',
                         'piano__codice']
        interfaces = (relay.Node, )


class RisorseVASType(DjangoObjectType):

    risorsa = DjangoFilterConnectionField(RisorsaNode)

    class Meta:
        model = RisorseVas
        filter_fields = ['risorsa__fase']
        interfaces = (relay.Node, )


class RisorseAdozioneVASType(DjangoObjectType):

    risorsa = DjangoFilterConnectionField(RisorsaNode)

    class Meta:
        model = RisorseAdozioneVas
        filter_fields = ['risorsa__fase']
        interfaces = (relay.Node, )


class RisorseAvvioType(DjangoObjectType):

    risorsa = DjangoFilterConnectionField(RisorsaNode)

    class Meta:
        model = RisorseAvvio
        filter_fields = ['risorsa__fase']
        interfaces = (relay.Node, )


class RisorseAdozioneType(DjangoObjectType):

    risorsa = DjangoFilterConnectionField(RisorsaNode)

    class Meta:
        model = RisorseAdozione
        filter_fields = ['risorsa__fase']
        interfaces = (relay.Node, )


class RisorseApprovazioneType(DjangoObjectType):

    risorsa = DjangoFilterConnectionField(RisorsaNode)

    class Meta:
        model = RisorseApprovazione
        filter_fields = ['risorsa__fase']
        interfaces = (relay.Node, )


class RisorsePubblicazioneType(DjangoObjectType):

    risorsa = DjangoFilterConnectionField(RisorsaNode)

    class Meta:
        model = RisorsePubblicazione
        filter_fields = ['risorsa__fase']
        interfaces = (relay.Node, )


class RisorseCopianificazioneType(DjangoObjectType):

    risorsa = DjangoFilterConnectionField(RisorsaNode)

    class Meta:
        model = RisorseCopianificazione
        filter_fields = ['risorsa__fase']
        interfaces = (relay.Node, )


class RisorsePianoControdedottoType(DjangoObjectType):

    risorsa = DjangoFilterConnectionField(RisorsaNode)

    class Meta:
        model = RisorsePianoControdedotto
        filter_fields = ['risorsa__fase']
        interfaces = (relay.Node, )


class RisorsePianoRevPostCPType(DjangoObjectType):

    risorsa = DjangoFilterConnectionField(RisorsaNode)

    class Meta:
        model = RisorsePianoRevPostCP
        filter_fields = ['risorsa__fase']
        interfaces = (relay.Node, )


class UtenteNode(DjangoObjectType):

    profilo = graphene.String()
    qualifica = graphene.String()
    ente = graphene.String()

    alerts_count = graphene.String()
    unread_threads_count = graphene.String()
    unread_messages = graphene.List(UserMessageType)

    def resolve_profilo(self, info, **args):
        psess = info.context.session.get('profilo', None)
        try:
            return Profilo[psess].name
        except KeyError:
            return None

    def resolve_qualifica(self, info, **args):
        psess = info.context.session.get('profilo', None)
        try:
            profilo = Profilo[psess]
        except KeyError:
            return None

        if profilo == Profilo.OPERATORE:
            return info.context.session.get('qualifica', None)

        return None

    def resolve_ente(self, info, **args):
        psess = info.context.session.get('profilo', None)
        try:
            profilo = Profilo[psess]
        except KeyError:
            return None

        if profilo in [Profilo.OPERATORE, Profilo.ADMIN_ENTE]:
            return info.context.session.get('qualifica', None)

        return None


    def resolve_alerts_count(self, info, **args):
        _alerts_count = 0

        # TODO
        # _pianos = []
        # _enti = []
        # _memberships = None
        # _memberships = self.memberships
        # if _memberships:
        #     for _m in _memberships.all():
        #         if _m.type.code == settings.RESPONSABILE_ISIDE_CODE:
        #             # RESPONSABILE_ISIDE_CODE cannot access to Piani at all
        #             continue
        #         else:
        #             _enti.append(_m.organization.code)
        #
        # token = info.context.session.get('token', None)
        # if token:
        #     _allowed_pianos = [_pt.piano.codice for _pt in Token.objects.filter(token__key=token)]
        #     _pianos = [_p for _p in Piano.objects.filter(codice__in=_allowed_pianos)]
        # else:
        #     _pianos = [_p for _p in Piano.objects.filter(ente__code__in=_enti)]
        #
        # _alert_states = [STATO_AZIONE.attesa, STATO_AZIONE.necessaria]
        # for _p in _pianos:
        #     _alerts_count += _p.azioni.filter(stato__in=_alert_states).count()

        return _alerts_count

    def resolve_unread_threads_count(self, info, **args):
        return Thread.unread(self).count()

    def resolve_unread_messages(self, info, **args):
        unread_messages = []
        for _t in Thread.unread(self).order_by('subject'):
            unread_messages.append(_t.latest_message)
        return unread_messages

    # def resolve_contact_type(self, info, **args):
    #     organization = info.context.session.get('organization', None)
    #     token = info.context.session.get('token', None)
    #     role = info.context.session.get('role', None)
    #     _tipologia_contatto = None
    #     try:
    #         if token:
    #             _tipologia_contatto = Contatto.tipologia_contatto(self, token=token)
    #         elif role:
    #             _tipologia_contatto = Contatto.tipologia_contatto(self, role=role)
    #         elif organization:
    #             _tipologia_contatto = Contatto.tipologia_contatto(self, organization=organization)
    #     except Exception as e:
    #         logger.exception(e)
    #     return _tipologia_contatto

    # def resolve_attore(self, info, **args):
    #     organization = info.context.session.get('organization', None)
    #     token = info.context.session.get('token', None)
    #     role = info.context.session.get('role', None)
    #     _attore = None
    #     try:
    #         if role:
    #             _attore = Contatto.attore(self, role=role)
    #         elif token:
    #             _attore = Contatto.attore(self, token=token)
    #         elif organization:
    #             _attore = Contatto.attore(self, organization=organization)
    #     except Exception as e:
    #         logger.exception(e)
    #     return _attore

    class Meta:
        model = Utente
        # Allow for some more advanced filtering here
        filter_fields = {
            'fiscal_code': ['exact'],
            'first_name': ['exact', 'icontains', 'istartswith'],
            'last_name': ['exact', 'icontains', 'istartswith'],
            'email': ['exact'],
        }
        exclude = ('password', 'is_active', 'is_superuser', 'last_login')
        interfaces = (relay.Node, )


class EnteNode(DjangoObjectType):

    class Meta:
        model = Ente
        # Allow for some more advanced filtering here
        filter_fields = {
            'id': ['exact'],
            'nome': ['exact', 'icontains', 'istartswith'],
            'descrizione': ['exact', 'icontains'],
        }
        interfaces = (relay.Node, )
        convert_choices_to_enum = False

    def resolve_tipo(self, info, **args):
        return self.tipo.name


class ProceduraVASNode(DjangoObjectType):

    ente = graphene.Field(EnteNode)
    risorsa = DjangoFilterConnectionField(RisorseVASType)
    documento_preliminare_vas = graphene.Field(RisorsaNode)
    documento_preliminare_verifica = graphene.Field(RisorsaNode)
    relazione_motivata_vas_semplificata = graphene.Field(RisorsaNode)

    def resolve_documento_preliminare_vas(self, info, **args):
        _risorsa = None
        if self.verifica_effettuata and \
        self.tipologia in (TipologiaVAS.VERIFICA,
                           TipologiaVAS.PROCEDIMENTO_SEMPLIFICATO,
                           TipologiaVAS.SEMPLIFICATA):
            _risorsa = self.risorse.filter(tipo='documento_preliminare_vas').first()
        return _risorsa

    def resolve_documento_preliminare_verifica(self, info, **args):
        _risorsa = None
        if self.tipologia in [TipologiaVAS.VERIFICA,
                              TipologiaVAS.PROCEDIMENTO_SEMPLIFICATO]:
            _risorsa = self.risorse.filter(tipo='vas_verifica').first()
        return _risorsa

    def resolve_relazione_motivata_vas_semplificata(self, info, **args):
        _risorsa = None
        if self.tipologia == TipologiaVAS.SEMPLIFICATA:
            _risorsa = self.risorse.filter(tipo='vas_semplificata').first()
        return _risorsa

    def resolve_tipologia(self, info, **args):
        return self.tipologia.name


    class Meta:
        model = ProceduraVAS
        # Allow for some more advanced filtering here
        filter_fields = {
            'ente': ['exact'],
            'piano__codice': ['exact'],
            'note': ['exact', 'icontains'],
            'tipologia': ['exact', 'icontains'],
        }
        interfaces = (relay.Node, )
        convert_choices_to_enum = False


class ProceduraAdozioneVASNode(DjangoObjectType):

    ente = graphene.Field(EnteNode)
    risorsa = DjangoFilterConnectionField(RisorseAdozioneVASType)

    def resolve_tipologia(self, info, **args):
        return self.tipologia.name

    class Meta:
        model = ProceduraAdozioneVAS
        # Allow for some more advanced filtering here
        filter_fields = {
            'ente': ['exact'],
            'piano__codice': ['exact'],
            'tipologia': ['exact', 'icontains'],
        }
        interfaces = (relay.Node, )


class ProceduraAvvioNode(DjangoObjectType):

    ente = graphene.Field(EnteNode)
    risorsa = DjangoFilterConnectionField(RisorseAvvioType)

    def resolve_conferenza_copianificazione(self, info, **args):
        return self.conferenza_copianificazione.name if self.conferenza_copianificazione else None


    class Meta:
        model = ProceduraAvvio
        # Allow for some more advanced filtering here
        filter_fields = {
            'ente': ['exact'],
            'piano__codice': ['exact'],
        }
        interfaces = (relay.Node, )
        convert_choices_to_enum = False


class ProceduraAdozioneNode(DjangoObjectType):

    ente = graphene.Field(EnteNode)
    risorsa = DjangoFilterConnectionField(RisorseAdozioneType)

    class Meta:
        model = ProceduraAdozione
        # Allow for some more advanced filtering here
        filter_fields = {
            'ente': ['exact'],
            'piano__codice': ['exact'],
        }
        interfaces = (relay.Node, )


class ProceduraApprovazioneNode(DjangoObjectType):

    ente = graphene.Field(EnteNode)
    risorsa = DjangoFilterConnectionField(RisorseApprovazioneType)

    class Meta:
        model = ProceduraApprovazione
        # Allow for some more advanced filtering here
        filter_fields = {
            'ente': ['exact'],
            'piano__codice': ['exact'],
        }
        interfaces = (relay.Node, )


class ProceduraPubblicazioneNode(DjangoObjectType):

    ente = graphene.Field(EnteNode)
    risorsa = DjangoFilterConnectionField(RisorsePubblicazioneType)

    class Meta:
        model = ProceduraPubblicazione
        # Allow for some more advanced filtering here
        filter_fields = {
            'ente': ['exact'],
            'piano__codice': ['exact'],
        }
        interfaces = (relay.Node, )


class SoggettoOperanteFilter(django_filters.FilterSet):

    qualifica = django_filters.CharFilter(method='qualifica_filter')

    class Meta:
        model = SoggettoOperante
        fields = ['id', 'piano', 'qualifica']

        def qualifica_filter(self, queryset, name, val):
            # logger.warning("*** FILTERING SOGGETTO OPERANTE BY QUALIFICA")
            return queryset.filter(qualifica_ufficio__qualifica=val)


class SoggettoOperanteNode(DjangoObjectType):

    class Meta:
        model = SoggettoOperante
        # Allow for some more advanced filtering here
        filter_fields = [
            'id',
            'qualifica',
            'qualifica_ufficio'
        ]
        interfaces = (relay.Node, )
        # filterset_class = SoggettoOperanteFilter


class ConsultazioneVASNode(DjangoObjectType):

    user = graphene.Field(UtenteNode)
    referente = graphene.Field(SoggettoOperanteNode)
    procedura_vas = graphene.Field(ProceduraVASNode)

    # def resolve_contatto(self, info, **args):
    #     _contatto = None
    #     if self.user:
    #         _contatto = Contatto.objects.filter(user=self.user).first()
    #     return _contatto

    class Meta:
        model = ConsultazioneVAS
        # Allow for some more advanced filtering here
        filter_fields = {
            'procedura_vas__piano__codice': ['exact'],
        }
        interfaces = (relay.Node, )


class ConferenzaCopianificazioneNode(DjangoObjectType):

    risorsa = DjangoFilterConnectionField(RisorseCopianificazioneType)

    class Meta:
        model = ConferenzaCopianificazione
        # Allow for some more advanced filtering here
        filter_fields = {
            'id_pratica': ['exact'],
            'piano__codice': ['exact'],
        }
        interfaces = (relay.Node, )


class PianoControdedottoNode(DjangoObjectType):

    risorsa = DjangoFilterConnectionField(RisorseCopianificazioneType)

    class Meta:
        model = PianoControdedotto
        # Allow for some more advanced filtering here
        filter_fields = {
            'piano__codice': ['exact'],
        }
        interfaces = (relay.Node, )


class UfficioNode(DjangoObjectType):

    class Meta:
        model = Ufficio # ufficio, qualifica
        filter_fields = ['uuid', 'nome', 'ente', 'ente__ipa']
        # interfaces = (relay.Node, )


class QualificaUfficioNode(DjangoObjectType):

    class Meta:
        model = QualificaUfficio # ufficio, qualifica
        filter_fields = ['qualifica', 'ufficio']
        convert_choices_to_enum = False
        # interfaces = (relay.Node, )

    def resolve_qualifica(self, info, **args):
        return self.qualifica.name


class PianoRevPostCPNode(DjangoObjectType):

    risorsa = DjangoFilterConnectionField(RisorseCopianificazioneType)

    class Meta:
        model = PianoRevPostCP
        # Allow for some more advanced filtering here
        filter_fields = {
            'piano__codice': ['exact'],
        }
        interfaces = (relay.Node, )


class PianoNode(DjangoObjectType):

    responsabile = graphene.Field(UtenteNode)
    ente = graphene.Field(EnteNode)
    storico_fasi = graphene.List(FasePianoStoricoType)
    risorsa = DjangoFilterConnectionField(RisorsePianoType)
    procedura_vas = graphene.Field(ProceduraVASNode)
    soggetto_proponente = graphene.Field(QualificaUfficioNode)
    soggetti_operanti = graphene.List(SoggettoOperanteNode, qualifica=graphene.String())

    alerts_count = graphene.String()
    azioni = graphene.List(AzioneNode)


    def resolve_azioni(self, info, **args):
        return Azione.objects.filter(piano=self)

    def resolve_alerts_count(self, info, **args):
        _alert_states = [STATO_AZIONE.attesa, STATO_AZIONE.necessaria]
        # return self.azioni.filter(stato__in=_alert_states).count()
        return Azione.objects \
            .filter(piano=self)\
            .filter(stato__in=_alert_states).count()

    def resolve_storico_fasi(self, info, **args):
        # Warning this is not currently paginated
        _hist = FasePianoStorico.objects.filter(piano=self)
        return list(_hist)

    def resolve_procedura_vas(self, info, **args):
        _vas = None
        try:
            _vas = ProceduraVAS.objects.get(piano=self)
        except BaseException:
            pass
        return _vas

    def resolve_soggetti_operanti(self, info , qualifica=None,**args):
        # Warning this is not currently paginated
        qs = SoggettoOperante.objects.filter(piano=self)
        if qualifica:
            qualifica = Qualifica.fix_enum(qualifica)
            qs = qs.filter(qualifica_ufficio__qualifica=qualifica)
        # logger.warning("*** RESOLVING SOGGETTO OPERANTE [q:{}]: {}".format(qualifica, qs.all().count()))
        return qs

    # TODO: check and remove this since it's mirroring a Piano field
    def resolve_soggetto_proponente(self, info, **args):
        return self.soggetto_proponente

    def resolve_tipologia(self, info, **args):
        logger.warning("*** RESOLVING TIPOLOGIA [type:{t}]: {o}".format(t=type(self.tipologia), o=self.tipologia))
        return self.tipologia.name

    def resolve_fase(self, info, **args):
        return self.fase.name

    class Meta:
        model = Piano
        # Allow for some more advanced filtering here
        filter_fields = {
            'codice': ['exact', 'icontains', 'istartswith'],
            'ente': ['exact'],
            'descrizione': ['exact', 'icontains'],
            'tipologia': ['exact'],
        }
        interfaces = (relay.Node, )
        convert_choices_to_enum = False


class QualificaChoiceNode(DjangoObjectType):

    qualifica = graphene.String()
    ufficio = graphene.String()

    def resolve_qualifica(self, info, **args):
        return self.qualifica_ufficio.qualifica.name

    def resolve_ufficio(self, info, **args):
        return self.qualifica_ufficio.ufficio.nome

    class Meta:
        # model = QualificaUfficio # qualifica_ufficio, utente
        model = Assegnatario # qualifica_ufficio, utente
        filter_fields = ['qualifica_ufficio']
        convert_choices_to_enum = False


class ProfiloChoiceNode(DjangoObjectType):
    qualifiche = graphene.List(QualificaChoiceNode)

    def resolve_profilo(self, info, **args):
        return self.profilo.name

    def resolve_qualifiche(self, info, **args):
        # logger.error("FOUND PROFILO {}".format(self.profilo))
        if Profilo.OPERATORE == Profilo.fix_enum(self.profilo):
            # logger.error('OPERATORE RICONOSCIUTO')

            # filter(assegnatario__utente=self.utente).
            ass = Assegnatario.objects. \
                    filter(utente=self.utente).  \
                    filter(qualifica_ufficio__ufficio__ente=self.ente)
            # logger.error("FOUND QUALIFICHE {}".format(len(ass)))
            # ret = [a.qualifica_ufficio.qualifica for a in ass]
            # return ret
            return ass
        else:
            # logger.error('OPERATORE NON RICONOSCIUTO')
            # logger.warning("PROFILO [{p}] TIPO [{t}]".format(p=self.profilo, t=type(self.profilo)))
            pass

        return None

    class Meta:
        model = ProfiloUtente # utente, profilo ente
        filter_fields = ['profilo', 'ente']
        # interfaces = (relay.Node, )
        convert_choices_to_enum = False


class UtenteChoiceNode(DjangoObjectType):
    profili = graphene.List(ProfiloChoiceNode)

    def resolve_profili(self, info):
        return ProfiloUtente.objects.filter(utente=self)

    class Meta:
        model = Utente
        # interfaces = (relay.Node, )
        filter_fields = {
            'fiscal_code': ['exact'],
            'first_name': ['exact', 'icontains', 'istartswith'],
            'last_name': ['exact', 'icontains', 'istartswith'],
            'email': ['exact'],
        }
        exclude = ('password', 'is_active', 'is_superuser', 'last_login')

    @classmethod
    def get_queryset(cls, queryset, info):
        if info.context.user.is_anonymous:
            return queryset.none()
        else:
            return queryset.filter(id=info.context.user.id)

        return queryset
