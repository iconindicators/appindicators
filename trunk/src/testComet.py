#!/usr/bin/env python3


import datetime, io, skyfield.api, skyfield.constants, skyfield.data.mpc


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

        else:
            dataframe = skyfield.data.mpc.load_mpcorb_dataframe( f ).set_index( "designation", drop = False )

            # https://github.com/skyfielders/python-skyfield/issues/449#issuecomment-694159517
            dataframe = dataframe[ ~dataframe.semimajor_axis_au.isnull() ]

#TODO By setting the index above for designation it allows access to the name below in the loop.
# Does this slow things down?  Is there another way to get the name?
#Do we need the name?
    if isComet:
        for name, row in dataframe.iterrows():
            try:
                body = sun + skyfield.data.mpc.comet_orbit( dataframe.loc[ name ], timeScale, skyfield.constants.GM_SUN_Pitjeva_2005_km3_s2 )
                ra, dec, earthBodyDistance = ( earth + topos ).at( t ).observe( body ).radec()
                ra, dec, sunBodyDistance = sun.at( t ).observe( body ).radec()
            except Exception as e:
                print( name )
                print( e )

    else:
        pass#TODO


# Download and save  
# https://minorplanetcenter.net/iau/Ephemerides/Distant/Soft00Distant.txt   FIX THIS!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# and adjust the date to the download date.
utcNow = datetime.datetime.strptime( "2020-11-24", "%Y-%m-%d" )

latitude = -33
longitude = 151
elevation = 100

print( "Skyfield:", skyfield.__version__ )

t = datetime.datetime.utcnow()

with open( "Soft00Cmt.txt" ) as f:
    orbitalElementData = f.readlines()

testSkyfield( orbitalElementData, utcNow, latitude, longitude, elevation, True )
print( "Skyfield comet:", ( datetime.datetime.utcnow() - t ) )