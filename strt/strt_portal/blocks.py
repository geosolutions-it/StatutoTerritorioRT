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


from wagtail.images.blocks import ImageChooserBlock
from wagtail.core.blocks import (
    CharBlock, StructBlock, TextBlock, RichTextBlock
)


class BaseBlock(StructBlock):

    title = CharBlock(required=False)
    subtitle = CharBlock(required=False)
    text = TextBlock(required=False)
    image = ImageChooserBlock(required=False)
    button_text = CharBlock(required=False)
    button_url = CharBlock(required=False)
    button_target = CharBlock(required=False)


class FirstSectionBlock(BaseBlock):

    class Meta:
        template = 'strt_portal/blocks/first_section_block.html'


class SecondSectionBlock(StructBlock):

    first_column = BaseBlock(label='first column content')
    second_column = BaseBlock(label='second column content')
    third_column = BaseBlock(label='third column content')

    class Meta:
        template = 'strt_portal/blocks/second_section_block.html'


class ThirdSectionBlock(StructBlock):

    main_block = BaseBlock(label='main content')
    details_block = RichTextBlock(label='detailed content')

    class Meta:
        template = 'strt_portal/blocks/third_section_block.html'


class DetailedBlock(BaseBlock):

    short_description = TextBlock(required=False)
    detailed_description = TextBlock(required=False)
    left_detailed_content = RichTextBlock(required=False)
    right_detailed_content = RichTextBlock(required=False)


class FourthSectionBlock(StructBlock):

    title = CharBlock(required=False)
    first_box = DetailedBlock(label='first box content')
    second_box = DetailedBlock(label='second box content')
    third_box = DetailedBlock(label='third box content')
    fourth_box = DetailedBlock(label='fourth box content')

    class Meta:
        template = 'strt_portal/blocks/fourth_section_block.html'


class FifthSectionBlock(BaseBlock):

    class Meta:
        template = 'strt_portal/blocks/fifth_section_block.html'


class SixthSectionBlock(BaseBlock):

    class Meta:
        template = 'strt_portal/blocks/sixth_section_block.html'
