#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import astrobase, astropyephem, astroskyfield, datetime, indicatorbase, logging, orbitalelement, twolineelement


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

logging.basicConfig( format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s", level = logging.DEBUG, handlers = [ indicatorbase.TruncatedFileHandler( "astroTest.log" ) ] )
utcNow = datetime.datetime.utcnow()
latitude = -33.8599722
longitude = 151.2111111
elevation = 100
magnitude = 6
hideIfBelowHorizon = False


#TODO rise/set not yet implemented in Skyfield
# https://github.com/skyfielders/python-skyfield/issues/115
tleData = twolineelement.download( "https://celestrak.com/NORAD/elements/visual.txt", logging )
satellites = [ ]
for key in tleData:
    satellites.append( key )

# print( "Running Skyfield..." )
resultsSkyfield = { }
# resultsSkyfield = astroskyfield.getAstronomicalInformation(
#     utcNow,
#     latitude, longitude, elevation,
#     astroskyfield.PLANETS,
#     astroskyfield.STARS,
#     [], [], #satellites, tleData,
#     [], [],
#     [], [],
#     magnitude,
#     hideIfBelowHorizon )

print( "Running Pyephem..." )
resultsPyephem = astropyephem.AstroPyephem.getAstronomicalInformation( 
    utcNow,
    latitude, longitude, elevation,
    astrobase.AstroBase.PLANETS,
    astrobase.AstroBase.STARS,
    satellites, tleData,
    [], [],
    [], [],
    magnitude,
    hideIfBelowHorizon )

print( "Crunching results..." )
compareResults( resultsPyephem, resultsSkyfield, astroskyfield.AstronomicalBodyType.Moon, astropyephem.NAME_TAG_MOON, astroskyfield.NAME_TAG_MOON, astropyephem.DATA_MOON, astroskyfield.DATA_MOON )
compareResults( resultsPyephem, resultsSkyfield, astroskyfield.AstronomicalBodyType.Sun, astropyephem.NAME_TAG_SUN, astroskyfield.NAME_TAG_SUN, astropyephem.DATA_SUN, astroskyfield.DATA_SUN )

for ( planetPyephem, planetSkyfield ) in zip( astropyephem.PLANETS, astroskyfield.PLANETS ):
    compareResults( resultsPyephem, resultsSkyfield, astroskyfield.AstronomicalBodyType.Planet, planetPyephem, planetSkyfield, astropyephem.DATA_PLANET, astroskyfield.DATA_PLANET )

# The list of stars between Pyephem and Skyfield do not match 100%, so choose a handful of stars common to both...
starsPyephem = [ "ACHERNAR", "ALGOL", "IZAR", "SAIPH" ]
starsSkyfield = [ "Achernar", "Algol", "Izar", "Saiph" ]
for ( starPyephem, starSkyfield ) in zip( starsPyephem, starsSkyfield ):
    compareResults( resultsPyephem, resultsSkyfield, astroSkyfield.AstronomicalBodyType.Star, starPyephem, starSkyfield, astropyephem.DATA_STAR, astroskyfield.DATA_STAR )