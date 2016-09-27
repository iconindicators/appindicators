#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# Open each of
#
#     2016_predictions_non-commercial_granted.xls
#     2016_predictions_non-commercial_granted_non UK ports.xls
#
# in LibreOffice Calc and Save As 'Text CSV' using TAB as the field delimiter and no text delimiter.
#
# Note that openpyxl would not work as it gave some Unicode error, so must convert to CSV and read that instead.
#
# Read in each CSV and produce output of the form:
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
           line = "[ \"" + line[ 0 ] + line[ 1 ] + "\", \"" + line[ 2 ] + "\", \"" + line[ 8 ] + "\" ],"
           line = line.replace( "ST.", "St." ).title()
           print( line )


process( "2016_predictions_non-commercial_granted_non UK ports.csv" )
print( "" )
process( "2016_predictions_non-commercial_granted.csv" )