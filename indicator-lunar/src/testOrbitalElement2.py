#!/usr/bin/env python3


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

        if isinstance( orbitalElement, ephem.EllipticalBody ):
            lastComma = orbitalElementData.rindex( "," )
            secondLastComma = orbitalElementData[ : lastComma ].rindex( "," )
            field12 = orbitalElementData[ secondLastComma + 1 : lastComma ]
            if field12.startswith( 'g' ):
                return orbitalElement._g, orbitalElement._k

            else:
                return orbitalElement._H, orbitalElement._G

        else: # Assume HyperbolicBody ParabolicBody
            return orbitalElement._g, orbitalElement._k


utcNow = datetime.datetime.strptime( "2021-03-24", "%Y-%m-%d" ) # Set to the date matching the data files.

latitude = -33
longitude = 151
elevation = 100


# Test PyEphem comets and minor planets...
#
# Data format:
#     http://www.clearskyinstitute.com/xephem/help/xephem.html#mozTocId215848
#
# Comets data source:
#     https://www.minorplanetcenter.net/iau/Ephemerides/Comets/Soft03Cmt.txt
#
# Minor Planets data source:
#     https://minorplanetcenter.net/iau/Ephemerides/Distant/Soft03Distant.txt
#
# Field 2 = e => field 12 = g or H, field 13 = k or G, specified by a leading g or H in field 12 (no g or H implies H). 
pyephemComet = "413P/Larson,e,15.9772,39.0258,186.0334,3.711010,0.1378687,0.42336952,343.5677,03/23.0/2021,2000,g 14.0,4.0" 
_Hg, _Gk = testPyEphem( pyephemComet, utcNow, latitude, longitude, elevation )
print( _Hg, _Gk )

# Field 2 = h => field 10 = g, field 11 = k
pyephemComet = "C/2015 D3 (PANSTARRS),h,05/02.3218/2016,128.5493,157.0632,2.9458,1.003528,8.142955,2000,5.5,4.0"
_g, _k = testPyEphem( pyephemComet, utcNow, latitude, longitude, elevation )
print( _g, _k )

# Field 2 = p => field 9 = g, field 10 = k
pyephemComet = "C/2018 F3 (Johnson),p,08/15.2314/2017,105.5348,293.0113,2.483172,173.0311,2000,13.0,4.0"
_g, _k = testPyEphem( pyephemComet, utcNow, latitude, longitude, elevation )
print( _g, _k )

# Field 2 = e => field 12 = g or H, field 13 = k or G, specified by a leading g or H in field 12 (no g or H implies H). 
pyephemMinorPlanet = "2010 LG61,e,123.8859,317.3744,352.1688,7.366687,0.0492942,0.81371070,163.4277,04/27.0/2019,2000,H,0.15"
_Hg, _Gk = testPyEphem( pyephemMinorPlanet, utcNow, latitude, longitude, elevation )
print( _Hg, _Gk )  # INCORRECT: There is no value defined in the data for H.


# Test Skyfield minor planets...
#
# Minor Planets data source:
#     https://minorplanetcenter.net/iau/Ephemerides/Distant/Soft00Distant.txt
#
skyfieldMinorPlanet = "K10L61G             K194R 163.42773  352.16876  317.37443  123.88594  0.8137107  0.04929419   7.3666867  7 MPO460897    17   1   55 days 0.84 M-v 38h MPC        0000         2010 LG61"
_H, _G = testSkyfield( skyfieldMinorPlanet, False )
print( _H, _G )