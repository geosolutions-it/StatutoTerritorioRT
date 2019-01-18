# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright 2018, GeoSolutions Sas.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.
#
#########################################################################

from django.contrib import admin

from .models import Fase, Risorsa, Piano, RisorsePiano

class RisorsePianoInline(admin.TabularInline):
    model = RisorsePiano


class PianoAdmin(admin.ModelAdmin):
    inlines = [RisorsePianoInline, ]

admin.site.register(Fase)
admin.site.register(Risorsa)
admin.site.register(Piano, PianoAdmin)
