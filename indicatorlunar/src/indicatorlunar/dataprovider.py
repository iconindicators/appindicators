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
Base class for downloading from a URL and loading from file,
data for comets minor planets and satellites.
'''


from abc import ABC, abstractmethod


class DataProvider( ABC ):
    '''
    Base class for downloading and persisting data for astronomical objects.
    '''

    @staticmethod
    @abstractmethod
    def download( filename, logging, *args ):
        '''
        Download data and save to file.

        Return True on success; false otherwise and may log.
        '''
        return True


    @staticmethod
    @abstractmethod
    def load( filename, logging, *args ):
        '''
        Load data from file and return in a dictionary.

        Return dictionary which may be empty and may log.
        '''
        return { }
