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


import datetime

import stardate


# Exercise the Stardate API.
print( "Stardate API version: " + stardate.get_version(), "\n" )

utc_now = datetime.datetime.now( datetime.timezone.utc )
print( "UTC now:", utc_now, "\n" )

stardate_issue, stardate_integer, stardate_fraction = \
    stardate.get_stardate_classic( utc_now )

print(
    "'classic' Stardate (issue, integer, fraction, fractionalPeriod):",
    stardate_issue, stardate_integer, stardate_fraction )

print(
    "'classic' Stardate (as string):",
    stardate.to_stardate_string( stardate_issue, stardate_integer, stardate_fraction, True, False ) )

# Use the calculated 'classic' Stardate to get the date/time (should be the same but rounding plays a part).
print(
    "UTC now from 'classic' Stardate:",
    stardate.get_gregorian_from_stardate_classic( stardate_issue, stardate_integer, stardate_fraction ) )

print()

stardate_integer, stardate_fraction = stardate.get_stardate_2009_revised( utc_now )
print(
    "'2009Revised' Stardate (integer, fraction, fractionalPeriod):",
    stardate_integer, stardate_fraction )

print(
    "'2009Revised' Stardate (as string):",
    stardate.to_stardate_string( None, stardate_integer, stardate_fraction, None, False ) )

# Use the calculated '2009Revised' Stardate to get the date/time (should be the same but rounding plays a part).
print(
    "UTC now from '2009Revised' Stardate:",
    stardate.get_gregorian_from_stardate_2009_revised( stardate_integer, stardate_fraction ) )
