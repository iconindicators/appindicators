#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# Iterate through the changelogs specified below and report:
#     Bad dates
#     Dates out of sequence
#     Release numbers out of sequence


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

for changeLog in changeLogs:
    errors = [ ]
    dates = [ ]
    releaseNumbers = [ ]
    with open( basePath + changeLog + changeLogPath ) as f:
        content = f.readlines()
        for line in content:
            if line.startswith( " -- " ):
                dateTime = line[ line.find( ">" ) + 1 : ].strip()
                dateTimeObject = datetime.strptime( dateTime, "%a, %d %b %Y %H:%M:%S %z" )
                dates.append( dateTimeObject )

            if line.startswith( "indicator-" ):
                releaseNumbers.append( line.split( '(' )[ 1 ].split( ')' )[ 0 ] )

    releaseNumbersUnsorted = releaseNumbers.copy()
    releaseNumbers.sort( key = lambda x: int( ''.join( filter( str.isdigit, x ) ) ), reverse = True )
    if releaseNumbersUnsorted != releaseNumbers:
        errors.append( "\tRelease numbers out of order!" )

    if dates != sorted( dates, reverse = True ):
        errors.append( "\tDates out of order!" )

    if errors:
        print( changeLog )
        for error in errors:
            print( error )