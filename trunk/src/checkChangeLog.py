#!/usr/bin/env python3
# -*- coding: utf-8 -*-



# TODO Description

from datetime import datetime



changeLogs = [
                "/home/bernard/Programming/IndicatorCalendar/packaging/debian/changelog",
                "/home/bernard/Programming/IndicatorFortune/packaging/debian/changelog",
                "/home/bernard/Programming/IndicatorLunar/packaging/debian/changelog",
                "/home/bernard/Programming/IndicatorPPADownloadStatistics/packaging/debian/changelog",
                "/home/bernard/Programming/IndicatorPunycode/packaging/debian/changelog",
                "/home/bernard/Programming/IndicatorScriptRunner/packaging/debian/changelog",
                "/home/bernard/Programming/IndicatorStardate/packaging/debian/changelog",
                "/home/bernard/Programming/IndicatorTide/packaging/debian/changelog",
                "/home/bernard/Programming/IndicatorVirtualBox/packaging/debian/changelog"
              ]

dateTimeFormat = "%a, %d %b %Y %H:%M:%S %z"
for changeLog in changeLogs:
    print( changeLog )
    dates = [ ]
    with open( changeLog ) as f:
        content = f.readlines()
        for line in content:
            if line.startswith( " -- " ):
                dateTime = line[ line.find( ">" ) + 1 : ].strip()
                dateTimeObject = datetime.strptime( dateTime, dateTimeFormat )
                dateTimeObjectAsString = dateTimeObject.strftime( dateTimeFormat ).replace( " 0", " " )
                if dateTime != dateTimeObjectAsString:
                    print( dateTime, "\t!=\t", dateTimeObjectAsString )

                dates.append( dateTimeObject )

    if dates != sorted( dates, reverse = True ):
        print( "Dates out of order!" )