#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import astroPyephem, astroSkyfield, datetime


utcNow = datetime.datetime.utcnow()
latitude = -33.8599722
longitude = 151.2111111
elevation = 100
magnitude = 6

resultsSkyfield = astroSkyfield.getAstronomicalInformation( utcNow,
                                                            latitude, longitude, elevation,
                                                            astroSkyfield.PLANETS,
                                                            astroSkyfield.STARS,
                                                            [], [],
                                                            [], [],
                                                            [], [],
                                                            magnitude )

print ( sorted( resultsSkyfield.items() ) )

resultsPyEphem = astroPyephem.getAstronomicalInformation( utcNow,
                                                          latitude, longitude, elevation,
                                                          astroPyephem.PLANETS,
                                                          astroPyephem.STARS,
                                                          [], [],
                                                          [], [],
                                                          [], [],
                                                          magnitude )

print ( sorted( resultsPyEphem.items() ) )
