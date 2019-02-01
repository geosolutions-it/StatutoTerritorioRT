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

import json

from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from graphene_django.views import HttpError
from graphene_file_upload.django import FileUploadGraphQLView

from graphql_extensions.views import GraphQLView


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
                responses
                and max(responses, key=lambda response: response[1])[1]
                or 200
            )
        else:
            result, status_code = self.get_response(request, data, show_graphiql)
        _res = json.loads(result)
        if 'errors' in _res and _res['errors'] and len(_res['errors']) > 0:
            _error = _res['errors'][0]
            e = HttpError(HttpResponse(status=_error['code'], content_type='application/json'), _error['message'])
            response = e.response
            # response.content = self.json_encode(request, {'errors': [self.format_error(e)]})
            response.content = self.json_encode(request, _res)
            return response

        return super().dispatch(request, *args, **kwargs)


class PrivateGraphQLView(HTTPErrorAwareMixin,
                         LoginRequiredMixin,
                         GraphQLView,
                         FileUploadGraphQLView):

    login_url = '/accounts/login/'
    redirect_field_name = 'next'
