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


from wagtail.admin.edit_handlers import StreamFieldPanel
from wagtail.core.fields import StreamField
from wagtail.core.models import Page
from .blocks import (
    FirstSectionBlock, SecondSectionBlock, ThirdSectionBlock,
    FourthSectionBlock, FifthSectionBlock, SixthSectionBlock
)


class Home(Page):
    """
    Statuto del Territorio RT Homepage.
    Put desired fields in the content_panels list below to manage
    the page contents in the Wagtail admin.
    """

    body = StreamField([
        ('First_section', FirstSectionBlock(
            verbose_name='First section block',
            blank=True
        )),
        ('Second_section', SecondSectionBlock(
            verbose_name='First section block',
            blank=True
        )),
        ('Third_section', ThirdSectionBlock(
            verbose_name='Third section block',
            blank=True
        )),
        ('Fourth_section', FourthSectionBlock(
            verbose_name='Fourth section block',
            blank=True
        )),
        ('Fifth_section', FifthSectionBlock(
            verbose_name='Fifth section block',
            blank=True
        )),
        ('Sixth_section', SixthSectionBlock(
            verbose_name='Sixth section block',
            blank=True
        ))
    ])

    content_panels = Page.content_panels + [
        StreamFieldPanel('body')
    ]
