#!/usr/bin/env python3


# Download and save 
#     https://www.minorplanetcenter.net/iau/Ephemerides/Comets/Soft00Cmt.txt
#     https://www.minorplanetcenter.net/iau/Ephemerides/Comets/Soft03Cmt.txt


import datetime, ephem, io, skyfield.api, skyfield.constants, skyfield.data.mpc


def testSkyfield( orbitalElementData, utcNow, latitude, longitude, elevation ):
    timeScale = skyfield.api.load.timescale( builtin = True )
    t = timeScale.utc( utcNow.year, utcNow.month, utcNow.day, utcNow.hour, utcNow.minute, utcNow.second )
    ephemeris = skyfield.api.load( "de421.bsp" )
    sun = ephemeris[ "sun" ]
    earth = ephemeris[ "earth" ]
    topos = skyfield.api.Topos( latitude_degrees = latitude, longitude_degrees = longitude, elevation_m = elevation )
    alt, az, earthSunDistance = ( earth + topos ).at( t ).observe( sun ).apparent().altaz()

    with io.BytesIO() as f:
        for orbitalElement in orbitalElementData:
            f.write( ( orbitalElement + '\n' ).encode() )

        f.seek( 0 )

        dataframe = skyfield.data.mpc.load_comets_dataframe( f ).set_index( "designation", drop = False )

    start = datetime.datetime.utcnow()
    for name, row in dataframe.iterrows():
        try:
            body = sun + skyfield.data.mpc.comet_orbit( dataframe.loc[ name ], timeScale, skyfield.constants.GM_SUN_Pitjeva_2005_km3_s2 )
            ra, dec, earthBodyDistance = ( earth + topos ).at( t ).observe( body ).radec()
            ra, dec, sunBodyDistance = sun.at( t ).observe( body ).radec()

        except Exception as e:
            print( name )
            print( e )
    print( "Skyfield2:", skyfield.__version__, '\n', "Duration:", datetime.datetime.utcnow() - start, '\n' )


def testPyEphem( orbitalElementData, utcNow, latitude, longitude, elevation ):
    observer = ephem.Observer()
    observer.date = ephem.Date( utcNow )
    observer.lat = str( latitude )
    observer.lon = str( longitude )
    observer.elev = elevation

    for line in orbitalElementData:
        if not line.startswith( "#" ): 
            comet = ephem.readdb( line )
            comet.compute( observer )
            sun = ephem.Sun()
            sun.compute( observer )


utcNow = datetime.datetime.strptime( "2020-11-24", "%Y-%m-%d" )

latitude = -33
longitude = 151
elevation = 100

t = datetime.datetime.utcnow()

with open( "Soft00Cmt.txt" ) as f:
    orbitalElementData = f.readlines()

testSkyfield( orbitalElementData, utcNow, latitude, longitude, elevation )
print( "Skyfield:", skyfield.__version__, '\n', "Duration:", datetime.datetime.utcnow() - t, '\n' )

t = datetime.datetime.utcnow()

with open( "Soft03Cmt.txt" ) as f:
    orbitalElementData = f.readlines()

testPyEphem( orbitalElementData, utcNow, latitude, longitude, elevation )
print( "PyEphem:", ephem.__version__, '\n', "Duration:", datetime.datetime.utcnow() - t, '\n' )

# Skyfield: 1.33 
#  Duration: 0:02:03.965268 
# 
# PyEphem: 3.7.6.0 
#  Duration: 0:00:00.002429 

