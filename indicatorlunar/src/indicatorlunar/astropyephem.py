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


''' Calculate astronomical information using PyEphem. '''


import datetime
import locale
import math

import ephem

from ephem.cities import _city_data

from . import eclipse

from .astrobase import AstroBase


class AstroPyEphem( AstroBase ):
    ''' Wrapper frontend to the PyEphem library. '''

    # Internally used to reference PyEphem objects.
    _CITY_LATITUDE = 0
    _CITY_LONGITUDE = 1
    _CITY_ELEVATION = 2

    _PYEPHEM_DATE_TUPLE_YEAR = 0
    _PYEPHEM_DATE_TUPLE_MONTH = 1
    _PYEPHEM_DATE_TUPLE_DAY = 2
    _PYEPHEM_DATE_TUPLE_HOUR = 3
    _PYEPHEM_DATE_TUPLE_MINUTE = 4
    _PYEPHEM_DATE_TUPLE_SECOND = 5

    _PYEPHEM_SATELLITE_RISING_DATE = 0
    _PYEPHEM_SATELLITE_RISING_ANGLE = 1
    _PYEPHEM_SATELLITE_CULMINATION_DATE = 2
    _PYEPHEM_SATELLITE_CULMINATION_ANGLE = 3
    _PYEPHEM_SATELLITE_SETTING_DATE = 4
    _PYEPHEM_SATELLITE_SETTING_ANGLE = 5


    @staticmethod
    def calculate(
        utc_now,
        latitude,
        longitude,
        elevation,
        planets,
        stars,
        satellites,
        satellite_data,
        start_hour_as_date_time_in_utc,
        end_hour_as_date_time_in_utc,
        comets,
        comet_data,
        minor_planets,
        minor_planet_data,
        minor_planet_apparent_magnitude_data,
        apparent_magnitude_maximum,
        logging ):
        '''
        Calculate the rise/set/az/alt for all bodies.
        '''
        data = { }

        # PyEphem date/time is NOT timezone aware.
        ephem_now = ephem.Date( utc_now )

        observer = ephem.city( "London" ) # Any name will do for now.
        observer.lat = str( latitude )
        observer.lon = str( longitude )
        observer.elev = elevation
        observer.date = ephem_now

        AstroPyEphem._calculate_moon(
            ephem_now,
            observer,
            data )

        AstroPyEphem._calculate_sun(
            ephem_now,
            observer,
            data )

        AstroPyEphem._calculate_planets(
            observer,
            data,
            planets,
            apparent_magnitude_maximum )

        AstroPyEphem._calculate_stars(
            observer,
            data,
            stars,
            apparent_magnitude_maximum )

        AstroPyEphem._calculate_comets(
            observer,
            data,
            comets, comet_data,
            apparent_magnitude_maximum,
            logging )

        AstroPyEphem._calculate_minor_planets(
            observer,
            data,
            minor_planets,
            minor_planet_data,
            apparent_magnitude_maximum,
            minor_planet_apparent_magnitude_data )

        AstroPyEphem._calculate_satellites(
            ephem_now,
            observer,
            data,
            satellites,
            satellite_data,
            start_hour_as_date_time_in_utc,
            end_hour_as_date_time_in_utc )

        return data


    @staticmethod
    def get_cities():
        '''
        Return the list of sorted cities.
        '''
        return sorted( _city_data.keys(), key = locale.strxfrm )


    @staticmethod
    def get_credit():
        '''
        Return rhe credit.
        '''
        return "PyEphem https://github.com/brandon-rhodes/pyephem"


    @staticmethod
    def get_latitude_longitude_elevation(
        city ):
        '''
        Return the city's latitude, longitude and elevation.
        '''
        city_ = _city_data.get( city )

        return (
            float( city_[ AstroPyEphem._CITY_LATITUDE ] ),
            float( city_[ AstroPyEphem._CITY_LONGITUDE ] ),
            city_[ AstroPyEphem._CITY_ELEVATION ] )


    @staticmethod
    def get_version():
        '''
        Return the version.
        '''
        return ephem.__version__


    @staticmethod
    def _calculate_moon(
        ephem_now,
        observer,
        data ):

        key = ( AstroBase.BodyType.MOON, AstroBase.NAME_TAG_MOON )
        moon = ephem.Moon( observer )
        sun = ephem.Sun( observer )

        # Needed for icon.
        data[ key + ( AstroBase.DATA_TAG_ILLUMINATION, ) ] = str( moon.phase )

        # Need for notification.
        phase = (
            AstroBase.get_lunar_phase(
                moon.phase,
                ephem.next_full_moon( ephem_now ),
                ephem.next_new_moon( ephem_now ) ) )

        data[ key + ( AstroBase.DATA_TAG_PHASE, ) ] = phase

        bright_limb = (
            AstroBase.get_zenith_angle_of_bright_limb(
                ephem_now.datetime().replace( tzinfo = datetime.timezone.utc ),
                sun.ra, sun.dec,
                moon.ra, moon.dec,
                float( observer.lat ), float( observer.lon ) ) )

        # Needed for icon.
        data[ key + ( AstroBase.DATA_TAG_BRIGHT_LIMB, ) ] = str( bright_limb )

        never_up = (
            AstroPyEphem._calculate_common(
                data,
                ( AstroBase.BodyType.MOON, AstroBase.NAME_TAG_MOON ),
                observer,
                moon ) )

        if not never_up:
            next_first_quarter = (
                ephem.next_first_quarter_moon( ephem_now ).datetime() )

            data[ key + ( AstroBase.DATA_TAG_FIRST_QUARTER, ) ] = (
                next_first_quarter.replace( tzinfo = datetime.timezone.utc ) )

            next_full = ephem.next_full_moon( ephem_now ).datetime()
            data[ key + ( AstroBase.DATA_TAG_FULL, ) ] = (
                next_full.replace( tzinfo = datetime.timezone.utc ) )

            next_last_quarter = (
                ephem.next_last_quarter_moon( ephem_now ).datetime() )

            data[ key + ( AstroBase.DATA_TAG_THIRD_QUARTER, ) ] = (
                next_last_quarter.replace( tzinfo = datetime.timezone.utc ) )

            next_new = ephem.next_new_moon( ephem_now ).datetime()
            data[ key + ( AstroBase.DATA_TAG_NEW, ) ] = (
                next_new.replace( tzinfo = datetime.timezone.utc ) )

            AstroPyEphem._calculate_eclipse( ephem_now, data, key, False )


    @staticmethod
    def _calculate_sun(
        ephem_now,
        observer,
        data ):

        sun = ephem.Sun()
        sun.compute( observer )

        never_up = (
            AstroPyEphem._calculate_common(
                data,
                ( AstroBase.BodyType.SUN, AstroBase.NAME_TAG_SUN ),
                observer,
                sun ) )

        if not never_up:
            key = ( AstroBase.BodyType.SUN, AstroBase.NAME_TAG_SUN )

            next_equinox = ephem.next_equinox( ephem_now ).datetime()
            data[ key + ( AstroBase.DATA_TAG_EQUINOX, ) ] = (
                next_equinox.replace( tzinfo = datetime.timezone.utc ) )

            next_solstice = ephem.next_solstice( ephem_now ).datetime()
            data[ key + ( AstroBase.DATA_TAG_SOLSTICE, ) ] = (
                next_solstice.replace( tzinfo = datetime.timezone.utc ) )

            AstroPyEphem._calculate_eclipse( ephem_now, data, key, True )


    @staticmethod
    def _calculate_eclipse(
        ephem_now,
        data,
        key,
        is_solar ):

        if is_solar:
            eclipse_function = "get_eclipse_solar"

        else:
            eclipse_function = "get_eclipse_lunar"

        date_time, eclipse_type, latitude, longitude = (
            getattr( eclipse, eclipse_function )(
                ephem_now.datetime().replace( tzinfo = datetime.timezone.utc ) ) )

        data[ key + ( AstroBase.DATA_TAG_ECLIPSE_DATE_TIME, ) ] = (
            date_time.replace( tzinfo = datetime.timezone.utc ) )

        data[ key + ( AstroBase.DATA_TAG_ECLIPSE_TYPE, ) ] = eclipse_type
        data[ key + ( AstroBase.DATA_TAG_ECLIPSE_LATITUDE, ) ] = latitude
        data[ key + ( AstroBase.DATA_TAG_ECLIPSE_LONGITUDE, ) ] = longitude


    @staticmethod
    def _calculate_planets(
        observer,
        data,
        planets,
        apparent_magnitude_maximum ):

        for planet in planets:
            body = getattr( ephem, planet.title() )()
            body.compute( observer )
            if body.mag <= apparent_magnitude_maximum:
                AstroPyEphem._calculate_common(
                    data,
                    ( AstroBase.BodyType.PLANET, planet ),
                    observer, body )


    @staticmethod
    def _calculate_stars(
        observer,
        data,
        stars,
        apparent_magnitude_maximum ):

        for star in stars:
            # Did a test obtaining the absolute magnitude directly from the
            # ephemeris before reading in and computing the body.
            #
            # After timing tests, this makes no difference, so follow the
            # "traditional" route of read, compute and obtain the absolute
            # magnitude.
            body = ephem.star( star.title() )
            body.compute( observer )
            if body.mag <= apparent_magnitude_maximum:
                AstroPyEphem._calculate_common(
                    data,
                    ( AstroBase.BodyType.STAR, star ),
                    observer,
                    body )


    @staticmethod
    def _calculate_comets(
        observer,
        data,
        comets,
        orbital_element_data,
        apparent_magnitude_maximum,
        logging ):

        sun = ephem.Sun()
        sun.compute( observer )
        for key in comets:
            if key in orbital_element_data:
                fields = orbital_element_data[ key ].get_data().split( ',' )
                object_type = fields[ 2 - 1 ]
                is_gk = True
                if object_type == 'e':
                    absolute_magnitude = fields[ 12 - 1 ]
                    slope_parameter = fields[ 13 - 1 ]
                    if absolute_magnitude.startswith( 'H' ):
                        is_gk = False
                        absolute_magnitude = absolute_magnitude[ 1 : ].strip()

                    elif absolute_magnitude.startswith( 'g' ):
                        absolute_magnitude = absolute_magnitude[ 1 : ].strip()

                elif object_type == 'h':
                    absolute_magnitude = fields[ 10 - 1 ]
                    slope_parameter = fields[ 11 - 1 ]

                elif object_type == 'p':
                    absolute_magnitude = fields[ 9 - 1 ]
                    slope_parameter = fields[ 10 - 1 ]

                else:
                    logging.warning(
                        "Found unknown object type " +
                        object_type +
                        " for comet " +
                        key )

                    continue

                body = (
                    AstroPyEphem._compute_minor_planet_or_comet_for_observer(
                        observer,
                        orbital_element_data[ key ].get_data() ) )

                if not AstroPyEphem._is_comet_or_minor_planet_bad( body ):
                    if is_gk:
                        apparent_magnitude = (
                            AstroBase.get_apparent_magnitude_gk(
                                float( absolute_magnitude ),
                                float( slope_parameter ),
                                body.earth_distance,
                                body.sun_distance ) )

                    else:
                        apparent_magnitude = (
                            AstroBase.get_apparent_magnitude_hg(
                                float( absolute_magnitude ),
                                float( slope_parameter ),
                                body.earth_distance,
                                body.sun_distance,
                                sun.earth_distance ) )

                    if apparent_magnitude <= apparent_magnitude_maximum:
                        AstroPyEphem._calculate_common(
                            data,
                            ( AstroBase.BodyType.COMET, key ),
                            observer,
                            body )


    @staticmethod
    def _calculate_minor_planets(
        observer,
        data,
        minor_planets,
        orbital_element_data,
        apparent_magnitude_maximum,
        apparent_magnitude_data ):

        for key in minor_planets:
            if key in orbital_element_data and key in apparent_magnitude_data:
                apparent_magnitude = (
                   float( apparent_magnitude_data[ key ].get_apparent_magnitude() ) )

                if apparent_magnitude < apparent_magnitude_maximum:
                    body = (
                        AstroPyEphem._compute_minor_planet_or_comet_for_observer(
                            observer,
                            orbital_element_data[ key ].get_data() ) )

                    if not AstroPyEphem._is_comet_or_minor_planet_bad( body ):
                        AstroPyEphem._calculate_common(
                            data,
                            ( AstroBase.BodyType.MINOR_PLANET, key ),
                            observer,
                            body )


    @staticmethod
    def _compute_minor_planet_or_comet_for_observer(
        observer,
        orbital_element_data ):

        body = ephem.readdb( orbital_element_data )
        body.compute( observer )
        return body


    @staticmethod
    def _is_comet_or_minor_planet_bad(
        body ):
        '''
        Data from Minor Planet Center at times contains ***** so guard against.

        MPC data is no longer used; regardless, continue to guard,
        regardless of the source.

        Further, near-parabolic orbits will trigger a RuntimeError in PyEphem:
            https://github.com/brandon-rhodes/pyephem/issues/239
        '''
        try:
            bad = (
                math.isnan( body.earth_distance ) or
                math.isnan( body.phase ) or
                math.isnan( body.size ) or
                math.isnan( body.sun_distance ) )

        except RuntimeError:
            bad = True

        return bad


    @staticmethod
    def _calculate_common(
        data,
        key,
        observer,
        body ):
        '''
        Calculates common attributes such as rise/set date/time,
        azimuth/altitude.

        Returns True if the body is never up; false otherwise.
        '''
        never_up = False
        try:
            # Must compute az/alt BEFORE rise/set otherwise results
            # will be incorrect.
            data[ key + ( AstroBase.DATA_TAG_AZIMUTH, ) ] = repr( body.az )
            data[ key + ( AstroBase.DATA_TAG_ALTITUDE, ) ] = repr( body.alt )

            next_rise = (
                observer.next_rising( body ).datetime() )

            data[ key + ( AstroBase.DATA_TAG_RISE_DATE_TIME, ) ] = (
                next_rise.replace( tzinfo = datetime.timezone.utc ) )

            next_set = (
                observer.next_setting( body ).datetime() )

            data[ key + ( AstroBase.DATA_TAG_SET_DATE_TIME, ) ] = (
                next_set.replace( tzinfo = datetime.timezone.utc ) )

        except ephem.AlwaysUpError:
            pass

        except ephem.NeverUpError:
            del data[ key + ( AstroBase.DATA_TAG_AZIMUTH, ) ]
            del data[ key + ( AstroBase.DATA_TAG_ALTITUDE, ) ]
            never_up = True

        return never_up


    @staticmethod
    def _calculate_satellites(
        ephem_now,
        observer,
        data,
        satellites,
        satellite_data,
        start_hour_as_date_time_in_utc,
        end_hour_as_date_time_in_utc ):

        utc_now = ephem_now.datetime().replace( tzinfo = datetime.timezone.utc )

        utc_now_plus_search_duration = (
            utc_now +
            datetime.timedelta( hours = AstroBase.SATELLITE_SEARCH_DURATION_HOURS ) )

        windows = (
            AstroBase.get_start_end_windows(
                utc_now,
                utc_now_plus_search_duration,
                start_hour_as_date_time_in_utc,
                end_hour_as_date_time_in_utc ) )

        observer_visible_passes = observer.copy()
        observer_visible_passes.pressure = 0
        observer_visible_passes.horizon = "-0:34"

        for satellite in satellites:
            if satellite in satellite_data:
                key = ( AstroBase.BodyType.SATELLITE, satellite )
                earth_satellite = (
                    ephem.readtle(
                        satellite_data[ satellite ].get_name(),
                        *satellite_data[ satellite ].get_tle_line_one_line_two() ) )

                for start_date_time, end_date_time in windows:
                    found_pass = (
                        AstroPyEphem._calculate_satellite(
                            ephem.Date( start_date_time ),
                            ephem.Date( end_date_time ),
                            data,
                            key,
                            earth_satellite,
                            observer,
                            observer_visible_passes ) )

                    if found_pass:
                        break

        # Observer's date was changed in the calculate satellite method,
        # so clean up before returning in case the observer is used later.
        observer.date = ephem_now


    @staticmethod
    def _calculate_satellite(
        start_date_time,
        end_date_time,
        data,
        key,
        earth_satellite,
        observer,
        observer_visible_passes ):

        found_pass = False
        current_date_time = start_date_time
        while current_date_time < end_date_time:
            observer.date = current_date_time
            earth_satellite.compute( observer )
            try:
                # Must set 'singlepass = False' as it is possible a pass
                # is too quick/low and an exception is thrown.
                # https://github.com/brandon-rhodes/pyephem/issues/164
                # https://github.com/brandon-rhodes/pyephem/pull/85/files
                next_pass = (
                    observer.next_pass( earth_satellite, singlepass = False ) )

                if AstroPyEphem._is_satellite_pass_valid( next_pass ):
                    pass_before_end_date_time = (
                        next_pass[ AstroPyEphem._PYEPHEM_SATELLITE_SETTING_DATE ]
                        <
                        end_date_time )

                    pass_is_visible = (
                        AstroPyEphem._is_satellite_pass_visible(
                            observer_visible_passes,
                            earth_satellite,
                            next_pass[ AstroPyEphem._PYEPHEM_SATELLITE_CULMINATION_DATE ] ) )

                    if pass_before_end_date_time and pass_is_visible:
                        next_rise = next_pass[ AstroPyEphem._PYEPHEM_SATELLITE_RISING_DATE ]
                        next_rise = next_rise.datetime().replace( tzinfo = datetime.timezone.utc )
                        data[ key + ( AstroBase.DATA_TAG_RISE_DATE_TIME, ) ] = (
                            next_rise )

                        data[ key + ( AstroBase.DATA_TAG_RISE_AZIMUTH, ) ] = (
                            repr( next_pass[ AstroPyEphem._PYEPHEM_SATELLITE_RISING_ANGLE ] ) )

                        next_set = next_pass[ AstroPyEphem._PYEPHEM_SATELLITE_SETTING_DATE ]
                        next_set = next_set.datetime().replace( tzinfo = datetime.timezone.utc )
                        data[ key + ( AstroBase.DATA_TAG_SET_DATE_TIME, ) ] = (
                            next_set )

                        data[ key + ( AstroBase.DATA_TAG_SET_AZIMUTH, ) ] = (
                            repr( next_pass[ AstroPyEphem._PYEPHEM_SATELLITE_SETTING_ANGLE ] ) )

                        found_pass = True
                        break

                    # Look for the next pass starting shortly after current set.
                    current_date_time = (
                        ephem.Date(
                            next_pass[ AstroPyEphem._PYEPHEM_SATELLITE_SETTING_DATE ] +
                            ephem.minute * 15 ) )

                else:
                    # Bad pass data, so look shortly after the current time.
                    current_date_time = (
                        ephem.Date( current_date_time + ephem.minute * 15 ) )

            except ValueError:
                if earth_satellite.circumpolar:
                    # Satellite never rises/sets,
                    # so can only show current position.
                    data[ key + ( AstroBase.DATA_TAG_AZIMUTH, ) ] = (
                        repr( earth_satellite.az ) )

                    data[ key + ( AstroBase.DATA_TAG_ALTITUDE, ) ] = (
                        repr( earth_satellite.alt ) )

                    found_pass = True

                break

        return found_pass


    @staticmethod
    def _is_satellite_pass_valid(
        satellite_pass ):
        '''
        Ensure
            The satellite pass is numerically valid.
            Rise time exceeds transit time.
            Transit time exceeds set time.
        '''
        return (
            satellite_pass
            and
            len( satellite_pass ) == 6
            and
            satellite_pass[ AstroPyEphem._PYEPHEM_SATELLITE_RISING_DATE ]
            and
            satellite_pass[ AstroPyEphem._PYEPHEM_SATELLITE_RISING_ANGLE ]
            and
            satellite_pass[ AstroPyEphem._PYEPHEM_SATELLITE_CULMINATION_DATE ]
            and
            satellite_pass[ AstroPyEphem._PYEPHEM_SATELLITE_CULMINATION_ANGLE ]
            and
            satellite_pass[ AstroPyEphem._PYEPHEM_SATELLITE_SETTING_DATE ]
            and
            satellite_pass[ AstroPyEphem._PYEPHEM_SATELLITE_SETTING_ANGLE ]
            and
            satellite_pass[ AstroPyEphem._PYEPHEM_SATELLITE_CULMINATION_DATE ]
            >
            satellite_pass[ AstroPyEphem._PYEPHEM_SATELLITE_RISING_DATE ]
            and
            satellite_pass[ AstroPyEphem._PYEPHEM_SATELLITE_SETTING_DATE ]
            >
            satellite_pass[ AstroPyEphem._PYEPHEM_SATELLITE_CULMINATION_DATE ] )


    @staticmethod
    def _is_satellite_pass_visible(
        observer_visible_passes,
        satellite,
        pass_date_time ):
        '''
        Determine if a satellite pass is visible.

            https://space.stackexchange.com/q/4339/3442
            https://stackoverflow.com/q/19739831/2156453
            https://celestrak.org/columns/v03n01
        '''
        observer_visible_passes.date = pass_date_time
        satellite.compute( observer_visible_passes )
        sun = ephem.Sun()
        sun.compute( observer_visible_passes )

        return (
            not satellite.eclipsed and
            sun.alt > ephem.degrees( "-18" ) and
            sun.alt < ephem.degrees( "-6" ) )
