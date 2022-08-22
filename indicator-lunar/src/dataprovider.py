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


#TODO Update
# Base class for calculating astronomical information for use with Indicator Lunar.


from abc import ABC, abstractmethod
from urllib.request import urlopen


class DataProvider( ABC ):

    URL_TIMEOUT_IN_SECONDS = 20


#TODO Need comment
    @staticmethod
    @abstractmethod
    def download( filename, logging, *args ): return True


#TODO Need comment
    @staticmethod
    @abstractmethod
    def load( filename, logging, *args ): return { }