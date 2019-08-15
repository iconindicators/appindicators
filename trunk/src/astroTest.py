#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from skyfield.api import Topos, load

import astroPyephem, astroSkyfield, datetime, satellite
from src.celestrak.TestCelestrak import tleData


def compareResults( resultsPyephem, resultsSkyfield, astronomicalBodyType, nameTagPyephem, nameTagSkyfield, dataTagsPyephem, dataTagsSkyfield ):

    results = [ ]
    for dataTag in dataTagsPyephem:
        if ( astronomicalBodyType, nameTagPyephem, dataTag ) in resultsPyephem and \
           ( astronomicalBodyType, nameTagSkyfield, dataTag ) not in resultsSkyfield:
            results.append( dataTag )

    if results:
        print( nameTagPyephem, "keys in Pyephem not in Skyfield:", results )

    results = [ ]
    for dataTag in dataTagsSkyfield:
        if ( astronomicalBodyType, nameTagSkyfield, dataTag ) in resultsSkyfield and \
           ( astronomicalBodyType, nameTagPyephem, dataTag ) not in resultsPyephem:
            results.append( dataTag )

    if results:
        print( nameTagSkyfield, "keys in Skyfield not in Pyephem:", results )

    results = [ ]
    for dataTag in dataTagsPyephem:
        keyPyephem = ( astronomicalBodyType, nameTagPyephem, dataTag )
        keySkyfield = ( astronomicalBodyType, nameTagSkyfield, dataTag )
        if keyPyephem in resultsPyephem and keySkyfield in resultsSkyfield and resultsPyephem[ keyPyephem ] != resultsSkyfield[ keySkyfield ]:
            results.append( dataTag )

    if results:
        print( nameTagPyephem, "values in Pyephem which differ from Skyfield:" )
        for dataTag in results:
            keyPyephem = ( astronomicalBodyType, nameTagPyephem, dataTag )
            keySkyfield = ( astronomicalBodyType, nameTagSkyfield, dataTag )
            print( "\t", dataTag, resultsPyephem[ keyPyephem ], resultsSkyfield[ keySkyfield ] )


utcNow = datetime.datetime.utcnow()
latitude = -33.8599722
longitude = 151.2111111
elevation = 100
magnitude = 6


#TODO rise/set not yet implemented in Skyfield
# https://github.com/skyfielders/python-skyfield/issues/115
tleData = satellite.download( "https://celestrak.com/NORAD/elements/visual.txt", None )
satellites = [ ]
for key in tleData:
    satellites.append( key )


print( "Running Skyfield..." )
resultsSkyfield = astroSkyfield.getAstronomicalInformation( utcNow,
                                                            latitude, longitude, elevation,
                                                            astroSkyfield.PLANETS,
                                                            astroSkyfield.STARS,
                                                            satellites, tleData,
                                                            [], [],
                                                            [], [],
                                                            magnitude )

print( "Running Pyephem..." )
resultsPyephem = astroPyephem.getAstronomicalInformation( utcNow,
                                                          latitude, longitude, elevation,
                                                          astroPyephem.PLANETS,
                                                          astroPyephem.STARS,
                                                          satellites, tleData,
                                                          [], [],
                                                          [], [],
                                                          magnitude )

print( "Crunching results..." )
compareResults( resultsPyephem, resultsSkyfield, astroSkyfield.AstronomicalBodyType.Moon, astroPyephem.NAME_TAG_MOON, astroSkyfield.NAME_TAG_MOON, astroPyephem.DATA_MOON, astroSkyfield.DATA_MOON )
compareResults( resultsPyephem, resultsSkyfield, astroSkyfield.AstronomicalBodyType.Sun, astroPyephem.NAME_TAG_SUN, astroSkyfield.NAME_TAG_SUN, astroPyephem.DATA_SUN, astroSkyfield.DATA_SUN )

for ( planetPyephem, planetSkyfield ) in zip( astroPyephem.PLANETS, astroSkyfield.PLANETS ):
    compareResults( resultsPyephem, resultsSkyfield, astroSkyfield.AstronomicalBodyType.Planet, planetPyephem, planetSkyfield, astroPyephem.DATA_PLANET, astroSkyfield.DATA_PLANET )

# The list of stars between Pyephem and Skyfield do not match 100%, so choose a handful of stars common to both...
starsPyephem = [ "ACHERNAR", "ALGOL", "IZAR", "SAIPH" ]
starsSkyfield = [ "Achernar", "Algol", "Izar", "Saiph" ]
for ( starPyephem, starSkyfield ) in zip( starsPyephem, starsSkyfield ):
    compareResults( resultsPyephem, resultsSkyfield, astroSkyfield.AstronomicalBodyType.Star, starPyephem, starSkyfield, astroPyephem.DATA_STAR, astroSkyfield.DATA_STAR )
