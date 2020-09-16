#!/usr/bin/env python3

import datetime, io, skyfield.api, skyfield.constants, skyfield.data.mpc

print( "Skyfield:", skyfield.__version__ )
latitude = -33
longitude = 151
now = datetime.datetime.strptime( "2020-08-08", "%Y-%m-%d" )
data = "    CK15A020  2015 08  1.8353  5.341055  1.000000  208.8369  258.5042  109.1696            10.5  4.0  C/2015 A2 (PANSTARRS)                                    MPC 93587"
timeScale = skyfield.api.load.timescale( builtin = True )
topos = skyfield.api.Topos( latitude_degrees = latitude, longitude_degrees = longitude )
ephemeris = skyfield.api.load( "de421.bsp" )
sun = ephemeris[ "sun" ]
earth = ephemeris[ "earth" ]
with io.BytesIO( data.encode() ) as f:
    dataframe = skyfield.data.mpc.load_comets_dataframe( f ).set_index( "designation", drop = False )
    body = sun + skyfield.data.mpc.comet_orbit( dataframe.loc[ "C/2015 A2 (PANSTARRS)" ], timeScale, skyfield.constants.GM_SUN_Pitjeva_2005_km3_s2 )
