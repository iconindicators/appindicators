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

    # Created to contain only commonly named stars using 'createephemerisstars.py'.
    STAR_DATA = [
        "3C 273,f|S|  ,12.48519276|-11.01,2.05239846|4.38,12.88", #TODO Waiting on https://github.com/brandon-rhodes/pyephem/issues/244 to see if we keep this.
        "ACAMAR,f|S|A4,2.97102074|-53.53,-40.30467239|25.71,2.88",
        "ACAMAR,f|S|A4,2.97102074|-53.53,-40.30467239|25.71,2.88",
        "ACHERNAR,f|S|B3,1.62856849|88.02,-57.23675744|-40.08,0.45",
        "ACRUX,f|S|B0,12.44330439|-35.37,-63.09909168|-14.73,0.77",
        "ADHARA,f|S|B2,6.97709679|2.63,-28.97208374|2.29,1.5",
        "AGENA,f|S|B1,14.06372347|-33.96,-60.37303932|-25.06,0.61",
        "ALBIREO,f|S|K3,19.51202239|-7.09,27.95968112|-5.63,3.05",
        "ALCOR,f|S|A5,13.42042721|120.35,54.98795774|-16.94,3.99",
        "ALCYONE,f|S|B7,3.79141014|19.35,24.10513714|-43.11,2.85",
        "ALDEBARAN,f|S|K5,4.59867740|62.78,16.50930138|-189.36,0.87",
        "ALDERAMIN,f|S|A7,21.30965876|149.91,62.58557256|48.27,2.45",
        "ALGENIB,f|S|B2,0.22059801|4.7,15.18359590|-8.24,2.83",
        "ALGIEBA,f|S|K0,10.33287623|310.77,19.84148875|-152.88,2.01",
        "ALGOL,f|S|B8,3.13614765|2.39,40.95564766|-1.44,2.09",
        "ALHENA,f|S|A0,6.62852808|-2.04,16.39925217|-66.92,1.93",
        "ALIOTH,f|S|A0,12.90048595|111.74,55.95982123|-8.99,1.76",
        "ALKAID,f|S|B3,13.79234379|-121.23,49.31326512|-15.56,1.85",
        "ALMAAK,f|S|B8,2.06498696|43.08,42.32972472|-50.85,2.1",
        "ALNAIR,f|S|B7,22.13721819|127.6,-46.96097539|-147.91,1.73",
        "ALNATH,f|S|B7,5.43819816|23.28,28.60745000|-174.22,1.65",
        "ALNILAM,f|S|B0,5.60355929|1.49,-1.20191983|-1.06,1.69",
        "ALNITAK,f|S|O9,5.67931309|3.99,-1.94257224|2.54,1.74",
        "ALPHARD,f|S|K3,9.45978980|-14.49,-8.65860253|33.25,1.99",
        "ALPHEKKA,f|S|A0,15.57813004|120.38,26.71469307|-89.44,2.22",
        "ALPHERATZ,f|S|B9,0.13979405|135.68,29.09043197|-162.95,2.07",
        "ALSHAIN,f|S|G8,19.92188706|46.35,6.40676348|-481.32,3.71",
        "ALTAIR,f|S|A7,19.84638864|536.82,8.86832203|385.54,0.76",
        "ANKAA,f|S|K0,0.43806972|232.76,-42.30598144|-353.64,2.4",
        "ANTARES,f|S|M1,16.49012803|-10.16,-26.43200250|-23.21,1.06",
        "ARCTURUS,f|S|K2,14.26102001|-1093.45,19.18241038|-1999.4,-0.05",
        "ARNEB,f|S|F0,5.54550442|3.27,-17.82228853|1.54,2.58",
        "BABCOCK'S STAR,f|S|A0,22.73541819|4.96,55.58922579|-0.98,8.83",
        "BARNARD'S STAR,f|S|sd,17.96347189|-797.84,4.69338850|10326.93,9.54",
        "BELLATRIX,f|S|B2,5.41885085|-8.75,6.34970223|-13.28,1.64",
        "BETELGEUSE,f|S|M2,5.91952924|27.33,7.40706274|10.86,0.45",
        "CAMPBELL'S STAR,f|S|WC,19.57923121|-4.16,30.51637117|-10.19,10.0",
        "CANOPUS,f|S|F0,6.39919718|19.99,-52.69566045|23.67,-0.62",
        "CAPELLA,f|S|M1,5.27815528|75.52,45.99799106|-427.13,0.08",
        "CAPH,f|S|F2,0.15296808|523.39,59.14977950|-180.42,2.28",
        "CASTOR,f|S|A2,7.57662855|-206.33,31.88827631|-148.18,1.58",
        "COR CAROLI,f|S|A0,12.93379649|-233.43,38.31837984|54.98,2.89",
        "CYG X-1,f|S|B0,19.97268767|-3.82,35.20160419|-7.62,8.84",
        "DENEB,f|S|A2,20.69053187|1.56,45.28033800|1.55,1.25",
        "DENEBOLA,f|S|A3,11.81766043|-499.02,14.57206038|-113.78,2.14",
        "DIPHDA,f|S|K0,0.72649196|232.79,-17.98660457|32.71,2.04",
        "DUBHE,f|S|F7,11.06213019|-136.46,61.75103324|-35.25,1.81",
        "ENIF,f|S|K2,21.73643281|30.02,9.87501126|1.38,2.38",
        "ETAMIN,f|S|K5,17.94343608|-8.52,51.48889500|-23.05,2.24",
        "FOMALHAUT,f|S|A3,22.96084626|329.22,-29.62223601|-164.22,1.17",
        "GROOMBRIDGE 1830,f|S|G8,11.88299133|4003.69,37.71867896|-5813.0,6.42",
        "HADAR,f|S|B1,14.06372347|-33.96,-60.37303932|-25.06,0.61",
        "HAMAL,f|S|K2,2.11955753|190.73,23.46242310|-145.77,2.01",
        "IZAR,f|S|A0,14.74978270|-50.65,27.07422246|20.0,2.35",
        "KAPTEYN'S STAR,f|S|M0,5.19460603|6506.05,-45.01841480|-5731.39,8.86",
        "KAUS AUSTRALIS,f|S|B9,18.40286620|-39.61,-34.38461611|-124.05,1.79",
        "KOCAB,f|S|K4,14.84509068|-32.29,74.15550496|11.91,2.07",
        "KRUGER 60,f|S|M2,22.46651886|-870.23,57.69587466|-471.1,9.59",
        "LUYTEN'S STAR,f|S|M5,7.45680528|571.27,5.22578531|-3694.25,9.84",
        "MARKAB,f|S|B9,23.07934827|61.1,15.20526441|-42.56,2.49",
        "MEGREZ,f|S|A3,12.25710003|103.56,57.03261698|7.81,3.32",
        "MENKAR,f|S|M2,3.03799227|-11.81,4.08973396|-78.76,2.54",
        "MERAK,f|S|A1,11.03068799|81.66,56.38242685|33.74,2.34",
        "MINTAKA,f|S|O9,5.53344464|1.67,-0.29909204|0.56,2.25",
        "MIRA,f|S|M5,2.32244241|10.33,-2.97764262|-239.48,6.47",
        "MIRACH,f|S|M0,1.16220100|175.59,35.62055768|-112.23,2.07",
        "MIRPHAK,f|S|F5,3.40538065|24.11,49.86117958|-26.01,1.79",
        "MIZAR,f|S|A2,13.39876192|121.23,54.92536183|-22.01,2.23",
        "NIHAL,f|S|G5,5.47075644|-5.03,-20.75944096|-85.92,2.81",
        "NUNKI,f|S|B2,18.92109048|13.87,-26.29672225|-52.65,2.05",
        "PHAD,f|S|A0,11.89717984|107.76,53.69476015|11.16,2.41",
        "PLEIONE,f|S|B7,3.81978223|18.71,24.13671204|-46.74,5.05",
        "POLARIS,f|S|F7,2.53030100|44.22,89.26410949|-11.74,1.97",
        "POLLUX,f|S|K0,7.75526397|-625.69,28.02619865|-45.95,1.16",
        "PROCYON,f|S|F5,7.65503283|-716.57,5.22499314|-1034.58,0.4",
        "PROXIMA,f|S|M5,14.49526359|-3775.64,-62.67948489|768.16,11.01",
        "RASALGETHI,f|S|M5,17.24412734|-6.71,14.39033282|32.78,2.78",
        "RASALHAGUE,f|S|A5,17.58224183|110.08,12.56003481|-222.61,2.08",
        "RED RECTANGLE,f|S|B8,6.33283777|-10.98,-10.63741419|-21.1,8.85",
        "REGULUS,f|S|B7,10.13953074|-249.4,11.96720709|4.91,1.36",
        "RIGEL,f|S|B8,5.24229787|1.87,-8.20164055|-0.56,0.18",
        "RIGIL KENT,f|S|G2,14.66013779|-3678.19,-60.83397588|481.84,-0.01",
        "SADALMELIK,f|S|G2,22.09639881|17.9,-0.31985069|-9.93,2.95",
        "SAIPH,f|S|B0,5.79594135|1.55,-9.66960477|-1.2,2.07",
        "SCHEAT,f|S|M2,23.06290487|187.76,28.08278908|137.61,2.44",
        "SHAULA,f|S|B1,17.56014444|-8.9,-37.10382115|-29.95,1.62",
        "SHEDIR,f|S|K0,0.67512237|50.36,56.53733107|-32.17,2.24",
        "SHELIAK,f|S|A8,18.83466519|1.1,33.36266704|-4.46,3.52",
        "SIRIUS,f|S|A0,6.75247697|-546.01,-16.71611569|-1223.08,-1.44",
        "SPICA,f|S|B1,13.41988313|-42.5,-11.16132203|-31.73,0.98",
        "TARAZED,f|S|K3,19.77099430|15.72,10.61326121|-3.08,2.72",
        "THUBAN,f|S|A0,14.07315271|-56.52,64.37585053|17.19,3.67",
        "UNUKALHAI,f|S|K2,15.73779857|134.66,6.42562701|44.14,2.63",
        "VAN MAANEN 2,f|S|DG,0.81941655|1233.05,5.38860957|-2710.56,12.37",
        "VEGA,f|S|A0,18.61564903|201.02,38.78369185|287.46,0.03",
        "VINDEMIATRIX,f|S|G8,13.03627697|-275.05,10.95915039|19.96,2.85",
        "ZAURAK,f|S|M1,3.96715732|60.51,-13.50851532|-111.34,2.97" ]


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

        if not AstroPyEphem.__calculateCommon( data, observer, moon, AstroBase.BodyType.MOON, AstroBase.NAME_TAG_MOON ):
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
        if not AstroPyEphem.__calculateCommon( data, observer, sun, AstroBase.BodyType.SUN, AstroBase.NAME_TAG_SUN ):
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
                AstroPyEphem.__calculateCommon( data, observer, body, AstroBase.BodyType.PLANET, planet )


    @staticmethod
    def __calculateStars( observer, data, stars, apparentMagnitudeMaximum ):
        for star in stars:
            body = ephem.readdb( next( x for x in AstroPyEphem.STAR_DATA if ( star + "," ) in x ) )
            body.compute( observer )
            if body.mag <= apparentMagnitudeMaximum:
                AstroPyEphem.__calculateCommon( data, observer, body, AstroBase.BodyType.STAR, star )

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
                    math.isnan( body.sun_distance ) # Have found the data file may contain ***** in lieu of actual data!

            except Exception as e:
#TODO Cannot release comets stuff until PyEphem 4.1.4 is released.
                # Some comets with a near-parabolic orbit will trigger an error...
                # https://github.com/brandon-rhodes/pyephem/issues/239
                bad = True

            return bad


        if apparentMagnitudeData is None:
            for key in cometsMinorPlanets:
                if key in orbitalElementData:
                    body = computeBody( observer, orbitalElementData[ key ].getData() )
                    if not isBad( body ) and body.mag <= apparentMagnitudeMaximum:
                        AstroPyEphem.__calculateCommon( data, observer, body, bodyType, key )

        else:
            for key in cometsMinorPlanets:
                if key in orbitalElementData and key in apparentMagnitudeData and float( apparentMagnitudeData[ key ].getApparentMagnitude() ) < apparentMagnitudeMaximum:
                    body = computeBody( observer, orbitalElementData[ key ].getData() )
                    if not isBad( body ):
                        AstroPyEphem.__calculateCommon( data, observer, body, bodyType, key )


    # Calculates common attributes such as rise/set date/time, azimuth/altitude.
    #
    # Returns True if the body is never up; false otherwise.
    @staticmethod
    def __calculateCommon( data, observer, body, bodyType, nameTag ):
        neverUp = False
        key = ( bodyType, nameTag )
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
                earthSatellite = ephem.readtle( satelliteData[ satellite ].getName(), *satelliteData[ satellite ].getLineOneLineTwo() )
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