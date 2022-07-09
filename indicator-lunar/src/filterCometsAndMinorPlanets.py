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


from enum import Enum
from pathlib import Path


import datetime, ephem, gzip, os, sys, tempfile
import lowellMinorPlanetToXEphem


class DataType( Enum ):
    LOWELL_MINOR_PLANET = 0
    MINOR_PLANET_CENTER_MINOR_PLANET = 1
    MINOR_PLANET_CENTER_COMET = 2


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


def __filterByName( inFile, outFile, names, nameStart, nameEnd ):
    if inFile.endswith( ".gz" ):
        fIn = gzip.open( inFile, 'rt' )

    else:
        fIn = open( inFile, 'r' )

    fOut = open( outFile, 'w' )
    for line in fIn:
        if len( line.strip() ) == 0:
            continue

        name = line[ nameStart - 1 : nameEnd ].strip()
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
def __filterByObservationsAndSanityCheck(
        inFile,
        nameStart, nameEnd,
        observationsStart, observationsEnd,
        magnitudeStart, magnitudeEnd,
        minimalNumberOfObservations = 100 ):
    if inFile.endswith( ".gz" ):
        fIn = gzip.open( inFile, 'rt' )

    else:
        fIn = open( inFile, 'r' )

    fOut = tempfile.NamedTemporaryFile( mode = 'w', delete = False )
    droppedBodies = 0
    for line in fIn:
        if len( line.strip() ) == 0:
            print( "Found empty line" )
            continue

        name = line[ nameStart - 1 : nameEnd ].replace( '(', '' ).replace( ')', '' ).strip()
        if len( name ) == 0:
            print( "Missing name:\n" + line )
            continue

        numberOfObservations = line[ observationsStart - 1 : observationsEnd ].strip()
        if int( numberOfObservations ) < minimalNumberOfObservations:
            droppedBodies += 1
            continue

        absoluteMagnitude = line[ magnitudeStart - 1 : magnitudeEnd ].strip()
        if len( absoluteMagnitude ) == 0:
            print( "Missing absolute magnitude:\n" + line )
            continue

        fOut.write( line )

    if droppedBodies > 0:
        print( "Number of bodies dropped due to fewer than", minimalNumberOfObservations, "observations:", droppedBodies )

    return fOut.name


def main( inFile, dataType, outFile ):
    if dataType == DataType.MINOR_PLANET_CENTER_COMET.name:
        print( "comets" )
        # bodiesBelowApparentMagnitudeLimit = __filterByApparentMagnitudeUsingPyEphem( mpcCometToXEphem.main( inFile ) )
        # filteredFile = __filterByName( fileToFilter, outFile, bodiesBelowApparentMagnitudeLimit, 103, 158 )

    elif dataType == DataType.LOWELL_MINOR_PLANET.name:
        filteredByObservations = __filterByObservationsAndSanityCheck( inFile, 1, 26, 101, 106, 43, 49 )
        pyephemFilteredByObservations = tempfile.NamedTemporaryFile( delete = False )
        lowellMinorPlanetToXEphem.main( filteredByObservations, pyephemFilteredByObservations.name )
        bodiesBelowApparentMagnitudeLimit = __filterByApparentMagnitudeUsingPyEphem( pyephemFilteredByObservations.name )
        filteredFile = __filterByName( inFile, outFile, bodiesBelowApparentMagnitudeLimit, 1, 26 )
        os.remove( filteredByObservations )
        os.remove( pyephemFilteredByObservations.name )
        print( "Created", outFile )

    elif dataType == DataType.MINOR_PLANET_CENTER_MINOR_PLANET.name:
        pass
        # filteredByObservations = __filterByObservationsAndSanityCheck( inFile, 167, 194, 118, 122, 9, 13 )
        # pyephemFilteredByObservations = mpcMinorPlanetToXEphem.main( filteredByObservations )
        # bodiesBelowApparentMagnitudeLimit = __filterByApparentMagnitudeUsingPyEphem( pyephemFilteredByObservations )
        # filteredFile = __filterByName( inFile, outFile, bodiesBelowApparentMagnitudeLimit, 167, 194 )

    else:
        print( "Unknown data type:", dataType )


if __name__ == "__main__":
    if len( sys.argv ) != 4:
        dataTypesMessage = ""
        for dataType in DataType:
            dataTypesMessage += "\n  " + str( dataType.name )

        message = \
            "Usage: python3 " + Path(__file__).name + " fileToFilter dataType outputFile" + \
            "\n\nData types:" + \
            dataTypesMessage + \
            "\n\nFor example:" + \
            "\n  python3  " + Path(__file__).name + " astorb.dat LOWELL_MINOR_PLANET astorb-filtered.dat" + \
            "\n  python3  " + Path(__file__).name + " astorb.dat.gz LOWELL_MINOR_PLANET astorb-filtered.dat" + \
            "\n  python3  " + Path(__file__).name + " MPCORB.DAT MINOR_PLANET_CENTER_MINOR_PLANET mpcorb-filtered.dat" + \
            "\n  python3  " + Path(__file__).name + " MPCORB.DAT.gz MINOR_PLANET_CENTER_MINOR_PLANET mpcorb-filtered.dat" + \
            "\n  python3  " + Path(__file__).name + " CometEls.txt MINOR_PLANET_CENTER_COMET comets-filtered.dat"

        raise SystemExit( message )

    main( sys.argv[ 1 ], sys.argv[ 2 ], sys.argv[ 3 ] )