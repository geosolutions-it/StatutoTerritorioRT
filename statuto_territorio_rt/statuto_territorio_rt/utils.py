#########################################################################
#
# Copyright 2018, GeoSolutions Sas.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.
#
#########################################################################

import os
from django.core.exceptions import ImproperlyConfigured


class Util(object):

    '''
    Base util class: it contains generic utility methods
    '''

    trueValues = ('yes', 'y', 'true', '1')

    @staticmethod
    def str_to_boolean(s=None, default=None):
        if s:
            if s.lower() in Util.trueValues:
                return True
            else:
                return False
        elif default and type(default) == bool:
            return default

    @staticmethod
    def str_to_integer(s=None, default=None):
        if s:
            try:
                integerNum = int(float(s))
                return integerNum
            except:
                pass
        elif default and type(default) == int:
            return default

    @staticmethod
    def str_to_float(s=None, default=None):
        if s:
            try:
                floatNum = float(s)
                return floatNum
            except:
                pass
        elif default and type(default) == float:
            return default

    @staticmethod
    def str_to_list(s=None, default=None, separator='|'):
        if s:
            try:
                return [item for item in s.split(separator)]
            except:
                pass
        elif default and type(default) == list:
            return default


class EnvUtil(object):

    '''
    This class contains methods to manage enviroment setup
    Extends Util class
    '''

    @staticmethod
    def get_env_var(var, type=None, default=None, separator=None):
        v = None
        if type == bool:
            # bool
            v = Util.str_to_boolean(os.getenv(var), default)
        elif type == int:
            # int
            v = Util.str_to_int(os.getenv(var), default)
        elif type == float:
            # float
            v = Util.str_to_float(os.getenv(var), default)
        elif type == list:
            # list
            v = Util.str_to_list(os.getenv(var), default, separator)
        else:
            # str
            v = os.getenv(var, default)
        if v:
            return v
        else:
            raise ImproperlyConfigured('Set the {0} environment variable'.format(var))