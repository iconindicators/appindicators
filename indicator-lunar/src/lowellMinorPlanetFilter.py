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


# Remove bodies from the Lowell Minor Planet Services asteroid orbital elements database:
#    which have a low number of observations;
#    with an apparent magnitude exceeding a limit,
# creating a new database from the result.
#
# Requires PyEphem for the apparent magnitude calculations.
#
# The asteroid orbital elements database (and format) is available at
#    https://asteroid.lowell.edu/main/astorb
# (both the compressed and uncompressed versions are supported).


from pathlib import Path


import datetime, ephem, gzip, sys, tempfile
import lowellMinorPlanetToXEphem


def __getApparentMagnitudeOverPeriod( orbitalElement, startDate, endDate, city, apparentMagnitudeMaximum, intervalInDaysBetweenBodyCompute ):
    currentDate = startDate
    city = ephem.city( "London" ) # Use any city; makes no difference to obtain the apparent magnitude.
    body = ephem.readdb( orbitalElement )
    while currentDate < endDate:
        city.date = currentDate
        body.compute( city )
        if body.mag <= apparentMagnitudeMaximum:
            break

        currentDate += datetime.timedelta( days = intervalInDaysBetweenBodyCompute )

    return body.mag


def __filterByName( inFile, names ):
    suffix = "-FILTERED" + ".dat"
    if inFile.endswith( ".gz" ):
        fIn = gzip.open( inFile, 'rt' )
        outFile = inFile[ 0 : -7 ] + suffix

    else:
        fIn = open( inFile, 'r' )
        outFile = inFile[ 0 : -4 ] + suffix

    fOut = open( outFile, 'w' )
    for line in fIn:
        if len( line.strip() ) == 0:
            continue

        name = line[ 1 - 1 : 26 ].strip()
        if name in names:
            fOut.write( line )

    return fOut.name


def __filterByApparentMagnitudeUsingPyEphem(
        inFile,
        apparentMagnitudeMaximum = 15.0, # Upper limit for apparent magnitude.
        durationInYears = 1, # Number of years over which to compute apparent magnitude.
        intervalInDaysBetweenApparentMagnitudeCalculations = 30 ):
    namesKept = [ ]
    startDate = datetime.datetime.utcnow()
    endDate = startDate + datetime.timedelta( days = 366 * durationInYears )
    with open( inFile, 'r' ) as fIn:
        city = ephem.city( "London" ) # Use any city; makes no difference to obtain the apparent magnitude.
        for line in fIn:
            apparentMagnitude = __getApparentMagnitudeOverPeriod( line, startDate, endDate, city, apparentMagnitudeMaximum, intervalInDaysBetweenApparentMagnitudeCalculations )
            if apparentMagnitude < apparentMagnitudeMaximum:
                namesKept.append( line[ : line.index( ',' ) ] )

    return namesKept


#TODO Do some statistical analysis...is 100 too low or too high?
def __filterByObservationsAndSanityCheck( inFile, minimalNumberOfObservations = 100 ):
    if inFile.endswith( ".gz" ):
        fIn = gzip.open( inFile, 'rt' )

    else:
        fIn = open( inFile, 'r' )

    fOut = tempfile.NamedTemporaryFile( mode = 'w', suffix = ".dat", delete = False )    
    droppedBodies = 0
    for line in fIn:
        if len( line.strip() ) == 0:
            print( "Found empty line" )
            continue

        name = line[ 1 - 1 : 26 ].strip()
        if '(' in name or ')' in name:
            print( "Found parenthesis in:", name )

        name = name.replace( '(', '' ).replace( ')', '' ).strip()
        if len( name ) == 0:
            print( "Missing name:\n" + line )
            continue

        numberOfObservations = line[ 101 - 1 : 106 ].strip()
        if int( numberOfObservations ) < minimalNumberOfObservations:
            droppedBodies += 1
            continue

        absoluteMagnitude = line[ 43 - 1 : 49 ].strip()
        if len( absoluteMagnitude ) == 0:
            print( "Missing absolute magnitude:\n" + line )
            continue

        fOut.write( line )

    if droppedBodies > 0:
        print( "Number of bodies dropped due to fewer than", minimalNumberOfObservations, "observations:", droppedBodies )

    return fOut.name


def main( fileToFilter ):
    astorbFilteredByObservations = __filterByObservationsAndSanityCheck( fileToFilter )
    pyephemFilteredByObservations = lowellMinorPlanetToXEphem.main( astorbFilteredByObservations )
    namesKept = __filterByApparentMagnitudeUsingPyEphem( pyephemFilteredByObservations )
    filteredFile = __filterByName( fileToFilter, namesKept )
    return filteredFile


if __name__ == "__main__":
    if len( sys.argv ) != 2:
        message = \
            "Usage: python3 " + Path(__file__).name + " fileToFilter" + \
            "\n\nFor example:" + \
            "\n  python3  " + Path(__file__).name + " astorb.dat" + \
            "\n  python3  " + Path(__file__).name + " astorb.dat.gz"

        raise SystemExit( message )

    print( "Created", main( sys.argv[ 1 ] ) )