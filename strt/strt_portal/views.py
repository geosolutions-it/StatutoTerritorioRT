#########################################################################
#
# Copyright 2018, GeoSolutions Sas.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.
#
#########################################################################


from django.views.generic.base import TemplateView


class PrivateAreaView(TemplateView):

    template_name = "strt_portal/private_area.html"


class SerapideView(TemplateView):

    template_name = "../../serapide-client/build/index.html" # serapide-client


class GeoportalView(TemplateView):

    template_name = "strt_portal/geoportal/geoportal.html"


class OpendataView(TemplateView):

    template_name = "strt_portal/opendata/opendata.html"


class GlossaryView(TemplateView):

    template_name = "strt_portal/glossary/glossary.html"
