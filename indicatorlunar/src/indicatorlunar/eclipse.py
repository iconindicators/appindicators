#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


'''
Lunar/solar eclipse tables up to and including the year 2040.

Eclipse Predictions by Fred Espenak, NASA/GSFC Emeritus
https://eclipse.gsfc.nasa.gov/eclipse.html
'''


import datetime

from enum import Enum


class EclipseType( Enum ):
    ''' Types of eclipses. '''
    ANNULAR = 0
    HYBRID = 1
    PARTIAL = 2
    PENUMBRAL = 3
    TOTAL = 4


_months = {
    "Jan" : "01",
    "Feb" : "02",
    "Mar" : "03",
    "Apr" : "04",
    "May" : "05",
    "Jun" : "06",
    "Jul" : "07",
    "Aug" : "08",
    "Sep" : "09",
    "Oct" : "10",
    "Nov" : "11",
    "Dec" : "12" }


# https://eclipse.gsfc.nasa.gov/5MCLE/5MKLEcatalog.txt
# https://eclipse.gsfc.nasa.gov/LEcat5/LEcatkey.html
_ECLIPSES_LUNAR = \
''' 09706   2025 Mar 14  06:59:56     75    311  123   T   -p   0.3484  2.2595  1.1784  362.6  218.3   65.4    3N  102W
    09707   2025 Sep 07  18:12:58     75    317  128   T   -p  -0.2752  2.3440  1.3619  326.7  209.4   82.1    6S   87E
    09708   2026 Mar 03  11:34:52     75    323  133   T   a-  -0.3765  2.1838  1.1507  338.6  207.2   58.3    6N  171W
    09709   2026 Aug 28  04:14:04     75    329  138   P   t-   0.4964  1.9645  0.9299  337.8  198.1    -      9S   63W
    09710   2027 Feb 20  23:14:06     76    335  143   N   a-  -1.0480  0.9266 -0.0569  241.0    -      -     10N   15E
    09711   2027 Jul 18  16:04:09     76    340  110   Ne  -t  -1.5758  0.0014 -1.0680   11.8    -      -     22S  121E
    09712   2027 Aug 17  07:14:59     76    341  148   N   t-   1.2797  0.5456 -0.5254  218.6    -      -     12S  108W
    09713   2028 Jan 12  04:14:13     76    346  115   P   -a   0.9817  1.0468  0.0662  250.7   56.0    -     23N   61W
    09714   2028 Jul 06  18:20:57     77    352  120   P   -t  -0.7903  1.4266  0.3892  310.6  141.5    -     23S   86E
    09715   2028 Dec 31  16:53:15     77    358  125   T   -p   0.3258  2.2742  1.2463  336.2  208.8   71.3   23N  108E
    09716   2029 Jun 26  03:23:22     77    364  130   T+  pp   0.0124  2.8266  1.8436  335.1  219.5  101.9   23S   50W
    09717   2029 Dec 20  22:43:12     78    370  135   T   p-  -0.3811  2.2008  1.1174  358.0  213.3   53.7   23N   19E
    09718   2030 Jun 15  18:34:34     78    376  140   P   a-   0.7534  1.4480  0.5025  278.2  144.4    -     23S   82E
    09719   2030 Dec 09  22:28:51     78    382  145   N   t-  -1.0731  0.9416 -0.1628  279.2    -      -     22N   21E
    09720   2031 May 07  03:52:02     78    387  112   N   -a  -1.0694  0.8814 -0.0904  237.3    -      -     18S   59W
    09721   2031 Jun 05  11:45:17     78    388  150   N   a-   1.4731  0.1292 -0.8199   95.6    -      -     21S  176W
    09722   2031 Oct 30  07:46:45     79    393  117   N   -h   1.1773  0.7161 -0.3204  231.8    -      -     15N  121W
    09723   2032 Apr 25  15:14:51     79    399  122   T   -a  -0.3558  2.2192  1.1913  342.4  211.2   65.5   14S  131E
    09724   2032 Oct 18  19:03:40     79    405  127   T   -p   0.4169  2.0830  1.1028  315.4  195.9   47.1   10N   71E
    09725   2033 Apr 14  19:13:51     80    411  132   T   t-   0.3954  2.1711  1.0944  361.2  215.0   49.2    9S   72E
    09726   2033 Oct 08  10:56:23     80    417  137   T   p-  -0.2889  2.3057  1.3497  312.6  202.4   78.8    6N  167W
    09727   2034 Apr 03  19:06:59     80    423  142   N   t-   1.1144  0.8545 -0.2274  265.4    -      -      5S   75E
    09728   2034 Sep 28  02:47:37     81    429  147   P   a-  -1.0110  0.9911  0.0144  248.7   26.7    -      1N   44W
    09729   2035 Feb 22  09:06:12     81    434  114   N   -a  -1.0367  0.9652 -0.0535  255.7    -      -      9N  133W
    09730   2035 Aug 19  01:12:15     81    440  119   P   -t   0.9433  1.1507  0.1037  289.8   76.5    -     12S   17W
    09731   2036 Feb 11  22:13:06     82    446  124   T   -p  -0.3110  2.2751  1.2995  316.1  201.9   74.5   14N   31E
    09732   2036 Aug 07  02:52:32     82    452  129   T+  pp   0.2004  2.5266  1.4544  372.1  231.3   95.3   16S   41W
    09733   2037 Jan 31  14:01:38     82    458  134   T   p-   0.3619  2.1803  1.2074  312.1  197.5   63.7   18N  153E
    09734   2037 Jul 27  04:09:53     83    464  139   P   t-  -0.5582  1.8584  0.8095  340.8  192.4    -     20S   60W
    09735   2038 Jan 21  03:49:52     83    470  144   N   a-   1.0710  0.8996 -0.1140  245.8    -      -     21N   54W
    09736   2038 Jun 17  02:45:02     83    475  111   N   -a   1.3082  0.4422 -0.5275  176.3    -      -     22S   41W
    09737   2038 Jul 16  11:35:56     84    476  149   N   a-  -1.2837  0.4999 -0.4952  192.4    -      -     23S  172W
    09738   2038 Dec 11  17:45:00     84    481  116   N   -t  -1.1448  0.8046 -0.2892  258.5    -      -     22N   93E
    09739   2039 Jun 06  18:54:25     84    487  121   P   -a   0.5460  1.8272  0.8846  296.7  179.3    -     22S   77E
    09740   2039 Nov 30  16:56:28     85    493  126   P   -t  -0.4721  2.0418  0.9426  360.1  206.0    -     21N  104E
    09741   2040 May 26  11:46:22     85    499  131   T-  p-  -0.1872  2.4938  1.5348  321.4  210.7   92.2   21S  177W
    09742   2040 Nov 18  19:04:40     85    505  136   T+  p-   0.2361  2.4525  1.3974  353.6  220.4   87.8   20N   70E'''


# https://eclipse.gsfc.nasa.gov/5MCSE/5MKSEcatalog.txt
# https://eclipse.gsfc.nasa.gov/SEcat5/catkey.html
_ECLIPSES_SOLAR = \
'''  9563  479   2025 Mar 29  10:48:36     75    312  149   P   t-   1.0405  0.9376  61.1N  77.1W   0   83
     9564  479   2025 Sep 21  19:43:04     75    318  154   P   t-  -1.0651  0.8550  60.9S 153.5E   0   89
     9565  479   2026 Feb 17  12:13:06     75    323  121   A   -t  -0.9743  0.9630  64.7S  86.8E  12  268  616  02m20s
     9566  479   2026 Aug 12  17:47:06     75    329  126   T   -p   0.8977  1.0386  65.2N  25.2W  26  248  294  02m18s
     9567  479   2027 Feb 06  16:00:48     76    335  131   A   -n  -0.2952  0.9281  31.3S  48.5W  73  334  282  07m51s
     9568  479   2027 Aug 02  10:07:50     76    341  136   T   nn   0.1421  1.0790  25.5N  33.2E  82  202  258  06m23s
     9569  479   2028 Jan 26  15:08:59     76    347  141   A   p-   0.3901  0.9208   3.0N  51.5W  67  161  323  10m27s
     9570  479   2028 Jul 22  02:56:40     77    353  146   T   p-  -0.6056  1.0560  15.6S 126.7E  53   17  230  05m10s
     9571  479   2029 Jan 14  17:13:48     77    359  151   P   t-   1.0553  0.8714  63.7N 114.2W   0  145
     9572  479   2029 Jun 12  04:06:13     77    364  118   P   -t   1.2943  0.4576  66.8N  66.2W   0  355
     9573  479   2029 Jul 11  15:37:19     77    365  156   P   t-  -1.4191  0.2303  64.3S  85.6W   0   30
     9574  479   2029 Dec 05  15:03:58     77    370  123   P   -t  -1.0609  0.8911  67.5S 135.7E   0  177
     9575  479   2030 Jun 01  06:29:13     78    376  128   A   -p   0.5626  0.9443  56.5N  80.1E  55  176  250  05m21s
     9576  479   2030 Nov 25  06:51:37     78    382  133   T   -n  -0.3867  1.0468  43.6S  71.2E  67    7  169  03m44s
     9577  479   2031 May 21  07:16:04     78    388  138   A   nn  -0.1970  0.9589   8.9N  71.7E  79  354  152  05m26s
     9578  479   2031 Nov 14  21:07:31     79    394  143   H   n-   0.3078  1.0106   0.6S 137.6W  72  189   38  01m08s
     9579  479   2032 May 09  13:26:42     79    400  148   A   t-  -0.9375  0.9957  51.3S   7.1W  20  345   44  00m22s
     9580  479   2032 Nov 03  05:34:13     79    406  153   P   t-   1.0643  0.8554  70.4N 132.6E   0  218
     9581  480   2033 Mar 30  18:02:36     80    411  120   T   -t   0.9778  1.0462  71.3N 155.8W  11  111  781  02m37s
     9582  480   2033 Sep 23  13:54:31     80    417  125   P   -t  -1.1583  0.6890  72.2S 121.2W   0   91
     9583  480   2034 Mar 20  10:18:45     80    423  130   T   -n   0.2894  1.0458  16.1N  22.2E  73  162  159  04m09s
     9584  480   2034 Sep 12  16:19:28     81    429  135   A   -p  -0.3936  0.9736  18.2S  72.6W  67   18  102  02m58s
     9585  480   2035 Mar 09  23:05:54     81    435  140   A   n-  -0.4368  0.9919  29.0S 154.9W  64  340   31  00m48s
     9586  480   2035 Sep 02  01:56:46     81    441  145   T   p-   0.3727  1.0320  29.1N 158.0E  68  199  116  02m54s
     9587  480   2036 Feb 27  04:46:49     82    447  150   P   t-  -1.1942  0.6286  71.6S 131.4W   0  242
     9588  480   2036 Jul 23  10:32:06     82    452  117   P   -t  -1.4250  0.1991  68.9S   3.6E   0   19
     9589  480   2036 Aug 21  17:25:45     82    453  155   P   t-   1.0825  0.8622  71.1N  47.0E   0  309
     9590  480   2037 Jan 16  09:48:55     82    458  122   P   -t   1.1477  0.7049  68.5N  20.8E   0  166
     9591  480   2037 Jul 13  02:40:36     83    464  127   T   -p  -0.7246  1.0413  24.8S 139.1E  43    3  201  03m58s
     9592  480   2038 Jan 05  13:47:11     83    470  132   A   -n   0.4169  0.9728   2.1N  25.4W  65  179  107  03m18s
     9593  480   2038 Jul 02  13:32:55     84    476  137   A   nn   0.0398  0.9911  25.4N  21.9W  88  179   31  01m00s
     9594  480   2038 Dec 26  01:00:10     84    482  142   T   n-  -0.2881  1.0268  40.3S 164.0E  73    5   95  02m18s
     9595  480   2039 Jun 21  17:12:54     84    488  147   A   p-   0.8312  0.9454  78.9N 102.1W  33  153  365  04m05s
     9596  480   2039 Dec 15  16:23:46     85    494  152   T   p-  -0.9458  1.0356  80.9S 172.8E  18  123  380  01m51s
     9597  480   2040 May 11  03:43:02     85    499  119   P   -t  -1.2529  0.5306  62.8S 174.4E   0  313
     9598  480   2040 Nov 04  19:09:02     85    505  124   P   -t   1.0993  0.8074  62.2N  53.4W   0  234'''


def get_eclipse_lunar( utc_now ):
    '''
    Gets the upcoming lunar eclipse.

    Returns a tuple:
        datetime in UTC with UTC timezone
        EclipseType
        latitude (south is negative)
        longitude (east is negative)
    '''
    return _get_eclipse( utc_now, _ECLIPSES_LUNAR, 1, 2, 3, 4, 5, 8, 16, 17 )


def get_eclipse_solar( utc_now ):
    '''
    Gets the upcoming solar eclipse.

    Returns a tuple:
        datetime in UTC with UTC timezone
        EclipseType
        latitude (south is negative)
        longitude (east is negative)
    '''
    return _get_eclipse( utc_now, _ECLIPSES_SOLAR, 2, 3, 4, 5, 6, 9, 13, 14 )


def _get_eclipse(
        utc_now,
        eclipses,
        field_year,
        field_month,
        field_day,
        field_time_utc,
        field_delta_t,
        field_type,
        field_latitude,
        field_longitude ):

    eclipse_information = None
    for line in eclipses.splitlines():
        fields = line.split()

        year = fields[ field_year ]
        month = fields[ field_month ]
        day = fields[ field_day ]
        time_utc = fields[ field_time_utc ]
        delta_t = fields[ field_delta_t ]

        # https://eclipse.gsfc.nasa.gov/LEcat5/deltat.html
        date_string = year + ", " + _months[ month ] + ", " + day + ", " + time_utc
        date_time = \
            datetime.datetime.strptime( date_string, "%Y, %m, %d, %H:%M:%S" ).replace( tzinfo = datetime.timezone.utc ) - \
            datetime.timedelta( seconds = int( delta_t ) )

        if utc_now <= date_time:
            eclipse_type = fields[ field_type ][ 0 ]
            latitude = fields[ field_latitude ]
            longitude = fields[ field_longitude ]

            the_latitude = str( int( float( latitude[ : -1 ] ) ) )
            if latitude.endswith( 'S' ):
                the_latitude = '-' + the_latitude

            the_longitude = str( int( float( longitude[ : -1 ] ) ) )
            if longitude.endswith( 'E' ):
                the_longitude = '-' + the_longitude

            eclipse_information = (
                date_time,
                _get_eclipse_type_from_table_value( eclipse_type ),
                the_latitude,
                the_longitude )

            break

    return eclipse_information


def get_eclipse_type_as_text( eclipse_type ):
    ''' Returns the translated descriptive text for a given eclipse type. '''
    if eclipse_type == EclipseType.ANNULAR:
        eclipse_type_text = _( "Annular" )

    elif eclipse_type == EclipseType.HYBRID:
        eclipse_type_text = _( "Hybrid (Annular/Total)" )

    elif eclipse_type == EclipseType.PARTIAL:
        eclipse_type_text = _( "Partial" )

    elif eclipse_type == EclipseType.PENUMBRAL:
        eclipse_type_text = _( "Penumbral" )

    else: # EclipseType.TOTAL:
        eclipse_type_text = _( "Total" )

    return eclipse_type_text


def _get_eclipse_type_from_table_value( eclipse_type_from_table_value ):
    '''
    https://eclipse.gsfc.nasa.gov/LEcat5/LEcatkey.html
    https://eclipse.gsfc.nasa.gov/SEcat5/catkey.html
    '''
    if eclipse_type_from_table_value == 'A':
        _eclipse_type = EclipseType.ANNULAR

    elif eclipse_type_from_table_value == 'H':
        _eclipse_type = EclipseType.HYBRID

    elif eclipse_type_from_table_value == 'P':
        _eclipse_type = EclipseType.PARTIAL

    elif eclipse_type_from_table_value == 'N':
        _eclipse_type = EclipseType.PENUMBRAL

    else: # T
        _eclipse_type = EclipseType.TOTAL

    return _eclipse_type
