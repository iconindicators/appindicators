#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


'''
Utility for converting markdown to html.

    *** NOT TO BE RUN DIRECTLY ***
'''

import sys

from readme_renderer.markdown import render # Installed by the calling script.

if "../" not in sys.path:
    sys.path.insert( 0, "../" )

from indicatorbase.src.indicatorbase import indicatorbase


def markdown_to_html( markdown, html ):
    content = ''.join( indicatorbase.IndicatorBase.read_text_file( markdown ) )
    content_rendered = render( content, variant = "CommonMark" )
    #TODO Can this be changed to use IndicatorBase.write_text_file()?
    with open( html, 'w', encoding = "utf-8" ) as f_out:
        f_out.write( content_rendered )
