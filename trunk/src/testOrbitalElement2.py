#!/usr/bin/env python3


# Data sources:
#     https://minorplanetcenter.net/iau/Ephemerides/Distant/Soft00Distant.txt 
#     https://minorplanetcenter.net/iau/Ephemerides/Distant/Soft03Distant.txt
#     https://minorplanetcenter.net/iau/Ephemerides/Unusual/Soft00Unusual.txt
#     https://minorplanetcenter.net/iau/Ephemerides/Unusual/Soft03Unusual.txt


from skyfield.data import mpc

import datetime, ephem, io


def testSkyfield( orbitalElementData, isComet ):
    with io.BytesIO() as f:
        f.write( ( orbitalElementData + '\n' ).encode() )
        f.seek( 0 )

        if isComet:
            dataframe = mpc.load_comets_dataframe( f )

        else:
            dataframe = mpc.load_mpcorb_dataframe( f )

    dataframe = dataframe.set_index( "designation", drop = False )
    for name, row in dataframe.iterrows():
        if isComet:
            return row[ "magnitude_g" ], row[ "magnitude_k" ]

        else: 
            return row[ "magnitude_H" ], row[ "magnitude_G" ]


def testPyEphem( orbitalElementData, utcNow, latitude, longitude, elevation ):
        observer = ephem.Observer()
        observer.date = ephem.Date( utcNow )
        observer.lat = str( latitude )
        observer.lon = str( longitude )
        observer.elev = elevation
        orbitalElement = ephem.readdb( orbitalElementData )
        orbitalElement.compute( observer )
        return orbitalElement._H, orbitalElement._G


pyephemComet = "2010 LG61,e,123.8859,317.3744,352.1688,7.366687,0.0492942,0.81371070,163.4277,04/27.0/2019,2000,H,0.15"
skyfieldComet = "K10L61G             K194R 163.42773  352.16876  317.37443  123.88594  0.8137107  0.04929419   7.3666867  7 MPO460897    17   1   55 days 0.84 M-v 38h MPC        0000         2010 LG61"

pyephemMinorPlanet = "2010 AZ85,e,17.7666,63.7137,265.6580,1.447667,0.5658494,0.00008261,177.0566,01/04.0/2010,2000,H,0.15"
skyfieldMinorPlanet = "K10A85Z             K1014 177.05658  265.65797   63.71372   17.76664  0.0000826  0.56584942   1.4476674  E MPO221139     9   1    1 days 0.47         MPC        0000         2010 AZ85"

utcNow = datetime.datetime.strptime( "2021-03-24", "%Y-%m-%d" ) # Set to the date matching the data files.

latitude = -33
longitude = 151
elevation = 100

# Comet
_H, _G = testPyEphem( pyephemComet, utcNow, latitude, longitude, elevation )
print( _H, _G )

_g, _k = testSkyfield( skyfieldComet, True )
print( _g, _k )

# Minor Planet
_H, _G = testPyEphem( pyephemMinorPlanet, utcNow, latitude, longitude, elevation )
print( _H, _G )

_H, _G = testSkyfield( skyfieldMinorPlanet, False )
print( _H, _G )