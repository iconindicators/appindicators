#!/usr/bin/env python3
# -*- coding: utf-8 -*-


#TODO Is it possible/feasible to list meteor showers?
# Daniel Franklin
# git@danielfranklin.id.au
# https://github.com/dfranklinau/astronote/blob/master/astronote/celestial.py
# Contacted Daniel; he hard coded meteor showers and has no other data.
#
# https://www.ta3.sk/IAUC22DB/MDC2022/
# https://www.ta3.sk/IAUC22DB/MDC2022/Roje/roje_lista.php?corobic_roje=1&sort_roje=0
# On a quick look, the data from ta3 above could be an ephemeris and be used to compute rise/set/az/alt.
# Issue is visibility...without a magnitude, how to determine if the shower is within range to be visible?
# Contacted maria.hajdukova@savba.sk and waiting to hear back.
#
# Contacted regina.rudawska@esa.int and waiting to hear back.
# Reply from Regina:
#    The IAU MDC is complete list of known showers. 
#    The data provided there is delivered to MDC by authors and present the mean solutions of each shower. 
#    If you are interested in meteor showers predictions, 
#    then you might have a look International Meteor Organization page
#    where they annually publish calendar: https://www.imo.net/resources/calendar.
#
# Maybe also contact
#   https://www.imo.net/members/imo_showers/working_shower_list
# as I may be able to use that data for predictions.
#
# From MPC, formats
#   https://www.minorplanetcenter.net/iau/info/MPOrbitFormat.html
#   https://www.minorplanetcenter.net/iau/info/CometOrbitFormat.html
#
# PyEphem (reading MPC catalog and/or stars)
#   https://rhodesmill.org/pyephem/quick.html
#   https://rhodesmill.org/pyephem/tutorial.html
#
# PyEphem Stars
#  /usr/local/lib/python3.8/dist_packages/ephem/stars.py
# Probably cannot use stars as per the format,
# 'f' is the second field meaning fixed,
# which meteor showers are not.
# Likely need e, h or p.


'''
:====================================================
: All records on J2000, velocities are VG    =
:===========================================================================================================================================
:IAU Meteor Data Center. Established meteor showers. V.2 
:===========================================================================================================================================
: Last update: September 27, 20:00:00 UTC, 2022  Modified by R. Rudawska, M. Hajdukova and T.J.Jopek         (97 comment lines)
:              DATA VALIDATION !!! bracket ' [ '  in the column ??? means that The data has been checked
:              Notice! List of shower group was remowed, their members are in the MDC 
:              The AdNo were modified when it was neccassary  (2022.05.10)
:              New status flags are implemented !! (2022.05.17) 
:              New parameters have been added: ecliptic coordinates of the radiant, sun-centered and Oepic theta and phi angles
:
: === Notes on proper citation of the MDC database.
:
:       Since its beginning (AD 2007), the IAM MDC shower database is maintained on an unpaid voluntary basis.
:       Several colleagues have asked us what reference to the shower database they should include in a published paper?
:       The correct references are:
:
:      Jenniskens, P.; Jopek, T.J.; Janches, D.; Hajdukov�. M.; Kokhirova, G.I.; Rudawska, R; 2020,
:          Planetary and Space Science, Vol. 182, article id. 104821
:
:      Jopek, T.J.; Kanuchova, Z.; 2017, Planetary and Space Science, Volume 143, p. 3-6
:
:      Jopek, T.J.; Kanuchova, Z.; 2014, in The Meteoroids 2013, Proceedings of the Astronomical Conference held at A.M. University,
:          Poznan, Poland, Aug. 26-30, 2013, Eds.: T.J. Jopek, F.J.M. Rietmeijer, J. Watanabe, I.P. Williams,
:          A.M. University Press, 2014, p. 353-364
:
:      Jopek, T.J.; Jenniskens, P.M.; in Meteoroids: The Smallest Solar System Bodies, Proceedings of the Meteroids Conference 
:          held in Breckenridge, Colorado, USA, May 24-28, 2010. Edited by W.J. Cooke, D.E. Moser, B.F. Hardin, and D. Janches,
:         NASA/CP-2011-216469., p. 7-13
:
:===========================================================================================================================================
:
:LP    - running number in the streamfulldata.txt file
:IAUNo - IAU numeral code
:AdNo  - for given shower - number of a set of parameters
:Code  - IAU 3 letter code
:s     - shower status flags:
:     -9 removed from the MDC - data not published
:     -8 no Look up table
:     -7 various faults: typo ... suspicious ...
:     -6 criterion R3; the shower has been found to be unreliable.
:     -5 not used yet
:     -4 criterion R2; duplicate, shower designation was changed; the data was added as another solution to the previously known stream 
:     -3 criterion R4; N < 3; only 1 or 2 members 
:     -2 criterion R1; lack, wrong or problems with references 
:     -1 to be removed from the list of established showers
:      0 single shower, working list  
:      1 single established shower, 
:      2 to be established shower
:  
:sho. des.   - shower designation (provisional name)
:shower name -  shower final name according to meteor shower nomenclature rules 
:activity - type of activity:  
:           annual
:           1965     - shower was active only in 1965,
:           1989/12  - observed in Dec.,
:           1989out  - shower outburst, 
:           variable - 
:           irr.     - irregular activity
:
:LoSb, LaSe - ecliptic longitude of the Sun at the beginning and the end of the shower activity
:LoS   - averaged ecliptic longitude of the Sun at the shower activity, (J2000,deg),
:Ra    - right asscention of the shower radiant (J2000, deg),
:De    - declination of the shower radiant (J2000, deg),
:dRa   - radiant daily motion in right asscention,
:dDe   - radiant daily motion in declination,
:Vg    - geocentric velocity (Km/sec),
:LoR   - ecliptic longitude of the shower radiant (J2000, deg),
:S_LoR - Sun centered ecliptic longitude of the shower radiant (deg),
:LaR   - ecliptic latitude of the radiant (J2000, deg),
:theta - Opik variable (deg) (see Froeschle, Valsecchi and Jopek, 1999, Cellestial Mechanics and Dynamical Astronomy, 73, 55-69),
:phi   - Opik variable (deg)  -,-
:Flags - flags indicating:
:232   - B if the epoch is B1950    (R - data transformed to J2000)
:233   - I if the Vinf is given     (R - Vinf transformed to VG)
:234   - A, M if the arithmetic mean, median values are given for the shower parameters
:235   - sparse
:236   - sparse 
:237   - Origin of a shower: 1/0  yes/no, space - not known 
:238   - Assessment of Reliability: space - not known, 0 - no assessment; 1- yes ... 
:a     - semimajor axis (AU),
:q     - perihelion distance (AU),
:e     - eccentricity,
:peri  - argument of perihelion (J2000, deg),
:node  - longitude of ascending node (J2000, deg),
:incl  - inclination of the orbit (J2000, deg),
:N     - number of members of the identified stream,
:Group - sparse   IAU numerical code of the main complex group,
:CG    - sparse serial number of the member of the complex group,
:Origin: parent body name ,,,
:Remarks,
:OTe: observation technique: C-CCD, P-photo, R-radar, T-TV, V-visual,
:L-T - Lookup Table file name,
:Refrence, maximum 200 characters!!
:
:  LP    IAUNo   AdNo  Code   s   sub.date            shower name-designation            activity     LoSb      LoSe      LoS        Ra       De        dRa       dDe       Vg         LoR      S_LoR     LaR      theta      phi       Flags      a         q         e       peri      node      inc         N      Group  CG            Origin                                                     Remarks                                                                                                                         Ote               L-T                             References                                                LT      SD  
:        10       20        30        40        50        60        70        80        90       100       110       120       130       140       150       160       170       180       190       200       210       220       230       240       250       260       270       280       290       300       310       320       330       340        350       360       370       380       390       400       410       420       430       440       450       460       470       480       490       500       510       520       530       540       550       560       570        580       590       600      610       620       630      640       650
+2345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
"00001"|"00001"|"000"|"CAP"|" 1"|"2006-mm-dd"|"alpha-Capricornids                      "|" annual "|"       "|"       "|"128.9  "|"306.6  "|"-8.2   "|"0.54   "|"0.25   "|"22.2   "|"306.91 "|"178.01 "|" 10.67 "|" 88.04 "|"259.32 "|"       "|"2.618  "|"0.602  "|"       "|"266.67 "|"128.9  "|"7.68   "|"00036"|"00000"|"00"|"169P/NEAT (= 2002 EX12)                 "|"                                                                                                                                                      "|"    "|"LookUp table file name"|"1] <A href='http://adsabs.harvard.edu/abs/2006mspc.book.....J' target=_blank>Jenniskens, 2006</A>"
"00002"|"00001"|"001"|"CAP"|" 1"|"2002-mm-dd"|"alpha-Capricornids                      "|" annual "|"       "|"       "|"122.3  "|"306.7  "|"-09.3  "|"0.91   "|"0.25   "|"23.4   "|"306.74 "|"184.44 "|"  9.58 "|" 94.37 "|"260.39 "|"       "|"       "|"0.550  "|"0.768  "|"273.3  "|"122.3  "|"7.7    "|"00269"|"00000"|"00"|"                                        "|"                                                                                                                                                      "|"R   "|"LookUp table file name"|"2] <A href='http://adsabs.harvard.edu/abs/2002dsso.conf...48G' target=_blank>Galligan & Baggaley, 2002</A>"
"00003"|"00001"|"002"|"CAP"|"-2"|"2001-mm-dd"|"alpha-Capricornids                      "|" annual "|"       "|"       "|"123.8  "|"303.4  "|"-10.6  "|"0.75   "|"0.28   "|"22.2   "|"303.23 "|"179.43 "|"  9.07 "|" 89.43 "|"260.93 "|"       "|"2.540  "|"0.594  "|"       "|"267.6  "|"123.8  "|"7.2    "|"     "|"00000"|"00"|"(9162) 1987 OA                          "|"N-?, shower data not found in the publication                                                                                                         "|"P   "|"LookUp table file name"|"3] <A href='http://adsabs.harvard.edu/abs/2001ESASP.495...55H' target=_blank>Hasegawa, 2001</A>"
"00004"|"00001"|"003"|"CAP"|" 1"|"1973-mm-dd"|"alpha-Capricornids                      "|" annual "|"123.70 "|"138.70 "|"127.70 "|"307.68 "|" -9.92 "|"  0.80 "|"  0.50 "|"22.8   "|"307.53 "|"179.83 "|"  8.75 "|" 89.84 "|"261.25 "|"R      "|"2.53   "|"0.59   "|"0.77   "|"269.00 "|"127.66 "|"  7.00 "|"00021"|"00000"|"00"|"                                        "|"                                                                                                                                                      "|"    "|"LookUp table file name"|"4] <A href='http://adsabs.harvard.edu/abs/1973NASSP.319..183C' target=_blank>Cook, 1973</A>"
"00005"|"00001"|"004"|"CAP"|" 1"|"2003-mm-dd"|"alpha-Capricornids                      "|" annual "|"       "|"       "|"127.9  "|"307.1  "|"-8.9   "|"       "|"       "|"22.6   "|"307.22 "|"179.32 "|"  9.87 "|" 89.33 "|"260.12 "|"      1"|"       "|"0.586  "|"0.770  "|"268.4  "|"127.9  "|"7.4    "|"00022"|"00000"|"00"|"                                        "|"                                                                                                                                                      "|"P   "|"LookUp table file name"|"5] <A href='http://adsabs.harvard.edu/abs/2003MNRAS.344..665J' target=_blank>Jopek et al., 2003</A>"
"00006"|"00001"|"005"|"CAP"|" 1"|"2008-mm-dd"|"alpha-Capricornids                      "|"2002/06 "|"116    "|"128    "|"123.5  "|"302.9  "|"-9.9   "|"0.66   "|"0.28   "|"22.2   "|"302.90 "|"179.40 "|"  9.86 "|" 89.40 "|"260.14 "|"       "|"2.35   "|"0.586  "|"0.75   "|"269.2  "|"123.3  "|"7.3    "|"00145"|"00000"|"00"|"                                        "|"Results obtained using wavelet analysis                                                                                                               "|"R   "|"LookUp table file name"|"6] <A href='http://adsabs.harvard.edu/abs/2008Icar..195..317B' target=_blank>Brown et al., 2008</A>"
"00007"|"00001"|"006"|"CAP"|" 1"|"2009-mm-dd"|"alpha-Capricornids                      "|"2007/08 "|"114.3  "|"138.4  "|"126.1  "|"305.7  "|"-9.4   "|"0.50   "|"0.26   "|"22.4   "|"305.74 "|"179.64 "|"  9.72 "|" 89.64 "|"260.28 "|"       "|"       "|"       "|"       "|"       "|"       "|"       "|"00122"|"00000"|"00"|"                                        "|"                                                                                                                                                      "|"T   "|"LookUp table file name"|"7] <A href='http://adsabs.harvard.edu/abs/2009JIMO...37...55S' target=_blank>SonotaCo, 2009</A>"
"00008"|"00001"|"007"|"CAP"|" 1"|"2009-mm-dd"|"alpha-Capricornids                      "|" annual "|"109    "|"138    "|"125    "|"305.1  "|"-10.2  "|"0.57   "|"0.27   "|"20.90  "|"304.97 "|"179.97 "|"  9.08 "|" 89.97 "|"260.92 "|" R     "|"       "|"       "|"       "|"       "|"       "|"       "|"02282"|"00000"|"00"|"                                        "|"                                                                                                                                                      "|"T   "|"LookUp table file name"|"8] <A href='http://adsabs.harvard.edu/abs/2009JIMO...37...98M' target=_blank>Molau and Rendtel, 2009</A>"
"00009"|"00001"|"008"|"CAP"|" 1"|"2015-08-23"|"alpha-Capricornids                      "|"2010/13 "|"101    "|"138    "|"127    "|"306.5  "|"-9.2   "|"0.97   "|"0.24   "|"23.0   "|"306.57 "|"179.57 "|"  9.73 "|" 89.57 "|"260.27 "|"  M   1"|"2.54   "|"0.578  "|"0.774  "|"268.9  "|"125.4  "|"7.5    "|"00646"|"00000"|"00"|"169P/NEAT                               "|"                                                                                                                                                      "|"T   "|"LookUp table file name"|"9] <A href='http://adsabs.harvard.edu/abs/2016Icar..266..331J' target=_blank>Jenniskens et al., 2016</A>"
"00010"|"00002"|"000"|"STA"|" 1"|"2002-mm-dd"|"Southern Taurids                        "|" annual "|"       "|"       "|"217.3  "|"48.7   "|"13     "|"0.73   "|"0.18   "|"28     "|" 49.80 "|"192.50 "|" -4.86 "|"102.46 "|"274.98 "|"       "|"2.07   "|"0.352  "|"0.825  "|"115.4  "|"37.3   "|"5.4    "|" 0097"|"00247"|"02"|"2P/Encke                                "|"member of Taurid Complex (247)                                                                                                                        "|"P   "|"LookUp table file name"|"1] <A href='http://adsabs.harvard.edu/abs/2002ESASP.500..177P' target=_blank>Porubcan & Kornos, 2002</A>"
'''

#TODO Random links that might help...
# https://github.com/drguthals/learnwithdrg/tree/main/OverTheMoon/meteor-showers
# https://en.wikipedia.org/wiki/List_of_meteor_showers
# https://en.wikipedia.org/wiki/Solar_longitude
# https://www.amsmeteors.org/meteor-showers/2020-meteor-shower-list/
# https://amsmeteors.org/meteor-showers/meteor-shower-calendar/
# https://www.popastro.com/main_spa1/meteor/meteor-showers/
# https://www.rmg.co.uk/stories/topics/meteor-shower-guide
# https://www.ta3.sk/IAUC22DB/MDC2007/Roje/roje_lista.php?corobic_roje=0&sort_roje=0
# https://www.imo.net/resources/calendar/
# https://www.imo.net/files/meteor-shower/cal2024.pdf
# https://learn.microsoft.com/en-us/training/modules/predict-meteor-showers-using-python/4-collect-data
# https://www.ta3.sk/IAUC22DB/MDC2022/
# https://stackoverflow.com/questions/25538926/solar-longitude-from-pyephem
# https://stackoverflow.com/questions/69873522/degree-of-solar-longitude-vs-earth-to-calculate-equinox-and-solstice-etc


path = "/home/bernard/Downloads/"
input = path + "streamestablisheddata2022.txt"
output = path + "meteorshowerxephem.txt"

orbitalElementDataType == OrbitalElement.DataType.XEPHEM_MINOR_PLANET
# orbitalElementDataType == OrbitalElement.DataType.SKYFIELD_MINOR_PLANET

with open( input, 'r', encoding = "utf-8" ) as fIn, open( output, 'w', encoding = "utf-8" ) as fOut:
    for line in fIn.read().splitlines():
        if line.startswith( ':' ) or line.startswith( '+' ):
            continue

        fields = line.strip().replace( '\"', '' ).split( '|' )

        showerStatusFlag = fields[ 4 ].strip()
        if showerStatusFlag != '1':
            continue

        activity = fields[ 7 ].strip()
        if activity != "annual":
            continue

        flags = fields[ 21 ]
#TODO Screen out for the epoch flag?
# What should be the epoch?
        # epoch = flags[ 0 ]
        # if epoch != "R":
        #     continue

        reliability = flags[ 6 ]
        if reliability != "1":
            continue

        semimajorAxis = fields[ 22 ].strip()
        if len( semimajorAxis ) == 0:
            continue

        orbitalEccentricity = fields[ 24 ].strip()
        if len( orbitalEccentricity ) == 0:
            continue

        argumentPerihelion = fields[ 25 ].strip()
        if len( argumentPerihelion ) == 0:
            continue

        longitudeAscendingNode = fields[ 26 ].strip()
        if len( longitudeAscendingNode ) == 0:
            continue

        inclinationToEcliptic = fields[ 27 ].strip()
        if len( inclinationToEcliptic ) == 0:
            continue

#TODO Missing:
        primaryDesignation = None
        meanAnomalyEpoch = None
        epochDate = None
        absoluteMagnitude = None
        slopeParameter = None

        # print( line )

        if orbitalElementDataType == OrbitalElement.DataType.XEPHEM_MINOR_PLANET:
            components = [
                primaryDesignation,
                'e',
                inclinationToEcliptic,
                longitudeAscendingNode,
                argumentPerihelion,
                semimajorAxis,
                '0',
                orbitalEccentricity,
                meanAnomalyEpoch,
                minorPlanet[ "epoch" ][ 5 : 7 ] + '/' + minorPlanet[ "epoch" ][ 8 : 10 ] + '/' + minorPlanet[ "epoch" ][ 0 : 4 ],
                "2000.0",
                absoluteMagnitude,
                slopeParameter ]

            fIn.write( ','.join( components )  + '\n' )

        else: #OrbitalElement.DataType.SKYFIELD_MINOR_PLANET
            components = [
                ' ' * 7, # number or designation packed
                ' ', # 8
                str( round( float( absoluteMagnitude ), 2 ) ).rjust( 5 ),
                ' ', # 14
                str( round( float( slopeParameter ), 2 ) ).rjust( 5 ),
                ' ', # 20
                DataProviderOrbitalElement.getPackedDate( minorPlanet[ "epoch" ][ 0 : 4 ], minorPlanet[ "epoch" ][ 5 : 7 ], minorPlanet[ "epoch" ][ 8 : 10 ] ).rjust( 5 ),
                ' ', # 26
                str( round( float( meanAnomalyEpoch ), 5 ) ).rjust( 9 ),
                ' ' * 2, # 36, 37
                str( round( float( argumentPerihelion ), 5 ) ).rjust( 9 ),
                ' ' * 2, # 47, 48
                str( round( float( longitudeAscendingNode ), 5 ) ).rjust( 9 ),
                ' ' * 2, # 58, 59
                str( round( float( inclinationToEcliptic ), 5 ) ).rjust( 9 ),
                ' ' * 2, # 69, 70
                str( round( float( orbitalEccentricity ), 7 ) ).rjust( 9 ),
                ' ', # 80
                ' ' * 11, # mean daily motion
                ' ', # 92
                str( round( float( semimajorAxis ), 7 ) ).rjust( 11 ),
                ' ' * 2, # 104, 105
                ' ', # uncertainty parameter
                ' ', # 107
                ' ' * 9, # reference
                ' ', # 117
                ' ' * 5, # observations
                ' ', # 123
                ' ' * 3, # oppositions
                ' ', # 127
                ' ' * ( 4 + 1 + 4 ), # multiple/single oppositions
                ' ', # 137
                ' ' * 4, # rms residual
                ' ', # 142
                ' ' * 3, # coarse indicator of perturbers
                ' ', # 146
                ' ' * 3, # precise indicator of perturbers
                ' ', # 150
                ' ' * 10, # computer name
                ' ', # 161
                ' ' * 4, # hexdigit flags
                ' ', # 166
                primaryDesignation.ljust( 194 - 167 + 1 ),
                ' ' * 8 ] # date last observation

            fOut.write( ''.join( components )  + '\n' )
