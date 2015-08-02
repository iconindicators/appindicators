#!/usr/bin/env python3


from urllib.request import urlopen


def getSatCat( url ):
    satCat = { } # Key: NORAD catalog number; Value: data line.
    data = urlopen( url ).read().decode( "utf8" ).splitlines()
    for line in data:
        noradCatalogNumber = line[ 13 : 18 ]
        satCat[ noradCatalogNumber ] = line

    return satCat


def getTLEData( tleURL ):
    tleData = { } # Key: ( satellite name (title), satellite number ) ; Value: ( line1, line2 )
    data = urlopen( tleURL ).read().decode( "utf8" ).splitlines()
    for i in range( 0, len( data ), 3 ):
        title = data[ i ].strip()
        line1 = data[ i + 1 ].strip()
        line2 = data[ i + 2 ].strip()
        number = line1[ 2 : 7 ]
        tleData[ ( title, number ) ] = [ line1, line2 ]

    return tleData


# Determine how many of the satellites in the Celestrak TLE data
# are rocket booster, debris, platform, payload or unknown.
# If the satCat is None, the payload will not be part of the result.
def getCountsOfObjectTypes( satelliteTLEData, satCat ):
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

        if satCat is not None:
            payloadFlag = satCat[ number ][ 20 ]
            if "*" in payloadFlag:
                payload.append( ( name, number ) )
                continue

        unknown.append( ( name, number ) )

    return ( rocketBooster, debris, platform, payload, unknown )


# If a satellite/object in the satcat data...
#    ...has a D or ? in column 22 as per http://celestrak.com/satcat/status.asp
#    ...has a date in columns 76-85 inclusive (is not whitespace/empty) 
# drop it as it is decayed.
# http://celestrak.com/satcat/satcat-format.asp
def getObjectsWhichAreNotDecayed( satCat ):
    objectsNotDecayed = [ ]
    for key in satCat:
        operationalStatusCode = satCat[ key ][ 21 ]
        if operationalStatusCode.upper() == "D" or operationalStatusCode.upper() == "?":
            continue

        decayDate = satCat[ key ][ 75 : 85 ]
        if decayDate.strip() == "":
            objectsNotDecayed.append( satCat[ key ][ 23 : 47 ].strip() )

    return objectsNotDecayed


def printObjectType( objectType, objectList ):
#     print( "\t" + objectType + ":", len( objectList ), sorted( objectList ) )
    print( "\t" + objectType + ":", len( objectList ) )


satCat = getSatCat( "file:///home/bernard/Desktop/satcat.txt" )
#satCat = getSatCat( "http://celestrak.com/pub/satcat.txt" )
print( "Number of objects in the catalogue:", len( satCat ) )

objectsNotDecayed = getObjectsWhichAreNotDecayed( satCat )
print( "Number of objects in the catalogue which are NOT decayed:", len( objectsNotDecayed ) )

tleURLs = [ "http://celestrak.com/NORAD/elements/tle-new.txt",
            "http://celestrak.com/NORAD/elements/stations.txt",
            "http://celestrak.com/NORAD/elements/visual.txt",
            "http://celestrak.com/NORAD/elements/1999-025.txt",
            "http://celestrak.com/NORAD/elements/iridium-33-debris.txt",
            "http://celestrak.com/NORAD/elements/cosmos-2251-debris.txt",
            "http://celestrak.com/NORAD/elements/2012-044.txt",
            "http://celestrak.com/NORAD/elements/weather.txt",
            "http://celestrak.com/NORAD/elements/noaa.txt",
            "http://celestrak.com/NORAD/elements/goes.txt",
            "http://celestrak.com/NORAD/elements/resource.txt",
            "http://celestrak.com/NORAD/elements/sarsat.txt",
            "http://celestrak.com/NORAD/elements/dmc.txt",
            "http://celestrak.com/NORAD/elements/tdrss.txt",
            "http://celestrak.com/NORAD/elements/argos.txt",
            "http://celestrak.com/NORAD/elements/geo.txt",
            "http://celestrak.com/NORAD/elements/intelsat.txt",
            "http://celestrak.com/NORAD/elements/gorizont.txt",
            "http://celestrak.com/NORAD/elements/raduga.txt",
            "http://celestrak.com/NORAD/elements/molniya.txt",
            "http://celestrak.com/NORAD/elements/iridium.txt",
            "http://celestrak.com/NORAD/elements/orbcomm.txt",
            "http://celestrak.com/NORAD/elements/globalstar.txt",
            "http://celestrak.com/NORAD/elements/amateur.txt",
            "http://celestrak.com/NORAD/elements/x-comm.txt",
            "http://celestrak.com/NORAD/elements/other-comm.txt",
            "http://celestrak.com/NORAD/elements/gps-ops.txt",
            "http://celestrak.com/NORAD/elements/glo-ops.txt",
            "http://celestrak.com/NORAD/elements/galileo.txt",
            "http://celestrak.com/NORAD/elements/beidou.txt",
            "http://celestrak.com/NORAD/elements/sbas.txt",
            "http://celestrak.com/NORAD/elements/nnss.txt",
            "http://celestrak.com/NORAD/elements/musson.txt",
            "http://celestrak.com/NORAD/elements/science.txt",
            "http://celestrak.com/NORAD/elements/geodetic.txt",
            "http://celestrak.com/NORAD/elements/engineering.txt",
            "http://celestrak.com/NORAD/elements/education.txt",
            "http://celestrak.com/NORAD/elements/military.txt",
            "http://celestrak.com/NORAD/elements/radar.txt",
            "http://celestrak.com/NORAD/elements/cubesat.txt",
            "http://celestrak.com/NORAD/elements/other.txt" ]

tleURLs = [ "http://celestrak.com/NORAD/elements/visual.txt" ]

tleData = { }
for tleURL in tleURLs:
    tleData.update( getTLEData( tleURL ) )

print( "Number of objects in the TLE data:", len( tleData ) )

rocketBooster, debris, platform, payload, unknown = getCountsOfObjectTypes( tleData, satCat )
print( "\nBreakdown of TLE objects from catalogue..." )
printObjectType( "R/B", rocketBooster )
printObjectType( "DEB", debris )
printObjectType( "PLAT", platform )
printObjectType( "PAYLOAD", payload )
printObjectType( "Unknowns", unknown )

rocketBooster, debris, platform, payload, unknown = getCountsOfObjectTypes( tleData, None )
print( "\nBreakdown of TLE objects from TLE..." )
printObjectType( "R/B", rocketBooster )
printObjectType( "DEB", debris )
printObjectType( "PLAT", platform )
printObjectType( "PAYLOAD", payload )
printObjectType( "Unknowns", unknown )
