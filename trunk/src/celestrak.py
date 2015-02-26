#!/usr/bin/env python3


# Icons...
# http://www.flaticon.com/search/satellite


# Determine how many of the satellites et al from Celestrak
# are rocket booster, debris, platform, payload or unknown
# by looking at the full text database from Celestrak.


from urllib.request import urlopen


def getSatCat( url ):
    satCat = { } # Key: Norad number; Value: data line.
    data = urlopen( url ).read().decode( "utf8" ).splitlines()
    for line in data:
        noradNumber = line[ 13 : 18 ]
        satCat[ noradNumber ] = line

    return satCat


def getSatelliteTLEData( url ):
    satelliteTLEData = { } # Key: ( satellite name, satellite number ) ; Value: satellite.TLE object.
    data = urlopen( url ).read().decode( "utf8" ).splitlines()
    for i in range( 0, len( data ), 3 ):
        title = data[ i ].strip()
        line1 = data[ i + 1 ].strip()
        line2 = data[ i + 2 ].strip()
        satelliteTLEData[ title ] = [ line1, line2 ]

    return satelliteTLEData


useSatCat = True
if useSatCat:
    satCat = getSatCat( "http://celestrak.com/pub/satcat.txt" )

satelliteTLEData = getSatelliteTLEData( "http://celestrak.com/NORAD/elements/visual.txt" )
unknowns = [ ]
rb = [ ]
deb = [ ]
plat = [ ]
pay = [ ]
for key in satelliteTLEData:
    title = key
    line1 = satelliteTLEData[ key ][ 0 ]
    line2 = satelliteTLEData[ key ][ 1 ]

    launchYear = line1[ 9 : 11 ]
    if int( launchYear ) < 57:
        launchYear = "20" + launchYear
    else:
        launchYear = "19" + launchYear 

    launchYear + "-" + line1[ 11 : 17 ].strip()

    name = title
    number = line1[ 2 : 7 ]
    internationalDesignator = launchYear

    if "R/B" in name.upper():
        rb.append( name )
        continue

    if "DEB" in name.upper():
        deb.append( name )
        continue

    if "PLAT" in name.upper():
        plat.append( name )
        continue

    if useSatCat:
        payload = satCat[ number ][ 20 ]
        if "*" in payload:
            pay.append( name )
            continue

    unknowns.append( name )

if useSatCat:
    print( "SatCat size:", len( satCat ) )

print( "TLE data size:", len( satelliteTLEData ) )
print( "R/B:", len( rb ), sorted( rb ) )
print( "DEB:", len( deb ), sorted( deb ) )
print( "PLAT:", len( plat ), sorted( plat ) )
print( "PAYLOAD:", len( pay ), sorted( pay ) )
print( "Unknowns:", len( unknowns ), sorted( unknowns ) )