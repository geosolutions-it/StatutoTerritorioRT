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

from django.contrib import admin

from .models import (
    # Fase,
    Risorsa,
    # Referente,
    SoggettoOperante,
    Delega,
    Azione,
    Piano, RisorsePiano,
    ProceduraVAS, RisorseVas,
    ProceduraAdozioneVAS, RisorseAdozioneVas,
    ProceduraAvvio, RisorseAvvio,
    ProceduraAdozione, RisorseAdozione,
    ProceduraApprovazione, RisorseApprovazione,
    ProceduraPubblicazione, RisorsePubblicazione,
    ParereVAS,
    ParereAdozioneVAS,
    ConferenzaCopianificazione,
    RisorseCopianificazione,
    PianoControdedotto,
    PianoRevPostCP,
    RisorsePianoControdedotto,
    RisorsePianoRevPostCP,
)


class RisorsePianoInline(admin.TabularInline):
    model = RisorsePiano


class RisorseVasInline(admin.TabularInline):
    model = RisorseVas


class RisorseAdozioneVasInline(admin.TabularInline):
    model = RisorseAdozioneVas


class RisorseAvvioInline(admin.TabularInline):
    model = RisorseAvvio


class RisorseAdozioneInline(admin.TabularInline):
    model = RisorseAdozione


class RisorseApprovazioneInline(admin.TabularInline):
    model = RisorseApprovazione


class RisorsePubblicazioneInline(admin.TabularInline):
    model = RisorsePubblicazione


class RisorseCopianificazioneInline(admin.TabularInline):
    model = RisorseCopianificazione


class RisorsePianoControdedottoInline(admin.TabularInline):
    model = RisorsePianoControdedotto


class RisorsePianoRevPostCPInline(admin.TabularInline):
    model = RisorsePianoRevPostCP


class SoggettoOperanteInline(admin.TabularInline):
     model = SoggettoOperante


# class TokensInline(admin.TabularInline):
#      model = Token


class ParereVASInline(admin.TabularInline):
    model = ParereVAS


class ParereAdozioneVASInline(admin.TabularInline):
    model = ParereAdozioneVAS


# class ReferenteAdmin(admin.ModelAdmin):
#     list_display = ('tipo', 'piano', 'ruolo', 'ufficio')


class PianoAdmin(admin.ModelAdmin):
    inlines = [#AzioniPianoInline,
               SoggettoOperanteInline,
               RisorsePianoInline]
               # TokensInline, ]


class ProceduraVASAdmin(admin.ModelAdmin):
    inlines = [RisorseVasInline, ]


class ProceduraAdozioneVASAdmin(admin.ModelAdmin):
    inlines = [RisorseAdozioneVasInline, ]


class ProceduraAvvioAdmin(admin.ModelAdmin):
    inlines = [RisorseAvvioInline, ]


class ProceduraAdozioneAdmin(admin.ModelAdmin):
    inlines = [ParereAdozioneVASInline, RisorseAdozioneInline, ]


class ProceduraApprovazioneAdmin(admin.ModelAdmin):
    inlines = [RisorseApprovazioneInline, ]


class ProceduraPubblicazioneAdmin(admin.ModelAdmin):
    inlines = [RisorsePubblicazioneInline, ]


class ConferenzaCopianificazioneAdmin(admin.ModelAdmin):
    inlines = [RisorseCopianificazioneInline, ]


class PianoControdedottoAdmin(admin.ModelAdmin):
    inlines = [RisorsePianoControdedottoInline, ]


class PianoRevPostCPAdmin(admin.ModelAdmin):
    inlines = [RisorsePianoRevPostCPInline, ]


# admin.site.register(Fase)
admin.site.register(Azione)
admin.site.register(Risorsa)
# admin.site.register(Referente, ReferenteAdmin)
admin.site.register(Piano, PianoAdmin)
admin.site.register(ProceduraVAS, ProceduraVASAdmin)
admin.site.register(ProceduraAdozioneVAS, ProceduraAdozioneVASAdmin)
admin.site.register(ProceduraAvvio, ProceduraAvvioAdmin)
admin.site.register(ProceduraAdozione, ProceduraAdozioneAdmin)
admin.site.register(ProceduraApprovazione, ProceduraApprovazioneAdmin)
admin.site.register(ProceduraPubblicazione, ProceduraPubblicazioneAdmin)
admin.site.register(ConferenzaCopianificazione, ConferenzaCopianificazioneAdmin)
admin.site.register(PianoControdedotto, PianoControdedottoAdmin)
admin.site.register(PianoRevPostCP, PianoRevPostCPAdmin)

@admin.register(Delega)
class DelegaModelAdmin(admin.ModelAdmin):
    # list_display = ['qualifica', 'delegante', 'piano','created', 'created_by']
    list_display = ['_piano', 'qualifica', '_delegante', '_key', '_user', 'created', '_created_by']
    search_fields = ['created', 'created_by']
    list_filter = ['created', 'created_by']

    def _delegante(self, obj):
        return '{}:{}'.format(
            obj.delegante.qualifica_ufficio.qualifica.name,
            obj.delegante.qualifica_ufficio.ufficio)

    def _piano(self, obj):
        return obj.delegante.piano.codice

    def _key(self, obj):
        return obj.token.key

    def _user(self, obj):
        return obj.token.user.get_full_name() if obj.token.user else None

    def _created_by(self, obj):
        return obj.created_by.get_full_name() if obj.created_by else None
