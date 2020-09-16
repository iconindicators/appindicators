#!/usr/bin/env python3

import datetime, io, skyfield.api, skyfield.constants, skyfield.data.mpc

print( "Skyfield:", skyfield.__version__ )

# Download and save  
# https://minorplanetcenter.net/iau/Ephemerides/Distant/Soft00Distant.txt
# and adjust the date to the download date.
now = datetime.datetime.strptime( "2020-09-16", "%Y-%m-%d" )

latitude = -33
longitude = 151
timeScale = skyfield.api.load.timescale( builtin = True )
t = timeScale.utc( now.year, now.month, now.day, now.hour, now.minute, now.second )
topos = skyfield.api.Topos( latitude_degrees = latitude, longitude_degrees = longitude )
ephemeris = skyfield.api.load( "de421.bsp" )
sun = ephemeris[ "sun" ]
earth = ephemeris[ "earth" ]
with open( "Soft00Distant.txt" ) as f:
   for line in f:
       with io.BytesIO( line.encode() ) as f:
           dataframe = skyfield.data.mpc.load_mpcorb_dataframe( f ).set_index( "designation", drop = False )
           name = line[ 166 : 194 ].strip()
           if "2012 DR30" in name:
               body = sun + skyfield.data.mpc.mpcorb_orbit( dataframe.loc[ name ], timeScale, skyfield.constants.GM_SUN_Pitjeva_2005_km3_s2 )
               print( name )
               ra, dec, sunBodyDistance = sun.at( t ).observe( body ).radec()
               ra, dec, earthBodyDistance = ( earth + topos ).at( t ).observe( body ).radec()