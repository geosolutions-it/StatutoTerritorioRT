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
import logging

from django.conf import settings
from django.core.mail import get_connection, EmailMessage
from django.template.loader import render_to_string
from django.utils.translation import ugettext
from django.contrib.sites.models import Site
import django.contrib.auth as auth

from pinax.notifications.backends.base import BaseBackend

logger = logging.getLogger(__name__)


class EmailBackend(BaseBackend):
    spam_sensitivity = 2

    def can_send(self, user, notice_type, scoping):
        if isinstance(user, auth.get_user_model()):
            can_send = super(EmailBackend, self).can_send(user, notice_type, scoping)
        else:
            can_send = True

        if can_send and user.email:
            return True
        return False

    def deliver(self, recipient, sender, notice_type, extra_context):
        # TODO: require this to be passed in extra_context

        logger.warning('*** Delivering to {}'.format(recipient))

        connection = get_connection()

        # Manually open the connection
        connection.open()

        try:
            context = self.default_context()
            context.update({
                "recipient": recipient,
                "sender": sender,
                "notice": ugettext(notice_type.display),
            })

            current_site = Site.objects.get_current()
            context.update({
                "current_site_name": current_site.name
            })

            # put in some Piano fields explicitly, since piano.codice etc seem not to work in template
            piano = extra_context["piano"]
            context.update({
                "piano_codice":      piano.codice,
                "piano_descrizione": piano.descrizione or '',
                "piano_ente":        piano.ente.nome,
            })

            context.update(extra_context)

            messages = self.get_formatted_messages((
                "short.txt",
                "full.txt"
            ), notice_type.label, context)

            context.update({
                "message_short": messages["short.txt"],
                "message":       messages["full.txt"]
            })

            subject = "".join(render_to_string("pinax/notifications/email_subject.txt", context).splitlines())
            body = render_to_string("pinax/notifications/email_body.txt", context)
            # if(recipient.)

            # logger.warning('*** MAIL BODY \n{}'.format(body))

            to = '"{name} {surname}"<{email}>'.format(
                email=recipient.email,
                name=recipient.first_name or '',
                surname=recipient.last_name or '')

            email = EmailMessage(
                subject=subject,
                body=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[to, ],
                reply_to=[settings.DEFAULT_FROM_EMAIL, ])
            email.content_subtype = "html"

            connection.send_messages([email, ])
            # The connection was already open so send_messages() doesn't close it.
        except BaseException as e:
            logger.error('Error in sending mail notification for [{}] to [{}]'.format(notice_type, recipient),
                         exc_info=e)
        finally:
            # We need to manually close the connection.
            connection.close()
