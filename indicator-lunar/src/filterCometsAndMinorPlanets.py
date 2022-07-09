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


from enum import Enum
from pathlib import Path


import datetime, ephem, gzip, os, sys, tempfile
import lowellMinorPlanetToXEphem, mpcCometToXEphem, mpcMinorPlanetToXEphem


class DataType( Enum ):
    LOWELL_MINOR_PLANET = 0
    MPC_MINOR_PLANET = 1
    MPC_COMET = 2


def getApparentMagnitudeOverPeriod( orbitalElement, startDate, endDate, city, apparentMagnitudeMaximum, intervalInDaysBetweenBodyCompute ):
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


def filterByName( inFile, outFile, names, nameStart, nameEnd ):
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


def filterByApparentMagnitude(
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
            apparentMagnitude = getApparentMagnitudeOverPeriod( line, startDate, endDate, city, apparentMagnitudeMaximum, intervalInDaysBetweenApparentMagnitudeCalculations )
            if apparentMagnitude < apparentMagnitudeMaximum:
                namesKept.append( line[ : line.index( ',' ) ] )

    return namesKept


def removeHeaderFromMPCORB( inFile ):
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


#TODO Do some statistical analysis...is 100 too low or too high?
#TODO Given that MPC comets do not have the observations field,
# might need to split this function into name/magnitude/sanity and observations,
# or just pass in a flag (or minimalNumberOfObservations = -1).
def filterByObservationsAndSanityCheck(
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


def filter( inFile, dataType, outFile ):
    if dataType == DataType.MPC_COMET.name:
#TODO...
        # filteredByObservations = filterByObservationsAndSanityCheck( inFile, 1, 26, 101, 106, 43, 49 ) #TODO Filter on sanity/name/magnitude but not observations.
        # filteredByObservationsXEphem = tempfile.NamedTemporaryFile( delete = False )
        # mpcCometToXEphem.convert( filteredByObservations, filteredByObservationsXEphem.name )
        # names = filterByApparentMagnitude( filteredByObservationsXEphem.name )
        # filterByName( inFile, outFile, names, 103, 158 )
        # os.remove( filteredByObservations )
        # os.remove( filteredByObservationsXEphem.name )
        # print( "Created", outFile )
        pass

    elif dataType == DataType.LOWELL_MINOR_PLANET.name:
        filteredByObservations = filterByObservationsAndSanityCheck( inFile, 1, 26, 101, 106, 43, 49 )
        filteredByObservationsXEphem = tempfile.NamedTemporaryFile( delete = False )
        lowellMinorPlanetToXEphem.convert( filteredByObservations, filteredByObservationsXEphem.name )
        names = filterByApparentMagnitude( filteredByObservationsXEphem.name )
        filterByName( inFile, outFile, names, 1, 26 )
        os.remove( filteredByObservations )
        os.remove( filteredByObservationsXEphem.name )
        print( "Created", outFile )

    elif dataType == DataType.MPC_MINOR_PLANET.name:
        fileToFilter = inFile
        if inFile == "MPCORB.DAT" or inFile == "MPCORB.DAT.gz":
            fileToFilter = removeHeaderFromMPCORB( inFile )

        filteredByObservations = filterByObservationsAndSanityCheck( fileToFilter, 167, 194, 118, 122, 9, 13 )
        filteredByObservationsXEphem = tempfile.NamedTemporaryFile( delete = False )
        mpcMinorPlanetToXEphem.convert( filteredByObservations, filteredByObservationsXEphem.name )
        names = filterByApparentMagnitude( filteredByObservationsXEphem.name )
        filterByName( fileToFilter, outFile, names, 1, 26 )
        os.remove( filteredByObservations )
        os.remove( filteredByObservationsXEphem.name )
        if inFile == "MPCORB.DAT" or inFile == "MPCORB.DAT.gz":
            os.remove( fileToFilter )

        print( "Created", outFile )

    else:
        print( "Unknown data type:", dataType )


if __name__ == "__main__":
    if len( sys.argv ) != 4:
        usage = "Usage: python3 " + Path(__file__).name + " fileToFilter dataType outputFile"

        dataTypes = "\n\nData types:"
        for dataType in DataType:
            dataTypes += "\n  " + str( dataType.name )

        examples = \
            "\n\nFor example:" + \
            "\n  python3  " + Path(__file__).name + " astorb.dat LOWELL_MINOR_PLANET astorb-filtered.dat" + \
            "\n  python3  " + Path(__file__).name + " astorb.dat.gz LOWELL_MINOR_PLANET astorb-filtered.dat" + \
            "\n" + \
            "\n  python3  " + Path(__file__).name + " MPCORB.DAT MPC_MINOR_PLANET mpcorb-filtered.dat" + \
            "\n  python3  " + Path(__file__).name + " MPCORB.DAT.gz MPC_MINOR_PLANET mpcorb-filtered.dat" + \
            "\n  python3  " + Path(__file__).name + " NEA.txt MPC_MINOR_PLANET NEA-filtered.txt" + \
            "\n  python3  " + Path(__file__).name + " PHA.txt MPC_MINOR_PLANET PHA-filtered.txt" + \
            "\n  python3  " + Path(__file__).name + " DAILY.DAT MPC_MINOR_PLANET DAILY-filtered.dat" + \
            "\n  python3  " + Path(__file__).name + " Distant.txt MPC_MINOR_PLANET Distant-filtered.txt" + \
            "\n  python3  " + Path(__file__).name + " Unusual.txt MPC_MINOR_PLANET Unusual-filtered.txt" + \
            "\n" + \
            "\n  python3  " + Path(__file__).name + " CometEls.txt MPC_COMET comets-filtered.dat"

        message = usage + dataTypes + examples

        raise SystemExit( message )

    filter( sys.argv[ 1 ], sys.argv[ 2 ], sys.argv[ 3 ] )