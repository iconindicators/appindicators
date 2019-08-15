#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import astroPyephem, astroSkyfield, datetime


# Not exactly useful as the keys for stars are different between Skyfield and Pyephem.
#TODO Would be more useful if we compared planets and then specific keys of the other objects
# (specific stars, comets, satellites).
def compareResults( resultsPyephem, resultsSkyfield ):

    results = [ ]
    for dataTag in astroPyephem.DATA_MOON:
        if ( astroPyephem.AstronomicalBodyType.Moon, astroPyephem.NAME_TAG_MOON, dataTag ) not in resultsSkyfield:
            results.append( dataTag )

    if results:
        print( "Moon keys in Pyephem not in Skyfield:", results )

    results = [ ]
    for dataTag in astroSkyfield.DATA_MOON:
        if ( astroSkyfield.AstronomicalBodyType.Moon, astroSkyfield.NAME_TAG_MOON, dataTag ) not in resultsPyephem:
            results.append( dataTag )

    if results:
        print( "Moon keys in Skyfield not in Pyephem:", results )

    results = [ ]
    for dataTag in astroPyephem.DATA_MOON:
        key = ( astroPyephem.AstronomicalBodyType.Moon, astroPyephem.NAME_TAG_MOON, dataTag )
        if key in resultsPyephem and key in resultsSkyfield and resultsPyephem[ key ] != resultsSkyfield[ key ]:
            results.append( dataTag )

    if results:
        print( "Moon values in Pyephem which differ from Skyfield:" )
        for dataTag in results:
            key = ( astroPyephem.AstronomicalBodyType.Moon, astroPyephem.NAME_TAG_MOON, dataTag )
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
compareResults( resultsPyephem, resultsSkyfield )