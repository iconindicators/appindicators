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
print( t.utc_jpl() )
topos = skyfield.api.Topos( latitude_degrees = latitude, longitude_degrees = longitude )
ephemeris = skyfield.api.load( "de421.bsp" )
sun = ephemeris[ "sun" ]
earth = ephemeris[ "earth" ]
# source = "Soft00Unusual.txt"
source = "Soft00Distant.txt"
# with open( source ) as f:
#    for line in f:
#        with io.BytesIO( line.encode() ) as f:
#            dataframe = skyfield.data.mpc.load_mpcorb_dataframe( f ).set_index( "designation", drop = False )
#            name = line[ 166 : 194 ].strip()
#            body = sun + skyfield.data.mpc.mpcorb_orbit( dataframe.loc[ name ], timeScale, skyfield.constants.GM_SUN_Pitjeva_2005_km3_s2 )
#            try:
#                ra, dec, sunBodyDistance = sun.at( t ).observe( body ).radec()
#                ra, dec, earthBodyDistance = ( earth + topos ).at( t ).observe( body ).radec()
#            except Exception as e:
#                print( name, e )


#TODO Hit an exception and logged it
# https://github.com/skyfielders/python-skyfield/issues/449
# So need to reproduce (maybe in test code)
# but also see if the suggestion of using the dataframe loaded once makes a difference (may need a new issue logged for that).
data = "K17M07B 14.2   0.15 K1794   0.00140   80.46498   58.25502   55.71379  0.9987471  0.00000466                MPO435133    33   1  174 days 0.34         MPC        0000         2017 MB7"
with io.BytesIO( data.encode() ) as f:
    dataframe = skyfield.data.mpc.load_mpcorb_dataframe( f ).set_index( "designation", drop = False )
    body = sun + skyfield.data.mpc.mpcorb_orbit( dataframe.loc[ "2017 MB7" ], timeScale, skyfield.constants.GM_SUN_Pitjeva_2005_km3_s2 )
    try:
        ra, dec, sunBodyDistance = sun.at( t ).observe( body ).radec()
        ra, dec, earthBodyDistance = ( earth + topos ).at( t ).observe( body ).radec()
    except Exception as e:
        print( e )

               
# /usr/local/lib/python3.6/dist-packages/jplephem/spk.py:227: RuntimeWarning: invalid value encountered in double_scalars
#   index2, offset2 = divmod(tdb2 * S_PER_DAY, intlen)
# 2012 DR30 ephemeris segment only covers dates 1899-07-28 23:59:18Z through 2053-10-08 23:58:51Z UT
# /usr/local/lib/python3.6/dist-packages/jplephem/spk.py:228: RuntimeWarning: invalid value encountered in divmod
#   index3, offset = divmod(offset1 + offset2, intlen)
# 2014 FE72 ephemeris segment only covers dates 1899-07-28 23:59:18Z through 2053-10-08 23:58:51Z UT
# 2015 TG387 ephemeris segment only covers dates 1899-07-28 23:59:18Z through 2053-10-08 23:58:51Z UT
# 2016 FL59 ephemeris segment only covers dates 1899-07-28 23:59:18Z through 2053-10-08 23:58:51Z UT
# 2017 MB7 ephemeris segment only covers dates 1899-07-28 23:59:18Z through 2053-10-08 23:58:51Z UT
#                