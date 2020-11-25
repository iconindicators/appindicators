#!/usr/bin/env python3


# Download and save 
#     https://www.minorplanetcenter.net/iau/Ephemerides/Comets/Soft00Cmt.txt
#     https://www.minorplanetcenter.net/iau/Ephemerides/Comets/Soft03Cmt.txt
#     https://www.minorplanetcenter.net/iau/Ephemerides/Bright/2018/Soft00Bright.txt
#     https://www.minorplanetcenter.net/iau/Ephemerides/Bright/2018/Soft03Bright.txt


import datetime, ephem, importlib, io, skyfield.api, skyfield.constants, skyfield.data.mpc


def testSkyfield( orbitalElementData, utcNow, latitude, longitude, elevation, isComet ):
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

        if isComet:
            dataframe = skyfield.data.mpc.load_comets_dataframe( f ).set_index( "designation", drop = False )
            orbitCalculationFunction = "comet_orbit"

        else:
            dataframe = skyfield.data.mpc.load_mpcorb_dataframe( f ).set_index( "designation", drop = False )
            orbitCalculationFunction = "mpcorb_orbit"

            # Remove bad data: https://github.com/skyfielders/python-skyfield/issues/449#issuecomment-694159517
            dataframe = dataframe[ ~dataframe.semimajor_axis_au.isnull() ]

    for name, row in dataframe.iterrows():
        body = sun + getattr( importlib.import_module( "skyfield.data.mpc" ), orbitCalculationFunction )( row, timeScale, skyfield.constants.GM_SUN_Pitjeva_2005_km3_s2 )
        ra, dec, earthBodyDistance = ( earth + topos ).at( t ).observe( body ).radec()
        ra, dec, sunBodyDistance = sun.at( t ).observe( body ).radec()


def testPyEphem( orbitalElementData, utcNow, latitude, longitude, elevation ):
    for line in orbitalElementData:
        if not line.startswith( "#" ):
            observer = ephem.Observer() # Not sure if the observer should be reset on each run or not...
            observer.date = ephem.Date( utcNow )
            observer.lat = str( latitude )
            observer.lon = str( longitude )
            observer.elev = elevation
            comet = ephem.readdb( line )
            comet.compute( observer )


utcNow = datetime.datetime.strptime( "2020-11-24", "%Y-%m-%d" ) # Set to the date of the data files.

latitude = -33
longitude = 151
elevation = 100


# Skyfield COMET
t = datetime.datetime.utcnow()
 
with open( "Soft00Cmt.txt" ) as f:
    orbitalElementData = f.readlines()
 
testSkyfield( orbitalElementData, utcNow, latitude, longitude, elevation, isComet = True )
print( "Skyfield COMET:", skyfield.__version__, '\n', "Duration:", datetime.datetime.utcnow() - t, '\n' )
 
 
# PyEphem COMET
t = datetime.datetime.utcnow()
 
with open( "Soft03Cmt.txt" ) as f:
    orbitalElementData = f.readlines()
 
testPyEphem( orbitalElementData, utcNow, latitude, longitude, elevation )
print( "PyEphem COMET:", ephem.__version__, '\n', "Duration:", datetime.datetime.utcnow() - t, '\n' )


# Skyfield MINOR PLANET
t = datetime.datetime.utcnow()

with open( "Soft00Bright.txt" ) as f:
    orbitalElementData = f.readlines()

testSkyfield( orbitalElementData, utcNow, latitude, longitude, elevation, isComet = False )
print( "Skyfield MINOR PLANET:", skyfield.__version__, '\n', "Duration:", datetime.datetime.utcnow() - t, '\n' )


# PyEphem MINOR PLANET
t = datetime.datetime.utcnow()

with open( "Soft03Bright.txt" ) as f:
    orbitalElementData = f.readlines()

testPyEphem( orbitalElementData, utcNow, latitude, longitude, elevation )
print( "PyEphem MINOR PLANET:", ephem.__version__, '\n', "Duration:", datetime.datetime.utcnow() - t, '\n' )