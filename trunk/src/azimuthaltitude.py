#!/usr/bin/env python3


# External verification:
# https://in-the-sky.org/data/object.php?id=0088P
# https://theskylive.com/88p-info
# https://heavens-above.com/comet.aspx?cid=88P
# https://www.calsky.com/cs.cgi/Comets/3?


import datetime, ephem, io, skyfield.api, skyfield.constants, skyfield.data.mpc


now = datetime.datetime.strptime( "2020-07-22", "%Y-%m-%d" )
latitude = -33
longitude = 151

cometName = "88P/Howell"

# https://minorplanetcenter.net/iau/Ephemerides/Comets/Soft03Cmt.txt
cometDataPyEphem = "88P/Howell,e,4.3838,56.6855,235.9159,3.105737,0.1800765,0.56433120,347.8225,07/21.0/2020,2000,g 11.0,6.0"

# https://minorplanetcenter.net/iau/Ephemerides/Comets/Soft00Cmt.txt
cometDataSkyfield = "0088P         2020 09 26.6241  1.353073  0.564331  235.9159   56.6855    4.3838  20200721  11.0  6.0  88P/Howell                                               MPEC 2019-JE2"


print( "PyEphem:", ephem.__version__ )
print( "Skyfield:", skyfield.__version__ )


# PyEphem
observer = ephem.Observer()
observer.date = ephem.Date( now )
observer.lat = latitude
observer.lon = longitude

body = ephem.readdb( cometDataPyEphem )
body.compute( observer )

print( "PyEphem comet", cometName,
       "\n\tAz:", body.az,
       "\n\tAlt:", body.alt,
       "\n\tRA:", body.ra,
       "\n\tDec:", body.dec )


# Skyfield
timeScale = skyfield.api.load.timescale( builtin = True )
topos = skyfield.api.Topos( latitude_degrees = latitude, longitude_degrees = longitude )
ephemeris = skyfield.api.load( "de421.bsp" )

with io.BytesIO( cometDataSkyfield.encode() ) as f:
    dataframe = skyfield.data.mpc.load_comets_dataframe( f ).set_index( "designation", drop = False )

sun = ephemeris[ "sun" ]
earth = ephemeris[ "earth" ]
body = sun + skyfield.data.mpc.comet_orbit( dataframe.loc[ cometName ], timeScale, skyfield.constants.GM_SUN_Pitjeva_2005_km3_s2 )

t = timeScale.utc( now.year, now.month, now.day, now.hour, now.minute, now.second )
alt, az, bodyDistanceToEarth = ( earth + topos ).at( t ).observe( body ).apparent().altaz()
ra, dec, bodyDistanceToEarth = ( earth + topos ).at( t ).observe( body ).radec()

print( "Skyfield comet", cometName,
       "\n\tAz:", az, 
       "\n\tAlt:", alt, 
       "\n\tRA:", ra, 
       "\n\tDec:", dec )