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


# Converts between Star Trek™ stardates and Gregorian date/times.
# There are two types of stardates: 'classic' and '2009 revised'.
#
#
# 'classic' stardates
# ===================
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
# Stardate [0]0000.0 commenced on midnight 2162/1/4.
# The stardate rate from this date to 2270/1/26 was 5 units per day.
#
# Between 2270/1/26 and 2283/10/5 ([19]7340.0 and [19]7840.0, respectively)
# the rate changes to 0.1 units per day.
#
# Between 2283/10/5 to 2323/1/1 ([19]7840.0 and [20]5006.0, respectively),
# the rate changes to 0.5 units per day.
#
# From 2323/1/1 ([20]5006.0) the rate changed to 1000 units per mean solar year.
# Also, stardate [20]5006.0 becomes [21]00000.0.
#
#
# '2009 revised'
# ==============
#
# The '2009 revised' stardate is based on https://en.wikipedia.org/wiki/Stardate.


import datetime, math


# The Gregorian dates which reflect the start date for each rate in the 'classic' stardate era.
# For example, an index of 3 (Gregorian date of 2283/10/5) corresponds to the rate of 0.5 stardate units per day.
# The month is one-based (January = 1).
__gregorianDates = [
    datetime.datetime( 2162, 1, 4, tzinfo = datetime.timezone( datetime.timedelta( hours = 0 ) ) ),
    datetime.datetime( 2162, 1, 4, tzinfo = datetime.timezone( datetime.timedelta( hours = 0 ) ) ),
    datetime.datetime( 2270, 1, 26, tzinfo = datetime.timezone( datetime.timedelta( hours = 0 ) ) ),
    datetime.datetime( 2283, 10, 5, tzinfo = datetime.timezone( datetime.timedelta( hours = 0 ) ) ),
    datetime.datetime( 2323, 1, 1, tzinfo = datetime.timezone( datetime.timedelta( hours = 0 ) ) ) ]


# Rates (in stardate units per day) for each 'classic' stardate era.
__stardateRates = [ 5.0, 5.0, 0.1, 0.5, 1000.0 / 365.2425 ]


def getVersion():
    return "Version 5.0 (2019-10-07)"


# Convert a Gregorian datetime.datetime in UTC to a 'classic' stardate.
#
#  gregorianDateTime A Gregorian datetime.datetime in UTC (1900 <= year <= 9500).
#
# Raises an exception if the Gregorian year is out the defined range.
#
# Returns a 'classic' stardate with the components:
#    stardate issue
#    stardate integer
#    stardate fraction
def getStardateClassic( gregorianDateTime ):
    if ( gregorianDateTime.year < 1900 ) or ( gregorianDateTime.year > 9500 ):
        raise Exception( "Gregorian year out of range: 1900 <= year <= 9500." )

    stardateIssues = [ -1, 0, 19, 19, 21 ]
    stardateIntegers = [ 0, 0, 7340, 7840, 0 ]
    stardateRange = [ 10000, 10000, 10000, 10000, 100000 ]
    index = -1

    # Determine into which era the given Gregorian date falls...
    year = gregorianDateTime.year
    month = gregorianDateTime.month # Month is one-based.
    day = gregorianDateTime.day
    if ( year < 2162 ) or ( year == 2162 and month == 1 and day < 4 ):
        # Pre-stardate (pre 2162/1/4)...do the conversion here because a negative time is generated and throws out all other cases.
        index = 0
        numberOfSeconds = ( __gregorianDates[ index ] - gregorianDateTime ).total_seconds()
        numberOfDays = numberOfSeconds / 60.0 / 60.0 / 24.0
        rate = __stardateRates[ index ]
        units = numberOfDays * rate

        stardateIssue = stardateIssues[ index ] - int( units / stardateRange[ index ] )

        remainder = stardateRange[ index ] - ( units % stardateRange[ index ] )
        stardateInteger = int( remainder )
        stardateFraction = int( remainder * 10.0 ) - ( int( remainder ) * 10 )

    else:
        # Remainder of time periods can be treated equally...
        if ( year == 2162 and month == 1 and day >= 4 ) or ( year == 2162 and month > 1 ) or ( year > 2162 and year < 2270 ) or ( year == 2270 and month == 1 and day < 26 ):
            index = 1 # First period of stardates (2162/1/4 - 2270/1/26).

        elif ( year == 2270 and month == 1 and day >= 26 ) or ( year == 2270 & month > 1 ) or ( year > 2270 and year < 2283 ) or ( year == 2283 and month < 10 ) or ( year == 2283 and month == 10 and day < 5 ):
            index = 2 # Second period of stardates (2270/1/26 - 2283/10/5).

        elif ( year == 2283 and month == 10 and day >= 5 ) or ( year == 2283 and month > 10 ) or ( year > 2283 and year < 2323 ):
            index = 3 # Third period of stardates (2283/10/5 - 2323/1/1).

        elif year >= 2323:
            index = 4 # Fourth period of stardates (2323/1/1 - ).

        else:
            raise Exception( "Invalid year/month/day: " + str( year ) + "/" + str( month ) + "/" + str( day ) )

        # Now convert...
        numberOfSeconds = ( gregorianDateTime - __gregorianDates[ index ] ).total_seconds()
        numberOfDays = numberOfSeconds / 60.0 / 60.0 / 24.0
        rate = __stardateRates[ index ]
        units = numberOfDays * rate
        stardateIssue = int( units / stardateRange[ index ] ) + stardateIssues[ index ]
        remainder = units % stardateRange[ index ]
        stardateInteger = int( remainder ) + stardateIntegers[ index ]
        stardateFraction = int( remainder * 10.0 ) - ( int( remainder ) * 10 )

    return stardateIssue, stardateInteger, stardateFraction


# Convert a Gregorian datetime.datetime in UTC to a '2009 revised' stardate.
#
#  gregorianDateTime A Gregorian datetime.datetime in UTC (1900 <= year <= 9500).
#
# Raises an exception if the Gregorian year is out the defined range.
#
# Returns a '2009 revised' stardate with the components:
#    stardate integer
#    stardate fraction
def getStardate2009Revised( gregorianDateTime ):
    if ( gregorianDateTime.year < 1900 ) or ( gregorianDateTime.year > 9500 ):
        raise Exception( "Gregorian year out of range: 1900 <= year <= 9500." )

    stardateInteger = gregorianDateTime.year
    stardateFraction = \
        ( datetime.date( gregorianDateTime.year, gregorianDateTime.month, gregorianDateTime.day ) - \
          datetime.date( gregorianDateTime.year, 1, 1 ) ).days + 1

    return stardateInteger, stardateFraction


# Converts the date/time to the corresponding stardate and determines
# how many seconds will elapse until that stardate will change.
#
#  gregorianDateTime A Gregorian datetime.datetime in UTC (1900 <= year <= 9500).
#  isClassic If True, the class stardate will be calculated; otherwise '2009 revised'.
#
# Raises an exception if the Gregorian year is out the defined range.
#
# Returns the number of seconds until the corresponding stardate will change.
def getNextUpdateInSeconds( gregorianDateTime, isClassic ):
    if ( gregorianDateTime.year < 1900 ) or ( gregorianDateTime.year > 9500 ):
        raise Exception( "Gregorian year out of range: 1900 <= year <= 9500." )

    if isClassic:
        stardateIssue, stardateInteger, stardateFraction = getStardateClassic( gregorianDateTime )

        stardateIssueNext = stardateIssue
        stardateIntegerNext = stardateInteger
        stardateFractionNext = stardateFraction + 1
        if stardateFractionNext == 10:
            stardateFractionNext = 0
            stardateIntegerNext += 1
            if stardateIntegerNext == 10000:
                stardateIntegerNext = 0
                stardateIssueNext += 1

        dateTimeOfNextStardate = getGregorianFromStardateClassic( stardateIssueNext, stardateIntegerNext, stardateFractionNext )
        numberOfSecondsToNextUpdate = int( math.ceil( ( dateTimeOfNextStardate - gregorianDateTime ).total_seconds() ) )

    else:
        oneSecondAfterMidnight = ( gregorianDateTime + datetime.timedelta( days = 1 ) ).replace( hour = 0, minute = 0, second = 1 )
        numberOfSecondsToNextUpdate = int( math.ceil( ( oneSecondAfterMidnight - gregorianDateTime ).total_seconds() ) )

    return numberOfSecondsToNextUpdate


# Convert a 'classic' stardate to a Gregorian datetime.datetime.
#
# Rules:
#  issue <= 19: 0 <= integer <= 9999, fraction >= 0.
#  issue == 20: 0 <= integer < 5006, fraction >= 0.
#  issue >= 21: 0 <= integer <= 99999, fraction >= 0.
#
#  stardateIssue The issue number for the stardate (can be negative).
#  stardateInteger The integer part of a stardate.
#  stardateFraction The fractional part of a stardate.
#
# Raises an exception if the issue/integer/fraction are out of the defined ranges.
#
# Returns a Gregorian datetime.datetime.
def getGregorianFromStardateClassic( stardateIssue, stardateInteger, stardateFraction ):
    if stardateIssue <= 19 and ( stardateInteger < 0 or stardateInteger > 9999 ):
        raise Exception( "Integer out of range: 0 <= integer <= 9999" )

    if stardateIssue == 20 and ( stardateInteger < 0 or stardateInteger >= 5006 ):
        raise Exception( "Integer out of range: 0 <= integer < 5006" )

    if stardateIssue >= 21 and ( stardateInteger < 0 or stardateInteger > 99999 ):
        raise Exception( "Integer out of range: 0 <= integer <= 99999" )

    if stardateFraction < 0:
        raise Exception( "Fraction cannot be negative." )

    fractionLength = len( str( stardateFraction ) )
    fractionDivisor = math.pow( 10.0, fractionLength )
    index = -1
    if stardateIssue < 0: # Pre-stardate (pre 2162/1/4).
        index = 0
        units = stardateIssue * 10000.0 + stardateInteger + stardateFraction / fractionDivisor

    elif stardateIssue >= 0 and stardateIssue < 19: # First period of stardates (2162/1/4 - 2270/1/26).
        index = 1
        units = stardateIssue * 1000.0 + stardateInteger + stardateFraction / fractionDivisor

    elif stardateIssue == 19 and stardateInteger < 7340: # First period of stardates (2162/1/4 - 2270/1/26).
        index = 1
        units = stardateIssue * 19.0 * 1000.0 + stardateInteger + stardateFraction / fractionDivisor

    elif stardateIssue == 19 and stardateInteger >= 7340 and stardateInteger < 7840: # Second period of stardates (2270/1/26 - 2283/10/5).
        index = 2
        units = stardateInteger + stardateFraction / fractionDivisor - 7340

    elif stardateIssue == 19 and stardateInteger >= 7840: # Third period of stardates (2283/10/5 - 2323/1/1).
        index = 3
        units = stardateInteger + stardateFraction / fractionDivisor - 7840

    elif stardateIssue == 20 and stardateInteger < 5006: # Third period of stardates (2283/10/5 - 2323/1/1).
        index = 3
        units = 1000.0 + stardateInteger + stardateFraction / fractionDivisor

    elif stardateIssue >= 21: # Fourth period of stardates (2323/1/1 - ).
        index = 4
        units = ( stardateIssue - 21 ) * 10000.0 + stardateInteger + stardateFraction / fractionDivisor

    else:
        raise Exception( "Illegal issue/integer: " + str( stardateIssue ) + "/" + str( stardateInteger ) )

    rate = __stardateRates[ index ]
    days = units / rate
    hours = ( days - int( days ) ) * 24.0
    minutes = ( hours - int( hours ) ) * 60.0
    seconds = ( minutes - int( minutes ) ) * 60.0

    gregorianDateTime = \
        datetime.datetime( 
            __gregorianDates[ index ].year, 
            __gregorianDates[ index ].month, 
            __gregorianDates[ index ].day, 
            tzinfo = datetime.timezone( datetime.timedelta( hours = 0 ) ) )

    gregorianDateTime += datetime.timedelta( int( days ), int( seconds ), 0, 0, int( minutes ), int( hours ) )
    return gregorianDateTime


# Convert a '2009 revised' stardate to a Gregorian datetime.datetime.
#
#  stardateInteger The integer part of a stardate (corresponds to a Gregorian year).
#  stardateFraction The fractional part of a stardate (0 <= fraction <= 365, or 366 if integer corresponds to a leap year).
#
# Raises an exception if the integer/fraction are out of the defined ranges.
#
# Returns a Gregorian datetime.datetime.
def getGregorianFromStardate2009Revised( stardateInteger, stardateFraction ):
    if stardateFraction < 0:
        raise Exception( "Fraction cannot be negative." )

    isLeapYear = ( stardateInteger % 4 == 0 and stardateInteger % 100 != 0 ) or stardateInteger % 400 == 0
    if isLeapYear:
        if stardateFraction > 366:
            raise Exception( "Integer cannot exceed 366." )

    else:
        if stardateFraction > 365:
            raise Exception( "Integer cannot exceed 365." )

    gregorianDateTime = datetime.date( stardateInteger, 1, 1 )
    gregorianDateTime += datetime.timedelta( days = ( stardateFraction - 1 ) )
    return gregorianDateTime


# Returns a stardate in string format.
#
#  stardateIssue The stardate issue (must be set to None for '2009 revised').
#  stardateInteger The stardate integer.
#  stardateFraction The stardate fraction.
#  showIssue If true, the issue will be included in the string (ignored for '2009 revised').
#  padded If true, the integer part of the string will be zero padded (if required).
#
# Returns A stardate in string format.
def toStardateString( stardateIssue, stardateInteger, stardateFraction, showIssue, padInteger ):
    stringBuilder = ""
    if stardateIssue is None:
        stringBuilder = str( stardateInteger ) + "." + str( stardateFraction )

    else:
        if showIssue:
            stringBuilder = "[" + str( stardateIssue ) + "] "

        if padInteger:
            if stardateIssue < 21:
                padding = len( "1000" ) - len( str( stardateInteger ) )

            else:
                padding = len( "10000" ) - len( str( stardateInteger ) )

            stardateInteger = str( stardateInteger )
            for i in range( padding ):
                stardateInteger = "0" + stardateInteger

            stringBuilder += str( stardateInteger )

        else:
            stringBuilder += str( stardateInteger )

        stringBuilder += "." + str( stardateFraction )

    return stringBuilder


# Determines if a 'classic' stardate requires zero padding.
#
# A 'classic' stardate with issue < 21 will have up to four digits in the integer part.
# However the integer part could be a single digit.
# If the integer part has fewer than four digits, the stardate is deemed to
# require padding.
#
# Similarly for a 'classic' stardate with issue >= 21, but there are five digits.
#
#  stardateIssue The stardate issue.
#  stardateInteger The stardate integer.
#
# Returns Returns True if the integer part contains fewer digits than the maximum for the particular issue.
def requiresPadding( stardateIssue, stardateInteger ):
    if stardateIssue < 21:
        paddingRequired = len( str( stardateInteger ) ) < 4

    else:
        paddingRequired = len( str( stardateInteger ) ) < 5

    return paddingRequired