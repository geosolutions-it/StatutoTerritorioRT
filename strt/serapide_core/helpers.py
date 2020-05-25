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

"""Script defined to create helper functions for graphql schema."""

import logging

from django.conf import settings
from django.utils.text import slugify
from inflector import Inflector, English
from graphql_relay.node.node import from_global_id

from strt_users.enums import Profilo
from strt_users.models import ProfiloUtente

INFLECTOR = Inflector(English)

logger = logging.getLogger(__name__)


def get_object(object_name, relayId, otherwise=None):
    try:
        return object_name.objects.get(pk=from_global_id(relayId)[1])
    except BaseException:
        return otherwise


def update_create_instance(instance, args, exception=['id']):
    if instance:
        [setattr(instance, key, value) for key, value in args.items() if key not in exception]

    # caution if you literally cloned this project, then be sure to have
    # elasticsearch running as every saved instance must go through
    # elasticsearch according to the way this project is configured.
    instance.save()

    return instance


def get_errors(e):
    # transform django errors to redux errors
    # django: {"key1": [value1], {"key2": [value2]}}
    # redux: ["key1", "value1", "key2", "value2"]
    fields = e.message_dict.keys()
    messages = ['; '.join(m) for m in e.message_dict.values()]
    errors = [i for pair in zip(fields, messages) for i in pair]
    return errors


def unslugify(value):
    return INFLECTOR.titleize(slugify(value, allow_unicode=True))
