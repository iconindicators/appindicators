#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# mpc@cfa.harvard.edu

# Download the following files:

# https://www.minorplanetcenter.org/iau/MPCORB/MPCORB.DAT
# https://www.minorplanetcenter.net/iau/Ephemerides/Bright/2018/Soft00Bright.txt
# https://www.minorplanetcenter.net/iau/Ephemerides/CritList/Soft00CritList.txt
# https://www.minorplanetcenter.net/iau/Ephemerides/Distant/Soft00Distant.txt
# https://www.minorplanetcenter.net/iau/Ephemerides/Unusual/Soft00Unusual.txt


minorPlanetFilenames = [
    "Soft00Bright.txt",
    "Soft00CritList.txt",
    "Soft00Distant.txt",
    "Soft00Unusual.txt" ]

# minorPlanets = [ ]
# for filename in minorPlanetFilenames:
#     with open( filename, 'r' ) as f:
#         minorPlanets += f.readlines()

minorPlanets = { }
for filename in minorPlanetFilenames:
    with open( filename, 'r' ) as f:
        for line in f:
            name = line[ 0 : 6 + 1 ]
            minorPlanets[ name ] = line

print( "Minor planets in files:", len( minorPlanets ) )

minorPlanetsDifferent = [ ]
foundBeginningOfData = False
chunkCount = 0
chunks = { }
with open( "MPCORB.DAT", 'r' ) as f:
    names = minorPlanets.keys()
    for line in f:
        if not foundBeginningOfData:
            if line.startswith( "----------" ):
                foundBeginningOfData = True

            continue

        # chunks[ line[ 0 : 6 + 1 ] ] = line # Use minor planet designation/name as key.
        # chunkCount += 1
        # if chunkCount == 10000:
        #     keys = chunks.keys()
        #     for minorPlanet in minorPlanets:
        #         designation = minorPlanet[ 0 : 6 + 1 ]
        #         if designation in keys and minorPlanet != chunks[ designation ]:
        #             minorPlanetsDifferent.append( designation )
        #
        #     chunks = { }
        #     chunkCount = 0

        name = line[ 0 : 6 + 1 ]
        if name in names:
            if line != minorPlanets[ name ]:
                minorPlanetsDifferent.append( name )

print( "Minor planets in files differing to database:", len( minorPlanetsDifferent ) )

minorPlanetMissing = [ ]
for minorPlanet in minorPlanets:
    designation = minorPlanet[ 0 : 6 + 1 ]
    if designation not in minorPlanetsDifferent:
        minorPlanetMissing.append( designation )

print( "Minor planets in files missing from database:", len( minorPlanetMissing ) )