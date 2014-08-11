#!/usr/bin/env python3
#
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
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import datetime, stardate


# Exercise the Stardate API.
currentStardate = stardate.Stardate()
print( "Stardate API version: " + currentStardate.getVersion() )

now = datetime.datetime.now()

# Get the 'classic' stardate for the current date/time.
currentStardate.setClassic( True )
currentStardate.setGregorian( now )
print( str( now ) + " = " + currentStardate.toStardateString( True, False ) + " 'classic'" )

# Use the calculated 'classic' stardate to get the date/time (should be the same but rounding plays a part).
currentStardate.setStardateClassic( currentStardate.getStardateIssue(), currentStardate.getStardateInteger(), currentStardate.getStardateFraction() )
print( currentStardate.toStardateString( True, False ) + " 'classic' = " + currentStardate.toGregorianString() )

# Get the '2009 revised' stardate from the current date/time.
currentStardate.setClassic( False ) 
currentStardate.setGregorian( now )
print( str( now ) + " = " + currentStardate.toStardateString( True, False ) + " '2009 revised'" )

# Use the calculated '2009 revised' stardate to get the date/time (will always be midnight).
currentStardate.setStardate2009Revised( currentStardate.getStardateInteger(), currentStardate.getStardateFraction() )
print( currentStardate.toStardateString( True, False ) + " '2009 revised' = " + currentStardate.toGregorianString() )