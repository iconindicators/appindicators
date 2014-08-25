#!/usr/bin/env python3


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


# Converts between Star Trek™ stardates and Gregorian date/times.
# There are two types of stardates: 'classic' and '2009 revised'.
#
#
# 'classic' stardates
# -------------------
#
# The 'classic' stardate is based on STARDATES IN STAR TREK FAQ V1.6 by Andrew Main.
#
# Stardates are related to Julian/Gregorian dates as depicted on the following time line:
#
#      <------x------x------x------x------x------x------x------>
#             |      |      |      |     |       |      |
#             |      |      |      |     |       |      |
#          6000 BC   |   1582 AD   | 2270-01-26  |  2323-01-01
#                    |             |             |
#                  46 BC       2162-01-04    2283-10-05
#
# From 6000 BC up to 46 BC, the Egyptian-developed calendar was used.
# Initially based on counting lunar cycles, it was eventually changed to a solar calendar.
#
# Between 46 BC to 1582 AD, the Julian calendar was used.
# This was the first calendar to introduce the "leap year".
#
# The Gregorian calendar commenced in 1582 and is in use to this day.
# It is based on a modified version of the Julian calendar.
#
# In 2162, stardates were developed by Starfleet.
# Stardate [0]0000.0 commenced on midnight 4/1/2162.  
# The stardate rate from this date to 26/1/2270 was 5 units per day.
#
# Between 26/1/2270 and 5/10/2283 ([19]7340.0 and [19]7840.0, respectively)
# the rate changes to 0.1 units per day.
#
# Between 5/10/2283 to 1/1/2323 ([19]7840.0 and [20]5006.0, respectively),
# the rate changes to 0.5 units per day.
#
# From 1/1/2323 ([20]5006.0) the rate changed to 1000 units per mean solar year (365.2425 days).  
# Also, stardate [20]5006.0 becomes [21]00000.0.
#
#
# '2009 revised'
# --------------
#
# The '2009 revised' stardate is based on http://en.wikipedia.org/wiki/Stardate.



import datetime, math


class Stardate( object ):

    def __init__( self ):
        self.API_VERSION = "Version 3.1 (2014-08-11)"

        # Rates (in stardate units per day) for each 'classic' stardate era. 
        self.stardateRates = [ 5.0, 5.0, 0.1, 0.5, 1000.0 / 365.2425 ]

        # The Gregorian dates which reflect the start date for each rate in the 'classic' stardate era.
        # For example, an index of 3 (Gregorian date of 5/10/2283) corresponds to the rate of 0.5 stardate units per day.
        # The month is one-based (January = 1).
        self.gregorianDates = []
        self.gregorianDates.append( datetime.datetime( 2162, 1, 4, ) )
        self.gregorianDates.append( datetime.datetime( 2162, 1, 4 ) )
        self.gregorianDates.append( datetime.datetime( 2270, 1, 26 ) )
        self.gregorianDates.append( datetime.datetime( 2283, 10, 5 ) )
        self.gregorianDates.append( datetime.datetime( 2323, 1, 1 ) )

        # Internal representation for the Gregorian date/time. 
        self.gregorianDateTime = None

        # Internal representation for the 'classic' stardate. 
        self.stardateIssue = None
        self.stardateInteger = None
        self.stardateFraction = None

        # The index specifying the specific 'classic' stardate rate.
        self.index = -1

        # If True = 'classic' conversion; False = '2009 revised' conversion.
        self.classic = True


    # Gets the API version.
    def getVersion( self ): return self.API_VERSION


    # Gets the period (in seconds) between updates/changes to the current stardate.
    def getStardateFractionalPeriod( self ):
        if self.classic:
            if self.index == -1: raise Exception( "Please set a valid gregorian date or stardate." )
            return int( 1.0 / ( self.stardateRates[ self.index ] / 24.0 / 60.0 / 60.0 ) / 10.0 )

        return ( 24 * 60 * 60 )


    # Sets the conversion method, either 'classic' or '2009 revised'.
    #
    #  classic If True, 'classic' conversion is used; otherwise '2009 revised' conversion.   
    def setClassic( self, classic ): self.classic = classic


    # Gets the conversion method, either 'classic' or '2009 revised'.
    #
    # Returns true if 'classic' conversion is used; false if '2009 revised' conversion.   
    def getClassic( self ): return self.classic


    # Sets a Gregorian date/time in UTC object for conversion to a ('classic' or '2009 revised') stardate.
    # Note the 'classic' status must be set PRIOR to setting the Gregorian date/time.
    #
    #  gregorianDateTime A Gregorian date/time in UTC to be converted to a stardate (1900 <= year <= 9500).
    #
    # Raises an exception if the Gregorian year is out the defined range.
    def setGregorian( self, gregorianDateTime ):
        if ( gregorianDateTime.year < 1900 ) or ( gregorianDateTime.year > 9500 ): raise Exception( "Gregorian year out of range: 1900 <= year <= 9500." )

        self.gregorianDateTime = gregorianDateTime
        if self.classic: self.__gregorianToStardateClassic()
        else: self.__gregorianToStardate2009Revised()


    # Sets a 'classic' stardate for conversion to a Gregorian date/time.
    #
    # Rules:
    #  issue <= 19: 0 <= integer <= 9999, fraction >= 0. 
    #  issue == 20: 0 <= integer < 5006, fraction >= 0. 
    #  issue >= 21: 0 <= integer <= 99999, fraction >= 0. 
    #
    #  issue The issue number for the stardate (can be negative).
    #  integer The integer part of a stardate.
    #  fraction The fractional part of a stardate.
    #
    # Raises an exception if the issue/integer/fraction are out of the defined ranges.
    def setStardateClassic( self, issue, integer, fraction ):
        if issue <= 19 and ( integer < 0 or integer > 9999 ): raise Exception( "Integer out of range: 0 <= integer <= 9999" )

        if issue == 20 and ( integer < 0 or integer >= 5006 ): raise Exception( "Integer out of range: 0 <= integer < 5006" )

        if issue >= 21 and ( integer < 0 or integer > 99999 ): raise Exception( "Integer out of range: 0 <= integer <= 99999" )

        if fraction < 0: raise Exception( "Fraction cannot be negative." )

        self.stardateIssue = issue
        self.stardateInteger = integer
        self.stardateFraction = fraction
        self.__stardateToGregorianClassic()


    # Sets a '2009 revised' stardate for conversion to a Gregorian date/time.
    #
    #  integer The integer part of a stardate (corresponds to a Gregorian year).
    #  fraction The fractional part of a stardate (0 <= fraction <= 365, or 366 if integer corresponds to a leap year).
    #
    # Raises an exception if the issue/integer/fraction are out of the defined ranges.
    def setStardate2009Revised( self, integer, fraction ):
        if fraction < 0: raise Exception( "Fraction cannot be negative." )

        isLeapYear = ( integer % 4 == 0 and integer % 100 != 0 ) or integer % 400 == 0
        if isLeapYear:
            if fraction > 366: raise Exception( "Integer cannot exceed 366." )
        else:
            if fraction > 365: raise Exception( "Integer cannot exceed 365." )

        self.stardateInteger = integer
        self.stardateFraction = fraction
        self.__stardateToGregorian2009Revised()


    # Returns the current Gregorian date/time in UTC.
    def getGregorian( self ): return self.gregorianDateTime


    # Returns the current 'classic' stardate issue value.
    def getStardateIssue( self ): return self.stardateIssue


    # Returns the current ('classic' or '2009 revised') stardate integer value.
    def getStardateInteger( self ): return self.stardateInteger


    # Returns the current ('classic' or '2009 revised') stardate fraction value.
    def getStardateFraction( self ): return self.stardateFraction


    # Returns the current value of the ('classic' or '2009 revised') stardate in string format.
    #
    #  showIssue    If True, the issue part of the 'classic' stardate will be included (ignored for '2009 revised').
    #  padInteger   If True, the integer part of the 'classic' stardate will be padded with zeros at the start (ignored for '2009 revised').
    def toStardateString( self, showIssue, padInteger ):
        stringBuilder = ""

        if self.classic:
            if showIssue: stringBuilder = "[" + str( self.stardateIssue ) + "] "

            if padInteger:
                if self.stardateIssue < 21: padding = len( "1000" ) - len( str( self.stardateInteger ) )
                else: padding = len( "10000" ) - len( str( self.stardateInteger ) )

                integer = str( self.stardateInteger )
                for i in range( padding ): integer = "0" + integer
                stringBuilder += str( integer )

            else: stringBuilder += str( self.stardateInteger )

            stringBuilder += "." + str( self.stardateFraction )

        else: stringBuilder = str( self.stardateInteger ) + "." + str( self.stardateFraction )

        return stringBuilder


    # Returns the current value of the Gregorian date/time in string format "%Y-%m-%d %H:%M:%S".
    def toGregorianString( self ): 
        if self.gregorianDateTime is None: return "Please set either a gregorian date or a stardate!"

        return self.gregorianDateTime.strftime( "%Y-%m-%d %H:%M:%S" )


    # Converts the current 'classic' stardate to the equivalent Gregorian date/time.
    def __stardateToGregorianClassic( self ):
        fractionLength = len( str( self.stardateFraction ) )
        fractionDivisor = math.pow( 10.0, fractionLength )
        self.index = -1
        if self.stardateIssue < 0: # Pre-stardate (pre 4/1/2162).
            self.index = 0
            units = self.stardateIssue * 10000.0 + self.stardateInteger + self.stardateFraction / fractionDivisor
        elif self.stardateIssue >= 0 and self.stardateIssue < 19: # First period of stardates (4/1/2162 - 26/1/2270).
            self.index = 1
            units = self.stardateIssue * 1000.0 + self.stardateInteger + self.stardateFraction / fractionDivisor
        elif self.stardateIssue == 19 and self.stardateInteger < 7340: # First period of stardates (4/1/2162 - 26/1/2270).
            self.index = 1
            units = self.stardateIssue * 19.0 * 1000.0 + self.stardateInteger + self.stardateFraction / fractionDivisor
        elif self.stardateIssue == 19 and self.stardateInteger >= 7340 and self.stardateInteger < 7840: # Second period of stardates (26/1/2270 - 5/10/2283)
            self.index = 2
            units = self.stardateInteger + self.stardateFraction / fractionDivisor - 7340
        elif self.stardateIssue == 19 and self.stardateInteger >= 7840: # Third period of stardates (5/10/2283 - 1/1/2323)
            self.index = 3
            units = self.stardateInteger + self.stardateFraction / fractionDivisor - 7840
        elif self.stardateIssue == 20 and self.stardateInteger < 5006: # Third period of stardates (5/10/2283 - 1/1/2323)
            self.index = 3
            units = 1000.0 + self.stardateInteger + self.stardateFraction / fractionDivisor
        elif self.stardateIssue >= 21: # Fourth period of stardates (1/1/2323 - )
            self.index = 4
            units = ( self.stardateIssue - 21 ) * 10000.0 + self.stardateInteger + self.stardateFraction / fractionDivisor
        else:
            raise Exception( "Illegal issue/integer: " + str( self.stardateIssue ) + "/" + str( self.stardateInteger ) )

        rate = self.stardateRates[ self.index ]
        days = units / rate
        hours = ( days - int( days ) ) * 24.0
        minutes = ( hours - int( hours ) ) * 60.0
        seconds = ( minutes - int( minutes ) ) * 60.0

        self.gregorianDateTime = datetime.datetime( self.gregorianDates[ self.index ].year, self.gregorianDates[ self.index ].month, self.gregorianDates[ self.index ].day )
        self.gregorianDateTime += datetime.timedelta( int( days ), int( seconds ), 0, 0, int( minutes ), int( hours ) )


    # Converts the current Gregorian date/time to the equivalent 'classic' stardate.
    def __gregorianToStardateClassic( self ):
        stardateIssues = [ -1, 0, 19, 19, 21 ]
        stardateIntegers = [ 0, 0, 7340, 7840, 0 ]
        stardateRange = [ 10000, 10000, 10000, 10000, 100000 ]
        self.index = -1

        # Determine which era the given Gregorian date falls...
        year = self.gregorianDateTime.year
        month = self.gregorianDateTime.month # Month is one-based.
        day = self.gregorianDateTime.day
        if ( year < 2162 ) or ( year == 2162 and month == 1 and day < 4 ):
            # Pre-stardate (pre 4/1/2162)...do the conversion here because a negative time is generated and throws out all other cases.          
            self.index = 0
            numberOfSeconds = ( self.gregorianDates[ self.index ] - self.gregorianDateTime ).total_seconds()
            numberOfDays = numberOfSeconds / 60.0 / 60.0 / 24.0
            rate = self.stardateRates[ self.index ]
            units = numberOfDays * rate

            self.stardateIssue = stardateIssues[ self.index ] - int( units / stardateRange[ self.index ] )

            remainder = stardateRange[ self.index ] - ( units % stardateRange[ self.index ] )
            self.stardateInteger = int( remainder )
            self.stardateFraction = int( remainder * 10.0 ) - ( int( remainder ) * 10 )
            return

        # Remainder of time periods can be treated equally...
        if ( year == 2162 and month == 1 and day >= 4 ) or ( year == 2162 and month > 1 ) or ( year > 2162 and year < 2270 ) or ( year == 2270 and month == 1 and day < 26 ):
            self.index = 1 # First period of stardates (4/1/2162 - 26/1/2270).
        elif ( year == 2270 and month == 1 and day >= 26 ) or ( year == 2270 & month > 1 ) or ( year > 2270 and year < 2283 ) or ( year == 2283 and month < 10 ) or ( year == 2283 and month == 10 and day < 5 ):
            self.index = 2 # Second period of stardates (26/1/2270 - 5/10/2283)
        elif ( year == 2283 and month == 10 and day >= 5 ) or ( year == 2283 and month > 10 ) or ( year > 2283 and year < 2323 ):
            self.index = 3 # Third period of stardates (5/10/2283 - 1/1/2323)
        elif year >= 2323:
            self.index = 4 # Fourth period of stardates (1/1/2323 - )
        else:
            raise Exception( "Invalid year/month/day: " + str( year ) + "/" + str( month ) + "/" + str( day ) )

        # Now convert...
        numberOfSeconds = ( self.gregorianDateTime - self.gregorianDates[ self.index ] ).total_seconds()
        numberOfDays = numberOfSeconds / 60.0 / 60.0 / 24.0
        rate = self.stardateRates[ self.index ]
        units = numberOfDays * rate
        self.stardateIssue = int( units / stardateRange[ self.index ] ) + stardateIssues[ self.index ]
        remainder = units % stardateRange[ self.index ]
        self.stardateInteger = int( remainder ) + stardateIntegers[ self.index ]
        self.stardateFraction = int( remainder * 10.0 ) - ( int( remainder ) * 10 )


    # Converts the current '2009 revised' stardate to the equivalent Gregorian date/time.
    def __stardateToGregorian2009Revised( self ):
        self.gregorianDateTime = datetime.date( self.stardateInteger, 1, 1 )
        self.gregorianDateTime += datetime.timedelta( days = self.stardateFraction )


    # Converts the current Gregorian date/time to the equivalent '2009 revised' stardate.
    def __gregorianToStardate2009Revised( self ):
        self.stardateIssue = None
        self.stardateInteger = self.gregorianDateTime.year
        self.stardateFraction = ( datetime.date( self.gregorianDateTime.year, self.gregorianDateTime.month, self.gregorianDateTime.day ) - datetime.date( self.gregorianDateTime.year, 1, 1 ) ).days + 1


    def __str__( self ): return "Classic: " + str( self.classic ) + "  |  Stardate: " + self.toStardateString( True, True ) + "  |  Gregorian: " + self.toGregorianString() 


    def __repr__( self ): return self.__str__()