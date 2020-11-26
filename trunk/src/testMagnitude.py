#!/usr/bin/env python3


# External verification:
# https://in-the-sky.org/data/object.php?id=0088P
# https://theskylive.com/88p-info
# https://heavens-above.com/comet.aspx?cid=88P
# https://www.calsky.com/cs.cgi/Comets/3?


import datetime, ephem, io, math, skyfield.api, skyfield.constants, skyfield.data.mpc


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
        apparentMagnitude = calculateApparentMagnitude_gk( body._g, body._k, body.earth_distance, body.sun_distance )
        print( "PyEphem", name,
               "\n\tMagnitude (from PyEphem):", body.mag,
               "\n\tEarth Body Disance AU:", body.earth_distance,
               "\n\tApparent Magnitude (calculated):", apparentMagnitude )

    else:
        apparentMagnitude = calculateApparentMagnitude_HG( body._H, body._G, body.earth_distance, body.sun_distance, sun.earth_distance )
        print( "PyEphem", name,
               "\n\tMagnitude (from PyEphem):", body.mag,
               "\n\tAbsolute Magnitude (H from data file):", body._H,
               "\n\tEarth Body Disance AU:", body.earth_distance,
               "\n\tApparent Magnitude (calculated):", apparentMagnitude )


def skyfieldCometMinorPlanet( now, latitude, longitude, name, data, isComet ):
    timeScale = skyfield.api.load.timescale( builtin = True )
    topos = skyfield.api.Topos( latitude_degrees = latitude, longitude_degrees = longitude )
    ephemeris = skyfield.api.load( "de421.bsp" )
    sun = ephemeris[ "sun" ]
    earth = ephemeris[ "earth" ]

    with io.BytesIO( data.encode() ) as f:
        if isComet:
            dataframe = skyfield.data.mpc.load_comets_dataframe( f ).set_index( "designation", drop = False )
            body = sun + skyfield.data.mpc.comet_orbit( dataframe.loc[ name ], timeScale, skyfield.constants.GM_SUN_Pitjeva_2005_km3_s2 )

        else:
            dataframe = skyfield.data.mpc.load_mpcorb_dataframe( f ).set_index( "designation", drop = False )
            body = sun + skyfield.data.mpc.mpcorb_orbit( dataframe.loc[ name ], timeScale, skyfield.constants.GM_SUN_Pitjeva_2005_km3_s2 )

    t = timeScale.utc( now.year, now.month, now.day, now.hour, now.minute, now.second )
    alt, az, earthSunDistance = ( earth + topos ).at( t ).observe( sun ).apparent().altaz()
    ra, dec, sunBodyDistance = ( sun ).at( t ).observe( body ).radec()
    alt, az, earthBodyDistance = ( earth + topos ).at( t ).observe( body ).apparent().altaz()
    ra, dec, earthBodyDistance = ( earth + topos ).at( t ).observe( body ).radec()

    apparentMagnitude = calculateApparentMagnitude_HG( dataframe.loc[ name ][ "magnitude_H" ], dataframe.loc[ name ][ "magnitude_G" ], earthBodyDistance.au, sunBodyDistance.au, earthSunDistance.au )

    print( "Skyfield", name,
           "\n\tAbsolute Magnitude (H from data file):", dataframe.loc[ name ][ "magnitude_H" ],
           "\n\tEarth Body Distance AU:", earthBodyDistance.au,
           "\n\tApparent Magnitude (calculated):", apparentMagnitude )


# https://www.clearskyinstitute.com/xephem/help/xephem.html#mozTocId564354
def calculateApparentMagnitude_gk( g_absoluteMagnitude, k_luminosityIndex, bodyEarthDistance, bodySunDistance ):
    return g_absoluteMagnitude + 5 * math.log10( bodyEarthDistance ) + 2.5 * k_luminosityIndex * math.log10( bodySunDistance )


# https://www.clearskyinstitute.com/xephem/help/xephem.html#mozTocId564354
# https://www.britastro.org/asteroids/dymock4.pdf
def calculateApparentMagnitude_HG( H_absoluteMagnitude, G_slope, bodyEarthDistance, bodySunDistance, earthSunDistance ):
    beta = math.acos( ( bodySunDistance * bodySunDistance + bodyEarthDistance * bodyEarthDistance - earthSunDistance * earthSunDistance ) / ( 2 * bodySunDistance * bodyEarthDistance ) )
    psi_t = math.exp( math.log( math.tan( beta / 2.0 ) ) * 0.63 )
    Psi_1 = math.exp( -3.33 * psi_t )
    psi_t = math.exp( math.log( math.tan( beta / 2.0 ) ) * 1.22 )
    Psi_2 = math.exp( -1.87 * psi_t )
    return H_absoluteMagnitude + 5.0 * math.log10( bodySunDistance * bodyEarthDistance ) - 2.5 * math.log10( ( 1 - G_slope ) * Psi_1 + G_slope * Psi_2 )


now = datetime.datetime.strptime( "2020-11-26", "%Y-%m-%d" )
latitude = -33
longitude = 151

cometName = "88P/Howell"

# https://minorplanetcenter.net/iau/Ephemerides/Comets/Soft03Cmt.txt
cometDataPyEphem = "88P/Howell,e,4.3836,56.6820,235.9074,3.105705,0.1800793,0.56432890,10.6951,11/25.0/2020,2000,g 11.0,6.0"

# Format: https://minorplanetcenter.net/iau/info/CometOrbitFormat.html
# https://minorplanetcenter.net/iau/Ephemerides/Comets/Soft00Cmt.txt
cometDataSkyfield = "0088P         2020 09 26.6087  1.353066  0.564329  235.9074   56.6820    4.3836  20201125  11.0  6.0  88P/Howell                                               MPEC 2019-JE2"

minorPlanetName = "(1) Ceres"

# https://minorplanetcenter.net/iau/Ephemerides/Bright/2018/Soft03Bright.txt
minorPlanetDataPyEphem = "1 Ceres,e,10.5935,80.3099,73.1153,2.767046,0.2141309,0.07553468,352.2305,03/23.0/2018,2000,H 3.34,0.12"

# Format: https://minorplanetcenter.net/iau/info/MPOrbitFormat.html
# https://minorplanetcenter.net/iau/Ephemerides/Bright/2018/Soft00Bright.txt
minorPlanetDataSkyfield = "00001    3.34  0.12 K183N 352.23052   73.11528   80.30992   10.59351  0.0755347  0.21413094   2.7670463  0 MPO431490  6689 114 1801-2018 0.60 M-v 30h MPC        0000              (1) Ceres"

print( "PyEphem:", ephem.__version__ )
print( "Skyfield:", skyfield.__version__ )

pyephemCometMinorPlanet( now, latitude, longitude, cometName, cometDataPyEphem, True )
skyfieldCometMinorPlanet( now, latitude, longitude, cometName, cometDataSkyfield, True )
pyephemCometMinorPlanet( now, latitude, longitude, minorPlanetName, minorPlanetDataPyEphem, False )
skyfieldCometMinorPlanet( now, latitude, longitude, minorPlanetName, minorPlanetDataSkyfield, False )