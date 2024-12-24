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


'''
Base class to provide tidal information used by Indicator Tide.
The end user must create their own Python script,
containing a class which extends this abstract base class and
implements the abstract method get_tide_data().
'''


from abc import ABC, abstractmethod


class TideDataGetterBase( ABC ):
    ''' Base class for obtaining tidal information. '''

    @staticmethod
    @abstractmethod
    def get_tide_data( logging = None, url_timeout_in_seconds = 20 ):
        '''
        User must implement this function within their own class
        to retrieve tidal data (from whatever source)
        and return a list of tidal readings.
        For example:

        import tide
        url = "http://url-used-to-obtain-tidal-information"

        # Convert tidal data from your URL to tide.Reading().

        return [
            tide.Reading( "Tuesday August 3rd", "4:07 AM", "The port", True, 1.6, url ),
            tide.Reading( "Tuesday August 3rd", "10:31 AM", "The port", False, 0.3, url ),
            tide.Reading( "Wednesday August 4th", "5:26 AM", "The port", True, 1.5, url ) ]

        Do not include @abstractmethod at the top of your own function.
        '''
        raise NotImplementedError()
