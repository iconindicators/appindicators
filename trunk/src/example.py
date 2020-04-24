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


import datetime, stardate


# Exercise the Stardate API.
print( "Stardate API version: " + stardate.getVersion(), "\n" )

utcNow = datetime.datetime.utcnow()
print( "UTC now:", utcNow, "\n" )

stardateClassic = stardate.getStardateClassic( utcNow )
print( "'classic' Stardate (issue, integer, fraction, fractionalPeriod):", stardateClassic )
print( "'classic' Stardate (as string):", stardate.toStardateString( stardateClassic[ 0 ], stardateClassic[ 1 ], stardateClassic[ 2 ], True, False ) )

# Use the calculated 'classic' Stardate to get the date/time (should be the same but rounding plays a part).
print( "UTC now from 'classic' Stardate:", stardate.getGregorianFromStardateClassic( stardateClassic[ 0 ], stardateClassic[ 1 ], stardateClassic[ 2 ] ), "\n" )

stardate2009Revised = stardate.getStardate2009Revised( utcNow )
print( "'2009Revised' Stardate (integer, fraction, fractionalPeriod):", stardate2009Revised )
print( "'2009Revised' Stardate (as string):", stardate.toStardateString( None, stardate2009Revised[ 0 ], stardate2009Revised[ 1 ], None, False ) )

# Use the calculated '2009Revised' Stardate to get the date/time (should be the same but rounding plays a part).
print( "UTC now from '2009Revised' Stardate:", stardate.getGregorianFromStardate2009Revised( stardate2009Revised[ 0 ], stardate2009Revised[ 1 ] ) )