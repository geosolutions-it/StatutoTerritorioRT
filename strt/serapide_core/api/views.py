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

import json
import logging
from collections import OrderedDict

from django.conf import settings

from django.core.paginator import QuerySetPaginator, Paginator

from django.http import HttpResponse, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from graphene_django.views import HttpError
from graphene_file_upload.django import FileUploadGraphQLView

from graphql_extensions.views import GraphQLView

from serapide_core.api.auth.user import is_recognizable, get_piani_visibili_id
from serapide_core.modello.enums_geo import (
    PO_CartografiaSupportoPrevisioniEnum,
    PO_CartografiaAssettiInsediativiEnum,
    PO_CartografiaDisciplinaInsediamentiEnum,
    PS_StrategiaEnum,
    PS_StatutoDelTerritorioEnum,
    PS_QuadroConoscitivoEnum, MAPPING_AZIONI_VALIDAZIONECARTO_LABEL,
)

from serapide_core.modello.models import (
    Piano,
    LottoCartografico,
    ElaboratoCartografico,
)

logger = logging.getLogger(__name__)


class HTTPErrorAwareMixin:

    def dispatch(self, request, *args, **kwargs):
        data = self.parse_body(request)
        show_graphiql = self.graphiql and self.can_display_graphiql(request, data)
        if self.batch:
            responses = [self.get_response(request, entry) for entry in data]
            result = "[{}]".format(
                ",".join([response[0] for response in responses])
            )
            status_code = (
                responses and
                max(responses, key=lambda response: response[1])[1] or 200
            )
        else:
            result, status_code = self.get_response(request, data, show_graphiql)
        _res = json.loads(result) if result else None
        if _res and 'errors' in _res and _res['errors'] and len(_res['errors']) > 0:
            _error = _res['errors'][0]
            _code = 400 if _error['code'] == 'error' else int(_error['code'])
            e = HttpError(HttpResponse(status=_code, content_type='application/json'), _error['message'])
            response = e.response
            # response.content = self.json_encode(request, {'errors': [self.format_error(e)]})
            response.content = self.json_encode(request, _res)
            return response
        if result and status_code:
            return HttpResponse(
                status=status_code, content=result, content_type="application/json"
            )
        else:
            return super().dispatch(request, *args, **kwargs)


class PrivateGraphQLView(HTTPErrorAwareMixin,
                         LoginRequiredMixin,
                         GraphQLView,
                         FileUploadGraphQLView):

    login_url = '/accounts/login/'
    redirect_field_name = 'next'


def geo_search(request, **kwargs):
    q = request.GET.get('q', None)
    page = request.GET.get('page', 1)
    limit = request.GET.get('limit', 10)
    include_empty = request.GET.get('include_empty', None)

    qs = get_piano_qs(request.user)

    if not include_empty:
        lotti_popolati = ElaboratoCartografico.objects.values('lotto').distinct()
        qs = qs.filter(lotto__in=lotti_popolati).distinct()

    if q:
        qs = qs.filter(descrizione__icontains=q)

    qs = qs.order_by('codice')

    paginator = Paginator(qs.all(), limit)
    page_obj = paginator.get_page(page)

    results = [ {
                'id': piano.codice,
                'type': piano.tipologia.value,
                'name': piano.descrizione,
                'comune': piano.ente.nome,
                'lastUpdate': piano.last_update,
            } for piano in page_obj ]

    response = {
        "page": page,
        "totalCount": paginator.count,
        'results': results
    }

    return JsonResponse(response, status=200)


def geo_get(request, pk=None):
    # piano: Piano = get_object_or_404(Piano, pk=pk)
    piano_qs = get_piano_qs(request.user)
    piano: Piano = piano_qs.filter(codice=pk).first()

    if not piano:
        return JsonResponse({'err':'piano non trovato'}, status=404)

    lotti = LottoCartografico.objects.filter(piano=piano)

    obj = OrderedDict()
    obj['id'] = piano.id
    obj['type'] = piano.tipologia.name
    obj['name'] = piano.descrizione
    obj['comune'] = piano.ente.nome

    map = OrderedDict()
    layers = []
    map['layers'] = layers
    obj['map'] = map

    geoserver_base_url = getattr(settings, 'GEOSERVER_BASE_URL')
    wms_url = '{}/wms'.format(geoserver_base_url)
    wfs_url = '{}/wfs'.format(geoserver_base_url)

    for lotto in lotti:
        for elaborato in ElaboratoCartografico.objects.filter(lotto=lotto):
            layer = OrderedDict()
            layers.append(layer)

            layer['id'] = elaborato.id
            layer['group'] = lotto.azione.tipologia.name
            layer['name'] = elaborato.get_layer_name()
            layer['description'] = find_layer_desc(elaborato.nome)
            layer['title'] = elaborato.nome
            layer['type'] = 'wms'
            layer['url'] = wms_url
            layer['search'] = {
                'url': wfs_url,
                'type': 'wfs' }
            bbox = OrderedDict()
            bbox['crs'] = elaborato.crs
            bounds = OrderedDict()
            bounds['minx'] = elaborato.minx
            bounds['maxx'] = elaborato.maxx
            bounds['miny'] = elaborato.miny
            bounds['maxy'] = elaborato.maxy
            bbox['bounds'] = bounds
            layer['bbox'] = bbox

            layer['visibility'] = True

    return JsonResponse(obj, status=200)


def find_layer_desc(nome_ec):
    for e in (PO_CartografiaSupportoPrevisioniEnum,
              PO_CartografiaAssettiInsediativiEnum,
              PO_CartografiaDisciplinaInsediamentiEnum,
              PS_StrategiaEnum,
              PS_StatutoDelTerritorioEnum,
              PS_QuadroConoscitivoEnum,):
        fixed = e.fix_enum(nome_ec, none_on_error=True)
        if fixed:
            return fixed.value

    return 'Sconosciuto'


def geo_groups(request):
    ret = [{
        'id': tipo_azione.name,
        'title': label,
    } for tipo_azione,label in MAPPING_AZIONI_VALIDAZIONECARTO_LABEL.items()]

    ret.reverse()

    return JsonResponse({'groups': ret}, status=200)


def get_piano_qs(user):
    if is_recognizable(user):
        id_piani = get_piani_visibili_id(user)
        return Piano.objects.filter(id__in=id_piani)
    else:
        return Piano.objects.none()
