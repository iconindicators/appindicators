#!/usr/bin/env python3

import datetime, io, skyfield.api, skyfield.constants, skyfield.data.mpc

print( "Skyfield:", skyfield.__version__ )
latitude = -33
longitude = 151
now = datetime.datetime.strptime( "2020-08-12", "%Y-%m-%d" )
data = "J94T00G  7.0   0.15 J949P   0.00000  353.02318   15.50983    6.76386  0.0000000  0.00358836  42.2543833  E MPC 24084     8   1    3 days              Marsden    0000         1994 TG"
timeScale = skyfield.api.load.timescale( builtin = True )
topos = skyfield.api.Topos( latitude_degrees = latitude, longitude_degrees = longitude )
ephemeris = skyfield.api.load( "de421.bsp" )
sun = ephemeris[ "sun" ]
earth = ephemeris[ "earth" ]
with io.BytesIO( data.encode() ) as f:
    dataframe = skyfield.data.mpc.load_mpcorb_dataframe( f ).set_index( "designation", drop = False )
    body = sun + skyfield.data.mpc.mpcorb_orbit( dataframe.loc[ "1994 TG" ], timeScale, skyfield.constants.GM_SUN_Pitjeva_2005_km3_s2 )
