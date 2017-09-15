#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# Open the UKHO ports file
#
#     Worldwide Granted Ports.xls
#
# in LibreOffice Calc and Save As 'Text CSV' using TAB as the field delimiter and no text delimiter.
#
# Note that openpyxl would not work as it gave some Unicode error, so must convert to CSV and read that instead.
#
# Amend the column numbers to match the port ID, port name and country and then call process to produce output of the form:
#     [ "1822", "Alger (Algiers)", "Algeria" ],
#     [ "1820", "Arzew", "Algeria" ],
#     ...


def process( fileName ):
    print( fileName )
    with open( fileName ) as f:
       for line in f:
           if line.startswith( "PortNo" ):
               continue

           line = line.strip().split( "\t" )
           line = "[ \"" + line[ 0 ] + line[ 1 ] + "\", \"" + line[ 2 ] + "\", \"" + line[ 10 ] + "\" ],"
           line = line.replace( "ST.", "St." ).title()
           print( line )


process( "Worldwide Granted Ports.csv" )