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
Backend which creates a planet ephemeris for use in astroskyfield.

                 *** NOT TO BE RUN DIRECTLY ***
'''


#TODO THinking that this stays as is and is called by the build_wheel.py
# process at some point (when building indicatorlunar with astroskyfield).
#
# How would the build know about this...?
# Probably should be called after the source is copied across.
# The build_wheel.py needs to check if the indicator == indicatorluar and if so,
# call this script/code...but how to specify the in.bsp?
# The in.bsp can be a different file over the years.


import datetime

from dateutil.relativedelta import relativedelta

from jplephem.daf import DAF
from jplephem.spk import SPK
from jplephem import calendar, excerpter


def _gregorian_to_julian( yyyy_slash_mm_slash_dd ):
    '''
    Taken from
        https://github.com/brandon-rhodes/python-jplephem/blob/master/jplephem/commandline.py
    '''
    fields = [ int( f ) for f in yyyy_slash_mm_slash_dd.split( '/' ) ]
    return calendar.compute_julian_date( *fields )


def create_ephemeris_planets(
    in_bsp,
    out_bsp,
    years ):

    today = datetime.date.today()
    start_date = today - relativedelta( months = 1 )
    end_date = today.replace( year = today.year + int( years ) )
    date_format = "%Y/%m/%d"

    with open( in_bsp, "rb" ) as f_in:
        spk = SPK( DAF( f_in ) )
        summaries = spk.daf.summaries()
        with open( out_bsp, "w+b" ) as f_out:
            excerpter.write_excerpt(
                spk,
                f_out,
                _gregorian_to_julian( start_date.strftime( date_format ) ),
                _gregorian_to_julian( end_date.strftime( date_format ) ),
                summaries )
