#!/usr/bin/env python3


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
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import locationData

DEFAULT_COUNTRY = "England"
DEFAULT_PORT_ID = "113"


def isValidPortID( portID ):
	isValid = False
	if portID is not None:
		for location in locationData.__locationsUnitedKingdomHydrographicOffice:
			if portID == location[ 2 ]:
				isValid = True
				break

	return isValid


# PortID may not be unique, but duplicates (hopefully) match the same country.
def getCountry( portID ): 
	country = DEFAULT_COUNTRY
	if portID is not None:
		for location in locationData.__locationsUnitedKingdomHydrographicOffice:
			if portID == location[ 2 ]:
				country = location[ 0 ]
				break

	return country


# Returns the port ID for the first matching country.
def getPortIDForCountry( country ):
	portID = DEFAULT_PORT_ID
	if country is not None:
		for location in locationData.__locationsUnitedKingdomHydrographicOffice:
			if country == location[ 0 ]:
				portID = location[ 2 ]
				break

	return portID


def getPortIDForCountryAndPort( country, port ):
	portID = DEFAULT_PORT_ID
	if country is not None and port is not None:
		for location in locationData.__locationsUnitedKingdomHydrographicOffice:
			if country == location[ 0 ] and port == location[ 1 ]:
				portID = location[ 2 ]
				break

	return portID


def getPortsForCountry( country ):
	if country is None or country not in getCountries():
		country = DEFAULT_COUNTRY

	ports = [ ]
	for location in locationData.__locationsUnitedKingdomHydrographicOffice:
		if location[ 0 ] == country and location[ 1 ] not in ports:
			ports.append( location[ 1 ] )

	return ports


def getCountries():
	countries = [ ]
	for location in locationData.__locationsUnitedKingdomHydrographicOffice:
		if location[ 0 ] not in countries:
			countries.append( location[ 0 ] )

	return countries