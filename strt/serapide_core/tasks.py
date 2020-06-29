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

from django.conf import settings

from celery import shared_task
from celery.utils.log import get_task_logger

# from serapide_core.signals import log
from serapide_core.geo import process_carto

from serapide_core.modello.models import (
    LottoCartografico,
    Azione,
    Piano,
)

from serapide_core.modello.enums import (
    TipoRisorsa,
    TipologiaAzione,
    StatoAzione,
    TipoReportAzione,
)

# from serapide_core.api.graphene.mutations.cartografica import esegui_procedura_cartografica
import serapide_core.api.piano_utils as utils
from strt_users.enums import QualificaRichiesta

task_logger = get_task_logger(__name__)
# logger = logging.getLogger(__name__)


@shared_task
def esegui_procedura_cartografica(lotto_id):
    """
    Chiamato da shared_task
    :param lotto:
    :return:
    """

    lotto: LottoCartografico = LottoCartografico.objects.filter(id=lotto_id).get()

    azione: Azione = lotto.azione
    tipologia  = azione.tipologia
    piano: Piano = azione.piano

    msgs = {
        TipoReportAzione.INFO : [],
        TipoReportAzione.WARN : [],
        TipoReportAzione.ERR : [],
    }

    # esegui roba
    if tipologia == TipologiaAzione.validazione_cartografia_adozione:
        for tipo in [TipoRisorsa.SUPPORTO_PREVISIONI_P_C,
                     TipoRisorsa.DISCIPLINA_INSEDIAMENTI,
                     TipoRisorsa.ASSETTI_INSEDIATIVI]:
            process_carto(piano, piano.procedura_adozione.risorse, lotto, tipo, msgs)

    elif tipologia == TipologiaAzione.cartografia_controdedotta:
        pass
    elif tipologia == TipologiaAzione.cartografia_cp_adozione:
        pass
    elif tipologia == TipologiaAzione.cartografia_approvazione:
        pass
    elif tipologia == TipologiaAzione.cartografia_cp_approvazione:
        pass
    else:
        raise Exception('Tipologia azione cartografica inaspettata [{}]'.format(tipologia))

    error = len(msgs[TipoReportAzione.ERR]) > 0

    # Log report
    for tipo_report,logger in (
            (TipoReportAzione.ERR, task_logger.error),
            (TipoReportAzione.WARN, task_logger.warning),
            (TipoReportAzione.INFO, task_logger.info,)):
        if len(msgs[tipo_report]):
            logger('{} - Elaborati cartografici'.format(tipo_report))
            for msg in msgs[tipo_report]:
                logger(' - {}'.format(msg))

    if error:
        utils.chiudi_azione(azione, stato=StatoAzione.FALLITA)
        # l'azione parent deve essere nuovamente eseguita
        utils.riapri_azione(lotto.azione_parent)
    else:
        utils.chiudi_azione(azione)
        crea_azione_post_cartografica(lotto.azione.piano, lotto.azione.tipologia)


def crea_azione_post_cartografica(piano: Piano, tipologia: TipologiaAzione):
    if tipologia == TipologiaAzione.validazione_cartografia_adozione:
        utils.crea_azione(
            Azione(
                piano=piano,
                tipologia=TipologiaAzione.pubblicazione_burt,
                qualifica_richiesta=QualificaRichiesta.COMUNE,
                stato=StatoAzione.NECESSARIA,
            ))
    elif tipologia == TipologiaAzione.cartografia_controdedotta:
        pass
    elif tipologia == TipologiaAzione.cartografia_cp_adozione:
        pass
    elif tipologia == TipologiaAzione.cartografia_approvazione:
        pass
    elif tipologia == TipologiaAzione.cartografia_cp_approvazione:
        pass
    else:
        raise Exception('Tipologia azione cartografica inaspettata [{}]'.format(tipologia))


@shared_task
def etj_test(msg) -> int:
    task_logger.info("TASK LOGGER --> " + msg)
    # logger.info("LOCAL LOGGER --> " + msg)
    return 42


@shared_task
def send_queued_notifications(self, *args):
    """Sends queued notifications.

    settings.PINAX_NOTIFICATIONS_QUEUE_ALL needs to be true in order to take
    advantage of this.

    """

    task_logger.info("RUNNING send_queued_notifications")

    try:
        from notification.engine import send_all
    except ImportError:
        return

    # Make sure application can write to location where lock files are stored
    if not args and getattr(settings, 'NOTIFICATION_LOCK_LOCATION', None):
        send_all(settings.NOTIFICATION_LOCK_LOCATION)
    else:
        send_all(*args)


# @shared_task
# def synch_actions(*args):
#     """TODO
#
#     """
#     task_logger.info("RUNNING SYNCH_INFO")
#
#     # import imp
#     # import inspect
#     # import datetime
#     # import importlib
#     #
#     # from django.utils import timezone
#     # from serapide_core.modello.enums import (
#     #     FASE, STATO_AZIONE)
#     # from serapide_core.modello.models import Piano
#
#     def fullname(o):
#         # o.__module__ + "." + o.__class__.__qualname__ is an example in
#         # this context of H.L. Mencken's "neat, plausible, and wrong."
#         # Python makes no guarantees as to whether the __module__ special
#         # attribute is defined, so we take a more circumspect approach.
#         # Alas, the module name is explicitly excluded from __qualname__
#         # in Python 3.
#         module = o.__class__.__module__
#         if module is None or module == str.__class__.__module__:
#             return o.__class__.__name__  # Avoid reporting __builtin__
#         else:
#             return module + '.' + o.__class__.__name__
#
#     def import_from_dotted_path(dotted_names, path=None):
#         """ import_from_dotted_path('foo.bar') -> from foo import bar; return bar """
#         next_module, remaining_names = dotted_names.split('.', 1)
#         fp, pathname, description = imp.find_module(next_module, path)
#         module = imp.load_module(next_module, fp, pathname, description)
#         if hasattr(module, remaining_names):
#             return getattr(module, remaining_names)
#         if '.' not in remaining_names:
#             return module
#         return import_from_dotted_path(remaining_names, path=module.__path__)
#
#     # _piani = Piano.objects.all().exclude(fase=FASE.pubblicazione)
#     #
#     # for _piano in _piani:
#     #     logger.info(" -------------------------------------- PIANO: %s / %s " % (_piano.codice, _piano.next_phase))
#     #     _azioni = _piano.azioni.filter(stato=STATO_AZIONE.attesa)
#     #     for _azione in _azioni:
#     #         _now = datetime.datetime.now(timezone.get_current_timezone())
#     #         if _azione.data and _now >= _azione.data:
#     #             _module = 'serapide_core.api.graphene.mutations.' + _piano.next_phase.strip()
#     #             mutations = importlib.import_module(_module)
#     #             for _c in dir(mutations):
#     #                 obj = import_from_dotted_path('.'.join([mutations.__name__, _c]))
#     #                 if inspect.isclass(obj) and getattr(obj, 'action', None):
#     #                     if _azione.tipologia == obj.action():
#     #                         logger.info(" -------------------------------------- AZIONE: %s / %s " % (_azione.tipologia, _azione.data))
#     #                         logger.info(" -------------------------------------- PACKAGE: %s " % fullname(_azione))
#     #                         obj.update_actions_for_phase(_piano.fase, _piano, obj.procedura(_piano), None)
