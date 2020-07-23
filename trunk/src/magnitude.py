#!/usr/bin/env python3


# External verification:
# https://in-the-sky.org/data/object.php?id=0088P
# https://theskylive.com/88p-info
# https://heavens-above.com/comet.aspx?cid=88P
# https://www.calsky.com/cs.cgi/Comets/3?


import datetime, ephem, io, math, skyfield.api, skyfield.constants, skyfield.data.mpc


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


# PyEphem - Comet
observer = ephem.Observer()
observer.date = ephem.Date( now )
observer.lat = str( latitude )
observer.lon = str( longitude )

body = ephem.readdb( cometDataPyEphem )
body.compute( observer )

# https://www.clearskyinstitute.com/xephem/help/xephem.html#mozTocId564354
apparentMagnitude = body._g + 5 * math.log10( body.earth_distance ) + 2.5 * body._k * math.log10( body.sun_distance )

sun = ephem.Sun()
sun.compute( observer )

print( "PyEphem comet", cometName,
       "\n\tAz:", body.az,
       "\n\tAlt:", body.alt,
       "\n\tRA:", body.ra,
       "\n\tDec:", body.dec,
       "\n\tg:", body._g,
       "\n\tk:", body._k,
       "\n\tEarth-Sun dist:", sun.earth_distance,
       "\n\tEarth-Body dist:", body.earth_distance,
       "\n\tSun-Body dist:", body.sun_distance,
       "\n\tAbs Mag:", body.mag,
       "\n\tApp Mag:", apparentMagnitude )


# PyEphem - Comet / Minor Planet
def pyephemCometMinorPlanet( now, latitude, longitude, name, data, isComet ):
    observer = ephem.Observer()
    observer.date = ephem.Date( now )
    observer.lat = str( latitude )
    observer.lon = str( longitude )

    body = ephem.readdb( data )
    body.compute( observer )

    # https://www.clearskyinstitute.com/xephem/help/xephem.html#mozTocId564354
    apparentMagnitude = body._g + 5 * math.log10( body.earth_distance ) + 2.5 * body._k * math.log10( body.sun_distance )

    sun = ephem.Sun()
    sun.compute( observer )

    print( "PyEphem", name,
           "\n\tAz:", body.az,
           "\n\tAlt:", body.alt,
           "\n\tRA:", body.ra,
           "\n\tDec:", body.dec,
           "\n\tg:", body._g,
           "\n\tk:", body._k,
           "\n\tEarth-Sun dist:", sun.earth_distance,
           "\n\tEarth-Body dist:", body.earth_distance,
           "\n\tSun-Body dist:", body.sun_distance,
           "\n\tAbs Mag:", body.mag,
           "\n\tApp Mag:", apparentMagnitude )


# Skyfield - Comet
timeScale = skyfield.api.load.timescale( builtin = True )
topos = skyfield.api.Topos( latitude_degrees = latitude, longitude_degrees = longitude )
ephemeris = skyfield.api.load( "de421.bsp" )

with io.BytesIO( cometDataSkyfield.encode() ) as f:
    dataframe = skyfield.data.mpc.load_comets_dataframe( f ).set_index( "designation", drop = False )

sun = ephemeris[ "sun" ]
earth = ephemeris[ "earth" ]
body = sun + skyfield.data.mpc.comet_orbit( dataframe.loc[ cometName ], timeScale, skyfield.constants.GM_SUN_Pitjeva_2005_km3_s2 )

t = timeScale.utc( now.year, now.month, now.day, now.hour, now.minute, now.second )
alt, az, earthSunDistance = ( earth + topos ).at( t ).observe( sun ).apparent().altaz()
ra, dec, sunBodyDistance = ( sun ).at( t ).observe( body ).radec()
alt, az, earthBodyDistance = ( earth + topos ).at( t ).observe( body ).apparent().altaz()
ra, dec, earthBodyDistance = ( earth + topos ).at( t ).observe( body ).radec()

# https://www.clearskyinstitute.com/xephem/help/xephem.html#mozTocId564354
beta = math.acos( ( sunBodyDistance.au * sunBodyDistance.au + earthBodyDistance.au * earthBodyDistance.au - earthSunDistance.au * earthSunDistance.au ) / ( 2 * sunBodyDistance.au * earthBodyDistance.au ) )
psi_t = math.exp( math.log10( math.tan( beta / 2.0 ) ) * 0.63 )
Psi_1 = math.exp( -3.33 * psi_t )
psi_t = math.exp( math.log( math.tan( beta / 2.0 ) ) * 1.22 )
Psi_2 = math.exp( -1.87 * psi_t )
apparentMagnitude = dataframe.loc[ cometName ][ "magnitude_H" ] + 5.0 * math.log10( sunBodyDistance.au * earthBodyDistance.au ) - 2.5 * math.log10( ( 1 - dataframe.loc[ cometName ][ "magnitude_G" ] ) * Psi_1 + dataframe.loc[ cometName ][ "magnitude_G" ] * Psi_2 )

print( "Skyfield comet", cometName,
       "\n\tAz:", az.dstr(), 
       "\n\tAlt:", alt.dstr(), 
       "\n\tRA:", ra, 
       "\n\tDec:", dec, 
       "\n\tH:", dataframe.loc[ cometName ][ "magnitude_H" ], 
       "\n\tG:", dataframe.loc[ cometName ][ "magnitude_G" ],
       "\n\tEarth-Sun dist:", earthSunDistance.au,
       "\n\tEarth-Body dist:", earthBodyDistance.au,
       "\n\tSun-Body dist:", sunBodyDistance.au,
       "\n\tApp Mag:", apparentMagnitude )