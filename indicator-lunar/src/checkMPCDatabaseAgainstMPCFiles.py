#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# Download the following files:

# From https://minorplanetcenter.net/data
    # https://www.minorplanetcenter.net/iau/MPCORB/MPCORB.DAT

# From https://minorplanetcenter.net/data
    # https://www.minorplanetcenter.net/iau/MPCORB/DAILY.DAT
    # https://www.minorplanetcenter.net/iau/MPCORB/NEA.txt
    # https://www.minorplanetcenter.net/iau/MPCORB/PHA.txt
    # https://www.minorplanetcenter.net/iau/MPCORB/Distant.txt
    # https://www.minorplanetcenter.net/iau/MPCORB/Unusual.txt

# From https://minorplanetcenter.net/iau/Ephemerides/Soft00.html
    # https://www.minorplanetcenter.net/iau/Ephemerides/Bright/2018/Soft00Bright.txt
    # https://www.minorplanetcenter.net/iau/Ephemerides/CritList/Soft00CritList.txt
    # https://www.minorplanetcenter.net/iau/Ephemerides/Distant/Soft00Distant.txt
    # https://www.minorplanetcenter.net/iau/Ephemerides/Unusual/Soft00Unusual.txt


# Format for files:
    # https://www.minorplanetcenter.net/iau/info/MPOrbitFormat.html
def checkAgainstDatabase( file ):
    minorPlanets = { }
    with open( file, 'r' ) as f:
        for line in f:
            name = line[ 0 : 6 + 1 ]
            minorPlanets[ name ] = line

    print( "Minor planets in", file + ':', len( minorPlanets ) )

    minorPlanetsDifferent = { }
    foundBeginningOfData = False
    names = minorPlanets.keys()
    with open( "MPCORB.DAT", 'r' ) as f:
        for line in f:
            if not foundBeginningOfData:
                if line.startswith( "----------" ):
                    foundBeginningOfData = True

                continue

            name = line[ 0 : 6 + 1 ]
            if name in names and line != minorPlanets[ name ]:
                minorPlanetsDifferent[ name ] = ""

    if minorPlanetsDifferent:
        print( "Different to database:", len( minorPlanetsDifferent ) )
        # print( '\t', minorPlanetsDifferent ) # Uncomment to show specific bodies.

    minorPlanetsMissing = minorPlanets.keys() - minorPlanetsDifferent.keys()
    if minorPlanetsMissing:
        print( "Missing from database:", len( minorPlanetsMissing ) )
        # print( '\t', minorPlanetsMissing ) # Uncomment to show specific bodies.

    print()


checkAgainstDatabase( "DAILY.DAT" )
checkAgainstDatabase( "NEA.txt" )
checkAgainstDatabase( "PHA.txt" )
checkAgainstDatabase( "Distant.txt" )
checkAgainstDatabase( "Unusual.txt" )
checkAgainstDatabase( "Soft00Bright.txt" )
checkAgainstDatabase( "Soft00CritList.txt" )
checkAgainstDatabase( "Soft00Distant.txt" )
checkAgainstDatabase( "Soft00Unusual.txt" )