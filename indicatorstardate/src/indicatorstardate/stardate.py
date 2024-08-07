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


import datetime
import math


# The Gregorian dates which reflect the start date for each rate in the 'classic' stardate era.
# For example, an index of 3 (Gregorian date of 2283/10/5) corresponds to the rate of 0.5 stardate units per day.
# The month is one-based (January = 1).
_gregorian_dates = [
    datetime.datetime( 2162, 1, 4, tzinfo = datetime.timezone( datetime.timedelta( hours = 0 ) ) ),
    datetime.datetime( 2162, 1, 4, tzinfo = datetime.timezone( datetime.timedelta( hours = 0 ) ) ),
    datetime.datetime( 2270, 1, 26, tzinfo = datetime.timezone( datetime.timedelta( hours = 0 ) ) ),
    datetime.datetime( 2283, 10, 5, tzinfo = datetime.timezone( datetime.timedelta( hours = 0 ) ) ),
    datetime.datetime( 2323, 1, 1, tzinfo = datetime.timezone( datetime.timedelta( hours = 0 ) ) ) ]


# Rates (in stardate units per day) for each 'classic' stardate era.
_stardate_rates = [ 5.0, 5.0, 0.1, 0.5, 1000.0 / 365.2425 ]


def get_version():
    return "Version 6.0 (2024-06-11)"


# Convert a Gregorian datetime.datetime in UTC to a 'classic' stardate.
#
#  The Gregorian datetime.datetime in UTC (1900 <= year <= 9500).
#
# Raises an exception if the Gregorian year is out the defined range.
#
# Returns a 'classic' stardate with the components:
#    stardate issue
#    stardate integer
#    stardate fraction
def get_stardate_classic( gregorian_date_time ):
    if ( gregorian_date_time.year < 1900 ) or ( gregorian_date_time.year > 9500 ):
        raise Exception( "Gregorian year out of range: 1900 <= year <= 9500." )

    stardate_issues = [ -1, 0, 19, 19, 21 ]
    stardate_integers = [ 0, 0, 7340, 7840, 0 ]
    stardate_ranges = [ 10000, 10000, 10000, 10000, 100000 ]
    index = -1

    # Determine into which era the given Gregorian date falls...
    year = gregorian_date_time.year
    month = gregorian_date_time.month # Month is one-based.
    day = gregorian_date_time.day
    if ( year < 2162 ) or ( year == 2162 and month == 1 and day < 4 ):
        # Pre-stardate era; do the conversion here as a negative time is generated.
        index = 0
        number_of_seconds = ( _gregorian_dates[ index ] - gregorian_date_time ).total_seconds()
        number_of_days = number_of_seconds / 60.0 / 60.0 / 24.0
        rate = _stardate_rates[ index ]
        units = number_of_days * rate

        stardate_issue = stardate_issues[ index ] - int( units / stardate_ranges[ index ] )

        remainder = stardate_ranges[ index ] - ( units % stardate_ranges[ index ] )
        stardate_integer = int( remainder )
        stardate_fraction = int( remainder * 10.0 ) - ( int( remainder ) * 10 )

    else:
        # First period of stardates (2162/1/4 - 2270/1/26).
        first_period = \
            ( year == 2162 and month == 1 and day >= 4 ) or \
            ( year == 2162 and month > 1 ) or \
            ( year > 2162 and year < 2270 ) or \
            ( year == 2270 and month == 1 and day < 26 )

        # Second period of stardates (2270/1/26 - 2283/10/5).
        second_period = \
            ( year == 2270 and month == 1 and day >= 26 ) or \
            ( year == 2270 & month > 1 ) or \
            ( year > 2270 and year < 2283 ) or \
            ( year == 2283 and month < 10 ) or \
            ( year == 2283 and month == 10 and day < 5 )

        # Third period of stardates (2283/10/5 - 2323/1/1).
        third_period = \
            ( year == 2283 and month == 10 and day >= 5 ) or \
            ( year == 2283 and month > 10 ) or \
            ( year > 2283 and year < 2323 )

        # Fourth period of stardates (2323/1/1 - ).
        fourth_period = year >= 2323

        if first_period:
            index = 1

        elif second_period:
            index = 2

        elif third_period:
            index = 3

        elif fourth_period:
            index = 4

        else:
            raise Exception( "Invalid year/month/day: " + str( year ) + "/" + str( month ) + "/" + str( day ) )

        # Now convert...
        number_of_seconds = (
            gregorian_date_time - _gregorian_dates[ index ] ).total_seconds()

        number_of_days = number_of_seconds / 60.0 / 60.0 / 24.0
        units = number_of_days * _stardate_rates[ index ]
        stardate_issue = int( units / stardate_ranges[ index ] ) + stardate_issues[ index ]
        remainder = units % stardate_ranges[ index ]
        stardate_integer = int( remainder ) + stardate_integers[ index ]
        stardate_fraction = int( remainder * 10.0 ) - ( int( remainder ) * 10 )

    return stardate_issue, stardate_integer, stardate_fraction


# Convert a Gregorian datetime.datetime in UTC to a '2009 revised' stardate.
#
#  The Gregorian datetime.datetime in UTC (1900 <= year <= 9500).
#
# Raises an exception if the Gregorian year is out the defined range.
#
# Returns a '2009 revised' stardate with the components:
#    stardate integer
#    stardate fraction
def get_stardate_2009_revised( gregorian_date_time ):
    if ( gregorian_date_time.year < 1900 ) or ( gregorian_date_time.year > 9500 ):
        raise Exception( "Gregorian year out of range: 1900 <= year <= 9500." )

    stardate_integer = gregorian_date_time.year
    stardate_fraction = (
        datetime.date( gregorian_date_time.year, gregorian_date_time.month, gregorian_date_time.day ) - \
        datetime.date( gregorian_date_time.year, 1, 1 ) ).days + 1

    return stardate_integer, stardate_fraction


# Converts the date/time to the corresponding stardate and determines
# how many seconds will elapse until that stardate will change.
#
#  The Gregorian datetime.datetime must be in UTC (1900 <= year <= 9500).
#  If classic is True, the classic stardate will be calculated; otherwise '2009 revised'.
#
# Raises an exception if the Gregorian year is out the defined range.
#
# Returns the number of seconds until the corresponding stardate will change.
def get_next_update_in_seconds( gregorian_date_time, is_classic ):
    if ( gregorian_date_time.year < 1900 ) or ( gregorian_date_time.year > 9500 ):
        raise Exception( "Gregorian year out of range: 1900 <= year <= 9500." )

    if is_classic:
        stardate_issue, stardate_integer, stardate_fraction = \
            get_stardate_classic( gregorian_date_time )

        stardate_issue_next = stardate_issue
        stardate_integer_next = stardate_integer
        stardate_fraction_next = stardate_fraction + 1
        if stardate_fraction_next == 10:
            stardate_fraction_next = 0
            stardate_integer_next += 1
            if stardate_integer_next == 10000:
                stardate_integer_next = 0
                stardate_issue_next += 1

        date_time_of_next_stardate = \
            get_gregorian_from_stardate_classic(
                stardate_issue_next,
                stardate_integer_next,
                stardate_fraction_next )

        number_of_seconds_to_next_update = \
            int( math.ceil( ( date_time_of_next_stardate - gregorian_date_time ).total_seconds() ) )

    else:
        one_second_after_midnight = \
            ( gregorian_date_time + datetime.timedelta( days = 1 ) ).replace( hour = 0, minute = 0, second = 1 )

        number_of_seconds_to_next_update = \
            int( math.ceil( ( one_second_after_midnight - gregorian_date_time ).total_seconds() ) )

    return number_of_seconds_to_next_update


# Convert a 'classic' stardate to a Gregorian datetime.datetime.
#
# Rules:
#  issue <= 19: 0 <= integer <= 9999, fraction >= 0.
#  issue == 20: 0 <= integer < 5006, fraction >= 0.
#  issue >= 21: 0 <= integer <= 99999, fraction >= 0.
#
#  The issue number for the stardate can be negative.
#
# Raises an exception if the issue/integer/fraction are out of the defined ranges.
#
# Returns a Gregorian datetime.datetime.
def get_gregorian_from_stardate_classic( stardate_issue, stardate_integer, stardate_fraction ):
    if stardate_issue <= 19 and ( stardate_integer < 0 or stardate_integer > 9999 ):
        raise Exception( "Integer out of range: 0 <= integer <= 9999" )

    if stardate_issue == 20 and ( stardate_integer < 0 or stardate_integer >= 5006 ):
        raise Exception( "Integer out of range: 0 <= integer < 5006" )

    if stardate_issue >= 21 and ( stardate_integer < 0 or stardate_integer > 99999 ):
        raise Exception( "Integer out of range: 0 <= integer <= 99999" )

    if stardate_fraction < 0:
        raise Exception( "Fraction cannot be negative." )

    fraction_length = len( str( stardate_fraction ) )
    fraction_divisor = math.pow( 10.0, fraction_length )
    index = -1
    if stardate_issue < 0: # Pre-stardate (pre 2162/1/4).
        index = 0
        units = stardate_issue * 10000.0 + stardate_integer + stardate_fraction / fraction_divisor

    elif stardate_issue >= 0 and stardate_issue < 19: # First period of stardates (2162/1/4 - 2270/1/26).
        index = 1
        units = stardate_issue * 1000.0 + stardate_integer + stardate_fraction / fraction_divisor

    elif stardate_issue == 19 and stardate_integer < 7340: # First period of stardates (2162/1/4 - 2270/1/26).
        index = 1
        units = stardate_issue * 19.0 * 1000.0 + stardate_integer + stardate_fraction / fraction_divisor

    elif stardate_issue == 19 and stardate_integer >= 7340 and stardate_integer < 7840: # Second period of stardates (2270/1/26 - 2283/10/5).
        index = 2
        units = stardate_integer + stardate_fraction / fraction_divisor - 7340

    elif stardate_issue == 19 and stardate_integer >= 7840: # Third period of stardates (2283/10/5 - 2323/1/1).
        index = 3
        units = stardate_integer + stardate_fraction / fraction_divisor - 7840

    elif stardate_issue == 20 and stardate_integer < 5006: # Third period of stardates (2283/10/5 - 2323/1/1).
        index = 3
        units = 1000.0 + stardate_integer + stardate_fraction / fraction_divisor

    elif stardate_issue >= 21: # Fourth period of stardates (2323/1/1 - ).
        index = 4
        units = ( stardate_issue - 21 ) * 10000.0 + stardate_integer + stardate_fraction / fraction_divisor

    else:
        raise Exception( "Illegal issue/integer: " + str( stardate_issue ) + "/" + str( stardate_integer ) )

    days = units / _stardate_rates[ index ]
    hours = ( days - int( days ) ) * 24.0
    minutes = ( hours - int( hours ) ) * 60.0
    seconds = ( minutes - int( minutes ) ) * 60.0

    gregorian_date_time = \
        datetime.datetime(
            _gregorian_dates[ index ].year,
            _gregorian_dates[ index ].month,
            _gregorian_dates[ index ].day,
            tzinfo = datetime.timezone( datetime.timedelta( hours = 0 ) ) )

    gregorian_date_time += \
        datetime.timedelta(
            int( days ),
            int( seconds ),
            0,
            0,
            int( minutes ),
            int( hours ) )

    return gregorian_date_time


# Convert a '2009 revised' stardate to a Gregorian datetime.datetime.
#
#  The integer part of a stardate corresponds to the Gregorian year.
#  The fractional part of a stardate (0 <= fraction <= 365, or 366 if integer corresponds to a leap year).
#
# Raises an exception if the integer/fraction are out of the defined ranges.
#
# Returns a Gregorian datetime.datetime.
def get_gregorian_from_stardate_2009_revised( stardate_integer, stardate_fraction ):
    if stardate_fraction < 0:
        raise Exception( "Fraction cannot be negative." )

    is_leap_year = ( stardate_integer % 4 == 0 and stardate_integer % 100 != 0 ) or stardate_integer % 400 == 0
    if is_leap_year:
        if stardate_fraction > 366:
            raise Exception( "Integer cannot exceed 366." )

    else:
        if stardate_fraction > 365:
            raise Exception( "Integer cannot exceed 365." )

    gregorian_date_time = datetime.date( stardate_integer, 1, 1 )
    gregorian_date_time += datetime.timedelta( days = ( stardate_fraction - 1 ) )
    return gregorian_date_time


# Returns a stardate in string format.
#
#  The stardate issue must be set to None for '2009 revised'.
#  If show_issue is True, the issue will be included in the string (ignored for '2009 revised').
#  If padded is True, the integer part of the string will be zero padded (if required).
#
# Returns A stardate in string format.
def to_stardate_string( stardate_issue, stardate_integer, stardate_fraction, show_issue, pad_integer ):
    string_builder = ""
    if stardate_issue is None:
        string_builder = str( stardate_integer ) + "." + str( stardate_fraction )

    else:
        if show_issue:
            string_builder = "[" + str( stardate_issue ) + "] "

        if pad_integer:
            if stardate_issue < 21:
                padding = len( "1000" ) - len( str( stardate_integer ) )

            else:
                padding = len( "10000" ) - len( str( stardate_integer ) )

            stardate_integer = str( stardate_integer )
            for i in range( padding ):
                stardate_integer = "0" + stardate_integer

            string_builder += str( stardate_integer )

        else:
            string_builder += str( stardate_integer )

        string_builder += "." + str( stardate_fraction )

    return string_builder


# Determines if a 'classic' stardate requires zero padding.
#
# A 'classic' stardate with issue < 21 will have up to four digits in the integer part.
# However the integer part could be a single digit.
# If the integer part has fewer than four digits, the stardate is deemed to
# require padding.
#
# Similarly for a 'classic' stardate with issue >= 21, but there are five digits.
#
# Returns True if the integer part contains fewer digits than the maximum for the particular issue.
def requires_padding( stardate_issue, stardate_integer ):
    if stardate_issue < 21:
        padding_required = len( str( stardate_integer ) ) < 4

    else:
        padding_required = len( str( stardate_integer ) ) < 5

    return padding_required
