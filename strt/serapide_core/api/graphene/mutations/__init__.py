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

def log_enter_mutate(logger, cls, piano, info):
    role = info.context.session['role'] if 'role' in info.context.session else None
    token = info.context.session['token'] if 'token' in info.context.session else None
    ente = piano.ente

    logger.info("MUTATE: {piano} {mutation} : {utente} ({role}) @ {ente} # {token}".format(
        piano=piano.codice,
        mutation=cls,
        utente=info.context.user,
        ente=ente,
        token=token,
        role=role
    ))
