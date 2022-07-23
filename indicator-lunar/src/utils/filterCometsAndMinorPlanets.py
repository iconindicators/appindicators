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


# Filter bodies from:
#
#    The Lowell Minor Planet Services or Minor Planet Center asteroids (minor planet) databases which have:
#        A low number of observations;
#        An apparent magnitude exceeding a limit;
#    creating a new file from the result.
#
#    The Minor Planet Center comets file which have:
#        An apparent magnitude exceeding a limit;
#    creating a new file from the result.
#
# Requires PyEphem for the apparent magnitude calculations.
#
# The default filtering removes bodies which:
#    Have no name;
#    Have no absolute magnitude;
#    Have fewer than 250 observations (where applicable);
#    Do not have an apparent magnitude less than 15 at some point, measured every 30 days over the course of 366 days.


from enum import Enum
from pathlib import Path

import datetime, ephem, gzip, importlib, os, sys, tempfile
import lowellMinorPlanetToXEphem, mpcCometToXEphem, mpcMinorPlanetToXEphem


class DataType( Enum ):
    LOWELL_MINOR_PLANET          = 0
    MPC_MINOR_PLANET_WITH_HEADER = 1
    MPC_MINOR_PLANET_NO_HEADER   = 2
    MPC_COMET                    = 3


def toDataType( dataTypeAsString ):
    dataTypeStringToEnum = {
        DataType.LOWELL_MINOR_PLANET.name : DataType.LOWELL_MINOR_PLANET,
        DataType.MPC_MINOR_PLANET_WITH_HEADER.name : DataType.MPC_MINOR_PLANET_WITH_HEADER,
        DataType.MPC_MINOR_PLANET_NO_HEADER.name : DataType.MPC_MINOR_PLANET_NO_HEADER,
        DataType.MPC_COMET.name : DataType.MPC_COMET }

    return dataTypeStringToEnum[ dataTypeAsString ]


def getApparentMagnitudeOverPeriod(
        orbitalElement,
        startDate, endDate,
        city,
        magnitudeMaximum, intervalInDaysBetweenBodyCompute ):

    currentDate = startDate
    city = ephem.city( "London" ) # Use any city; makes no difference to obtain the apparent magnitude.
    body = ephem.readdb( orbitalElement )
    while currentDate < endDate:
        city.date = currentDate
        body.compute( city )
        if body.mag <= magnitudeMaximum:
            break

        currentDate += datetime.timedelta( days = intervalInDaysBetweenBodyCompute )

    return body.mag


def filterByApparentMagnitude(
        inFile,
        apparentMagnitudeMaximum = 15.0, # Upper limit for apparent magnitude.
        durationInYears = 1, # Number of years over which to compute apparent magnitude.
        intervalInDaysBetweenApparentMagnitudeCalculations = 30 ):

    print( "Filter by apparent magnitude..." )
    namesKept = [ ]
    startDate = datetime.datetime.utcnow()
    endDate = startDate + datetime.timedelta( days = 366 * durationInYears )
    with open( inFile, 'r' ) as fIn:
        city = ephem.city( "London" ) # Use any city; makes no difference to obtain the apparent magnitude.
        for line in fIn:
            apparentMagnitude = getApparentMagnitudeOverPeriod( line, startDate, endDate, city, apparentMagnitudeMaximum, intervalInDaysBetweenApparentMagnitudeCalculations )
            if apparentMagnitude < apparentMagnitudeMaximum:
                namesKept.append( line[ : line.index( ',' ) ] )

    return namesKept


def filterByName( inFile, outFile, names, nameStart, nameEnd ):
    print( "Filter by name..." )
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


def removeHeaderFromMPCORB( inFile ):
    print( "Removing MPCORB header..." )
    if inFile.endswith( ".gz" ):
        fIn = gzip.open( inFile, 'rt' )

    else:
        fIn = open( inFile, 'r' )

    fOut = tempfile.NamedTemporaryFile( mode = 'w', delete = False )
    endOfHeader = False
    for line in fIn:
        if endOfHeader:
            fOut.write( line )

        elif line.startswith( "----------" ):
            endOfHeader = True

    return fOut.name


def filterByObservations(
        inFile,
        observationsStart, observationsEnd,
        minimalNumberOfObservations = 250 ):

    print( "Filter by observations..." )
    fIn = open( inFile, 'r' )
    fOut = tempfile.NamedTemporaryFile( mode = 'w', delete = False )
    totalBodies = 0
    droppedBodies = 0
    for line in fIn:
        totalBodies += 1

        numberOfObservations = line[ observationsStart - 1 : observationsEnd ].strip()
        if int( numberOfObservations ) < minimalNumberOfObservations:
            droppedBodies += 1
            continue

        fOut.write( line )

    if droppedBodies > 0:
        print( "Dropped", droppedBodies, "bodies out of", totalBodies, "due to fewer than", minimalNumberOfObservations, "observations." )

    return fOut.name


# To filter a data file which does not contain observations,
# such as CometEls.txt, set observationsStart = -1.
def filterBySanityCheck(
        inFile,
        nameStart, nameEnd,
        magnitudeStart, magnitudeEnd,
        observationsStart, observationsEnd ):

    print( "Filter by sanity check..." )
    if inFile.endswith( ".gz" ):
        fIn = gzip.open( inFile, 'rt' )

    else:
        fIn = open( inFile, 'r' )

    fOut = tempfile.NamedTemporaryFile( mode = 'w', delete = False )
    for line in fIn:
        if len( line.strip() ) == 0:
            print( "Found empty line" )
            continue

        name = line[ nameStart - 1 : nameEnd ].strip()
        if len( name ) == 0:
            print( "Missing name:\n" + line )
            continue

        absoluteMagnitude = line[ magnitudeStart - 1 : magnitudeEnd ].strip()
        if len( absoluteMagnitude ) == 0:
            print( "Missing absolute magnitude:\n" + line )
            continue

        if observationsStart > -1:
            numberOfObservations = line[ observationsStart - 1 : observationsEnd ].strip()
            if len( numberOfObservations ) == 0:
                print( "Missing observations:\n" + line )
                continue

        fOut.write( line )

    return fOut.name


def filter( inFile, dataType, outFile ):
    dataType = toDataType( dataType )
    fileToFilter = inFile
    if dataType == DataType.MPC_COMET:
        nameStart = 103
        nameEnd = 158
        magnitudeStart = 92
        magnitudeEnd = 95
        observationsStart = -1
        observationsEnd = -1
        convertToXEphemFunction = getattr( importlib.import_module( "mpcCometToXEphem" ), "convert" )

    elif dataType == DataType.LOWELL_MINOR_PLANET:
        nameStart = 1
        nameEnd = 25
        magnitudeStart = 43
        magnitudeEnd = 47
        observationsStart = 101
        observationsEnd = 105
        convertToXEphemFunction = getattr( importlib.import_module( "lowellMinorPlanetToXEphem" ), "convert" )

    elif dataType == DataType.MPC_MINOR_PLANET_NO_HEADER or dataType == DataType.MPC_MINOR_PLANET_WITH_HEADER:
        nameStart = 167
        nameEnd = 194
        magnitudeStart = 9
        magnitudeEnd = 13
        observationsStart = 118
        observationsEnd = 122
        convertToXEphemFunction = getattr( importlib.import_module( "mpcMinorPlanetToXEphem" ), "convert" )

        if dataType == DataType.MPC_MINOR_PLANET_WITH_HEADER:
            fileToFilter = removeHeaderFromMPCORB( inFile )

    else:
        raise SystemExit( "Unknown data type: " + dataType )

    # Initial filtering
    filteredBySanityCheck = filterBySanityCheck( fileToFilter, nameStart, nameEnd, magnitudeStart, magnitudeEnd, observationsStart, observationsEnd )

    if dataType == DataType.MPC_COMET:
        filteredByObservations = filteredBySanityCheck

    else: # DataType.LOWELL_MINOR_PLANET or DataType.MPC_MINOR_PLANET_NO_HEADER or DataType.MPC_MINOR_PLANET_WITH_HEADER
        filteredByObservations = filterByObservations( filteredBySanityCheck, observationsStart, observationsEnd )

    filteredByObservationsConvertedToXEphem = tempfile.NamedTemporaryFile( delete = False ).name

    # Converting
    print( "Converting to XEphem..." )
    if dataType == DataType.MPC_MINOR_PLANET_NO_HEADER:
        convertToXEphemFunction( filteredByObservations, False, filteredByObservationsConvertedToXEphem )

    elif dataType == DataType.MPC_MINOR_PLANET_WITH_HEADER:
        convertToXEphemFunction( filteredByObservations, True, filteredByObservationsConvertedToXEphem )

    else:
        convertToXEphemFunction( filteredByObservations, filteredByObservationsConvertedToXEphem )

    # Final filtering
    names = filterByApparentMagnitude( filteredByObservationsConvertedToXEphem )
    filterByName( fileToFilter, outFile, names, nameStart, nameEnd )

    # Clean up
    if dataType == DataType.MPC_MINOR_PLANET_WITH_HEADER:
        os.remove( fileToFilter )

    os.remove( filteredBySanityCheck )

    if not( dataType == DataType.MPC_COMET ):
        os.remove( filteredByObservations )

    os.remove( filteredByObservationsConvertedToXEphem )

    print( "Created", outFile )


def filterORIGINAL( inFile, dataType, outFile ):
    fileToFilter = inFile
    if dataType == DataType.MPC_COMET.name:
        nameStart = 103
        nameEnd = 158
        magnitudeStart = 92
        magnitudeEnd = 95
        observationsStart = -1
        observationsEnd = -1
        convertToXEphemFunction = getattr( importlib.import_module( "mpcCometToXEphem" ), "convert" )

    elif dataType == DataType.LOWELL_MINOR_PLANET.name:
        nameStart = 1
        nameEnd = 25
        magnitudeStart = 43
        magnitudeEnd = 47
        observationsStart = 101
        observationsEnd = 105
        convertToXEphemFunction = getattr( importlib.import_module( "lowellMinorPlanetToXEphem" ), "convert" )

    elif dataType == DataType.MPC_MINOR_PLANET.name:
        nameStart = 167
        nameEnd = 194
        magnitudeStart = 9
        magnitudeEnd = 13
        observationsStart = 118
        observationsEnd = 122
        convertToXEphemFunction = getattr( importlib.import_module( "mpcMinorPlanetToXEphem" ), "convert" )

        if inFile.endswith( "MPCORB.DAT" ) or inFile.endswith( "MPCORB.DAT.gz" ):
            fileToFilter = removeHeaderFromMPCORB( inFile )

    else:
        raise SystemExit( "Unknown data type: " + dataType )

    # Filtering, converting...
    filteredBySanityCheck = filterBySanityCheck( fileToFilter, nameStart, nameEnd, magnitudeStart, magnitudeEnd, observationsStart, observationsEnd )

    if dataType == DataType.MPC_COMET.name:
        filteredByObservations = filteredBySanityCheck

    else: # DataType.LOWELL_MINOR_PLANET or DataType.MPC_MINOR_PLANET
        filteredByObservations = filterByObservations( filteredBySanityCheck, observationsStart, observationsEnd )

    filteredByObservationsConvertedToXEphem = tempfile.NamedTemporaryFile( delete = False ).name

    print( "Converting to XEphem..." )
    convertToXEphemFunction( filteredByObservations, filteredByObservationsConvertedToXEphem )

    names = filterByApparentMagnitude( filteredByObservationsConvertedToXEphem )
    filterByName( fileToFilter, outFile, names, nameStart, nameEnd )

    # Clean up
    if dataType == DataType.MPC_MINOR_PLANET.name:
        if inFile.endswith( "MPCORB.DAT" ) or inFile.endswith( "MPCORB.DAT.gz" ):
            os.remove( fileToFilter )

    os.remove( filteredBySanityCheck )

    if dataType == DataType.LOWELL_MINOR_PLANET.name or dataType == DataType.MPC_MINOR_PLANET.name:
        os.remove( filteredByObservations )

    os.remove( filteredByObservationsConvertedToXEphem )

    print( "Created", outFile )


if __name__ == "__main__":
    if len( sys.argv ) != 4:
        usage = "Usage: python3 " + Path(__file__).name + " fileToFilter dataType outputFile"

        dataTypes = "\n\nData types:"
        for dataType in DataType:
            dataTypes += "\n  " + str( dataType.name )

        examples = \
            "\n\nFor example:" + \
            "\n  python3  " + Path(__file__).name + " astorb.dat " + DataType.LOWELL_MINOR_PLANET.name + " astorb-filtered.dat" + \
            "\n  python3  " + Path(__file__).name + " astorb.dat.gz " + DataType.LOWELL_MINOR_PLANET.name + " astorb-filtered.dat" + \
            "\n" + \
            "\n  python3  " + Path(__file__).name + " MPCORB.DAT " + DataType.MPC_MINOR_PLANET_WITH_HEADER.name + " MPCORB-filtered.DAT" + \
            "\n  python3  " + Path(__file__).name + " MPCORB.DAT.gz " + DataType.MPC_MINOR_PLANET_WITH_HEADER.name + " MPCORB-filtered.DAT" + \
            "\n  python3  " + Path(__file__).name + " NEA.txt " + DataType.MPC_MINOR_PLANET_NO_HEADER.name + " NEA-filtered.txt" + \
            "\n  python3  " + Path(__file__).name + " PHA.txt " + DataType.MPC_MINOR_PLANET_NO_HEADER.name + " PHA-filtered.txt" + \
            "\n  python3  " + Path(__file__).name + " DAILY.DAT " + DataType.MPC_MINOR_PLANET_NO_HEADER.name + " DAILY-filtered.DAT" + \
            "\n  python3  " + Path(__file__).name + " Distant.txt " + DataType.MPC_MINOR_PLANET_NO_HEADER.name + " Distant-filtered.txt" + \
            "\n  python3  " + Path(__file__).name + " Unusual.txt " + DataType.MPC_MINOR_PLANET_NO_HEADER.name + " Unusual-filtered.txt" + \
            "\n" + \
            "\n  python3  " + Path(__file__).name + " CometEls.txt " + DataType.MPC_COMET.name + " CometEls-filtered.txt"

        message = usage + dataTypes + examples

        raise SystemExit( message )

    filter( sys.argv[ 1 ], sys.argv[ 2 ], sys.argv[ 3 ] )
    
# TODO Test ALL vaiants again...I'm getting empty out put files.

# TODO Make the app mag and obs as paramenters...maybe as just globasl.     
    