#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# Iterate through the changelogs specified below and report:
#     Bad dates
#     Dates out of sequence
#     Release numbers out of sequence
#     Line length exceeds 80 characters


from datetime import datetime


basePath = "../../"
changeLogPath = "/packaging/debian/changelog"
changeLogs = [
    "indicator-fortune",
    "indicator-lunar",
    "indicator-on-this-day",
    "indicator-ppa-download-statistics",
    "indicator-punycode",
    "indicator-script-runner",
    "indicator-stardate",
    "indicator-tide",
    "indicator-virtual-box" ]

for changeLog in changeLogs:
    try:
        errors = [ ]
        dates = [ ]
        releaseNumbers = [ ]
        lineNumbers = [ ]
        with open( basePath + changeLog + changeLogPath ) as f:
            content = f.readlines()
            for line in content:
                if line.startswith( " -- " ):
                    dateTime = line[ line.find( ">" ) + 1 : ].strip()
                    dateTimeObject = datetime.strptime( dateTime, "%a, %d %b %Y %H:%M:%S %z" )
                    dates.append( dateTimeObject )

                if line.startswith( "indicator-" ):
                    releaseNumbers.append( line.split( '(' )[ 1 ].split( ')' )[ 0 ] )

                if not line.startswith( " -- " ) and len( line ) > 80:
                    lineNumbers.append( line )
    except Exception as e:
        print( changeLog )
        print( e )
        
    releaseNumbersUnsorted = releaseNumbers.copy()
    releaseNumbers.sort( key = lambda x: int( ''.join( filter( str.isdigit, x ) ) ), reverse = True )
    if releaseNumbersUnsorted != releaseNumbers:
        errors.append( "\tRelease numbers out of order!" )

    if dates != sorted( dates, reverse = True ):
        errors.append( "\tDates out of order!" )

    for date in dates:
        if date.replace( tzinfo = None ) > datetime.now():
            print( changeLog, "has future date:", date )


    if lineNumbers:
        errors.append( "\tOne or more lines exceed 80 character limit." )

    if errors:
        print( changeLog )
        for error in errors:
            print( error )
            
        if lineNumbers:
            print( "Line numbers exceeding 80 characters:" )
            for line in lineNumbers:
                print( "\t", line )
