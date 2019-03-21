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

from .models import (
    Fase,
    Risorsa,
    Contatto,
    Azione, AzioniPiano,
    Piano, RisorsePiano,
    ProceduraVAS, RisorseVas,
    ProceduraAvvio, RisorseAvvio,
    AutoritaCompetenteVAS,
    AutoritaIstituzionali,
    AltriDestinatari,
    SoggettiSCA,
    PianoAuthTokens,
    ConsultazioneVAS
)


class AzioniPianoInline(admin.TabularInline):
    model = AzioniPiano


class RisorsePianoInline(admin.TabularInline):
    model = RisorsePiano


class RisorseVasInline(admin.TabularInline):
    model = RisorseVas


class RisorseAvvioInline(admin.TabularInline):
    model = RisorseAvvio


class AutoritaCompetenteVASInline(admin.TabularInline):
    model = AutoritaCompetenteVAS


class AutoritaIstituzionaliInline(admin.TabularInline):
    model = AutoritaIstituzionali


class AltriDestinatariInline(admin.TabularInline):
    model = AltriDestinatari


class SoggettiSCAInline(admin.TabularInline):
    model = SoggettiSCA


class TokensInline(admin.TabularInline):
    model = PianoAuthTokens


class PianoAdmin(admin.ModelAdmin):
    inlines = [AzioniPianoInline,
               AutoritaCompetenteVASInline,
               AutoritaIstituzionaliInline,
               AltriDestinatariInline,
               SoggettiSCAInline,
               RisorsePianoInline,
               TokensInline, ]


class ProceduraVASAdmin(admin.ModelAdmin):
    inlines = [RisorseVasInline, ]


class ProceduraAvvioAdmin(admin.ModelAdmin):
    inlines = [RisorseAvvioInline, ]


admin.site.register(Fase)
admin.site.register(Azione)
admin.site.register(Risorsa)
admin.site.register(Contatto)
admin.site.register(Piano, PianoAdmin)
admin.site.register(ProceduraVAS, ProceduraVASAdmin)
admin.site.register(ProceduraAvvio, ProceduraAvvioAdmin)
admin.site.register(ConsultazioneVAS)
