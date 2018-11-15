#########################################################################
#
# Copyright 2018, GeoSolutions Sas.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.
#
#########################################################################


import threading


_thread_locals = threading.local()

def set_current_user(user):
    _thread_locals.user=user

def get_current_user():
    return getattr(_thread_locals, 'user', None)