#!/usr/bin/env python3


# Possible source of icons...
# http://www.flaticon.com/search/satellite


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


# Determine how many of the satellites from Celestrak are
# rocket booster, debris, platform, payload or unknown.
def getCountsOfSatelliteTypes( satelliteTLEData, satCat ):
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

        payload = satCat[ number ][ 20 ]
        if "*" in payload:
            pay.append( name )
            continue

    unknowns.append( name )

    return ( rb, deb, plat, pay, unknowns )



# If a satellite in the satcat data...
#    Has a D or ? in column 22 as per http://celestrak.com/satcat/status.asp
#    Has a date in columns 76-85 inclusive (is not whitespace/empty) 
# drop it as it is decayed as per http://celestrak.com/satcat/satcat-format.asp
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


satelliteTLEData = getSatelliteTLEData( "http://celestrak.com/NORAD/elements/visual.txt" )
print( "Number of satellites in TLE data:", len( satelliteTLEData ) )


satCat = getSatCat( "file:///home/bernard/Desktop/satcat.txt" )
#satCat = getSatCat( "http://celestrak.com/pub/satcat.txt" )
print( "Number of satellites in the catalogue:", len( satCat ) )


rb, deb, plat, pay, unknowns = getCountsOfSatelliteTypes( satelliteTLEData, satCat )
print( "R/B:", len( rb ), sorted( rb ) )
print( "DEB:", len( deb ), sorted( deb ) )
print( "PLAT:", len( plat ), sorted( plat ) )
print( "PAYLOAD:", len( pay ), sorted( pay ) )
print( "Unknowns:", len( unknowns ), sorted( unknowns ) )


satellitesNonDecayed = getSatellitesNonDecayed( satCat )
print( "Number of satellites not decayed in the catalogue:", len( satellitesNonDecayed ) )