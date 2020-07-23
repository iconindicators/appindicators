#!/usr/bin/env python3


# External verification:
# https://in-the-sky.org/data/object.php?id=0088P
# https://theskylive.com/88p-info
# https://heavens-above.com/comet.aspx?cid=88P
# https://www.calsky.com/cs.cgi/Comets/3?


import datetime, ephem, io, math, skyfield.api, skyfield.constants, skyfield.data.mpc


# PyEphem - Comet / Minor Planet
def pyephemCometMinorPlanet( now, latitude, longitude, name, data, isComet ):
    observer = ephem.Observer()
    observer.date = ephem.Date( now )
    observer.lat = str( latitude )
    observer.lon = str( longitude )

    body = ephem.readdb( data )
    body.compute( observer )

    sun = ephem.Sun()
    sun.compute( observer )

    if isComet:
        apparentMagnitude = getApparentMagnitude_gk( body._g, body._k, body.earth_distance, body.sun_distance )

    else:
        apparentMagnitude = getApparentMagnitude_GH( body._G, body._H, body.earth_distance, body.sun_distance, sun.earth_distance )

    print( "PyEphem", name,
           "\n\tAz:", body.az,
           "\n\tAlt:", body.alt,
           "\n\tRA:", body.ra,
           "\n\tDec:", body.dec,
           "\n\tEarth-Sun dist:", sun.earth_distance,
           "\n\tEarth-Body dist:", body.earth_distance,
           "\n\tSun-Body dist:", body.sun_distance,
           "\n\tAbs Mag:", body.mag,
           "\n\tApp Mag:", apparentMagnitude )


# Skyfield - Comet / Minor Planet
def skyfieldCometMinorPlanet( now, latitude, longitude, name, data, isComet ):
    timeScale = skyfield.api.load.timescale( builtin = True )
    topos = skyfield.api.Topos( latitude_degrees = latitude, longitude_degrees = longitude )
    ephemeris = skyfield.api.load( "de421.bsp" )

    sun = ephemeris[ "sun" ]
    earth = ephemeris[ "earth" ]

    if isComet:
        with io.BytesIO( data.encode() ) as f:
            dataframe = skyfield.data.mpc.load_comets_dataframe( f ).set_index( "designation", drop = False )

        body = sun + skyfield.data.mpc.comet_orbit( dataframe.loc[ name ], timeScale, skyfield.constants.GM_SUN_Pitjeva_2005_km3_s2 )

    else:
        with io.BytesIO( data.encode() ) as f:
            dataframe = skyfield.data.mpc.load_mpcorb_dataframe( f ).set_index( "designation", drop = False )

        body = sun + skyfield.data.mpc.mpcorb_orbit( dataframe.loc[ name ], timeScale, skyfield.constants.GM_SUN_Pitjeva_2005_km3_s2 )

    t = timeScale.utc( now.year, now.month, now.day, now.hour, now.minute, now.second )
    alt, az, earthSunDistance = ( earth + topos ).at( t ).observe( sun ).apparent().altaz()
    ra, dec, sunBodyDistance = ( sun ).at( t ).observe( body ).radec()
    alt, az, earthBodyDistance = ( earth + topos ).at( t ).observe( body ).apparent().altaz()
    ra, dec, earthBodyDistance = ( earth + topos ).at( t ).observe( body ).radec()

    apparentMagnitude = getApparentMagnitude_GH( dataframe.loc[ name ][ "magnitude_G" ], dataframe.loc[ name ][ "magnitude_H" ], earthBodyDistance.au, sunBodyDistance.au, earthSunDistance.au )

    print( "Skyfield", name,
           "\n\tAz:", az.dstr(),
           "\n\tAlt:", alt.dstr(),
           "\n\tRA:", ra,
           "\n\tDec:", dec,
           "\n\tEarth-Sun dist:", earthSunDistance.au,
           "\n\tEarth-Body dist:", earthBodyDistance.au,
           "\n\tSun-Body dist:", sunBodyDistance.au,
           "\n\tAbs Mag:", dataframe.loc[ name ][ "magnitude_H" ],
           "\n\tApp Mag:", apparentMagnitude )


# https://www.clearskyinstitute.com/xephem/help/xephem.html#mozTocId564354
def getApparentMagnitude_gk( g_absoluteMagnitude, k_luminosityIndex, bodyEarthDistance, bodySunDistance ):
    return g_absoluteMagnitude + 5 * math.log10( bodyEarthDistance ) + 2.5 * k_luminosityIndex * math.log10( bodySunDistance )


# https://www.clearskyinstitute.com/xephem/help/xephem.html#mozTocId564354
def getApparentMagnitude_GH( G_slope, H_absoluteMagnitude, bodyEarthDistance, bodySunDistance, earthSunDistance ):
    beta = math.acos( ( bodySunDistance * bodySunDistance + bodyEarthDistance * bodyEarthDistance - earthSunDistance * earthSunDistance ) / ( 2 * bodySunDistance * bodyEarthDistance ) )
    psi_t = math.exp( math.log10( math.tan( beta / 2.0 ) ) * 0.63 )
    Psi_1 = math.exp( -3.33 * psi_t )
    psi_t = math.exp( math.log( math.tan( beta / 2.0 ) ) * 1.22 )
    Psi_2 = math.exp( -1.87 * psi_t )
    return H_absoluteMagnitude + 5.0 * math.log10( bodySunDistance * bodyEarthDistance ) - 2.5 * math.log10( ( 1 - G_slope ) * Psi_1 + G_slope * Psi_2 )


now = datetime.datetime.strptime( "2020-07-23", "%Y-%m-%d" )
latitude = -33
longitude = 151

cometName = "88P/Howell"

# https://minorplanetcenter.net/iau/Ephemerides/Comets/Soft03Cmt.txt
cometDataPyEphem = "88P/Howell,e,4.3838,56.6855,235.9159,3.105737,0.1800765,0.56433120,347.8225,07/21.0/2020,2000,g 11.0,6.0"

# https://minorplanetcenter.net/iau/Ephemerides/Comets/Soft00Cmt.txt
cometDataSkyfield = "0088P         2020 09 26.6241  1.353073  0.564331  235.9159   56.6855    4.3838  20200721  11.0  6.0  88P/Howell                                               MPEC 2019-JE2"

minorPlanetName = "(1) Ceres"

# https://minorplanetcenter.net/iau/Ephemerides/Bright/2018/Soft03Bright.txt
minorPlanetDataPyEphem = "1 Ceres,e,10.5935,80.3099,73.1153,2.767046,0.2141309,0.07553468,352.2305,03/23.0/2018,2000,H 3.34,0.12"

# https://minorplanetcenter.net/iau/Ephemerides/Bright/2018/Soft00Bright.txt
minorPlanetDataSkyfield = "00001    3.34  0.12 K183N 352.23052   73.11528   80.30992   10.59351  0.0755347  0.21413094   2.7670463  0 MPO431490  6689 114 1801-2018 0.60 M-v 30h MPC        0000              (1) Ceres"

print( "PyEphem:", ephem.__version__ )
print( "Skyfield:", skyfield.__version__ )

pyephemCometMinorPlanet( now, latitude, longitude, cometName, cometDataPyEphem, True )
skyfieldCometMinorPlanet( now, latitude, longitude, cometName, cometDataSkyfield, True )
pyephemCometMinorPlanet( now, latitude, longitude, minorPlanetName, minorPlanetDataPyEphem, False )
skyfieldCometMinorPlanet( now, latitude, longitude, minorPlanetName, minorPlanetDataSkyfield, False )