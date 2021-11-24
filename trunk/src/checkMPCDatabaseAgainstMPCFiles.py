#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# mpc@cfa.harvard.edu

# MINOR_PLANET_URL = "https://minorplanetcenter.net/iau/Ephemerides/"
#
# MINOR_PLANET_BRIGHT_URL_MPC = MINOR_PLANET_URL + "Bright/2018/Soft00Bright.txt"
# MINOR_PLANET_BRIGHT_URL_XEPHEM = MINOR_PLANET_URL + "Bright/2018/Soft03Bright.txt"
#
# MINOR_PLANET_CRITICAL_URL_MPC = MINOR_PLANET_URL + "CritList/Soft00CritList.txt"
# MINOR_PLANET_CRITICAL_URL_XEPHEM = MINOR_PLANET_URL + "CritList/Soft03CritList.txt"
#
# MINOR_PLANET_DISTANT_URL_MPC = MINOR_PLANET_URL + "Distant/Soft00Distant.txt"
# MINOR_PLANET_DISTANT_URL_XEPHEM = MINOR_PLANET_URL + "Distant/Soft03Distant.txt"
#
# MINOR_PLANET_UNUSUAL_URL = MINOR_PLANET_URL + "Unusual/Soft00Unusual.txt"
# MINOR_PLANET_UNUSUAL_URL_XEPHEM_FORMAT = MINOR_PLANET_URL + "Unusual/Soft03Unusual.txt"


#TODO Read in big file, then read in each file and check line for line in big file.
# https://www.minorplanetcenter.org/iau/MPCORB/MPCORB.DAT
minorPlanetFilenames = [
    "Soft00Bright.txt",
    "Soft00CritList.txt",
    "Soft00Distant.txt",
    "Soft00Unusual.txt" ]

minorPlanets = [ ]
for filename in minorPlanetFilenames:
    with open( filename, 'r' ) as f:
        minorPlanets += f.readlines()

print( "Minor planets in files:", len(minorPlanets ) )

minorPlanetsDifferent = [ ]
foundBeginningOfData = False
count = 0
databaseChunks = { }
with open( "MPCORB.DAT", 'r' ) as f:
    for line in f:
        if not foundBeginningOfData:
            if line.startswith( "----------" ):
                foundBeginningOfData = True

            continue

        databaseChunks[ line[ 0 : 6 + 1 ] ] = line
        count += 1
        if count == 10000:
            keys = databaseChunks.keys()
            for minorPlanet in minorPlanets:
                designation = minorPlanet[ 0 : 6 + 1 ]
                if designation in keys and minorPlanet != databaseChunks[ designation ]:
                    minorPlanetsDifferent.append( designation )

            databaseChunks = { }
            count = 0

print( "Minor planets in files differing to database:", len( minorPlanetsDifferent ) )

minorPlanetMissing = [ ]
for minorPlanet in minorPlanets:
    designation = minorPlanet[ 0 : 6 + 1 ]
    if designation not in minorPlanetsDifferent:
        minorPlanetMissing.append( designation )

print( "Minor planets in files missing from database:", len( minorPlanetMissing ) )



#
# minorPlanetFilenames = [
#     "Soft00Bright.txt",
#     "Soft00CritList.txt",
#     "Soft00Distant.txt",
#     "Soft00Unusual.txt" ]
#
# minorPlanetContents = { }
# for filename in minorPlanetFilenames:
#     with open( filename, 'r' ) as f:
#         minorPlanetContents[ filename ] = f.readlines()
#
# for filename in minorPlanetContents:
#     print( filename, len( minorPlanetContents[ filename ] ) )
#
# foundBeginningOfData = False
# count = 0
# databaseChunks = [ ]
# with open( "MPCORB.DAT", 'r' ) as f:
#     for line in f:
#         if not foundBeginningOfData:
#             if line.startswith( "----------" ):
#                 foundBeginningOfData = True
#
#             continue
#
#         # print( line )
#         # break
#
#         databaseChunks.append( line )
#         count += 1
#         if count == 10000:
#             for filename in minorPlanetContents:
#                 for line in minorPlanetContents[ filename ]:
#                     designation = line[ 0 : 6 + 1 ] # Offset for zero index, so really is 1 - 7.
#                     if designation in databaseChunks
#                 pass
#                 present = [ line for line in minorPlanetContents[ filename ] if line in databaseChunks ]
#                 # print( len( present ) )
#             print( databaseChunks[ 0 ] )
#             # print( len( databaseChunks ) )
#
#             databaseChunks = [ ]
#             count = 0
# #
# #     for filename in minorPlanetFiles:
# #         print( filename, len( minorPlanetFiles[ filename ] ) )

