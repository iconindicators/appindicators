#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# Iterate through each indicator's main file and changelog, 
# compare the version numbers and report any difference against each other
# and the released version on LaunchPad.


basePath = "../../"
changeLogPath = "/packaging/debian/changelog"
sourcePath = "/src/"
indicators = [
    [ "IndicatorFortune", "indicator-fortune", "1.0.33" ],
    [ "IndicatorLunar", "indicator-lunar", "1.0.84" ],
    [ "IndicatorOnThisDay", "indicator-on-this-day", "1.0.8" ],
    [ "IndicatorPPADownloadStatistics", "indicator-ppa-download-statistics", "1.0.71" ],
    [ "IndicatorPunycode", "indicator-punycode", "1.0.10" ],
    [ "IndicatorScriptRunner", "indicator-script-runner", "1.0.12" ],
    [ "IndicatorStardate", "indicator-stardate", "1.0.39" ],
    [ "IndicatorTide", "indicator-tide", "1.0.21" ],
    [ "IndicatorVirtualBox", "indicator-virtual-box", "1.0.65" ] ]


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