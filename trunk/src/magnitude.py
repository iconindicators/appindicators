#!/usr/bin/env python3


# https://minorplanetcenter.net/iau/Ephemerides/Comets/Soft03Cmt.txt


import datetime, ephem, io, math, skyfield.api, skyfield.constants, skyfield.data.mpc


now = datetime.datetime.strptime( "2020-07-19", "%Y-%m-%d" )
latitude = -33
longitude = 151

cometName = "88P/Howell"
cometDataPyEphem = "88P/Howell,e,4.3838,56.6855,235.9160,3.105725,0.1800776,0.56432968,347.2821,07/18.0/2020,2000,g 11.0,6.0"
cometDataSkyfield = "0088P         2020 09 26.6245  1.353071  0.564328  235.9161   56.6855    4.3838  20200714  11.0  6.0  88P/Howell                                               MPEC 2019-JE2"

# https://in-the-sky.org/data/object.php?id=0088P
# https://theskylive.com/88p-info
# https://heavens-above.com/comet.aspx?cid=88P&lat=0&lng=0&loc=Unspecified&alt=0&tz=UCT&cul=en


# PyEphem - Comet
ephemNow = ephem.Date( now )

observer = ephem.Observer()
observer.date = ephemNow
observer.lat = latitude
observer.lon = longitude

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
       "\n\tSun-Earth dist:", sun.earth_distance,
       "\n\tEarth dist:", body.earth_distance,
       "\n\tSun dist:", body.sun_distance,
       "\n\tAbs Mag:", body.mag,
       "\n\tApp Mag:", apparentMagnitude )


# Skyfield - Comet
timeScale = skyfield.api.load.timescale( builtin = True )
topos = skyfield.api.Topos( latitude_degrees = latitude, longitude_degrees = longitude )
ephemeris = skyfield.api.load( "de421.bsp" )

with io.BytesIO( cometDataSkyfield.encode() ) as f:
    dataframe = skyfield.data.mpc.load_comets_dataframe( f )

dataframe = dataframe.set_index( "designation", drop = False )
sun = ephemeris[ "sun" ]
earth = ephemeris[ "earth" ]
body = sun + skyfield.data.mpc.comet_orbit( dataframe.loc[ cometName ], timeScale, skyfield.constants.GM_SUN_Pitjeva_2005_km3_s2 )

t = timeScale.utc( now.year, now.month, now.day, now.hour, now.minute, now.second )
alt, az, sunEarthDistance = ( earth + topos ).at( t ).observe( sun ).apparent().altaz()
ra, dec, bodyDistanceToSun = ( sun ).at( t ).observe( body ).radec()
alt, az, bodyDistanceToEarth = ( earth + topos ).at( t ).observe( body ).apparent().altaz()
ra, dec, bodyDistanceToEarth = ( earth + topos ).at( t ).observe( body ).radec()

# https://www.clearskyinstitute.com/xephem/help/xephem.html#mozTocId564354
beta = math.acos( ( bodyDistanceToSun.au * bodyDistanceToSun.au + bodyDistanceToEarth.au * bodyDistanceToEarth.au - sunEarthDistance.au * sunEarthDistance.au ) / ( 2 * bodyDistanceToSun.au * bodyDistanceToEarth.au ) )
psi_t = math.exp( math.log10( math.tan( beta / 2.0 ) ) * 0.63 )
Psi_1 = math.exp( -3.33 * psi_t )
psi_t = math.exp( math.log( math.tan( beta / 2.0 ) ) * 1.22 )
Psi_2 = math.exp( -1.87 * psi_t )
apparentMagnitude = dataframe.loc[ cometName ][ "magnitude_H" ] + 5.0 * math.log10( bodyDistanceToSun.au * bodyDistanceToEarth.au ) - 2.5 * math.log10( ( 1 - dataframe.loc[ cometName ][ "magnitude_G" ] ) * Psi_1 + dataframe.loc[ cometName ][ "magnitude_G" ] * Psi_2 )

print( "Skyfield comet", cometName,
       "\n\tAz:", az.dstr(), 
       "\n\tAlt:", alt.dstr(), 
       "\n\tRA:", ra, 
       "\n\tDec:", dec, 
       "\n\tH:", dataframe.loc[ cometName ][ "magnitude_H" ], 
       "\n\tG:", dataframe.loc[ cometName ][ "magnitude_G" ],
       "\n\tSun-Earth dist:", sunEarthDistance.au,
       "\n\tEarth dist:", bodyDistanceToEarth.au,
       "\n\tSun dist:", bodyDistanceToSun.au,
       "\n\tApp Mag:", apparentMagnitude )