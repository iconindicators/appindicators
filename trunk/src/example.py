#!/usr/bin/env python
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


import datetime
import stardate

# Exercise the Stardate API.

currentStardate = stardate.Stardate()

print "Stardate API version: " + currentStardate.getVersion()

stardateIssue = -28
stardateInteger = 6857
stardateFraction = 59
currentStardate.setStardate( stardateIssue, stardateInteger, stardateFraction )
print "Stardate [" + str( stardateIssue ) + "] " + str( stardateInteger ) + "." + str( stardateFraction ) + " = " + currentStardate.toGregorianString()

gregorianYear = 2012
gregorianMonth = 6
gregorianDay = 11
gregorianHour = 16
gregorianMinute = 49
gregorianSecond = 20
currentStardate.setGregorian( datetime.datetime( gregorianYear, gregorianMonth, gregorianDay, gregorianHour, gregorianMinute, gregorianSecond ) )
print "Gregorian " + str( gregorianYear ) + "/" + str( gregorianMonth ) + "/" + str( gregorianDay ) + " " + str( gregorianHour ) + ":" + str( gregorianMinute ) + ":" + str( gregorianSecond ) + " (y/m/d h:m:s) = " + currentStardate.toStardateString( False, True )
