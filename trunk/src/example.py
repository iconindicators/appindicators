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
now = datetime.datetime.now()
currentStardate = stardate.Stardate() # By default, 'classic' will be used.
print( "Stardate API version: " + currentStardate.getVersion() )


# Test 'classic' stardate.
currentStardate.setGregorian( now )
print( str( now.year ) + "/" + str( now.month ) + "/" + str( now.day ) + " " + 
       str( now.hour ) + ":" + str( now.minute ) + ":" + str( now.second ) + " (y/m/d h:m:s) = " + 
       currentStardate.toStardateString( True ) + " 'classic'" )

currentStardate.setStardateClassic( currentStardate.getStardateIssue(), currentStardate.getStardateInteger(), currentStardate.getStardateFraction() )
print( "[" + str( currentStardate.getStardateIssue() ) + "] " + 
       str( currentStardate.getStardateInteger() ) + "." + 
       str( currentStardate.getStardateFraction() ) + " 'classic' = " + 
       currentStardate.toGregorianString() )


# Test '2009 revised' stardate.
currentStardate.setClassic( False ) # Now using '2009 revised'.
currentStardate.setGregorian( now )
print( str( now.year ) + "/" + str( now.month ) + "/" + str( now.day ) + " " + 
       str( now.hour ) + ":" + str( now.minute ) + ":" + str( now.second ) + " (y/m/d h:m:s) = " + 
       currentStardate.toStardateString( True ) + " '2009 revised'" )

currentStardate.setStardate2009Revised( currentStardate.getStardateInteger(), currentStardate.getStardateFraction() )
print( str( currentStardate.getStardateInteger() ) + "." + 
       str( currentStardate.getStardateFraction() ) + " '2009 revised' = " + 
       currentStardate.toGregorianString() )