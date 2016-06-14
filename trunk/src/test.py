#!/usr/bin/env python3


import encodings.idna


def convert( domain ):
    convertedDomain = ""
    if domain.find( "xn--" ) == -1:
        labels = [ ]
        for label in domain.split( "." ):    
            labels.append( ( encodings.idna.ToASCII( encodings.idna.nameprep( label ) ) ) )
        convertedDomain = str( b'.'.join( labels ), "utf-8" )
    else:
        for label in domain.split( "." ):    
            convertedDomain += encodings.idna.ToUnicode( encodings.idna.nameprep( label ) ) + "."

        convertedDomain = convertedDomain[ : -1 ]

    return convertedDomain


def report( domain, expected, result ):
    print( "Domain:\n\t", domain )
    print( "Expected:\n\t", expected )
    print( "Result\n\t", convert( domain ) )
    print( )



domain = "www.Alliancefrançaise.nu"
expected = "www.xn--alliancefranaise-npb.nu"
report( domain, expected, convert( domain ) )

domain = "www.xn--alliancefranaise-npb.nu"
expected = "www.Alliancefrançaise.nu"
report( domain, expected, convert( domain ) )

domain = "www.xn--bcher-kva.de"
expected = "www.bücher.de"
report( domain, expected, convert( domain ) )

domain = "www.bücher.de"
expected = "www.xn--bcher-kva.de"
report( domain, expected, convert( domain ) )
