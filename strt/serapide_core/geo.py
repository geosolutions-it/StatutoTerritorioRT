import datetime
import logging
import os
import shutil
import fiona
import zipfile


from django.conf import settings
from django.utils import timezone

from serapide_core.modello.enums_geo import MAPPING_RISORSA_ENUM
from serapide_core.modello.models import (
    LottoCartografico,
    ElaboratoCartografico,
    Azione,
    Piano,
    Risorsa,
    AzioneReport, PianoControdedotto, PianoRevPostCP,
)

from serapide_core.modello.enums import (
    TipoRisorsa,
    TipologiaAzione,
    StatoAzione,
    TipoReportAzione,
)

logger = logging.getLogger(__name__)


def handle_message(lotto: LottoCartografico, tipo: TipoReportAzione, msg_dict, message):
    msg_dict[tipo].append(message)

    report = AzioneReport(
        azione = lotto.azione,
        tipo = tipo,
        messaggio = message,
        data = datetime.datetime.now(timezone.get_current_timezone())
    )
    report.save()


def process_carto(lotto: LottoCartografico, tipo: TipoRisorsa, msg: list):
    '''
    - check resource exists
    - unzip resource file
    - search for all shp file in zip
    - for all valid shp
      - insert shp info in db
      - TODO: ingest
      
    :param piano:
    :param risorse: querySet delle risorse da esaminare
    :param tipo:
    :param errs: lista di errori alla quale appendere eventuali errori riscontrati
    :return:
    '''

    expected_shapefiles = MAPPING_RISORSA_ENUM.get(tipo, None)
    if expected_shapefiles is None:
        # Non dovrebbe accadere: è un errore nella definizione delle liste
        handle_message(lotto, TipoReportAzione.ERR, msg, "*** Lista di shapefile accettabili vuota. Tipo: {tipo}"
                       .format(tipo=tipo.value))
        return
    exp_names = [item.name for item in expected_shapefiles]

    risorse = get_risorse(lotto)

    risorse_filtrate: Risorsa = risorse.filter(tipo=tipo.value, archiviata=False)
    risorse_cnt = risorse_filtrate.all().count()

    if risorse_cnt > 1:
        handle_message(lotto, TipoReportAzione.ERR, msg, "Troppe risorse di tipo: {}".format(tipo.value))
        return
    elif risorse_cnt == 0:
        handle_message(lotto, TipoReportAzione.INFO, msg, "Risorsa non trovata: {}".format(tipo.value))
        return

    risorsa = risorse_filtrate.get()

    root_dir = getattr(settings, 'STORAGE_ROOT_DIR', False)
    res_step = '{:08}_{}'.format(risorsa.id,tipo.value)
    resource_dir = os.path.join(root_dir, lotto.piano.codice, 'geo', res_step)
    unzip_dir = os.path.join(resource_dir, 'unzip')

    # Handle temp dir
    if os.path.exists(resource_dir):
        shutil.rmtree(resource_dir)

    os.makedirs(unzip_dir)

    # Unzip resource file
    try:
        with zipfile.ZipFile(risorsa.file, 'r') as zip_ref:
            zip_ref.extractall(unzip_dir)
    except Exception as e:
        handle_message(lotto, TipoReportAzione.ERR, msg, "Errore nell'estrazione file {file}: {err}".format(
            file=os.path.basename(risorsa.file.name),
            err=e))
        risorsa.valida = False
        risorsa.save()
        return

    # Search for SHP files
    shp_list = search_shp(unzip_dir)  # shapefile with full path

    continue_processing = True

    if len(shp_list) == 0:
        handle_message(lotto, TipoReportAzione.ERR, msg, "Nessuno shapefile trovato. Tipo: {tipo}"
                       .format(tipo=tipo.value))
        continue_processing = False
    else:
        for fullpathshape in shp_list:
            base = os.path.basename(fullpathshape)
            base, _ = os.path.splitext(base)
            if base not in exp_names:
                handle_message(lotto, TipoReportAzione.ERR, msg, 'Shapefile inaspettato {file}. Tipo: {tipo}'
                               .format(file=base, tipo=tipo))
                continue_processing = False
                continue

    if not continue_processing:
        risorsa.valida = False
        risorsa.save()
        return

    for shp in shp_list:
        shp_err = validate_shp(lotto, shp)
        if shp_err:
            shp_base = os.path.basename(shp)
            handle_message(lotto, TipoReportAzione.ERR, msg, 'Errore validazione {file}: {err}'.format(file=shp_base, err=shp_err))
            continue_processing = False
            continue

    if not continue_processing:
        risorsa.valida = False
        risorsa.save()
        return

    rezip_dir = os.path.join(resource_dir, 'rezip')
    os.makedirs(rezip_dir)

    for shp in shp_list:
        handle_message(lotto, TipoReportAzione.INFO, msg,
                       'Shapefile accettato {file}'.format(file=os.path.basename(shp)))
        rezip_shp(shp, rezip_dir)

    risorsa.valida = True
    risorsa.save()


def search_shp(dir):
    shps = []

    for root, dirs, files in os.walk(dir):
        for file in files:
            if file.endswith(".shp"):
                logger.info('Found shp: {} / {}'.format(root, file))
                shps.append(os.path.join(root, file))

    return shps


def validate_shp(lotto, shp_file):
    try:
        with fiona.open(shp_file, 'r') as c:
            epsg = c.crs.get('init', None)

            # coordinate nel sistema di riferimento Gauss-Boaga fuso Ovest (codice EPSG:3003)
            # o nel sistema di riferimento UTM-ETRF2000 epoca 2008.0 fuso 32 (codice EPSG: 6707).
            if epsg not in ('epsg:3003', 'epsg:6707'):
                return 'CRS non consentito: {}'.format(c.crs)

            basename = os.path.basename(shp_file)
            basename,_ = os.path.splitext(basename)

            ec = ElaboratoCartografico(
                lotto=lotto,
                nome=basename,
                crs=epsg,
                minx=c.bounds[0],
                maxx=c.bounds[1],
                miny=c.bounds[2],
                maxy=c.bounds[3],
                ingerito=False,
            )
            ec.save()

    except Exception as ex:
        logger.warning('Errore in validazione', exc_info=True)
        return 'Errore lettura shp: {}'.format(ex)

    return None


def rezip_shp(shp_file, destination_dir):

    src_basename = os.path.basename(shp_file)
    src_barename, _ = os.path.splitext(src_basename)
    dest_zip = os.path.join(destination_dir, '{}.zip'.format(src_barename))

    shp_source_dir = os.path.dirname(shp_file)

    with zipfile.ZipFile(dest_zip, 'w') as zip_file:
        for file in os.listdir(shp_source_dir):
            basename = os.path.basename(file)
            if basename.startswith(src_barename):
                zip_file.write(os.path.join(shp_source_dir, file), basename)


def get_risorse(lotto: LottoCartografico):

    tipologia: TipologiaAzione = lotto.azione_parent.tipologia

    if tipologia == TipologiaAzione.trasmissione_adozione:
        return lotto.piano.procedura_adozione.risorse

    elif tipologia == TipologiaAzione.piano_controdedotto:
        return PianoControdedotto.objects.filter(piano=lotto.piano).get().risorse

    elif tipologia == TipologiaAzione.rev_piano_post_cp:
        return PianoRevPostCP.objects.filter(piano=lotto.piano).get().risorse

    elif tipologia == TipologiaAzione.trasmissione_approvazione:
        return lotto.piano.procedura_approvazione.risorse

    elif tipologia == TipologiaAzione.esito_conferenza_paesaggistica_ap:
        return None  # TODO

    else:
        raise Exception('Tipologia azione cartografica inaspettata [{}]'.format(tipologia))