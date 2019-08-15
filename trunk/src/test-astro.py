#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import astro, astroSkyfield

utcNow = datetime.datetime.utcnow()
latitude = -33.8599722
longitude = 151.2111111
elevation = 100
magnitude = 6

resultsSkyfield = astroSkyfield.getAstronomicalInformation( utcnow,
                                                            latitude , longitude, elevation,
                                                            astroSkyfield.PLANETS,
                                                            astroSkyfield.STARS,
                                                            [], [],
                                                            [], [],
                                                            [], [],
                                                            magnitude )

resultsPyEphem = astro.getAstronomicalInformation( utcnow,
                                                            latitude , longitude, elevation,
                                                            astro.PLANETS,
                                                            astro.STARS,
                                                            [], [],
                                                            [], [],
                                                            [], [],
                                                            magnitude )