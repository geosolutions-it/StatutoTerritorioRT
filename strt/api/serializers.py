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

from rest_framework import serializers
from strt_users.models import (Qualifica, Profilo)


class QualificaSerializer(serializers.ModelSerializer):

    class Meta:
        model = Qualifica
        fields = '__all__'


class ProfiloSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profilo
        fields = '__all__'
