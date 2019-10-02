#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# Iterate through the changelogs specified below and report:
#     Bad dates
#     Dates out of sequence

#TODO Add check for version numbers that increase and have no gaps. 


from datetime import datetime


basePath = "../../"
changeLogPath = "/packaging/debian/changelog"
changeLogs = [
    "IndicatorFortune",
    "IndicatorLunar",
    "IndicatorOnThisDay",
    "IndicatorPPADownloadStatistics",
    "IndicatorPunycode",
    "IndicatorScriptRunner",
    "IndicatorStardate",
    "IndicatorTide",
    "IndicatorVirtualBox" ]

dateTimeFormat = "%a, %d %b %Y %H:%M:%S %z"
for changeLog in changeLogs:
    changeLog = basePath + changeLog + changeLogPath
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