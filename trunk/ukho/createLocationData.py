#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# Run LibreOffice Calc, open the file
#
#     2018 Current Tidal Prediction Ports.xlsx
#
# then Save As 'Text CSV' with the filename
#
#     Current Tidal Prediction Ports.csv
#
# using TAB as the field delimiter.
#
# Note that openpyxl would not work as it gave some Unicode error, so must convert to CSV and read that instead.
#
# Ensure the columns in the CSV file match as follows:
#     A = Port Number
#     B = Suffix
#     C = Port Name
#     I = Country
#
# Then run the code below to produce an output of the form:
#     [ "1822", "Alger (Algiers)", "Algeria" ],
#     [ "1820", "Arzew", "Algeria" ],
#     [ "2065B", "Bleaker Island", "Falkland Islands" ],
#     ...
#
# which can then be used to paste into ports.py


with open( "Current Tidal Prediction Ports.csv" ) as f:
   for line in f:
       if not line.startswith( "PortNo" ):
           line = line.strip().split( "\t" )
           line = "[ \"" + line[ 0 ] + line[ 1 ] + "\", \"" + line[ 2 ] + "\", \"" + line[ 8 ] + "\" ],"
           line = line.title().replace( "St. ", "St." ).replace( "St.", "St. " ).replace( "'S", "'s" )
           print( line )