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
import rules
import logging
import graphene
import traceback

from django.conf import settings

from django.utils.translation import ugettext_lazy as _

from django.core.files.storage import default_storage
from django.core.files.uploadedfile import (
    TemporaryUploadedFile,
    InMemoryUploadedFile
)

from graphene_file_upload.scalars import Upload

from graphql_extensions.exceptions import GraphQLError

from serapide_core.modello.models import (
    Piano,
    Risorsa,
    ProceduraVAS,
    ProceduraAvvio,
    ConferenzaCopianificazione,
    RisorsePiano,
    RisorseVas,
    RisorseAvvio,
    RisorseCopianificazione,
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
        if info.context.user and rules.test_rule('strt_core.api.can_access_private_area', info.context.user):
            # Fetching input arguments
            _codice_piano = input['codice']
            _tipo_file = input['tipo_file']

            try:
                # Validating 'Piano'
                _piano = Piano.objects.get(codice=_codice_piano)
                if rules.test_rule('strt_core.api.can_edit_piano', info.context.user, _piano) and \
                rules.test_rule('strt_core.api.can_update_piano', info.context.user, _piano):
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
                else:
                    return GraphQLError(_("Forbidden"), code=403)
            except BaseException as e:
                tb = traceback.format_exc()
                logger.error(tb)
                return GraphQLError(e, code=500)

        # Something went wrong
        return GraphQLError(_("Not Allowed"), code=405)


class UploadRisorsaVAS(UploadBaseBase):

    success = graphene.Boolean()
    procedura_vas_aggiornata = graphene.Field(types.ProceduraVASNode)
    file_name = graphene.String()

    @classmethod
    def mutate(cls, root, info, file, **input):
        if info.context.user and rules.test_rule('strt_core.api.can_access_private_area', info.context.user):
            # Fetching input arguments
            _uuid_vas = input['codice']
            _tipo_file = input['tipo_file']

            try:
                # Validating 'Procedura VAS'
                _procedura_vas = ProceduraVAS.objects.get(uuid=_uuid_vas)
                if rules.test_rule('strt_core.api.can_edit_piano', info.context.user, _procedura_vas.piano):

                    if _tipo_file == 'parere_sca' and \
                    not rules.test_rule('strt_core.api.parere_sca_ok', info.context.user, _procedura_vas):
                        return GraphQLError(_("Forbidden"), code=403)

                    if _tipo_file == 'parere_verifica_vas' and \
                    not rules.test_rule('strt_core.api.parere_verifica_vas_ok', info.context.user, _procedura_vas):
                        return GraphQLError(_("Forbidden"), code=403)

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
                else:
                    return GraphQLError(_("Forbidden"), code=403)
            except BaseException as e:
                tb = traceback.format_exc()
                logger.error(tb)
                return GraphQLError(e, code=500)

        # Something went wrong
        return GraphQLError(_("Not Allowed"), code=405)


class UploadRisorsaAvvio(UploadBaseBase):

    success = graphene.Boolean()
    procedura_avvio_aggiornata = graphene.Field(types.ProceduraAvvioNode)
    file_name = graphene.String()

    @classmethod
    def mutate(cls, root, info, file, **input):
        if info.context.user and rules.test_rule('strt_core.api.can_access_private_area', info.context.user):
            # Fetching input arguments
            _uuid_avvio = input['codice']
            _tipo_file = input['tipo_file']

            try:
                # Validating 'Procedura VAS'
                _procedura_avvio = ProceduraAvvio.objects.get(uuid=_uuid_avvio)
                if rules.test_rule('strt_core.api.can_edit_piano', info.context.user, _procedura_avvio.piano):
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
                else:
                    return GraphQLError(_("Forbidden"), code=403)
            except BaseException as e:
                tb = traceback.format_exc()
                logger.error(tb)
                return GraphQLError(e, code=500)

        # Something went wrong
        return GraphQLError(_("Not Allowed"), code=405)


class UploadRisorsaCopianificazione(UploadBaseBase):

    success = graphene.Boolean()
    conferenza_copianificazione_aggiornata = graphene.Field(types.ConferenzaCopianificazioneNode)
    file_name = graphene.String()

    @classmethod
    def mutate(cls, root, info, file, **input):
        if info.context.user and rules.test_rule('strt_core.api.can_access_private_area', info.context.user):
            # Fetching input arguments
            _uuid_cc = input['codice']
            _tipo_file = input['tipo_file']

            try:
                # Validating 'Procedura VAS'
                _conferenza_copianificazione = ConferenzaCopianificazione.objects.get(uuid=_uuid_cc)
                if rules.test_rule('strt_core.api.can_edit_piano',
                                   info.context.user,
                                   _conferenza_copianificazione.piano):
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
                                conferenza_copianificazione_aggiornata=_conferenza_copianificazione,
                                risorsa=_risorsa).save()
                    return UploadRisorsaCopianificazione(
                        conferenza_copianificazione_aggiornata=_conferenza_copianificazione,
                        success=_success,
                        file_name=_resources[0].nome)
                else:
                    return GraphQLError(_("Forbidden"), code=403)
            except BaseException as e:
                tb = traceback.format_exc()
                logger.error(tb)
                return GraphQLError(e, code=500)

        # Something went wrong
        return GraphQLError(_("Not Allowed"), code=405)


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
        if info.context.user and rules.test_rule('strt_core.api.can_access_private_area', info.context.user):
            # Fetching input arguments
            _id = input['risorsa_id']
            _codice_piano = input['codice']
            # TODO: Andrebbe controllato se la risorsa in funzione del tipo e della fase del piano è eliminabile o meno
            try:
                _piano = Piano.objects.get(codice=_codice_piano)
                if rules.test_rule('strt_core.api.can_edit_piano', info.context.user, _piano) and \
                rules.test_rule('strt_core.api.can_update_piano', info.context.user, _piano):
                    _risorsa = Risorsa.objects.get(uuid=_id)
                    _success = DeleteRisorsaBase.handle_downloaded_data(_risorsa)
                    return DeleteRisorsa(piano_aggiornato=_piano, success=_success)
                else:
                    return GraphQLError(_("Forbidden"), code=403)
            except BaseException as e:
                tb = traceback.format_exc()
                logger.error(tb)
                return GraphQLError(e, code=500)

        # Something went wrong
        return GraphQLError(_("Not Allowed"), code=405)


class DeleteRisorsaVAS(DeleteRisorsaBase):

    success = graphene.Boolean()
    procedura_vas_aggiornata = graphene.Field(types.ProceduraVASNode)

    @classmethod
    def mutate(cls, root, info, **input):
        if info.context.user and rules.test_rule('strt_core.api.can_access_private_area', info.context.user):
            # Fetching input arguments
            _id = input['risorsa_id']
            _uuid_vas = input['codice']
            # TODO: Andrebbe controllato se la risorsa in funzione del tipo e della fase del piano è eliminabile o meno
            try:
                _procedura_vas = ProceduraVAS.objects.get(uuid=_uuid_vas)
                if rules.test_rule('strt_core.api.can_edit_piano', info.context.user, _procedura_vas.piano):
                    _risorsa = Risorsa.objects.get(uuid=_id)

                    if _risorsa.tipo == 'parere_sca' and \
                    not rules.test_rule('strt_core.api.parere_sca_ok', info.context.user, _procedura_vas):
                        return GraphQLError(_("Forbidden"), code=403)

                    if _risorsa.tipo == 'parere_verifica_vas' and \
                    not rules.test_rule('strt_core.api.parere_verifica_vas_ok', info.context.user, _procedura_vas):
                        return GraphQLError(_("Forbidden"), code=403)

                    _success = DeleteRisorsaBase.handle_downloaded_data(_risorsa)
                    return DeleteRisorsaVAS(procedura_vas_aggiornata=_procedura_vas, success=_success)
                else:
                    return GraphQLError(_("Forbidden"), code=403)
            except BaseException as e:
                tb = traceback.format_exc()
                logger.error(tb)
                return GraphQLError(e, code=500)

        # Something went wrong
        return GraphQLError(_("Not Allowed"), code=405)


class DeleteRisorsaAvvio(DeleteRisorsaBase):

    success = graphene.Boolean()
    procedura_avvio_aggiornata = graphene.Field(types.ProceduraAvvioNode)

    @classmethod
    def mutate(cls, root, info, **input):
        if info.context.user and rules.test_rule('strt_core.api.can_access_private_area', info.context.user):
            # Fetching input arguments
            _id = input['risorsa_id']
            _uuid_avvio = input['codice']
            # TODO: Andrebbe controllato se la risorsa in funzione del tipo e della fase del piano è eliminabile o meno
            try:
                _procedura_avvio = ProceduraAvvio.objects.get(uuid=_uuid_avvio)
                if rules.test_rule('strt_core.api.can_edit_piano', info.context.user, _procedura_avvio.piano):
                    _risorsa = Risorsa.objects.get(uuid=_id)
                    _success = DeleteRisorsaBase.handle_downloaded_data(_risorsa)
                    return DeleteRisorsaAvvio(procedura_avvio_aggiornata=_procedura_avvio, success=_success)
                else:
                    return GraphQLError(_("Forbidden"), code=403)
            except BaseException as e:
                tb = traceback.format_exc()
                logger.error(tb)
                return GraphQLError(e, code=500)

        # Something went wrong
        return GraphQLError(_("Not Allowed"), code=405)


class DeleteRisorsaCopianificazione(DeleteRisorsaBase):

    success = graphene.Boolean()
    conferenza_copianificazione_aggiornata = graphene.Field(types.ConferenzaCopianificazioneNode)

    @classmethod
    def mutate(cls, root, info, **input):
        if info.context.user and rules.test_rule('strt_core.api.can_access_private_area', info.context.user):
            # Fetching input arguments
            _id = input['risorsa_id']
            _uuid_cc = input['codice']
            # TODO: Andrebbe controllato se la risorsa in funzione del tipo e della fase del piano è eliminabile o meno
            try:
                _conferenza_copianificazione = ConferenzaCopianificazione.objects.get(uuid=_uuid_cc)
                if rules.test_rule('strt_core.api.can_edit_piano',
                                   info.context.user,
                                   _conferenza_copianificazione.piano):
                    _risorsa = Risorsa.objects.get(uuid=_id)
                    _success = DeleteRisorsaBase.handle_downloaded_data(_risorsa)
                    return DeleteRisorsaCopianificazione(
                        conferenza_copianificazione_aggiornata=_conferenza_copianificazione, success=_success)
                else:
                    return GraphQLError(_("Forbidden"), code=403)
            except BaseException as e:
                tb = traceback.format_exc()
                logger.error(tb)
                return GraphQLError(e, code=500)

        # Something went wrong
        return GraphQLError(_("Not Allowed"), code=405)
