#!/usr/bin/env python3


# Search for a regex/string in all revisions/versions of a file in a Subversion working directory.
#
# Reference:
    # https://eli.thegreenplace.net/2012/05/22/grep-through-code-history-with-git-mercurial-or-svn/


import re, subprocess


fullPathToFile = "/home/bernard/Programming/Indicators/indicator-lunar/src/astroskyfield.py"
regularExpressionToFind = "pytz"


def runCommand( cmd ): return subprocess.check_output( cmd.split(), universal_newlines = True )


print( "May first need to run from a terminal\n" )
print( "\tsvn info " + fullPathToFile + "\n" )

latestRevision = runCommand( "svn info " + fullPathToFile ).partition( "Revision: ")[ 2 ].partition( "\n" )[ 0 ]
print( "File to check: " + fullPathToFile )
print( "Regular expression or string: " + regularExpressionToFind )
print( "Number of revisions: " + latestRevision )


print( "\nLooking for revisions which match..." )
log = runCommand( "svn log " + fullPathToFile )
for ver in re.findall( "r\d+", log, flags = re.MULTILINE ):
    contents = runCommand( "svn cat -r %s %s" % ( ver.rstrip( 'r' ), fullPathToFile ) )
    if re.search( regularExpressionToFind, contents ):
        print( ver )

print( "Done")
