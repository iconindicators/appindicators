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

stardateIssue, stardateInteger, stardateFraction = stardate.getStardateClassic( utcNow )
print( "'classic' Stardate (issue, integer, fraction, fractionalPeriod):", stardateIssue, stardateInteger, stardateFraction )
print( "'classic' Stardate (as string):", stardate.toStardateString( stardateIssue, stardateInteger, stardateFraction, True, False ) )

# Use the calculated 'classic' Stardate to get the date/time (should be the same but rounding plays a part).
print( "UTC now from 'classic' Stardate:", stardate.getGregorianFromStardateClassic( stardateIssue, stardateInteger, stardateFraction ) )

print()

stardateInteger, stardateFraction = stardate.getStardate2009Revised( utcNow )
print( "'2009Revised' Stardate (integer, fraction, fractionalPeriod):", stardateInteger, stardateFraction )
print( "'2009Revised' Stardate (as string):", stardate.toStardateString( None, stardateInteger, stardateFraction, None, False ) )

# Use the calculated '2009Revised' Stardate to get the date/time (should be the same but rounding plays a part).
print( "UTC now from '2009Revised' Stardate:", stardate.getGregorianFromStardate2009Revised( stardateInteger, stardateFraction ) )