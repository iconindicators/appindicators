#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


# Calculate astronomical information using PyEphem.


try:
    from ephem.cities import _city_data
    import ephem
    available = True

except ImportError:
    available = False

from astrobase import AstroBase
from distutils.version import LooseVersion

import datetime, eclipse, locale, math


class AstroPyEphem( AstroBase ):

    # DO NOT EDIT: Content must be created using 'createephemerisstars.py'.
    __EPHEMERIS_STARS = {
        "ACAMAR"            : "ACAMAR,f|S|A4,2.97102074|-53.53,-40.30467239|25.71,2.88",
        "ACHERNAR"          : "ACHERNAR,f|S|B3,1.62856849|88.02,-57.23675744|-40.08,0.45",
        "ACRUX"             : "ACRUX,f|S|B0,12.44330439|-35.37,-63.09909168|-14.73,0.77",
        "ADHARA"            : "ADHARA,f|S|B2,6.97709679|2.63,-28.97208374|2.29,1.5",
        "ALCOR"             : "ALCOR,f|S|A5,13.42042721|120.35,54.98795774|-16.94,3.99",
        "ALCYONE"           : "ALCYONE,f|S|B7,3.79141014|19.35,24.10513714|-43.11,2.85",
        "ALDEBARAN"         : "ALDEBARAN,f|S|K5,4.59867740|62.78,16.50930138|-189.36,0.87",
        "ALDERAMIN"         : "ALDERAMIN,f|S|A7,21.30965876|149.91,62.58557256|48.27,2.45",
        "ALFIRK"            : "ALFIRK,f|S|B2,21.47766587|12.6,70.56071602|8.73,3.23",
        "ALGENIB"           : "ALGENIB,f|S|B2,0.22059801|4.7,15.18359590|-8.24,2.83",
        "ALGIEBA"           : "ALGIEBA,f|S|K0,10.33287623|310.77,19.84148875|-152.88,2.01",
        "ALGOL"             : "ALGOL,f|S|B8,3.13614765|2.39,40.95564766|-1.44,2.09",
        "ALHENA"            : "ALHENA,f|S|A0,6.62852808|-2.04,16.39925217|-66.92,1.93",
        "ALIOTH"            : "ALIOTH,f|S|A0,12.90048595|111.74,55.95982123|-8.99,1.76",
        "ALKAID"            : "ALKAID,f|S|B3,13.79234379|-121.23,49.31326512|-15.56,1.85",
        "ALMACH"            : "ALMACH,f|S|B8,2.06498696|43.08,42.32972472|-50.85,2.1",
        "ALNAIR"            : "ALNAIR,f|S|B7,22.13721819|127.6,-46.96097539|-147.91,1.73",
        "ALNILAM"           : "ALNILAM,f|S|B0,5.60355929|1.49,-1.20191983|-1.06,1.69",
        "ALNITAK"           : "ALNITAK,f|S|O9,5.67931309|3.99,-1.94257224|2.54,1.74",
        "ALPHARD"           : "ALPHARD,f|S|K3,9.45978980|-14.49,-8.65860253|33.25,1.99",
        "ALPHECCA"          : "ALPHECCA,f|S|A0,15.57813004|120.38,26.71469307|-89.44,2.22",
        "ALPHERATZ"         : "ALPHERATZ,f|S|B9,0.13979405|135.68,29.09043197|-162.95,2.07",
        "ALSHAIN"           : "ALSHAIN,f|S|G8,19.92188706|46.35,6.40676348|-481.32,3.71",
        "ALTAIR"            : "ALTAIR,f|S|A7,19.84638864|536.82,8.86832203|385.54,0.76",
        "ANKAA"             : "ANKAA,f|S|K0,0.43806972|232.76,-42.30598144|-353.64,2.4",
        "ANTARES"           : "ANTARES,f|S|M1,16.49012803|-10.16,-26.43200250|-23.21,1.06",
        "ARCTURUS"          : "ARCTURUS,f|S|K2,14.26102001|-1093.45,19.18241038|-1999.4,-0.05",
        "ARKAB POSTERIOR"   : "ARKAB POSTERIOR,f|S|F2,19.38698247|92.78,-44.79977847|-53.73,4.27",
        "ARKAB PRIOR"       : "ARKAB PRIOR,f|S|B9,19.37730347|7.31,-44.45896465|-22.43,3.96",
        "ARNEB"             : "ARNEB,f|S|F0,5.54550442|3.27,-17.82228853|1.54,2.58",
        "ATLAS"             : "ATLAS,f|S|B8,3.81937293|17.77,24.05341547|-44.7,3.62",
        "ATRIA"             : "ATRIA,f|S|K2,16.81108191|17.85,-69.02771505|-32.92,1.91",
        "AVIOR"             : "AVIOR,f|S|K3,8.37523211|-25.34,-59.50948307|22.72,1.86",
        "BELLATRIX"         : "BELLATRIX,f|S|B2,5.41885085|-8.75,6.34970223|-13.28,1.64",
        "BETELGEUSE"        : "BETELGEUSE,f|S|M2,5.91952924|27.33,7.40706274|10.86,0.45",
        "CANOPUS"           : "CANOPUS,f|S|F0,6.39919718|19.99,-52.69566045|23.67,-0.62",
        "CAPELLA"           : "CAPELLA,f|S|M1,5.27815528|75.52,45.99799106|-427.13,0.08",
        "CAPH"              : "CAPH,f|S|F2,0.15296808|523.39,59.14977950|-180.42,2.28",
        "CASTOR"            : "CASTOR,f|S|A2,7.57662855|-206.33,31.88827631|-148.18,1.58",
        "CEBALRAI"          : "CEBALRAI,f|S|K2,17.72454254|-40.67,4.56730283|158.8,2.76",
        "DENEB"             : "DENEB,f|S|A2,20.69053187|1.56,45.28033800|1.55,1.25",
        "DENEBOLA"          : "DENEBOLA,f|S|A3,11.81766043|-499.02,14.57206038|-113.78,2.14",
        "DIPHDA"            : "DIPHDA,f|S|K0,0.72649196|232.79,-17.98660457|32.71,2.04",
        "DUBHE"             : "DUBHE,f|S|F7,11.06213019|-136.46,61.75103324|-35.25,1.81",
        "ELECTRA"           : "ELECTRA,f|S|B6,3.74792703|21.55,24.11333922|-44.92,3.72",
        "ELNATH"            : "ELNATH,f|S|B7,5.43819816|23.28,28.60745000|-174.22,1.65",
        "ELTANIN"           : "ELTANIN,f|S|K5,17.94343608|-8.52,51.48889500|-23.05,2.24",
        "ENIF"              : "ENIF,f|S|K2,21.73643281|30.02,9.87501126|1.38,2.38",
        "FOMALHAUT"         : "FOMALHAUT,f|S|A3,22.96084626|329.22,-29.62223601|-164.22,1.17",
        "GACRUX"            : "GACRUX,f|S|M4,12.51943314|27.94,-57.11321175|-264.33,1.59",
        "GIENAH"            : "GIENAH,f|S|B8,12.26343617|-159.58,-17.54192948|22.31,2.58",
        "HADAR"             : "HADAR,f|S|B1,14.06372347|-33.96,-60.37303932|-25.06,0.61",
        "HAMAL"             : "HAMAL,f|S|K2,2.11955753|190.73,23.46242310|-145.77,2.01",
        "IZAR"              : "IZAR,f|S|A0,14.74978270|-50.65,27.07422246|20.0,2.35",
        "KAUS AUSTRALIS"    : "KAUS AUSTRALIS,f|S|B9,18.40286620|-39.61,-34.38461611|-124.05,1.79",
        "KOCHAB"            : "KOCHAB,f|S|K4,14.84509068|-32.29,74.15550496|11.91,2.07",
        "MAIA"              : "MAIA,f|S|B8,3.76377962|21.09,24.36774851|-45.03,3.87",
        "MARKAB"            : "MARKAB,f|S|B9,23.07934827|61.1,15.20526441|-42.56,2.49",
        "MEGREZ"            : "MEGREZ,f|S|A3,12.25710003|103.56,57.03261698|7.81,3.32",
        "MENKALINAN"        : "MENKALINAN,f|S|A2,5.99214525|-56.41,44.94743277|-0.88,1.9",
        "MENKAR"            : "MENKAR,f|S|M2,3.03799227|-11.81,4.08973396|-78.76,2.54",
        "MENKENT"           : "MENKENT,f|S|K0,14.11137457|-519.29,-36.36995451|-517.87,2.06",
        "MERAK"             : "MERAK,f|S|A1,11.03068799|81.66,56.38242685|33.74,2.34",
        "MEROPE"            : "MEROPE,f|S|B6,3.77210384|21.17,23.94835835|-42.67,4.14",
        "MIAPLACIDUS"       : "MIAPLACIDUS,f|S|A2,9.21999318|-157.66,-69.71720776|108.91,1.67",
        "MIMOSA"            : "MIMOSA,f|S|B0,12.79535087|-48.24,-59.68876364|-12.82,1.25",
        "MINTAKA"           : "MINTAKA,f|S|O9,5.53344464|1.67,-0.29909204|0.56,2.25",
        "MIRACH"            : "MIRACH,f|S|M0,1.16220100|175.59,35.62055768|-112.23,2.07",
        "MIRFAK"            : "MIRFAK,f|S|F5,3.40538065|24.11,49.86117958|-26.01,1.79",
        "MIRZAM"            : "MIRZAM,f|S|B1,6.37832924|-3.45,-17.95591772|-0.47,1.98",
        "MIZAR"             : "MIZAR,f|S|A2,13.39876192|121.23,54.92536183|-22.01,2.23",
        "NAOS"              : "NAOS,f|S|O5,8.05973519|-30.82,-40.00314770|16.77,2.21",
        "NIHAL"             : "NIHAL,f|S|G5,5.47075644|-5.03,-20.75944096|-85.92,2.81",
        "NUNKI"             : "NUNKI,f|S|B2,18.92109048|13.87,-26.29672225|-52.65,2.05",
        "PEACOCK"           : "PEACOCK,f|S|B2,20.42746051|7.71,-56.73509009|-86.15,1.94",
        "PHECDA"            : "PHECDA,f|S|A0,11.89717984|107.76,53.69476015|11.16,2.41",
        "POLARIS"           : "POLARIS,f|S|F7,2.53030100|44.22,89.26410949|-11.74,1.97",
        "POLLUX"            : "POLLUX,f|S|K0,7.75526397|-625.69,28.02619865|-45.95,1.16",
        "PROCYON"           : "PROCYON,f|S|F5,7.65503283|-716.57,5.22499314|-1034.58,0.4",
        "RASALGETHI"        : "RASALGETHI,f|S|M5,17.24412734|-6.71,14.39033282|32.78,2.78",
        "RASALHAGUE"        : "RASALHAGUE,f|S|A5,17.58224183|110.08,12.56003481|-222.61,2.08",
        "REGULUS"           : "REGULUS,f|S|B7,10.13953074|-249.4,11.96720709|4.91,1.36",
        "RIGEL"             : "RIGEL,f|S|B8,5.24229787|1.87,-8.20164055|-0.56,0.18",
        "RIGIL KENTAURUS"   : "RIGIL KENTAURUS,f|S|G2,14.66013779|-3678.19,-60.83397588|481.84,-0.01",
        "RUKBAT"            : "RUKBAT,f|S|B8,19.39810458|32.67,-40.61593992|-120.81,3.96",
        "SABIK"             : "SABIK,f|S|A2,17.17296871|41.16,-15.72491023|97.65,2.43",
        "SADALMELIK"        : "SADALMELIK,f|S|G2,22.09639881|17.9,-0.31985069|-9.93,2.95",
        "SADR"              : "SADR,f|S|F8,20.37047275|2.43,40.25667924|-0.93,2.23",
        "SAIPH"             : "SAIPH,f|S|B0,5.79594135|1.55,-9.66960477|-1.2,2.07",
        "SCHEAT"            : "SCHEAT,f|S|M2,23.06290487|187.76,28.08278908|137.61,2.44",
        "SCHEDAR"           : "SCHEDAR,f|S|K0,0.67512237|50.36,56.53733107|-32.17,2.24",
        "SHAULA"            : "SHAULA,f|S|B1,17.56014444|-8.9,-37.10382115|-29.95,1.62",
        "SHELIAK"           : "SHELIAK,f|S|A8,18.83466519|1.1,33.36266704|-4.46,3.52",
        "SIRIUS"            : "SIRIUS,f|S|A0,6.75247697|-546.01,-16.71611569|-1223.08,-1.44",
        "SPICA"             : "SPICA,f|S|B1,13.41988313|-42.5,-11.16132203|-31.73,0.98",
        "SUHAIL"            : "SUHAIL,f|S|K4,9.13326624|-23.21,-43.43258935|14.28,2.23",
        "SULAFAT"           : "SULAFAT,f|S|B9,18.98239518|-2.76,32.68955742|1.77,3.25",
        "TARAZED"           : "TARAZED,f|S|K3,19.77099430|15.72,10.61326121|-3.08,2.72",
        "TAYGETA"           : "TAYGETA,f|S|B6,3.75347069|19.35,24.46727760|-41.63,4.3",
        "THUBAN"            : "THUBAN,f|S|A0,14.07315271|-56.52,64.37585053|17.19,3.67",
        "UNUKALHAI"         : "UNUKALHAI,f|S|K2,15.73779857|134.66,6.42562701|44.14,2.63",
        "VEGA"              : "VEGA,f|S|A0,18.61564903|201.02,38.78369185|287.46,0.03",
        "VINDEMIATRIX"      : "VINDEMIATRIX,f|S|G8,13.03627697|-275.05,10.95915039|19.96,2.85",
        "WEZEN"             : "WEZEN,f|S|F8,7.13985674|-2.75,-26.39319967|3.33,1.83",
        "ZAURAK"            : "ZAURAK,f|S|M1,3.96715732|60.51,-13.50851532|-111.34,2.97",
        "ZUBENELGENUBI"     : "ZUBENELGENUBI,f|S|A3,14.84797587|-105.69,-16.04177819|-69.0,2.75" }


    # Internally used to reference PyEphem objects.
    __PYEPHEM_CITY_LATITUDE = 0
    __PYEPHEM_CITY_LONGITUDE = 1
    __PYEPHEM_CITY_ELEVATION = 2

    __PYEPHEM_DATE_TUPLE_YEAR = 0
    __PYEPHEM_DATE_TUPLE_MONTH = 1
    __PYEPHEM_DATE_TUPLE_DAY = 2
    __PYEPHEM_DATE_TUPLE_HOUR = 3
    __PYEPHEM_DATE_TUPLE_MINUTE = 4
    __PYEPHEM_DATE_TUPLE_SECOND = 5

    __PYEPHEM_SATELLITE_RISING_DATE = 0
    __PYEPHEM_SATELLITE_RISING_ANGLE = 1
    __PYEPHEM_SATELLITE_CULMINATION_DATE = 2
    __PYEPHEM_SATELLITE_CULMINATION_ANGLE = 3
    __PYEPHEM_SATELLITE_SETTING_DATE = 4
    __PYEPHEM_SATELLITE_SETTING_ANGLE = 5


    @staticmethod
    def calculate(
            utcNow,
            latitude, longitude, elevation,
            planets,
            stars,
            satellites, satelliteData, startHourAsDateTimeInUTC, endHourAsDateTimeInUTC,
            comets, cometData, cometApparentMagnitudeData,
            minorPlanets, minorPlanetData, minorPlanetApparentMagnitudeData,
            apparentMagnitudeMaximum,
            logging ):

        data = { }

        ephemNow = ephem.Date( utcNow )

        observer = ephem.city( "London" ) # Any name will do; add in the correct latitude/longitude/elevation.
        observer.lat = str( latitude )
        observer.lon = str( longitude )
        observer.elev = elevation
        observer.date = ephemNow

        AstroPyEphem.__calculateMoon( ephemNow, observer, data )
        AstroPyEphem.__calculateSun( ephemNow, observer, data )
        AstroPyEphem.__calculatePlanets( observer, data, planets, apparentMagnitudeMaximum )
        AstroPyEphem.__calculateStars( observer, data, stars, apparentMagnitudeMaximum )

        AstroPyEphem.__calculateCometsMinorPlanets(
            observer, data,
            AstroBase.BodyType.COMET, comets, cometData, cometApparentMagnitudeData,
            apparentMagnitudeMaximum )

        AstroPyEphem.__calculateCometsMinorPlanets(
            observer, data,
            AstroBase.BodyType.MINOR_PLANET, minorPlanets, minorPlanetData, minorPlanetApparentMagnitudeData,
            apparentMagnitudeMaximum )

        AstroPyEphem.__calculateSatellites( ephemNow, observer, data, satellites, satelliteData, startHourAsDateTimeInUTC, endHourAsDateTimeInUTC )

        return data


    @staticmethod
    def getCities():
        return sorted( _city_data.keys(), key = locale.strxfrm )


    @staticmethod
    def getCredit():
        return _( "Calculations courtesy of PyEphem/XEphem. https://rhodesmill.org/pyephem" )


    @staticmethod
    def getLatitudeLongitudeElevation( city ):
        return \
            float( _city_data.get( city )[ AstroPyEphem.__PYEPHEM_CITY_LATITUDE ] ), \
            float( _city_data.get( city )[ AstroPyEphem.__PYEPHEM_CITY_LONGITUDE ] ), \
            _city_data.get( city )[ AstroPyEphem.__PYEPHEM_CITY_ELEVATION ]


    @staticmethod
    def getStatusMessage():
        minimalRequiredVersion = "4.1.3"
        installationCommand = "sudo apt-get install -y python3-pip\nsudo pip3 install --ignore-installed --upgrade ephem"
        message = None
        if not available:
            message = _( "PyEphem could not be found. Install using:\n\n" + installationCommand )

        elif LooseVersion( ephem.__version__ ) < LooseVersion( minimalRequiredVersion ):
            message = \
                _( "PyEphem must be version {0} or greater. Please upgrade:\n\n" + \
               installationCommand ).format( minimalRequiredVersion )

        return message


    @staticmethod
    def getVersion():
        return ephem.__version__


    @staticmethod
    def __calculateMoon( ephemNow, observer, data ):
        key = ( AstroBase.BodyType.MOON, AstroBase.NAME_TAG_MOON )
        moon = ephem.Moon( observer )
        sun = ephem.Sun( observer )

        data[ key + ( AstroBase.DATA_TAG_ILLUMINATION, ) ] = str( int( moon.phase ) ) # Needed for icon.

        phase = AstroBase.getLunarPhase( int( moon.phase ), ephem.next_full_moon( ephemNow ), ephem.next_new_moon( ephemNow ) ) # Need for notification.
        data[ key + ( AstroBase.DATA_TAG_PHASE, ) ] = phase

        brightLimb = AstroBase.getZenithAngleOfBrightLimb( ephemNow.datetime(), sun.ra, sun.dec, moon.ra, moon.dec, float( observer.lat ), float( observer.lon ) )
        data[ key + ( AstroBase.DATA_TAG_BRIGHT_LIMB, ) ] = str( brightLimb ) # Needed for icon.

        if not AstroPyEphem.__calculateCommon( data, ( AstroBase.BodyType.MOON, AstroBase.NAME_TAG_MOON ), observer, moon ):
            data[ key + ( AstroBase.DATA_TAG_FIRST_QUARTER, ) ] = AstroBase.toDateTimeString( ephem.next_first_quarter_moon( ephemNow ).datetime() )
            data[ key + ( AstroBase.DATA_TAG_FULL, ) ] = AstroBase.toDateTimeString( ephem.next_full_moon( ephemNow ).datetime() )
            data[ key + ( AstroBase.DATA_TAG_THIRD_QUARTER, ) ] = AstroBase.toDateTimeString( ephem.next_last_quarter_moon( ephemNow ).datetime() )
            data[ key + ( AstroBase.DATA_TAG_NEW, ) ] = AstroBase.toDateTimeString( ephem.next_new_moon( ephemNow ).datetime() )

            dateTime, eclipseType, latitude, longitude = eclipse.getEclipse( ephemNow.datetime(), True )
            data[ key + ( AstroBase.DATA_TAG_ECLIPSE_DATE_TIME, ) ] = dateTime
            data[ key + ( AstroBase.DATA_TAG_ECLIPSE_TYPE, ) ] = eclipseType
            data[ key + ( AstroBase.DATA_TAG_ECLIPSE_LATITUDE, ) ] = latitude
            data[ key + ( AstroBase.DATA_TAG_ECLIPSE_LONGITUDE, ) ] = longitude


    @staticmethod
    def __calculateSun( ephemNow, observer, data ):
        sun = ephem.Sun()
        sun.compute( observer )
        if not AstroPyEphem.__calculateCommon( data, ( AstroBase.BodyType.SUN, AstroBase.NAME_TAG_SUN ), observer, sun ):
            key = ( AstroBase.BodyType.SUN, AstroBase.NAME_TAG_SUN )
            equinox = ephem.next_equinox( ephemNow )
            solstice = ephem.next_solstice( ephemNow )
            data[ key + ( AstroBase.DATA_TAG_EQUINOX, ) ] = AstroBase.toDateTimeString( equinox.datetime() )
            data[ key + ( AstroBase.DATA_TAG_SOLSTICE, ) ] = AstroBase.toDateTimeString( solstice.datetime() )

            dateTime, eclipseType, latitude, longitude = eclipse.getEclipse( ephemNow.datetime(), False )
            data[ key + ( AstroBase.DATA_TAG_ECLIPSE_DATE_TIME, ) ] = dateTime
            data[ key + ( AstroBase.DATA_TAG_ECLIPSE_TYPE, ) ] = eclipseType
            data[ key + ( AstroBase.DATA_TAG_ECLIPSE_LATITUDE, ) ] = latitude
            data[ key + ( AstroBase.DATA_TAG_ECLIPSE_LONGITUDE, ) ] = longitude


    @staticmethod
    def __calculatePlanets( observer, data, planets, apparentMagnitudeMaximum ):
        for planet in planets:
            body = getattr( ephem, planet.title() )()
            body.compute( observer )
            if body.mag <= apparentMagnitudeMaximum:
                AstroPyEphem.__calculateCommon( data, ( AstroBase.BodyType.PLANET, planet ), observer, body )


    @staticmethod
    def __calculateStars( observer, data, stars, apparentMagnitudeMaximum ):
        for star in stars:
            # Did test obtaining the absolute magnitude directly from the ephemeris
            # before reading in and computing the body.
            # After timing tests, this makes no difference, so follow "traditional" route of
            # read, compute and obtain the absolute magnitude.
            body = ephem.readdb( AstroPyEphem.__EPHEMERIS_STARS[ star.upper() ] )
            body.compute( observer )
            if body.mag <= apparentMagnitudeMaximum:
                AstroPyEphem.__calculateCommon( data, ( AstroBase.BodyType.STAR, star ), observer, body )


    @staticmethod
    def __calculateCometsMinorPlanets( observer, data, bodyType, cometsMinorPlanets, orbitalElementData, apparentMagnitudeData, apparentMagnitudeMaximum ):

        def computeBody( observer, orbitalElementData ):
            body = ephem.readdb( orbitalElementData )
            body.compute( observer )
            return body


        def isBad( body ):
            try:
                bad = \
                    math.isnan( body.earth_distance ) or \
                    math.isnan( body.phase ) or \
                    math.isnan( body.size ) or \
                    math.isnan( body.sun_distance ) # Have found MPC data may contain ***** in lieu of actual data!

            except Exception as e:
#TODO Cannot release comets stuff until PyEphem 4.1.4 is released.
#TODO Once running PyEphem 4.1.4, can then easily determine which comets are causing the error and maybe report back to COBS.
                # Some comets with a near-parabolic orbit will trigger an error...
                # https://github.com/brandon-rhodes/pyephem/issues/239
                bad = True

            return bad


        if apparentMagnitudeData is None:
            for key in cometsMinorPlanets:
                if key in orbitalElementData:
                    body = computeBody( observer, orbitalElementData[ key ].getData() )
                    if not isBad( body ) and body.mag <= apparentMagnitudeMaximum:
                        AstroPyEphem.__calculateCommon( data, ( bodyType, key ), observer, body )

        else:
            for key in cometsMinorPlanets:
                if key in orbitalElementData and \
                   key in apparentMagnitudeData and \
                   float( apparentMagnitudeData[ key ].getApparentMagnitude() ) < apparentMagnitudeMaximum:
                    body = computeBody( observer, orbitalElementData[ key ].getData() )
                    if not isBad( body ):
                        AstroPyEphem.__calculateCommon( data, ( bodyType, key ), observer, body )


    # Calculates common attributes such as rise/set date/time, azimuth/altitude.
    #
    # Returns True if the body is never up; false otherwise.
    @staticmethod
    def __calculateCommon( data, key, observer, body ):
        neverUp = False
        try:
            # Must compute az/alt BEFORE rise/set otherwise results will be incorrect.
            data[ key + ( AstroBase.DATA_TAG_AZIMUTH, ) ] = repr( body.az )
            data[ key + ( AstroBase.DATA_TAG_ALTITUDE, ) ] = repr( body.alt )
            data[ key + ( AstroBase.DATA_TAG_RISE_DATE_TIME, ) ] = AstroBase.toDateTimeString( observer.next_rising( body ).datetime() )
            data[ key + ( AstroBase.DATA_TAG_SET_DATE_TIME, ) ] = AstroBase.toDateTimeString( observer.next_setting( body ).datetime() )

        except ephem.AlwaysUpError:
            pass

        except ephem.NeverUpError:
            del data[ key + ( AstroBase.DATA_TAG_AZIMUTH, ) ]
            del data[ key + ( AstroBase.DATA_TAG_ALTITUDE, ) ]
            neverUp = True

        return neverUp


    @staticmethod
    def __calculateSatellites( ephemNow, observer, data, satellites, satelliteData, startHourAsDateTimeInUTC, endHourAsDateTimeInUTC ):
        now = ephemNow.datetime().replace( tzinfo = datetime.timezone.utc )
        end = now + datetime.timedelta( hours = AstroBase.SATELLITE_SEARCH_DURATION_HOURS )
        windows = AstroBase.getStartEndWindows( now, end, startHourAsDateTimeInUTC, endHourAsDateTimeInUTC )

        observerVisiblePasses = observer.copy()
        observerVisiblePasses.pressure = 0
        observerVisiblePasses.horizon = "-0:34"

        for satellite in satellites:
            if satellite in satelliteData:
                key = ( AstroBase.BodyType.SATELLITE, satellite )
                earthSatellite = ephem.readtle( satelliteData[ satellite ].getName(), *satelliteData[ satellite ].getTLELineOneLineTwo() )
                for startDateTime, endDateTime in windows:
                    if AstroPyEphem.__calculateSatellite( ephem.Date( startDateTime ), ephem.Date( endDateTime ), data, key, earthSatellite, observer, observerVisiblePasses ):
                        break

        # The observer's date was constantly changed in the calculate satellite method,
        # so clean up before returning in case the observer is used later.
        observer.date = ephemNow


    @staticmethod
    def __calculateSatellite( startDateTime, endDateTime, data, key, earthSatellite, observer, observerVisiblePasses ):
        foundPass = False
        currentDateTime = startDateTime
        while currentDateTime < endDateTime:
            observer.date = currentDateTime
            earthSatellite.compute( observer )
            try:
                # Must set 'singlepass = False' as it is possible a pass is too quick/low and an exception is thrown.
                # https://github.com/brandon-rhodes/pyephem/issues/164
                # https://github.com/brandon-rhodes/pyephem/pull/85/files
                nextPass = observer.next_pass( earthSatellite, singlepass = False )
                if AstroPyEphem.__isSatellitePassValid( nextPass ):
                    passBeforeEndDateTime = nextPass[ AstroPyEphem.__PYEPHEM_SATELLITE_SETTING_DATE ] < endDateTime
                    passIsVisible = AstroPyEphem.__isSatellitePassVisible( observerVisiblePasses, earthSatellite, nextPass[ AstroPyEphem.__PYEPHEM_SATELLITE_CULMINATION_DATE ] )
                    if passBeforeEndDateTime and passIsVisible:
                        data[ key + ( AstroBase.DATA_TAG_RISE_DATE_TIME, ) ] = \
                            AstroBase.toDateTimeString( nextPass[ AstroPyEphem.__PYEPHEM_SATELLITE_RISING_DATE ].datetime() )

                        data[ key + ( AstroBase.DATA_TAG_RISE_AZIMUTH, ) ] = repr( nextPass[ AstroPyEphem.__PYEPHEM_SATELLITE_RISING_ANGLE ] )

                        data[ key + ( AstroBase.DATA_TAG_SET_DATE_TIME, ) ] = \
                            AstroBase.toDateTimeString( nextPass[ AstroPyEphem.__PYEPHEM_SATELLITE_SETTING_DATE ].datetime() )

                        data[ key + ( AstroBase.DATA_TAG_SET_AZIMUTH, ) ] = repr( nextPass[ AstroPyEphem.__PYEPHEM_SATELLITE_SETTING_ANGLE ] )
                        foundPass = True
                        break

                    # Look for the next pass starting shortly after current set.
                    currentDateTime = ephem.Date( nextPass[ AstroPyEphem.__PYEPHEM_SATELLITE_SETTING_DATE ] + ephem.minute * 15 ) # Bad pass data, so look shortly after the current time.

                else:
                    currentDateTime = ephem.Date( currentDateTime + ephem.minute * 15 ) # Bad pass data, so look shortly after the current time.

            except ValueError:
                if earthSatellite.circumpolar: # Satellite never rises/sets, so can only show current position.
                    data[ key + ( AstroBase.DATA_TAG_AZIMUTH, ) ] = repr( earthSatellite.az )
                    data[ key + ( AstroBase.DATA_TAG_ALTITUDE, ) ] = repr( earthSatellite.alt )
                    foundPass = True

                break

        return foundPass


    # Ensure:
    #    The satellite pass is numerically valid.
    #    Rise time exceeds transit time.
    #    Transit time exceeds set time.
    @staticmethod
    def __isSatellitePassValid( satellitePass ):
        return \
            satellitePass and \
            len( satellitePass ) == 6 and \
            satellitePass[ AstroPyEphem.__PYEPHEM_SATELLITE_RISING_DATE ] and \
            satellitePass[ AstroPyEphem.__PYEPHEM_SATELLITE_RISING_ANGLE ] and \
            satellitePass[ AstroPyEphem.__PYEPHEM_SATELLITE_CULMINATION_DATE ] and \
            satellitePass[ AstroPyEphem.__PYEPHEM_SATELLITE_CULMINATION_ANGLE ] and \
            satellitePass[ AstroPyEphem.__PYEPHEM_SATELLITE_SETTING_DATE ] and \
            satellitePass[ AstroPyEphem.__PYEPHEM_SATELLITE_SETTING_ANGLE ] and \
            satellitePass[ AstroPyEphem.__PYEPHEM_SATELLITE_CULMINATION_DATE ] > satellitePass[ AstroPyEphem.__PYEPHEM_SATELLITE_RISING_DATE ] and \
            satellitePass[ AstroPyEphem.__PYEPHEM_SATELLITE_SETTING_DATE ] > satellitePass[ AstroPyEphem.__PYEPHEM_SATELLITE_CULMINATION_DATE ]


    # Determine if a satellite pass is visible.
    #
    #    https://space.stackexchange.com/questions/4339/calculating-which-satellite-passes-are-visible
    #    https://stackoverflow.com/questions/19739831/is-there-any-way-to-calculate-the-visual-magnitude-of-a-satellite-iss
    #    https://www.celestrak.com/columns/v03n01
    @staticmethod
    def __isSatellitePassVisible( observerVisiblePasses, satellite, passDateTime ):
        observerVisiblePasses.date = passDateTime

        satellite.compute( observerVisiblePasses )
        sun = ephem.Sun()
        sun.compute( observerVisiblePasses )

        return \
            satellite.eclipsed is False and \
            sun.alt > ephem.degrees( "-18" ) and \
            sun.alt < ephem.degrees( "-6" )