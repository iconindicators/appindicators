#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import astroPyephem, astroSkyfield, datetime


def compareResults( resultsPyephem, resultsSkyfield, astronomicalBodyType, nameTag, dataTagsPyephem, dataTagsSkyfield ):

    results = [ ]
    for dataTag in dataTagsPyephem:
        if ( astronomicalBodyType, nameTag, dataTag ) in resultsPyephem and \
           ( astronomicalBodyType, nameTag, dataTag ) not in resultsSkyfield:
            results.append( dataTag )

    if results:
        print( nameTag, "keys in Pyephem not in Skyfield:", results )

    results = [ ]
    for dataTag in dataTagsSkyfield:
        if ( astronomicalBodyType, nameTag, dataTag ) in resultsSkyfield and \
           ( astronomicalBodyType, nameTag, dataTag ) not in resultsPyephem:
            results.append( dataTag )

    if results:
        print( nameTag, "keys in Skyfield not in Pyephem:", results )

    results = [ ]
    for dataTag in dataTagsPyephem:
        key = ( astronomicalBodyType, nameTag, dataTag )
        if key in resultsPyephem and key in resultsSkyfield and resultsPyephem[ key ] != resultsSkyfield[ key ]:
            results.append( dataTag )

    if results:
        print( nameTag, "values in Pyephem which differ from Skyfield:" )
        for dataTag in results:
            key = ( astronomicalBodyType, nameTag, dataTag )
            print( "\t", dataTag, resultsPyephem[ key ], resultsSkyfield[ key ] )


utcNow = datetime.datetime.utcnow()
latitude = -33.8599722
longitude = 151.2111111
elevation = 100
magnitude = 6

print( "Running Skyfield..." )
resultsSkyfield = astroSkyfield.getAstronomicalInformation( utcNow,
                                                            latitude, longitude, elevation,
                                                            astroSkyfield.PLANETS,
                                                            astroSkyfield.STARS,
                                                            [], [],
                                                            [], [],
                                                            [], [],
                                                            magnitude )

print( "Running Pyephem..." )
resultsPyephem = astroPyephem.getAstronomicalInformation( utcNow,
                                                          latitude, longitude, elevation,
                                                          astroPyephem.PLANETS,
                                                          astroPyephem.STARS,
                                                          [], [],
                                                          [], [],
                                                          [], [],
                                                          magnitude )

print( "Crunching results..." )
compareResults( resultsPyephem, resultsSkyfield, astroSkyfield.AstronomicalBodyType.Moon, astroSkyfield.NAME_TAG_MOON, astroPyephem.DATA_MOON, astroSkyfield.DATA_MOON )
compareResults( resultsPyephem, resultsSkyfield, astroSkyfield.AstronomicalBodyType.Sun, astroSkyfield.NAME_TAG_SUN, astroPyephem.DATA_SUN, astroSkyfield.DATA_SUN )
