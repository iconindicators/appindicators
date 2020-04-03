#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# Iterate through each indicator's main file and changelog, 
# compare the version numbers and report any difference against each other
# and the released version on LaunchPad.


basePath = "../../"
changeLogPath = "/packaging/debian/changelog"
sourcePath = "/src/"
indicators = [
    [ "IndicatorFortune", "indicator-fortune", "1.0.30" ],
    [ "IndicatorLunar", "indicator-lunar", "1.0.80" ],
    [ "IndicatorOnThisDay", "indicator-on-this-day", "1.0.6" ],
    [ "IndicatorPPADownloadStatistics", "indicator-ppa-download-statistics", "1.0.67" ],
    [ "IndicatorPunycode", "indicator-punycode", "1.0.8" ],
    [ "IndicatorScriptRunner", "indicator-script-runner", "1.0.11" ],
    [ "IndicatorStardate", "indicator-stardate", "1.0.38" ],
    [ "IndicatorTide", "indicator-tide", "1.0.19" ],
    [ "IndicatorVirtualBox", "indicator-virtual-box", "1.0.62" ] ]


for project, source, versionOnPPA in indicators:
    with open( basePath + project + changeLogPath ) as f:
        content = f.readlines()
        for line in content:
            versionChangeLog = line[ line.index( '(' ) + 1 : line.index( ')' ) - 2 ]
            break
 
    with open( basePath + project + sourcePath + source + ".py" ) as f:
        content = f.readlines()
        for line in content:
            if "version =" in line:
                versionSource = line[ line.index( '"' ) + 1 : line.index( ',' ) - 1 ]
                break

    if versionChangeLog != versionSource or versionChangeLog != versionOnPPA:
        print( project, "has version mismatch:" )
        print( "\tPPA:", versionOnPPA )
        print( "\tChangeLog:", versionChangeLog )
        print( "\tSource", versionSource )