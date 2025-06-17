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
# call this script/code...but how to specify the in.bsp (and possibly even the years)?
# The in.bsp can be a different/updated file over the years of various releases.
#
# Maybe instead of passing in the in.bsp and number of years,
# they are hardcoded in this script/function/code,
# but the parameters are printed to the screen so are visible during the build.#
#
# Thinking more, how does the stars.dat get put into the build/wheel?
# I think the in.bsp (whatever file that is) and the hip_main.dat need to be 
# present and hard coded into the create planets/stars ephemeris scripts/functions.
# in.bsp and hip_main.dat can live anywhere else outside the dev tree, or
# even perhaps in the dev tree at the top perhaps in a directory called data?
#
# So build_wheel.py also needs to call a function to create_stars ephemeris.
# Also create_stars could have two entry points: one function that is called
# to create the list of stars and other stuff which is done only once; the other
# is a function to call during the build which creates stars.dat
#
# Maybe define a module (file.py) in {indicator}/tools/build_wheel.py or something
# like that with a single function called build() that build_wheel.py calls
# if it exists (so only gets called for lunar).
# So tools/build_wheel.py then calls the create_planets_ephemeris.py and
# create_stars_ephemeris.py.
#
# Note that create_stars_ephemeris.py will have two entry points:
# one to be called to create/init all stuff for the lunar called one time only;
# another to be called during build just for stars.dat
#
# Both stars/planets build will need pip install (skyfield, jplephem, python-dateutil)
# so is it possible to do that install here in the function called by build_wheel?
#
# Will need a main
# https://stackoverflow.com/questions/59703821/import-module-without-running-it
# in the files/modules that create planets/stars


#TODO Given importing a module will run that module unless there is a __main__,
# check all the scripts with a _ in tools and lunar/tools.  Will say
# _create_ephemeris_stars.py run when being imported (maybe put in a print line
# to see if being called twice).  
# Do the same for _build_wheel.py to see if it is being run twice by build_wheel.py.

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
