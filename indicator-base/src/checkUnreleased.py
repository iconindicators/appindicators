#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# Iterate through each indicator's main file and changelog, 
# compare the version numbers and report any difference against each other
# and the released version on LaunchPad.


basePath = "../../"
changeLogPath = "/packaging/debian/changelog"
sourcePath = "/src/"
indicators = [
    [ "indicator-fortune", "1.0.35" ],
    [ "indicator-lunar", "1.0.92" ],
    [ "indicator-on-this-day", "1.0.9" ],
    [ "indicator-ppa-download-statistics", "1.0.74" ],
    [ "indicator-punycode", "1.0.11" ],
    [ "indicator-script-runner", "1.0.16" ],
    [ "indicator-stardate", "1.0.40" ],
    [ "indicator-tide", "1.0.24" ],
    [ "indicator-virtual-box", "1.0.69" ] ]


for project, versionOnPPA in indicators:
    with open( basePath + project + changeLogPath ) as f:
        content = f.readlines()
        for line in content:
            versionChangeLog = line[ line.index( '(' ) + 1 : line.index( ')' ) - 2 ]
            break
 
    with open( basePath + project + sourcePath + project + ".py" ) as f:
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
