#########################################################################
#
# Copyright 2018, GeoSolutions Sas.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.
#
#########################################################################


from wagtail.images.blocks import ImageChooserBlock
from wagtail.core.blocks import (
    CharBlock, StructBlock
)


class BaseBlock(StructBlock):
    '''
    Base StructBlock for the page elements
    '''
    title = CharBlock(
        required=False
    )
    subtitle = CharBlock(
        required=False
    )
    text = CharBlock(
        required=False
    )
    image = ImageChooserBlock(
        required=True
    )
    button_text = CharBlock(
        required=False
    )

    class Meta:
        abstract = True


class FirstSectionBlock(BaseBlock):

    class Meta:
        template = 'strt_portal/blocks/first_section_block.html'







