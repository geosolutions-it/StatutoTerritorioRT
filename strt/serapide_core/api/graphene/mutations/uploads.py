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

import os
import logging
import graphene
import traceback

from django.conf import settings

from django.core.files.storage import default_storage
from django.core.files.uploadedfile import (
    TemporaryUploadedFile,
    InMemoryUploadedFile
)

from graphene_file_upload.scalars import Upload

from graphql_extensions.exceptions import GraphQLError

import serapide_core.api.auth.vas as auth_vas
import serapide_core.api.auth.user as auth

from serapide_core.modello.enums import (
    TipoRisorsa,
    TipologiaAzione,
)

from serapide_core.modello.models import (
    Piano,
    Risorsa,
    ProceduraVAS,
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

    isExecuted,
)

from .. import types


logger = logging.getLogger(__name__)


class UploadBaseBase(graphene.Mutation):

    class Arguments:
        codice = graphene.String(required=True)
        tipo_file = graphene.String(required=True)
        file = Upload(required=True)

    @classmethod
    def handle_uploaded_data(cls, file, media_prefix, fase, tipo_file=None, user=None):
        # Ensuring Media Folder exists and is writable
        _base_media_folder = os.path.join(settings.MEDIA_ROOT, media_prefix)
        if not os.path.exists(_base_media_folder):
            os.makedirs(_base_media_folder)
        if not isinstance(file, list):
            file = [file]
        resources = []
        for f in file:
            _dimensione_file = f.size / 1024  # size in KB
            if os.path.exists(_base_media_folder) and \
            type(f) in (TemporaryUploadedFile, InMemoryUploadedFile):
                _file_name = str(f)
                _file_path = '{}/{}'.format(media_prefix, _file_name)
                _risorsa = None

                with default_storage.open(_file_path, 'wb+') as _destination:
                    for _chunk in f.chunks():
                        _destination.write(_chunk)
                    _risorsa = Risorsa.create(
                        _file_name,
                        _destination,
                        tipo_file,
                        _dimensione_file,
                        fase)
                    _risorsa.user = user
                    _risorsa.save()
                    resources.append(_risorsa)
                    # _full_path = os.path.join(settings.MEDIA_ROOT, _file_path)
                    # Remove original uploaded/temporary file
                    os.remove(_destination.name)
        return resources

    @classmethod
    def mutate(cls, root, info, file, **input):
        pass


class UploadFile(UploadBaseBase):

    piano_aggiornato = graphene.Field(types.PianoNode)
    success = graphene.Boolean()
    file_name = graphene.String()

    @classmethod
    def mutate(cls, root, info, file, **input):

        if not auth.is_recognizable(info.context.user):
            return GraphQLError("Not Authorized - Utente non riconosciuto", code=401)

        # Fetching input arguments
        _codice_piano = input['codice']
        _tipo_file = input['tipo_file']

        try:
            # Validating 'Piano'
            _piano = Piano.objects.get(codice=_codice_piano)  # TODO 404

            if not auth.can_access_piano(info.context.user, _piano):
                return GraphQLError("Forbidden - Utente non abilitato ad editare questo piano", code=403)

            _resources = UploadBaseBase.handle_uploaded_data(
                file,
                _codice_piano,
                _piano.fase,
                _tipo_file,
                info.context.user
            )
            _success = False
            if _resources and len(_resources) > 0:
                _success = True
                for _risorsa in _resources:
                    RisorsePiano(piano=_piano, risorsa=_risorsa).save()
            return UploadFile(piano_aggiornato=_piano, success=_success, file_name=_resources[0].nome)

        except BaseException as e:
            tb = traceback.format_exc()
            logger.error(tb)
            return GraphQLError(e, code=500)


class UploadRisorsaVAS(UploadBaseBase):

    success = graphene.Boolean()
    procedura_vas_aggiornata = graphene.Field(types.ProceduraVASNode)
    file_name = graphene.String()

    @classmethod
    def mutate(cls, root, info, file, **input):

        if not auth.is_recognizable(info.context.user):
            return GraphQLError("Not Authorized - Utente non riconosciuto", code=401)

        # Fetching input arguments
        _uuid_vas = input['codice']
        _tipo_file = input['tipo_file']

        try:
            # Validating 'Procedura VAS'
            _procedura_vas = ProceduraVAS.objects.get(uuid=_uuid_vas)
            _piano = _procedura_vas.piano

            if not auth.can_access_piano(info.context.user, _piano):
                return GraphQLError("Forbidden - Utente non abilitato ad editare questo piano", code=403)

            if _tipo_file == TipoRisorsa.PARERE_SCA.value:
                # if _procedura_vas.risorse.filter(tipo=_tipo_file, archiviata=False, user=info.context.user).exists():
                #     return GraphQLError('Precondition failed - Non si possono aggiungere ulteriori pareri SCA', code=412)

                if isExecuted(_piano.getFirstAction(TipologiaAzione.trasmissione_pareri_sca)):
                    return GraphQLError('Risorsa inviata e non modificabile', code=403)

            if _tipo_file == TipoRisorsa.PARERE_VERIFICA_VAS.value and \
                    not auth_vas.parere_verifica_vas_ok(info.context.user, _procedura_vas):
                return GraphQLError('Precondition failed - Verifica VAS esistente', code=412)

            # not rules.test_rule('strt_core.api.parere_verifica_vas_ok', info.context.user, _procedura_vas):
            #     return GraphQLError(_("Forbidden"), code=403)

            _resources = UploadBaseBase.handle_uploaded_data(
                file,
                _uuid_vas,
                _procedura_vas.piano.fase,
                _tipo_file,
                info.context.user
            )
            _success = False
            if _resources and len(_resources) > 0:
                _success = True
                for _risorsa in _resources:
                    RisorseVas(procedura_vas=_procedura_vas, risorsa=_risorsa).save()
            return UploadRisorsaVAS(
                procedura_vas_aggiornata=_procedura_vas,
                success=_success,
                file_name=_resources[0].nome)

        except BaseException as e:
            tb = traceback.format_exc()
            logger.error(tb)
            return GraphQLError(e, code=500)


class UploadRisorsaAdozioneVAS(UploadBaseBase):

    success = graphene.Boolean()
    procedura_vas_aggiornata = graphene.Field(types.ProceduraAdozioneVASNode)
    file_name = graphene.String()

    @classmethod
    def mutate(cls, root, info, file, **input):

        if not auth.is_recognizable(info.context.user):
            return GraphQLError("Not Authorized - Utente non riconosciuto", code=401)

        # Fetching input arguments
        _uuid_vas = input['codice']
        _tipo_file = input['tipo_file']

        try:
            _procedura_vas = ProceduraAdozioneVAS.objects.get(uuid=_uuid_vas)
            _piano = _procedura_vas.piano

            if not auth.can_access_piano(info.context.user, _piano):
                return GraphQLError("Forbidden - Utente non abilitato ad editare questo piano", code=403)

            _resources = UploadBaseBase.handle_uploaded_data(
                file,
                _uuid_vas,
                _procedura_vas.piano.fase,
                _tipo_file,
                info.context.user
            )
            _success = False
            if _resources and len(_resources) > 0:
                _success = True
                for _risorsa in _resources:
                    RisorseAdozioneVas(procedura_adozione_vas=_procedura_vas, risorsa=_risorsa).save()
            return UploadRisorsaAdozioneVAS(
                procedura_vas_aggiornata=_procedura_vas,
                success=_success,
                file_name=_resources[0].nome)

        except BaseException as e:
            tb = traceback.format_exc()
            logger.error(tb)
            return GraphQLError(e, code=500)


class UploadRisorsaAvvio(UploadBaseBase):

    success = graphene.Boolean()
    procedura_avvio_aggiornata = graphene.Field(types.ProceduraAvvioNode)
    file_name = graphene.String()

    @classmethod
    def mutate(cls, root, info, file, **input):

        if not auth.is_recognizable(info.context.user):
            return GraphQLError("Not Authorized - Utente non riconosciuto", code=401)

        # Fetching input arguments
        _uuid_avvio = input['codice']
        _tipo_file = input['tipo_file']

        _procedura_avvio = ProceduraAvvio.objects.get(uuid=_uuid_avvio)
        _piano = _procedura_avvio.piano

        if not auth.can_access_piano(info.context.user, _piano):
            return GraphQLError("Forbidden - Utente non abilitato ad editare questo piano", code=403)

        try:
            _resources = UploadBaseBase.handle_uploaded_data(
                file,
                _uuid_avvio,
                _procedura_avvio.piano.fase,
                _tipo_file,
                info.context.user
            )
            _success = False
            if _resources and len(_resources) > 0:
                _success = True
                for _risorsa in _resources:
                    RisorseAvvio(procedura_avvio=_procedura_avvio, risorsa=_risorsa).save()

            return UploadRisorsaAvvio(
                procedura_avvio_aggiornata=_procedura_avvio,
                success=_success,
                file_name=_resources[0].nome)

        except BaseException as e:
            tb = traceback.format_exc()
            logger.error(tb)
            return GraphQLError(e, code=500)


class UploadRisorsaAdozione(UploadBaseBase):

    success = graphene.Boolean()
    procedura_adozione_aggiornata = graphene.Field(types.ProceduraAdozioneNode)
    file_name = graphene.String()

    @classmethod
    def mutate(cls, root, info, file, **input):

        if not auth.is_recognizable(info.context.user):
            return GraphQLError("Not Authorized - Utente non riconosciuto", code=401)

        # Fetching input arguments
        _uuid_adozione = input['codice']
        _tipo_file = input['tipo_file']

        try:
            _procedura_adozione = ProceduraAdozione.objects.get(uuid=_uuid_adozione)
            _piano = _procedura_adozione.piano

            if not auth.can_access_piano(info.context.user, _piano):
                return GraphQLError("Forbidden - Utente non abilitato ad editare questo piano", code=403)

            _resources = UploadBaseBase.handle_uploaded_data(
                file,
                _uuid_adozione,
                _procedura_adozione.piano.fase,
                _tipo_file,
                info.context.user
            )
            _success = False
            if _resources and len(_resources) > 0:
                _success = True
                for _risorsa in _resources:
                    RisorseAdozione(procedura_adozione=_procedura_adozione, risorsa=_risorsa).save()
            return UploadRisorsaAdozione(
                procedura_adozione_aggiornata=_procedura_adozione,
                success=_success,
                file_name=_resources[0].nome)

        except BaseException as e:
            tb = traceback.format_exc()
            logger.error(tb)
            return GraphQLError(e, code=500)


class UploadRisorsaApprovazione(UploadBaseBase):

    success = graphene.Boolean()
    procedura_approvazione_aggiornata = graphene.Field(types.ProceduraApprovazioneNode)
    file_name = graphene.String()

    @classmethod
    def mutate(cls, root, info, file, **input):

        if not auth.is_recognizable(info.context.user):
            return GraphQLError("Not Authorized - Utente non riconosciuto", code=401)

        # Fetching input arguments
        _uuid_approvazione = input['codice']
        _tipo_file = input['tipo_file']

        try:
            _procedura_approvazione = ProceduraApprovazione.objects.get(uuid=_uuid_approvazione)
            _piano = _procedura_approvazione.piano

            if not auth.can_access_piano(info.context.user, _piano):
                return GraphQLError("Forbidden - Utente non abilitato ad editare questo piano", code=403)

            _resources = UploadBaseBase.handle_uploaded_data(
                file,
                _uuid_approvazione,
                _procedura_approvazione.piano.fase,
                _tipo_file,
                info.context.user
            )
            _success = False
            if _resources and len(_resources) > 0:
                _success = True
                for _risorsa in _resources:
                    RisorseApprovazione(procedura_approvazione=_procedura_approvazione, risorsa=_risorsa).save()
            return UploadRisorsaApprovazione(
                procedura_approvazione_aggiornata=_procedura_approvazione,
                success=_success,
                file_name=_resources[0].nome)

        except BaseException as e:
            tb = traceback.format_exc()
            logger.error(tb)
            return GraphQLError(e, code=500)


class UploadRisorsaPubblicazione(UploadBaseBase):

    success = graphene.Boolean()
    procedura_pubblicazione_aggiornata = graphene.Field(types.ProceduraPubblicazioneNode)
    file_name = graphene.String()

    @classmethod
    def mutate(cls, root, info, file, **input):

        if not auth.is_recognizable(info.context.user):
            return GraphQLError("Not Authorized - Utente non riconosciuto", code=401)

        # Fetching input arguments
        _uuid_pubblicazione = input['codice']
        _tipo_file = input['tipo_file']

        try:
            _procedura_pubblicazione = ProceduraPubblicazione.objects.get(uuid=_uuid_pubblicazione)
            _piano = _procedura_pubblicazione.piano

            if not auth.can_access_piano(info.context.user, _piano):
                return GraphQLError("Forbidden - Utente non abilitato ad editare questo piano", code=403)

            _resources = UploadBaseBase.handle_uploaded_data(
                file,
                _uuid_pubblicazione,
                _procedura_pubblicazione.piano.fase,
                _tipo_file,
                info.context.user
            )
            _success = False
            if _resources and len(_resources) > 0:
                _success = True
                for _risorsa in _resources:
                    RisorsePubblicazione(
                        procedura_pubblicazione=_procedura_pubblicazione, risorsa=_risorsa).save()
            return UploadRisorsaPubblicazione(
                procedura_pubblicazione_aggiornata=_procedura_pubblicazione,
                success=_success,
                file_name=_resources[0].nome)

        except BaseException as e:
            tb = traceback.format_exc()
            logger.error(tb)
            return GraphQLError(e, code=500)


class UploadRisorsaCopianificazione(UploadBaseBase):

    success = graphene.Boolean()
    conferenza_copianificazione_aggiornata = graphene.Field(types.ConferenzaCopianificazioneNode)
    file_name = graphene.String()

    @classmethod
    def mutate(cls, root, info, file, **input):

        if not auth.is_recognizable(info.context.user):
            return GraphQLError("Forbidden - Utente non riconosciuto", code=403)

        # Fetching input arguments
        _uuid_cc = input['codice']
        _tipo_file = input['tipo_file']

        try:
            _conferenza_copianificazione = ConferenzaCopianificazione.objects.get(uuid=_uuid_cc)
            _piano = _conferenza_copianificazione.piano

            if not auth.can_access_piano(info.context.user, _piano):
                return GraphQLError("Forbidden - Utente non abilitato ad editare questo piano", code=403)

            _resources = UploadBaseBase.handle_uploaded_data(
                file,
                _uuid_cc,
                _conferenza_copianificazione.piano.fase,
                _tipo_file,
                info.context.user
            )
            _success = False
            if _resources and len(_resources) > 0:
                _success = True
                for _risorsa in _resources:
                    RisorseCopianificazione(
                        conferenza_copianificazione=_conferenza_copianificazione,
                        risorsa=_risorsa).save()
            return UploadRisorsaCopianificazione(
                conferenza_copianificazione_aggiornata=_conferenza_copianificazione,
                success=_success,
                file_name=_resources[0].nome)

        except BaseException as e:
            tb = traceback.format_exc()
            logger.error(tb)
            return GraphQLError(e, code=500)


class UploadRisorsaPianoControdedotto(UploadBaseBase):

    success = graphene.Boolean()
    piano_controdedotto_aggiornato = graphene.Field(types.PianoControdedottoNode)
    file_name = graphene.String()

    @classmethod
    def mutate(cls, root, info, file, **input):

        if not auth.is_recognizable(info.context.user):
            return GraphQLError("Not Authorized - Utente non riconosciuto", code=401)

        # Fetching input arguments
        _uuid_cc = input['codice']
        _tipo_file = input['tipo_file']

        try:
            _piano_controdedotto = PianoControdedotto.objects.get(uuid=_uuid_cc)
            _piano = _piano_controdedotto.piano

            if not auth.can_access_piano(info.context.user, _piano):
                return GraphQLError("Forbidden - Utente non abilitato ad editare questo piano", code=403)

            _resources = UploadBaseBase.handle_uploaded_data(
                file,
                _uuid_cc,
                _piano_controdedotto.piano.fase,
                _tipo_file,
                info.context.user
            )
            _success = False
            if _resources and len(_resources) > 0:
                _success = True
                for _risorsa in _resources:
                    RisorsePianoControdedotto(
                        piano_controdedotto=_piano_controdedotto,
                        risorsa=_risorsa).save()
            return UploadRisorsaPianoControdedotto(
                piano_controdedotto_aggiornato=_piano_controdedotto,
                success=_success,
                file_name=_resources[0].nome)

        except BaseException as e:
            tb = traceback.format_exc()
            logger.error(tb)
            return GraphQLError(e, code=500)


class UploadRisorsaPianoRevPostCP(UploadBaseBase):

    success = graphene.Boolean()
    piano_rev_post_cp_aggiornato = graphene.Field(types.PianoRevPostCPNode)
    file_name = graphene.String()

    @classmethod
    def mutate(cls, root, info, file, **input):

        if not auth.is_recognizable(info.context.user):
            return GraphQLError("Not Authorized - Utente non riconosciuto", code=401)

        # Fetching input arguments
        _uuid_cc = input['codice']
        _tipo_file = input['tipo_file']

        try:
            _piano_rev_post_cp = PianoRevPostCP.objects.get(uuid=_uuid_cc)
            _piano = _piano_rev_post_cp.piano

            if not auth.can_access_piano(info.context.user, _piano):
                return GraphQLError("Forbidden - Utente non abilitato ad editare questo piano", code=403)

            _resources = UploadBaseBase.handle_uploaded_data(
                file,
                _uuid_cc,
                _piano_rev_post_cp.piano.fase,
                _tipo_file,
                info.context.user
            )
            _success = False
            if _resources and len(_resources) > 0:
                _success = True
                for _risorsa in _resources:
                    RisorsePianoRevPostCP(
                        piano_rev_post_cp=_piano_rev_post_cp,
                        risorsa=_risorsa).save()
            return UploadRisorsaPianoRevPostCP(
                piano_rev_post_cp_aggiornato=_piano_rev_post_cp,
                success=_success,
                file_name=_resources[0].nome)

        except BaseException as e:
            tb = traceback.format_exc()
            logger.error(tb)
            return GraphQLError(e, code=500)


class DeleteRisorsaBase(graphene.Mutation):

    class Arguments:
        risorsa_id = graphene.ID(required=True)
        codice = graphene.String(required=True)

    @classmethod
    def handle_downloaded_data(cls, risorsa):
        """
        Deletes file from filesystem
        when corresponding `MediaFile` object is deleted.
        """
        try:
            # if risorsa.file:
            #     if os.path.isfile(risorsa.file.path) and os.path.exists(risorsa.file.path):
            #         os.remove(risorsa.file.path)
            # risorsa.delete()
            risorsa.archiviata = True
            risorsa.save()
            return risorsa.archiviata
        except BaseException:
            tb = traceback.format_exc()
            logger.error(tb)
            return False

    @classmethod
    def mutate(cls, root, info, **input):
        pass


class DeleteRisorsa(DeleteRisorsaBase):

    success = graphene.Boolean()
    piano_aggiornato = graphene.Field(types.PianoNode)

    @classmethod
    def mutate(cls, root, info, **input):

        if not auth.is_recognizable(info.context.user):
            return GraphQLError("Utente non autenticato", code=401)

        # Fetching input arguments
        _id = input['risorsa_id']
        _codice_piano = input['codice']
        # TODO: Andrebbe controllato se la risorsa in funzione del tipo e della fase del piano è eliminabile o meno
        try:
            _piano = Piano.objects.get(codice=_codice_piano)

            if not auth.can_access_piano(info.context.user, _piano):
                return GraphQLError("Forbidden - Utente non abilitato ad editare questo piano", code=403)

            _risorsa = Risorsa.objects.get(uuid=_id)
            _success = DeleteRisorsaBase.handle_downloaded_data(_risorsa)
            return DeleteRisorsa(piano_aggiornato=_piano, success=_success)

        except BaseException as e:
            tb = traceback.format_exc()
            logger.error(tb)
            return GraphQLError(e, code=500)


class DeleteRisorsaVAS(DeleteRisorsaBase):

    success = graphene.Boolean()
    procedura_vas_aggiornata = graphene.Field(types.ProceduraVASNode)

    @classmethod
    def mutate(cls, root, info, **input):

        if not auth.is_recognizable(info.context.user):
            return GraphQLError("Utente non autenticato", code=401)

        # Fetching input arguments
        _id = input['risorsa_id']
        _uuid_vas = input['codice']
        # TODO: Andrebbe controllato se la risorsa in funzione del tipo e della fase del piano è eliminabile o meno
        try:
            _procedura_vas = ProceduraVAS.objects.get(uuid=_uuid_vas)
            _piano = _procedura_vas.piano

            if not auth.can_access_piano(info.context.user, _piano):
                return GraphQLError("Forbidden - Utente non abilitato ad editare questo piano", code=403)

            _risorsa = Risorsa.objects.get(uuid=_id)

            if _risorsa.tipo == TipoRisorsa.PARERE_SCA.value:
                # if not auth_vas.parere_sca_ok(info.context.user, _procedura_vas):
                #     return GraphQLError("Risorsa non eliminabile", code=403)
                if isExecuted(_piano.getFirstAction(TipologiaAzione.trasmissione_pareri_sca)):
                    return GraphQLError('Risorsa inviata e non modificabile', code=403)

            if _risorsa.tipo == TipoRisorsa.PARERE_VERIFICA_VAS and \
                    not auth_vas.parere_verifica_vas_ok(info.context.user, _procedura_vas):
                return GraphQLError("Risorsa non eliminabile", code=403)

            _success = DeleteRisorsaBase.handle_downloaded_data(_risorsa)
            return DeleteRisorsaVAS(procedura_vas_aggiornata=_procedura_vas, success=_success)

        except BaseException as e:
            tb = traceback.format_exc()
            logger.error(tb)
            return GraphQLError(e, code=500)


class DeleteRisorsaAdozioneVAS(DeleteRisorsaBase):

    success = graphene.Boolean()
    procedura_vas_aggiornata = graphene.Field(types.ProceduraAdozioneVASNode)

    @classmethod
    def mutate(cls, root, info, **input):

        if not auth.is_recognizable(info.context.user):
            return GraphQLError("Utente non autenticato", code=401)

        # Fetching input arguments
        _id = input['risorsa_id']
        _uuid_vas = input['codice']
        # TODO: Andrebbe controllato se la risorsa in funzione del tipo e della fase del piano è eliminabile o meno
        try:
            _procedura_vas = ProceduraAdozioneVAS.objects.get(uuid=_uuid_vas)
            _piano = _procedura_vas.piano

            if not auth.can_access_piano(info.context.user, _piano):
                return GraphQLError("Forbidden - Utente non abilitato ad editare questo piano", code=403)

            _risorsa = Risorsa.objects.get(uuid=_id)

            _success = DeleteRisorsaBase.handle_downloaded_data(_risorsa)
            return DeleteRisorsaAdozioneVAS(procedura_vas_aggiornata=_procedura_vas, success=_success)

        except BaseException as e:
            tb = traceback.format_exc()
            logger.error(tb)
            return GraphQLError(e, code=500)


class DeleteRisorsaAvvio(DeleteRisorsaBase):

    success = graphene.Boolean()
    procedura_avvio_aggiornata = graphene.Field(types.ProceduraAvvioNode)

    @classmethod
    def mutate(cls, root, info, **input):

        if not auth.is_recognizable(info.context.user):
            return GraphQLError("Utente non autenticato", code=401)

        # Fetching input arguments
        _id = input['risorsa_id']
        _uuid_avvio = input['codice']
        # TODO: Andrebbe controllato se la risorsa in funzione del tipo e della fase del piano è eliminabile o meno
        try:
            _procedura_avvio = ProceduraAvvio.objects.get(uuid=_uuid_avvio)
            _piano = _procedura_avvio.piano

            if not auth.can_access_piano(info.context.user, _piano):
                return GraphQLError("Forbidden - Utente non abilitato ad editare questo piano", code=403)

            _risorsa = Risorsa.objects.get(uuid=_id)
            _success = DeleteRisorsaBase.handle_downloaded_data(_risorsa)
            return DeleteRisorsaAvvio(procedura_avvio_aggiornata=_procedura_avvio, success=_success)

        except BaseException as e:
            tb = traceback.format_exc()
            logger.error(tb)
            return GraphQLError(e, code=500)


class DeleteRisorsaAdozione(DeleteRisorsaBase):

    success = graphene.Boolean()
    procedura_adozione_aggiornata = graphene.Field(types.ProceduraAdozioneNode)

    @classmethod
    def mutate(cls, root, info, **input):

        if not auth.is_recognizable(info.context.user):
            return GraphQLError("Utente non autenticato", code=401)
        # Fetching input arguments
        _id = input['risorsa_id']
        _uuid_adozione = input['codice']
        # TODO: Andrebbe controllato se la risorsa in funzione del tipo e della fase del piano è eliminabile o meno
        try:
            _procedura_adozione = ProceduraAdozione.objects.get(uuid=_uuid_adozione)
            _piano = _procedura_adozione.piano

            if not auth.can_access_piano(info.context.user, _piano):
                return GraphQLError("Forbidden - Utente non abilitato ad editare questo piano", code=403)

            _risorsa = Risorsa.objects.get(uuid=_id)
            _success = DeleteRisorsaBase.handle_downloaded_data(_risorsa)
            return DeleteRisorsaAdozione(procedura_adozione_aggiornata=_procedura_adozione, success=_success)

        except BaseException as e:
            tb = traceback.format_exc()
            logger.error(tb)
            return GraphQLError(e, code=500)


class DeleteRisorsaApprovazione(DeleteRisorsaBase):

    success = graphene.Boolean()
    procedura_approvazione_aggiornata = graphene.Field(types.ProceduraApprovazioneNode)

    @classmethod
    def mutate(cls, root, info, **input):

        if not auth.is_recognizable(info.context.user):
            return GraphQLError("Utente non autenticato", code=401)

        # Fetching input arguments
        _id = input['risorsa_id']
        _uuid_approvazione = input['codice']
        # TODO: Andrebbe controllato se la risorsa in funzione del tipo e della fase del piano è eliminabile o meno
        try:
            _procedura_approvazione = ProceduraApprovazione.objects.get(uuid=_uuid_approvazione)
            _piano = _procedura_approvazione.piano

            if not auth.can_access_piano(info.context.user, _piano):
                return GraphQLError("Forbidden - Utente non abilitato ad editare questo piano", code=403)

            _risorsa = Risorsa.objects.get(uuid=_id)
            _success = DeleteRisorsaBase.handle_downloaded_data(_risorsa)
            return DeleteRisorsaApprovazione(
                procedura_approvazione_aggiornata=_procedura_approvazione, success=_success)

        except BaseException as e:
            tb = traceback.format_exc()
            logger.error(tb)
            return GraphQLError(e, code=500)


class DeleteRisorsaPubblicazione(DeleteRisorsaBase):

    success = graphene.Boolean()
    procedura_pubblicazione_aggiornata = graphene.Field(types.ProceduraPubblicazioneNode)

    @classmethod
    def mutate(cls, root, info, **input):

        if not auth.is_recognizable(info.context.user):
            return GraphQLError("Utente non autenticato", code=401)

        # Fetching input arguments
        _id = input['risorsa_id']
        _uuid_pubblicazione = input['codice']
        # TODO: Andrebbe controllato se la risorsa in funzione del tipo e della fase del piano è eliminabile o meno
        try:
            _procedura_pubblicazione = ProceduraPubblicazione.objects.get(uuid=_uuid_pubblicazione)
            _piano = _procedura_pubblicazione.piano

            if not auth.can_access_piano(info.context.user, _piano):
                return GraphQLError("Forbidden - Utente non abilitato ad editare questo piano", code=403)

            _risorsa = Risorsa.objects.get(uuid=_id)
            _success = DeleteRisorsaBase.handle_downloaded_data(_risorsa)
            return DeleteRisorsaPubblicazione(
                procedura_pubblicazione_aggiornata=_procedura_pubblicazione, success=_success)

        except BaseException as e:
            tb = traceback.format_exc()
            logger.error(tb)
            return GraphQLError(e, code=500)


class DeleteRisorsaCopianificazione(DeleteRisorsaBase):

    success = graphene.Boolean()
    conferenza_copianificazione_aggiornata = graphene.Field(types.ConferenzaCopianificazioneNode)

    @classmethod
    def mutate(cls, root, info, **input):

        if not auth.is_recognizable(info.context.user):
            return GraphQLError("Utente non autenticato", code=401)

        # Fetching input arguments
        _id = input['risorsa_id']
        _uuid_cc = input['codice']
        # TODO: Andrebbe controllato se la risorsa in funzione del tipo e della fase del piano è eliminabile o meno
        try:
            _conferenza_copianificazione = ConferenzaCopianificazione.objects.get(uuid=_uuid_cc)
            _piano = _conferenza_copianificazione.piano

            if not auth.can_access_piano(info.context.user, _piano):
                return GraphQLError("Forbidden - Utente non abilitato ad editare questo piano", code=403)

            _risorsa = Risorsa.objects.get(uuid=_id)
            _success = DeleteRisorsaBase.handle_downloaded_data(_risorsa)
            return DeleteRisorsaCopianificazione(
                conferenza_copianificazione_aggiornata=_conferenza_copianificazione, success=_success)

        except BaseException as e:
            tb = traceback.format_exc()
            logger.error(tb)
            return GraphQLError(e, code=500)


class DeleteRisorsaPianoControdedotto(DeleteRisorsaBase):

    success = graphene.Boolean()
    piano_controdedotto_aggiornato_aggiornato = graphene.Field(types.PianoControdedottoNode)

    @classmethod
    def mutate(cls, root, info, **input):

        if not auth.is_recognizable(info.context.user):
            return GraphQLError("Utente non autenticato", code=401)

        # Fetching input arguments
        _id = input['risorsa_id']
        _uuid_cc = input['codice']
        # TODO: Andrebbe controllato se la risorsa in funzione del tipo e della fase del piano è eliminabile o meno
        try:
            _piano_controdedotto = PianoControdedotto.objects.get(uuid=_uuid_cc)
            _piano = _piano_controdedotto.piano

            if not auth.can_access_piano(info.context.user, _piano):
                return GraphQLError("Forbidden - Utente non abilitato ad editare questo piano", code=403)

            _risorsa = Risorsa.objects.get(uuid=_id)
            _success = DeleteRisorsaBase.handle_downloaded_data(_risorsa)
            return DeleteRisorsaPianoControdedotto(
                piano_controdedotto_aggiornato_aggiornato=_piano_controdedotto, success=_success)

        except BaseException as e:
            tb = traceback.format_exc()
            logger.error(tb)
            return GraphQLError(e, code=500)


class DeleteRisorsaPianoRevPostCP(DeleteRisorsaBase):

    success = graphene.Boolean()
    piano_rev_post_cp_aggiornato = graphene.Field(types.PianoRevPostCPNode)

    @classmethod
    def mutate(cls, root, info, **input):

        if not auth.is_recognizable(info.context.user):
            return GraphQLError("Utente non autenticato", code=401)

        # Fetching input arguments
        _id = input['risorsa_id']
        _uuid_cc = input['codice']
        # TODO: Andrebbe controllato se la risorsa in funzione del tipo e della fase del piano è eliminabile o meno
        try:
            _piano_rev_post_cp = PianoRevPostCP.objects.get(uuid=_uuid_cc)
            _piano = _piano_rev_post_cp.piano

            if not auth.can_access_piano(info.context.user, _piano):
                return GraphQLError("Forbidden - Utente non abilitato ad editare questo piano", code=403)

            _risorsa = Risorsa.objects.get(uuid=_id)
            _success = DeleteRisorsaBase.handle_downloaded_data(_risorsa)
            return DeleteRisorsaPianoRevPostCP(
                piano_rev_post_cp_aggiornato=_piano_rev_post_cp, success=_success)

        except BaseException as e:
            tb = traceback.format_exc()
            logger.error(tb)
            return GraphQLError(e, code=500)

