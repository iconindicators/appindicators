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

        elif "DEB" in name.upper():
            debris.append( ( name, number ) )

        elif "PLAT" in name.upper():
            platform.append( ( name, number ) )

        else:
            if satCat is None:
                unknown.append( ( name, number ) )

            else:
                payloadFlag = satCat[ number ][ 20 ]
                if "*" in payloadFlag:
                    payload.append( ( name, number ) )

                else:
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
    print( "\t" + objectType + ":", len( objectList ), sorted( objectList ) )


satCat = getSatCat( "file:./satcat.txt" )
#satCat = getSatCat( "http://celestrak.com/pub/satcat.txt" )
print( "Number of objects in the catalogue:", len( satCat ) )

objectsNotDecayed = getObjectsWhichAreNotDecayed( satCat )
print( "Number of objects in the catalogue which are NOT decayed:", len( objectsNotDecayed ) )

tleURLs = [ "http://celestrak.com/NORAD/elements/tle-new.txt",
            "http://celestrak.com/NORAD/elements/stations.txt",
            "http://celestrak.com/NORAD/elements/visual.txt",
            "http://celestrak.com/NORAD/elements/active.txt",
            "http://celestrak.com/NORAD/elements/analyst.txt",
            "http://celestrak.com/NORAD/elements/2019-006.txt",
            "http://celestrak.com/NORAD/elements/1999-025.txt",
            "http://celestrak.com/NORAD/elements/iridium-33-debris.txt",
            "http://celestrak.com/NORAD/elements/cosmos-2251-debris.txt",
            "http://celestrak.com/NORAD/elements/weather.txt",
            "http://celestrak.com/NORAD/elements/noaa.txt",
            "http://celestrak.com/NORAD/elements/goes.txt",
            "http://celestrak.com/NORAD/elements/resource.txt",
            "http://celestrak.com/NORAD/elements/sarsat.txt",
            "http://celestrak.com/NORAD/elements/dmc.txt",
            "http://celestrak.com/NORAD/elements/tdrss.txt",
            "http://celestrak.com/NORAD/elements/argos.txt",
            "http://celestrak.com/NORAD/elements/planet.txt",
            "http://celestrak.com/NORAD/elements/spire.txt",
            "http://celestrak.com/NORAD/elements/geo.txt",
            "http://celestrak.com/NORAD/elements/gpz.txt",
            "http://celestrak.com/NORAD/elements/gpz-plus.txt",
            "http://celestrak.com/NORAD/elements/intelsat.txt",
            "http://celestrak.com/NORAD/elements/ses.txt",
            "http://celestrak.com/NORAD/elements/iridium.txt",
            "http://celestrak.com/NORAD/elements/oneweb.txt",
            "http://celestrak.com/NORAD/elements/orbcomm.txt",
            "http://celestrak.com/NORAD/elements/globalstar.txt",
            "http://celestrak.com/NORAD/elements/amatuer.txt",
            "http://celestrak.com/NORAD/elements/x-comm.txt",
            "http://celestrak.com/NORAD/elements/other-comm.txt",
            "http://celestrak.com/NORAD/elements/satnogs.txt",
            "http://celestrak.com/NORAD/elements/gorizont.txt",
            "http://celestrak.com/NORAD/elements/raduga.txt",
            "http://celestrak.com/NORAD/elements/molniya.txt",
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


# Output is below...
# ...given that the ISS is a payload, it is impossible to discriminate the ISS and other similar objects
# from other non-descript payloads.
#
#
# Number of objects in the catalogue: 45348
# Number of objects in the catalogue which are NOT decayed: 20472
# Number of objects in the TLE data: 162

# Breakdown of TLE objects from catalogue...
#     R/B: 96 [('ARIANE 40 R/B', '20443'), ('ARIANE 40 R/B', '21610'), ('ARIANE 40 R/B', '22830'), ('ARIANE 40+ R/B', '23561'), ('ARIANE 5 R/B', '28499'), ('ATLAS CENTAUR R/B', '06155'), ('CUSAT 2 & FALCON 9 R/B', '39271'), ('CZ-2C R/B', '28222'), ('CZ-2C R/B', '28480'), ('CZ-2C R/B', '31114'), ('CZ-2C R/B', '43521'), ('CZ-2D R/B', '28738'), ('CZ-4B R/B', '25732'), ('CZ-4B R/B', '27432'), ('CZ-4B R/B', '28059'), ('CZ-4B R/B', '28415'), ('CZ-4B R/B', '29507'), ('DELTA 1 R/B', '20323'), ('DELTA 2 R/B', '25876'), ('DELTA 2 R/B(1)', '20303'), ('DELTA 2 R/B(1)', '20362'), ('DELTA 2 R/B(1)', '20453'), ('H-2A R/B', '27601'), ('H-2A R/B', '28932'), ('H-2A R/B', '38341'), ('IDEFIX & ARIANE 42P R/B', '27422'), ('SL-12 R/B(2)', '15772'), ('SL-14 R/B', '11267'), ('SL-14 R/B', '11672'), ('SL-14 R/B', '13553'), ('SL-14 R/B', '14820'), ('SL-14 R/B', '15945'), ('SL-14 R/B', '16496'), ('SL-14 R/B', '16792'), ('SL-14 R/B', '16882'), ('SL-14 R/B', '17567'), ('SL-14 R/B', '17912'), ('SL-14 R/B', '18153'), ('SL-14 R/B', '18749'), ('SL-14 R/B', '19574'), ('SL-14 R/B', '20262'), ('SL-14 R/B', '20466'), ('SL-14 R/B', '20511'), ('SL-14 R/B', '21423'), ('SL-16 R/B', '16182'), ('SL-16 R/B', '17590'), ('SL-16 R/B', '19120'), ('SL-16 R/B', '19650'), ('SL-16 R/B', '20625'), ('SL-16 R/B', '22220'), ('SL-16 R/B', '22285'), ('SL-16 R/B', '22566'), ('SL-16 R/B', '22803'), ('SL-16 R/B', '23088'), ('SL-16 R/B', '23343'), ('SL-16 R/B', '23405'), ('SL-16 R/B', '23705'), ('SL-16 R/B', '24298'), ('SL-16 R/B', '25400'), ('SL-16 R/B', '25407'), ('SL-16 R/B', '25861'), ('SL-16 R/B', '26070'), ('SL-16 R/B', '28353'), ('SL-16 R/B', '31793'), ('SL-27 R/B', '40354'), ('SL-3 R/B', '00877'), ('SL-3 R/B', '04814'), ('SL-3 R/B', '05118'), ('SL-3 R/B', '10114'), ('SL-3 R/B', '12465'), ('SL-3 R/B', '12904'), ('SL-3 R/B', '13068'), ('SL-3 R/B', '13154'), ('SL-3 R/B', '13403'), ('SL-3 R/B', '13819'), ('SL-3 R/B', '14208'), ('SL-3 R/B', '16111'), ('SL-3 R/B', '19046'), ('SL-4 R/B', '39679'), ('SL-6 R/B(2)', '20666'), ('SL-8 R/B', '02802'), ('SL-8 R/B', '03230'), ('SL-8 R/B', '05730'), ('SL-8 R/B', '07004'), ('SL-8 R/B', '08459'), ('SL-8 R/B', '11574'), ('SL-8 R/B', '12139'), ('SL-8 R/B', '15483'), ('SL-8 R/B', '19257'), ('SL-8 R/B', '20775'), ('SL-8 R/B', '21088'), ('SL-8 R/B', '21876'), ('SL-8 R/B', '21938'), ('SL-8 R/B', '25723'), ('THOR AGENA D R/B', '00733'), ('TITAN 4B R/B', '26474')]
#     DEB: 1 [('CREW DRAGON DEMO-1 DEB', '44064')]
#     PLAT: 0 []
#     PAYLOAD: 65 [('AEOLUS', '43600'), ('AJISAI (EGS)', '16908'), ('AKARI (ASTRO-F)', '28939'), ('ALOS (DAICHI)', '28931'), ('ALOS-2', '39766'), ('AQUA', '27424'), ('ASTEX 1', '05560'), ('ASTRO-H (HITOMI)', '41337'), ('ATLAS CENTAUR 2', '00694'), ('COSMO-SKYMED 1', '31598'), ('COSMOS 1408', '13552'), ('COSMOS 1455', '14032'), ('COSMOS 1500', '14372'), ('COSMOS 1536', '14699'), ('COSMOS 1544', '14819'), ('COSMOS 1626', '15494'), ('COSMOS 1743', '16719'), ('COSMOS 1812', '17295'), ('COSMOS 1833', '17589'), ('COSMOS 1844', '17973'), ('COSMOS 1867', '18187'), ('COSMOS 1892', '18421'), ('COSMOS 1933', '18958'), ('COSMOS 1953', '19210'), ('COSMOS 1975', '19573'), ('COSMOS 2058', '20465'), ('COSMOS 2084', '20663'), ('COSMOS 2151', '21422'), ('COSMOS 2219', '22219'), ('COSMOS 2221', '22236'), ('COSMOS 2228', '22286'), ('COSMOS 2242', '22626'), ('COSMOS 2278', '23087'), ('COSMOS 2428', '31792'), ('COSMOS 482 DESCENT CRAFT', '06073'), ('ENVISAT', '27386'), ('ERBS', '15354'), ('ERS-1', '21574'), ('ERS-2', '23560'), ('GENESIS 1', '29252'), ('GENESIS 2', '31789'), ('HELIOS 1B', '25977'), ('HST', '20580'), ('HXMT (HUIYAN)', '42758'), ('INTERCOSMOS 24', '20261'), ('INTERCOSMOS 25', '21819'), ('ISIS 1', '03669'), ('ISS (ZARYA)', '25544'), ('KORONAS-FOTON', '33504'), ('METEOR 1-29', '11251'), ('METEOR PRIRODA', '12585'), ('MIDORI II (ADEOS-II)', '27597'), ('OAO 2', '03597'), ('OAO 3 (COPERNICUS)', '06153'), ('OKEAN-3', '21397'), ('OKEAN-O', '25860'), ('ORBVIEW 2 (SEASTAR)', '24883'), ('RESURS-DK 1', '29228'), ('SAOCOM 1A', '43641'), ('SEASAT 1', '10967'), ('SERT 2', '04327'), ('SHENZHOU-11 MODULE', '41868'), ('SUZAKU (ASTRO-EII)', '28773'), ('TERRA', '25994'), ('YAOGAN 29', '41038')]
#     Unknowns: 0 []
# 
# Breakdown of TLE objects from TLE...
#     R/B: 96 [('ARIANE 40 R/B', '20443'), ('ARIANE 40 R/B', '21610'), ('ARIANE 40 R/B', '22830'), ('ARIANE 40+ R/B', '23561'), ('ARIANE 5 R/B', '28499'), ('ATLAS CENTAUR R/B', '06155'), ('CUSAT 2 & FALCON 9 R/B', '39271'), ('CZ-2C R/B', '28222'), ('CZ-2C R/B', '28480'), ('CZ-2C R/B', '31114'), ('CZ-2C R/B', '43521'), ('CZ-2D R/B', '28738'), ('CZ-4B R/B', '25732'), ('CZ-4B R/B', '27432'), ('CZ-4B R/B', '28059'), ('CZ-4B R/B', '28415'), ('CZ-4B R/B', '29507'), ('DELTA 1 R/B', '20323'), ('DELTA 2 R/B', '25876'), ('DELTA 2 R/B(1)', '20303'), ('DELTA 2 R/B(1)', '20362'), ('DELTA 2 R/B(1)', '20453'), ('H-2A R/B', '27601'), ('H-2A R/B', '28932'), ('H-2A R/B', '38341'), ('IDEFIX & ARIANE 42P R/B', '27422'), ('SL-12 R/B(2)', '15772'), ('SL-14 R/B', '11267'), ('SL-14 R/B', '11672'), ('SL-14 R/B', '13553'), ('SL-14 R/B', '14820'), ('SL-14 R/B', '15945'), ('SL-14 R/B', '16496'), ('SL-14 R/B', '16792'), ('SL-14 R/B', '16882'), ('SL-14 R/B', '17567'), ('SL-14 R/B', '17912'), ('SL-14 R/B', '18153'), ('SL-14 R/B', '18749'), ('SL-14 R/B', '19574'), ('SL-14 R/B', '20262'), ('SL-14 R/B', '20466'), ('SL-14 R/B', '20511'), ('SL-14 R/B', '21423'), ('SL-16 R/B', '16182'), ('SL-16 R/B', '17590'), ('SL-16 R/B', '19120'), ('SL-16 R/B', '19650'), ('SL-16 R/B', '20625'), ('SL-16 R/B', '22220'), ('SL-16 R/B', '22285'), ('SL-16 R/B', '22566'), ('SL-16 R/B', '22803'), ('SL-16 R/B', '23088'), ('SL-16 R/B', '23343'), ('SL-16 R/B', '23405'), ('SL-16 R/B', '23705'), ('SL-16 R/B', '24298'), ('SL-16 R/B', '25400'), ('SL-16 R/B', '25407'), ('SL-16 R/B', '25861'), ('SL-16 R/B', '26070'), ('SL-16 R/B', '28353'), ('SL-16 R/B', '31793'), ('SL-27 R/B', '40354'), ('SL-3 R/B', '00877'), ('SL-3 R/B', '04814'), ('SL-3 R/B', '05118'), ('SL-3 R/B', '10114'), ('SL-3 R/B', '12465'), ('SL-3 R/B', '12904'), ('SL-3 R/B', '13068'), ('SL-3 R/B', '13154'), ('SL-3 R/B', '13403'), ('SL-3 R/B', '13819'), ('SL-3 R/B', '14208'), ('SL-3 R/B', '16111'), ('SL-3 R/B', '19046'), ('SL-4 R/B', '39679'), ('SL-6 R/B(2)', '20666'), ('SL-8 R/B', '02802'), ('SL-8 R/B', '03230'), ('SL-8 R/B', '05730'), ('SL-8 R/B', '07004'), ('SL-8 R/B', '08459'), ('SL-8 R/B', '11574'), ('SL-8 R/B', '12139'), ('SL-8 R/B', '15483'), ('SL-8 R/B', '19257'), ('SL-8 R/B', '20775'), ('SL-8 R/B', '21088'), ('SL-8 R/B', '21876'), ('SL-8 R/B', '21938'), ('SL-8 R/B', '25723'), ('THOR AGENA D R/B', '00733'), ('TITAN 4B R/B', '26474')]
#     DEB: 1 [('CREW DRAGON DEMO-1 DEB', '44064')]
#     PLAT: 0 []
#     PAYLOAD: 0 []
#     Unknowns: 65 [('AEOLUS', '43600'), ('AJISAI (EGS)', '16908'), ('AKARI (ASTRO-F)', '28939'), ('ALOS (DAICHI)', '28931'), ('ALOS-2', '39766'), ('AQUA', '27424'), ('ASTEX 1', '05560'), ('ASTRO-H (HITOMI)', '41337'), ('ATLAS CENTAUR 2', '00694'), ('COSMO-SKYMED 1', '31598'), ('COSMOS 1408', '13552'), ('COSMOS 1455', '14032'), ('COSMOS 1500', '14372'), ('COSMOS 1536', '14699'), ('COSMOS 1544', '14819'), ('COSMOS 1626', '15494'), ('COSMOS 1743', '16719'), ('COSMOS 1812', '17295'), ('COSMOS 1833', '17589'), ('COSMOS 1844', '17973'), ('COSMOS 1867', '18187'), ('COSMOS 1892', '18421'), ('COSMOS 1933', '18958'), ('COSMOS 1953', '19210'), ('COSMOS 1975', '19573'), ('COSMOS 2058', '20465'), ('COSMOS 2084', '20663'), ('COSMOS 2151', '21422'), ('COSMOS 2219', '22219'), ('COSMOS 2221', '22236'), ('COSMOS 2228', '22286'), ('COSMOS 2242', '22626'), ('COSMOS 2278', '23087'), ('COSMOS 2428', '31792'), ('COSMOS 482 DESCENT CRAFT', '06073'), ('ENVISAT', '27386'), ('ERBS', '15354'), ('ERS-1', '21574'), ('ERS-2', '23560'), ('GENESIS 1', '29252'), ('GENESIS 2', '31789'), ('HELIOS 1B', '25977'), ('HST', '20580'), ('HXMT (HUIYAN)', '42758'), ('INTERCOSMOS 24', '20261'), ('INTERCOSMOS 25', '21819'), ('ISIS 1', '03669'), ('ISS (ZARYA)', '25544'), ('KORONAS-FOTON', '33504'), ('METEOR 1-29', '11251'), ('METEOR PRIRODA', '12585'), ('MIDORI II (ADEOS-II)', '27597'), ('OAO 2', '03597'), ('OAO 3 (COPERNICUS)', '06153'), ('OKEAN-3', '21397'), ('OKEAN-O', '25860'), ('ORBVIEW 2 (SEASTAR)', '24883'), ('RESURS-DK 1', '29228'), ('SAOCOM 1A', '43641'), ('SEASAT 1', '10967'), ('SERT 2', '04327'), ('SHENZHOU-11 MODULE', '41868'), ('SUZAKU (ASTRO-EII)', '28773'), ('TERRA', '25994'), ('YAOGAN 29', '41038')]