#!/usr/bin/env python3


from urllib.request import urlopen


def getSatCat( url ):
    satCat = { } # Key: NORAD catalog number; Value: data line.
    data = urlopen( url ).read().decode( "utf8" ).splitlines()
    for line in data:
        noradCatalogNumber = line[ 13 : 18 ]
        satCat[ noradCatalogNumber ] = line

    return satCat


def getSatelliteTLEData( url ):
    satelliteTLEData = { } # Key: ( satellite name (title), satellite number ) ; Value: ( line1, line2 )
    data = urlopen( url ).read().decode( "utf8" ).splitlines()
    for i in range( 0, len( data ), 3 ):
        title = data[ i ].strip()
        line1 = data[ i + 1 ].strip()
        line2 = data[ i + 2 ].strip()
        number = line1[ 2 : 7 ]
        satelliteTLEData[ ( title, number ) ] = [ line1, line2 ]

    return satelliteTLEData


# Determine how many of the satellites in the Celestrak TLE data
# are rocket booster, debris, platform, payload or unknown.
def getCountsOfSatelliteTypes( satelliteTLEData, satCat ):
    unknown = [ ]
    rocketBooster = [ ]
    debris = [ ]
    platform = [ ]
    payload = [ ]

    for name, number in satelliteTLEData:
        if "R/B" in name.upper():
            rocketBooster.append( ( name, number ) )
            continue

        if "DEB" in name.upper():
            debris.append( ( name, number ) )
            continue

        if "PLAT" in name.upper():
            platform.append( ( name, number ) )
            continue

        payloadFlag = satCat[ number ][ 20 ]
        if "*" in payloadFlag:
            payload.append( ( name, number ) )
            continue

        unknown.append( ( name, number ) )

    return ( rocketBooster, debris, platform, payload, unknown )


# If a satellite in the satcat data...
#    ...has a D or ? in column 22 as per http://celestrak.com/satcat/status.asp
#    ...has a date in columns 76-85 inclusive (is not whitespace/empty) 
# drop it as it is decayed.
# http://celestrak.com/satcat/satcat-format.asp
def getSatellitesNonDecayed( satCat ):
    satellitesNonDecayed = [ ]
    for key in satCat:
        operationalStatusCode = satCat[ key ][ 21 ]
        if operationalStatusCode.upper() == "D" or operationalStatusCode.upper() == "?":
            continue

        decayDate = satCat[ key ][ 75 : 85 ]
        if decayDate.strip() == "":
            satellitesNonDecayed.append( satCat[ key ][ 23 : 47 ].strip() )

    return satellitesNonDecayed


satCat = getSatCat( "file:///home/bernard/Desktop/satcat.txt" )
#satCat = getSatCat( "http://celestrak.com/pub/satcat.txt" )
print( "Number of satellites in the catalogue:", len( satCat ) )


satelliteTLEData = getSatelliteTLEData( "http://celestrak.com/NORAD/elements/visual.txt" )
print( "Number of satellites in TLE data:", len( satelliteTLEData ) )


rocketBooster, debris, platform, payload, unknown = getCountsOfSatelliteTypes( satelliteTLEData, satCat )
print( "R/B:", len( rocketBooster ), sorted( rocketBooster ) )
print( "DEB:", len( debris ), sorted( debris ) )
print( "PLAT:", len( platform ), sorted( platform ) )
print( "PAYLOAD:", len( payload ), sorted( payload ) )
print( "Unknowns:", len( unknown ), sorted( unknown ) )


satellitesNonDecayed = getSatellitesNonDecayed( satCat )
print( "Number of satellites NOT decayed in the catalogue:", len( satellitesNonDecayed ) )