#!/usr/bin/env python3


# Refer to https://github.com/skyfielders/python-skyfield/issues/416


# Download and save 
#     https://www.minorplanetcenter.net/iau/Ephemerides/Comets/Soft00Cmt.txt
#     https://www.minorplanetcenter.net/iau/Ephemerides/Comets/Soft03Cmt.txt
#     https://www.minorplanetcenter.net/iau/Ephemerides/Bright/2018/Soft00Bright.txt
#     https://www.minorplanetcenter.net/iau/Ephemerides/Bright/2018/Soft03Bright.txt


# External verification:
# https://in-the-sky.org/data/object.php?id=0088P
# https://theskylive.com/88p-info
# https://heavens-above.com/comet.aspx?cid=88P
# https://www.calsky.com/cs.cgi/Comets/3?


import datetime, ephem, io, math, skyfield.api, skyfield.constants, skyfield.data.mpc


def pyephemCometMinorPlanet( utcNow, latitude, longitude, name, data, isComet ):
    observer = ephem.Observer()
    observer.date = ephem.Date( utcNow )
    observer.lat = str( latitude )
    observer.lon = str( longitude )

    body = ephem.readdb( getData( name, data ) )
    body.compute( observer )

    sun = ephem.Sun()
    sun.compute( observer )

    if isComet:
        apparentMagnitude = getApparentMagnitude_gk( body._g, body._k, body.earth_distance, body.sun_distance )
        print( "PyEphem", name,
               "\n\tMagnitude (from PyEphem):", body.mag,
               "\n\tAbsolute Magnitude (g from data file):", body._g,
               "\n\tEarth Body Distance AU:", body.earth_distance,
               "\n\tApparent Magnitude (calculated):", apparentMagnitude,
               "\n" )

    else:
        apparentMagnitude = getApparentMagnitude_HG( body._H, body._G, body.earth_distance, body.sun_distance, sun.earth_distance )
        print( "PyEphem", name,
               "\n\tMagnitude (from PyEphem):", body.mag,
               "\n\tAbsolute Magnitude (H from data file):", body._H,
               "\n\tEarth Body Distance AU:", body.earth_distance,
               "\n\tApparent Magnitude (calculated):", apparentMagnitude,
               "\n" )


def skyfieldCometMinorPlanet( utcNow, latitude, longitude, name, data, isComet ):
    topos = skyfield.api.Topos( latitude_degrees = latitude, longitude_degrees = longitude )
    ephemeris = skyfield.api.load( "de421.bsp" )
    sun = ephemeris[ "sun" ]
    earth = ephemeris[ "earth" ]

    timeScale = skyfield.api.load.timescale( builtin = True )
    t = timeScale.utc( utcNow.year, utcNow.month, utcNow.day, utcNow.hour, utcNow.minute, utcNow.second )
    alt, az, earthSunDistance = ( earth + topos ).at( t ).observe( sun ).apparent().altaz()

    with io.BytesIO( getData( name, data ).encode() ) as f:
        if isComet:
            dataframe = skyfield.data.mpc.load_comets_dataframe( f ).set_index( "designation", drop = False )
            body = sun + skyfield.data.mpc.comet_orbit( dataframe.loc[ name ], timeScale, skyfield.constants.GM_SUN_Pitjeva_2005_km3_s2 )

        else:
            dataframe = skyfield.data.mpc.load_mpcorb_dataframe( f ).set_index( "designation", drop = False )
            body = sun + skyfield.data.mpc.mpcorb_orbit( dataframe.loc[ name ], timeScale, skyfield.constants.GM_SUN_Pitjeva_2005_km3_s2 )

    ra, dec, sunBodyDistance = ( sun ).at( t ).observe( body ).radec()
    alt, az, earthBodyDistance = ( earth + topos ).at( t ).observe( body ).apparent().altaz()

    if isComet:
        # The fields "magnitude_H" and "magnitude_G" really should be called "magnitude_g" and "magnitude_k".
        apparentMagnitude = getApparentMagnitude_gk( dataframe.loc[ name ][ "magnitude_H" ], dataframe.loc[ name ][ "magnitude_G" ], earthBodyDistance.au, sunBodyDistance.au )
        print( "Skyfield", name,
               "\n\tAbsolute Magnitude (g from data file):", dataframe.loc[ name ][ "magnitude_H" ],
               "\n\tEarth Body Distance AU:", earthBodyDistance.au,
               "\n\tApparent Magnitude (calculated):", apparentMagnitude,
               "\n" )

    else:
        apparentMagnitude = getApparentMagnitude_HG( dataframe.loc[ name ][ "magnitude_H" ], dataframe.loc[ name ][ "magnitude_G" ], earthBodyDistance.au, sunBodyDistance.au, earthSunDistance.au )

        print( "Skyfield", name,
               "\n\tAbsolute Magnitude (H from data file):", dataframe.loc[ name ][ "magnitude_H" ],
               "\n\tEarth Body Distance AU:", earthBodyDistance.au,
               "\n\tApparent Magnitude (calculated):", apparentMagnitude,
               "\n" )


# https://stackoverflow.com/a/30197797/2156453
def getData( orbitalElementName, orbitalElementData ):
    return next( ( s for s in orbitalElementData if orbitalElementName in s ), None )


# https://www.clearskyinstitute.com/xephem/help/xephem.html#mozTocId564354
def getApparentMagnitude_gk( g_absoluteMagnitude, k_luminosityIndex, bodyEarthDistanceAU, bodySunDistanceAU ):
    return g_absoluteMagnitude + \
           5 * math.log10( bodyEarthDistanceAU ) + \
           2.5 * k_luminosityIndex * math.log10( bodySunDistanceAU )


# Calculate apparent magnitude (returns None on error).
#
# https://www.clearskyinstitute.com/xephem/help/xephem.html#mozTocId564354
# https://www.britastro.org/asteroids/dymock4.pdf
def getApparentMagnitude_HG( H_absoluteMagnitude, G_slope, bodyEarthDistanceAU, bodySunDistanceAU, earthSunDistanceAU ):
    beta = math.acos( \
                        ( bodySunDistanceAU * bodySunDistanceAU + \
                          bodyEarthDistanceAU * bodyEarthDistanceAU - \
                          earthSunDistanceAU * earthSunDistanceAU ) / \
                        ( 2 * bodySunDistanceAU * bodyEarthDistanceAU ) \
                    )

    psi_t = math.exp( math.log( math.tan( beta / 2.0 ) ) * 0.63 )
    Psi_1 = math.exp( -3.33 * psi_t )
    psi_t = math.exp( math.log( math.tan( beta / 2.0 ) ) * 1.22 )
    Psi_2 = math.exp( -1.87 * psi_t )

    # Have found a combination of G_slope, Psi_1 and Psi_2 can lead to a negative value in the log calculation.
    try:
        apparentMagnitude = H_absoluteMagnitude + \
                            5.0 * math.log10( bodySunDistanceAU * bodyEarthDistanceAU ) - \
                            2.5 * math.log10( ( 1 - G_slope ) * Psi_1 + G_slope * Psi_2 )

    except:
        apparentMagnitude = None

    return apparentMagnitude


utcNow = datetime.datetime.strptime( "2020-11-29", "%Y-%m-%d" )
latitude = -33
longitude = 151

print( "PyEphem:", ephem.__version__ )
print( "Skyfield:", skyfield.__version__ )
print()

with open( "Soft03Cmt.txt" ) as f:
    orbitalElementData = f.readlines()
    pyephemCometMinorPlanet( utcNow, latitude, longitude, "88P/Howell", orbitalElementData, True )

with open( "Soft00Cmt.txt" ) as f:
    orbitalElementData = f.readlines()
    skyfieldCometMinorPlanet( utcNow, latitude, longitude, "88P/Howell", orbitalElementData, True )

with open( "Soft03Bright.txt" ) as f:
    orbitalElementData = f.readlines()
    pyephemCometMinorPlanet( utcNow, latitude, longitude, "1 Ceres", orbitalElementData, False )

with open( "Soft00Bright.txt" ) as f:
    orbitalElementData = f.readlines()
    skyfieldCometMinorPlanet( utcNow, latitude, longitude, "(1) Ceres", orbitalElementData, False )