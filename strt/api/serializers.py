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
from strt_users.models import Qualifica


class QualificaSerializer(serializers.ModelSerializer):

    class Meta:
        model = Qualifica
        fields = '__all__'


# class RuoloSerializer(serializers.ModelSerializer):
#
#     type = QualificaSerializer()
#
#     class Meta:
#         model = Ruolo
#         fields = '__all__'
