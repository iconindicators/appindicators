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


''' Exercise the Stardate API. '''


import datetime

import stardate


print( f"Stardate API version: {stardate.get_version() }\n" )

utc_now = datetime.datetime.now( datetime.timezone.utc )
print( f"UTC now: { utc_now }\n" )

#TODO Remove \
stardate_issue, stardate_integer, stardate_fraction = \
    stardate.get_stardate_classic( utc_now )

print(
    f"'classic' Stardate components (issue, integer, fraction): " + \
    f"{ stardate_issue } { stardate_integer } { stardate_fraction }" )

stardate_as_string = \
    stardate.to_stardate_string(
        stardate_issue,
        stardate_integer,
        stardate_fraction,
        True,
        False )

print( f"'classic' Stardate string: { stardate_as_string }" )

# Use the calculated 'classic' Stardate to get the date/time;
# should be the same but rounding plays a part.
utc_now_from_stardate_classic = \
    stardate.get_gregorian_from_stardate_classic(
        stardate_issue,
        stardate_integer,
        stardate_fraction )
print( f"UTC now from 'classic' Stardate: { utc_now_from_stardate_classic }\n" )

stardate_integer, stardate_fraction = \
    stardate.get_stardate_2009_revised( utc_now )
print(
    f"'2009 Revised' Stardate components (integer, fraction): "
    f"{ stardate_integer }, { stardate_fraction }" )

print(
    "'2009 Revised' Stardate (as string):",
    stardate.to_stardate_string( None, stardate_integer, stardate_fraction, None, False ) )

# Use the calculated '2009 Revised' Stardate to get the date/time;
# should be the same but rounding plays a part.
utc_now_from_stardate_2009 = \
    stardate.get_gregorian_from_stardate_2009_revised(
        stardate_integer,
        stardate_fraction )
print( f"UTC now from '2009 Revised' Stardate: { utc_now_from_stardate_2009 } " )
