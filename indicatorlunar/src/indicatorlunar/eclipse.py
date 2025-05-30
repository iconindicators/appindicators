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
Lunar/solar eclipse tables up to and including the year 2099.

Eclipse Predictions by Fred Espenak, NASA/GSFC Emeritus.
https://eclipse.gsfc.nasa.gov/eclipse.html
'''


import datetime

from enum import auto, IntEnum


class EclipseType( IntEnum ):
    ''' Types of eclipses. '''
    ANNULAR = auto()
    HYBRID = auto()
    PARTIAL = auto()
    PENUMBRAL = auto()
    TOTAL = auto()


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
_ECLIPSES_LUNAR = (
''' 2025  Sep  07  18:12:58   75  T    6S   87E
    2026  Mar  03  11:34:52   75  T    6N  171W
    2026  Aug  28  04:14:04   75  P    9S   63W
    2027  Feb  20  23:14:06   76  N   10N   15E
    2027  Jul  18  16:04:09   76  Ne  22S  121E
    2027  Aug  17  07:14:59   76  N   12S  108W
    2028  Jan  12  04:14:13   76  P   23N   61W
    2028  Jul  06  18:20:57   77  P   23S   86E
    2028  Dec  31  16:53:15   77  T   23N  108E
    2029  Jun  26  03:23:22   77  T+  23S   50W
    2029  Dec  20  22:43:12   78  T   23N   19E
    2030  Jun  15  18:34:34   78  P   23S   82E
    2030  Dec  09  22:28:51   78  N   22N   21E
    2031  May  07  03:52:02   78  N   18S   59W
    2031  Jun  05  11:45:17   78  N   21S  176W
    2031  Oct  30  07:46:45   79  N   15N  121W
    2032  Apr  25  15:14:51   79  T   14S  131E
    2032  Oct  18  19:03:40   79  T   10N   71E
    2033  Apr  14  19:13:51   80  T    9S   72E
    2033  Oct  08  10:56:23   80  T    6N  167W
    2034  Apr  03  19:06:59   80  N    5S   75E
    2034  Sep  28  02:47:37   81  P    1N   44W
    2035  Feb  22  09:06:12   81  N    9N  133W
    2035  Aug  19  01:12:15   81  P   12S   17W
    2036  Feb  11  22:13:06   82  T   14N   31E
    2036  Aug  07  02:52:32   82  T+  16S   41W
    2037  Jan  31  14:01:38   82  T   18N  153E
    2037  Jul  27  04:09:53   83  P   20S   60W
    2038  Jan  21  03:49:52   83  N   21N   54W
    2038  Jun  17  02:45:02   83  N   22S   41W
    2038  Jul  16  11:35:56   84  N   23S  172W
    2038  Dec  11  17:45:00   84  N   22N   93E
    2039  Jun  06  18:54:25   84  P   22S   77E
    2039  Nov  30  16:56:28   85  P   21N  104E
    2040  May  26  11:46:22   85  T-  21S  177W
    2040  Nov  18  19:04:40   85  T+  20N   70E
    2041  May  16  00:43:03   86  P   20S   12W
    2041  Nov  08  04:35:05   86  P   18N   73W
    2042  Apr  05  14:30:11   86  N    5S  144E
    2042  Sep  29  10:45:47   87  N    2N  163W
    2043  Mar  25  14:32:04   87  T    2S  144E
    2043  Sep  19  01:51:50   88  T    2S   29W
    2044  Mar  13  19:38:33   88  T    2N   68E
    2044  Sep  07  11:20:44   88  T    5S  171W
    2045  Mar  03  07:43:26   89  N    6N  113W
    2045  Aug  27  13:54:50   89  N    9S  152E
    2046  Jan  22  13:02:37   90  P   21N  168E
    2046  Jul  18  01:06:05   90  P   22S   14W
    2047  Jan  12  01:26:14   90  T   22N   19W
    2047  Jul  07  10:35:45   91  T-  23S  157W
    2048  Jan  01  06:53:55   91  T   23N  102W
    2048  Jun  26  02:02:28   92  P   23S   30W
    2048  Dec  20  06:27:48   92  N   22N   97W
    2049  May  17  11:26:39   92  N   21S  172W
    2049  Jun  15  19:14:12   92  N   22S   72E
    2049  Nov  09  15:52:11   93  N   18N  118E
    2050  May  06  22:32:02   94  T   17S   21E
    2050  Oct  30  03:21:47   95  T   14N   54W
    2051  Apr  26  02:16:28   96  T   13S   34W
    2051  Oct  19  19:11:50   97  T-  10N   69E
    2052  Apr  14  02:18:06   98  N    9S   34W
    2052  Oct  08  10:45:58   99  P    5N  164W
    2053  Mar  04  17:22:10   99  N    5N  102E
    2053  Aug  29  08:05:50  100  Nx   8S  121W
    2054  Feb  22  06:51:27  101  T   10N   99W
    2054  Aug  18  09:26:30  102  T   13S  140W
    2055  Feb  11  22:46:17  103  T   14N   22E
    2055  Aug  07  10:53:18  104  P   17S  161W
    2056  Feb  01  12:26:06  105  N   18N  177E
    2056  Jun  27  10:03:09  106  N   22S  149W
    2056  Jul  26  18:43:24  106  N   20S   81E
    2056  Dec  22  01:48:56  107  N   22N   27W
    2057  Jun  17  02:26:20  108  P   23S   36W
    2057  Dec  11  00:53:38  109  P   23N   15W
    2058  Jun  06  19:15:48  110  T-  23S   71E
    2058  Nov  30  03:16:18  111  T+  22N   52W
    2059  May  27  07:55:35  112  P   22S  119W
    2059  Nov  19  13:01:36  113  P   20N  161E
    2060  Apr  15  21:37:04  114  N    9S   37E
    2060  Oct  09  18:53:32  115  N    6N   74E
    2060  Nov  08  04:04:15  115  N   18N   65W
    2061  Apr  04  21:54:05  116  T    6S   33E
    2061  Sep  29  09:38:13  117  T    2N  146W
    2062  Mar  25  03:33:50  118  T    2S   52W
    2062  Sep  18  18:34:02  119  T    1S   80E
    2063  Mar  14  16:05:49  120  P    1N  121E
    2063  Sep  07  20:41:12  121  N    5S   49E
    2064  Feb  02  21:48:57  122  P   18N   37E
    2064  Jul  28  07:52:48  123  P   20S  116W
    2065  Jan  22  09:58:58  124  T   20N  146W
    2065  Jul  17  17:48:40  125  T-  21S   95E
    2066  Jan  11  15:04:47  126  T   21N  136E
    2066  Jul  07  09:30:29  127  P   22S  141W
    2066  Dec  31  14:30:10  128  N   22N  144E
    2067  May  28  18:56:08  129  N   23S   76E
    2067  Jun  27  02:41:06  129  N   22S   39W
    2067  Nov  21  00:04:42  130  N   21N    4W
    2068  May  17  05:42:17  131  P   20S   86W
    2068  Nov  09  11:47:00  132  T   18N  180E
    2069  May  06  09:09:57  133  T+  17S  138W
    2069  Oct  30  03:35:06  134  T-  14N   57W
    2070  Apr  25  09:21:24  135  Nx  12S  140W
    2070  Oct  19  18:51:12  137  P    9N   74E
    2071  Mar  16  01:31:09  137  N    1N   20W
    2071  Sep  09  15:05:41  138  N    4S  133E
    2072  Mar  04  15:23:07  140  T    6N  133E
    2072  Aug  28  16:05:42  141  T    9S  119E
    2073  Feb  22  07:24:53  142  T   10N  107W
    2073  Aug  17  17:42:41  143  T   13S   96E
    2074  Feb  11  20:55:58  144  N   15N   50E
    2074  Jul  08  17:21:38  145  N   21S  101E
    2074  Aug  07  01:56:03  145  N   17S   27W
    2075  Jan  02  09:55:03  146  N   22N  147W
    2075  Jun  28  09:55:35  147  P   23S  147W
    2075  Dec  22  08:55:55  148  P   23N  134W
    2076  Jun  17  02:39:47  149  T-  23S   39W
    2076  Dec  10  11:34:51  150  T+  23N  175W
    2077  Jun  06  14:59:52  151  P   24S  135E
    2077  Nov  29  21:35:53  152  P   23N   34E
    2078  Apr  27  04:35:44  153  N   13S   68W
    2078  Oct  21  03:08:03  154  N   10N   50W
    2078  Nov  19  12:40:04  154  N   21N  166E
    2079  Apr  16  05:10:45  155  P   10S   77W
    2079  Oct  10  17:30:30  156  T    7N   95E
    2080  Apr  04  11:23:38  157  T    6S  170W
    2080  Sep  29  01:52:42  158  T    3N   30W
    2081  Mar  25  00:22:01  159  P    3S    4W
    2081  Sep  18  03:35:26  161  N    1S   55W
    2082  Feb  13  06:29:19  161  P   14N   93W
    2082  Aug  08  14:46:42  163  Nx  17S  141E
    2083  Feb  02  18:26:46  164  T   17N   88E
    2083  Jul  29  01:05:34  165  T-  19S   14W
    2084  Jan  22  23:13:00  166  T   19N   15E
    2084  Jul  17  16:58:51  167  P   20S  107E
    2085  Jan  10  22:32:29  168  N   21N   24E
    2085  Jun  08  02:17:36  169  N   24S   34W
    2085  Jul  07  10:04:40  169  N   21S  149W
    2085  Dec  01  08:25:35  170  N   23N  128W
    2086  May  28  12:43:47  171  P   22S  169E
    2086  Nov  20  20:19:42  172  P   20N   52E
    2087  May  17  15:55:20  173  T+  19S  121E
    2087  Nov  10  12:05:33  174  T-  17N  175E
    2088  May  05  16:16:50  175  P   16S  116E
    2088  Oct  30  03:03:20  177  P   13N   49W
    2089  Mar  26  09:34:14  178  N    4S  142W
    2089  Sep  19  22:11:17  179  N    0N   26E
    2090  Mar  15  23:48:31  180  T    1N    6E
    2090  Sep  08  22:52:29  181  T    5S   17E
    2091  Mar  05  15:58:22  182  T    6N  124E
    2091  Aug  29  00:38:25  183  T   10S    8W
    2092  Feb  23  05:20:59  184  N   11N   76W
    2092  Jul  19  00:41:58  185  Ne  19S    8W
    2092  Aug  17  09:13:59  185  N   14S  136W
    2093  Jan  12  18:00:03  186  N   20N   93E
    2093  Jul  08  17:24:18  187  P   22S  101E
    2094  Jan  01  17:00:06  188  P   22N  107E
    2094  Jun  28  10:01:57  190  T+  23S  149W
    2094  Dec  21  19:56:32  191  T+  24N   61E
    2095  Jun  17  22:00:11  192  P   24S   31E
    2095  Dec  11  06:15:02  193  P   24N   95W
    2096  May  07  11:24:42  194  N   16S  171W
    2096  Jun  06  02:43:41  194  Nb  24S   41W
    2096  Oct  31  11:30:23  195  N   13N  175W
    2096  Nov  29  21:22:22  195  N   23N   37E
    2097  Apr  26  12:18:17  196  P   13S  176E
    2097  Oct  21  01:30:55  197  T   11N   26W
    2098  Apr  15  19:04:48  198  T-  10S   74E
    2098  Oct  10  09:19:58  200  T    7N  143W
    2099  Apr  05  08:30:56  201  P    7S  127W
    2099  Sep  29  10:36:38  202  Nx   3N  161W''' )


# https://eclipse.gsfc.nasa.gov/5MCSE/5MKSEcatalog.txt
# https://eclipse.gsfc.nasa.gov/SEcat5/catkey.html
_ECLIPSES_SOLAR = (
''' 2025  Sep  21  19:43:04   75  P   60.9S  153.5E
    2026  Feb  17  12:13:06   75  A   64.7S   86.8E
    2026  Aug  12  17:47:06   75  T   65.2N   25.2W
    2027  Feb  06  16:00:48   76  A   31.3S   48.5W
    2027  Aug  02  10:07:50   76  T   25.5N   33.2E
    2028  Jan  26  15:08:59   76  A    3.0N   51.5W
    2028  Jul  22  02:56:40   77  T   15.6S  126.7E
    2029  Jan  14  17:13:48   77  P   63.7N  114.2W
    2029  Jun  12  04:06:13   77  P   66.8N   66.2W
    2029  Jul  11  15:37:19   77  P   64.3S   85.6W
    2029  Dec  05  15:03:58   77  P   67.5S  135.7E
    2030  Jun  01  06:29:13   78  A   56.5N   80.1E
    2030  Nov  25  06:51:37   78  T   43.6S   71.2E
    2031  May  21  07:16:04   78  A    8.9N   71.7E
    2031  Nov  14  21:07:31   79  H    0.6S  137.6W
    2032  May  09  13:26:42   79  A   51.3S    7.1W
    2032  Nov  03  05:34:13   79  P   70.4N  132.6E
    2033  Mar  30  18:02:36   80  T   71.3N  155.8W
    2033  Sep  23  13:54:31   80  P   72.2S  121.2W
    2034  Mar  20  10:18:45   80  T   16.1N   22.2E
    2034  Sep  12  16:19:28   81  A   18.2S   72.6W
    2035  Mar  09  23:05:54   81  A   29.0S  154.9W
    2035  Sep  02  01:56:46   81  T   29.1N  158.0E
    2036  Feb  27  04:46:49   82  P   71.6S  131.4W
    2036  Jul  23  10:32:06   82  P   68.9S    3.6E
    2036  Aug  21  17:25:45   82  P   71.1N   47.0E
    2037  Jan  16  09:48:55   82  P   68.5N   20.8E
    2037  Jul  13  02:40:36   83  T   24.8S  139.1E
    2038  Jan  05  13:47:11   83  A    2.1N   25.4W
    2038  Jul  02  13:32:55   84  A   25.4N   21.9W
    2038  Dec  26  01:00:10   84  T   40.3S  164.0E
    2039  Jun  21  17:12:54   84  A   78.9N  102.1W
    2039  Dec  15  16:23:46   85  T   80.9S  172.8E
    2040  May  11  03:43:02   85  P   62.8S  174.4E
    2040  Nov  04  19:09:02   85  P   62.2N   53.4W
    2041  Apr  30  11:52:21   86  T    9.6S   12.2E
    2041  Oct  25  01:36:22   86  A    9.9N  162.9E
    2042  Apr  20  02:17:30   86  T   27.0N  137.3E
    2042  Oct  14  02:00:42   87  A   23.7S  137.8E
    2043  Apr  09  18:57:49   87  T+  61.3N  152.0E
    2043  Oct  03  03:01:49   88  A-  61.0S   35.3E
    2044  Feb  28  20:24:39   88  As  62.2S   25.6W
    2044  Aug  23  01:17:02   88  T   64.3N  120.4W
    2045  Feb  16  23:56:07   89  A   28.3S  166.2W
    2045  Aug  12  17:42:39   89  T   25.9N   78.5W
    2046  Feb  05  23:06:26   90  A    4.8N  171.4W
    2046  Aug  02  10:21:13   90  T   12.7S   15.2E
    2047  Jan  26  01:33:18   90  P   62.9N  111.7E
    2047  Jun  23  10:52:31   91  P   65.8N  178.0W
    2047  Jul  22  22:36:17   91  P   63.4S  160.2E
    2047  Dec  16  23:50:12   91  P   66.4S    6.6W
    2048  Jun  11  12:58:53   92  A   63.7N   11.5W
    2048  Dec  05  15:35:27   92  T   46.1S   56.4W
    2049  May  31  13:59:59   92  A   15.3N   29.9W
    2049  Nov  25  05:33:48   93  H    3.8S   95.2E
    2050  May  20  20:42:50   94  H   40.1S  123.7W
    2050  Nov  14  13:30:53   95  P   69.5N    1.0E
    2051  Apr  11  02:10:39   95  P   71.6N   32.2E
    2051  Oct  04  21:02:14   96  P   72.0S  117.7E
    2052  Mar  30  18:31:53   97  T   22.4N  102.5W
    2052  Sep  22  23:39:10   98  A   25.7S  175.0E
    2053  Mar  20  07:08:19   99  A   23.0S   83.0E
    2053  Sep  12  09:34:09  100  T   21.5N   41.7E
    2054  Mar  09  12:33:40  101  P   72.0S   97.9E
    2054  Aug  03  18:04:02  102  Pe  69.8S  121.3W
    2054  Sep  02  01:09:34  102  P   71.7N   82.3W
    2055  Jan  27  17:54:05  103  P   69.5N  112.2W
    2055  Jul  24  09:57:50  104  T   33.3S   25.8E
    2056  Jan  16  22:16:45  105  A    3.9N  153.5W
    2056  Jul  12  20:21:59  106  A   19.4N  123.7W
    2057  Jan  05  09:47:52  107  T   39.2S   35.2E
    2057  Jul  01  23:40:15  108  A   71.5N  176.2W
    2057  Dec  26  01:14:35  109  T   84.9S   21.8E
    2058  May  22  10:39:25  110  P   63.5S   61.1E
    2058  Jun  21  00:19:35  110  Pb  65.9N    9.9E
    2058  Nov  16  03:23:07  111  P   62.9N  174.2E
    2059  May  11  19:22:16  112  T   10.7S  100.4W
    2059  Nov  05  09:18:15  113  A    8.7N   47.1E
    2060  Apr  30  10:10:00  114  T   28.0N   20.9E
    2060  Oct  24  09:24:10  115  A   25.8S   28.1E
    2061  Apr  20  02:56:49  116  T   64.5N   59.2E
    2061  Oct  13  10:32:10  117  A   62.1S   54.4W
    2062  Mar  11  04:26:16  118  P   61.0S  147.1W
    2062  Sep  03  08:54:27  119  P   61.3N  150.3E
    2063  Feb  28  07:43:30  120  A   25.2S   77.7E
    2063  Aug  24  01:22:11  121  T   25.6N  168.4E
    2064  Feb  17  07:00:23  122  A    7.0N   69.7E
    2064  Aug  12  17:46:06  123  T   10.9S   96.0W
    2065  Feb  05  09:52:26  124  P   62.2N   21.9W
    2065  Jul  03  17:33:52  125  P   64.8N   71.9E
    2065  Aug  02  05:34:17  125  P   62.7S   46.5E
    2065  Dec  27  08:39:56  126  P   65.4S  149.2W
    2066  Jun  22  19:25:48  127  A   70.1N   96.4W
    2066  Dec  17  00:23:40  128  T   47.4S  175.8E
    2067  Jun  11  20:42:26  129  A   21.0N  130.2W
    2067  Dec  06  14:03:43  130  H    6.0S   32.4W
    2068  May  31  03:56:39  131  T   31.0S  123.2E
    2068  Nov  24  21:32:30  132  P   68.5N  131.1W
    2069  Apr  21  10:11:09  133  P   71.0N  101.3W
    2069  May  20  17:53:18  133  Pb  68.8S   69.9W
    2069  Oct  15  04:19:56  134  P   71.6S    5.5W
    2070  Apr  11  02:36:09  135  T   29.1N  135.1E
    2070  Oct  04  07:08:57  136  A   32.8S   60.4E
    2071  Mar  31  15:01:06  138  A   16.7S   37.0W
    2071  Sep  23  17:20:28  139  T   14.2N   76.7W
    2072  Mar  19  20:10:31  140  P   72.2S   30.4W
    2072  Sep  12  08:59:20  141  T   69.8N  102.0E
    2073  Feb  07  01:55:59  142  P   70.5N  114.9E
    2073  Aug  03  17:15:23  143  T   43.2S   89.4W
    2074  Jan  27  06:44:15  144  A    6.6N   78.8E
    2074  Jul  24  03:10:32  145  A   12.8N  133.7E
    2075  Jan  16  18:36:04  146  T   37.2S   94.1W
    2075  Jul  13  06:05:44  147  A   63.1N   95.2E
    2076  Jan  06  10:07:27  148  T   87.2S  173.7W
    2076  Jun  01  17:31:22  149  P   64.4S   51.2W
    2076  Jul  01  06:50:43  149  P   67.0N   98.1W
    2076  Nov  26  11:43:01  150  P   63.7N   40.1E
    2077  May  22  02:46:05  151  T   13.1S  148.3E
    2077  Nov  15  17:07:56  152  A    7.8N   70.8W
    2078  May  11  17:56:55  153  T   28.1N   93.7W
    2078  Nov  04  16:55:44  154  A   27.8S   83.3W
    2079  May  01  10:50:13  155  T   66.2N   46.3W
    2079  Oct  24  18:11:21  156  A   63.4S  160.6W
    2080  Mar  21  12:20:15  157  P   60.9S   85.9E
    2080  Sep  13  16:38:09  158  P   61.1N   25.8E
    2081  Mar  10  15:23:31  159  A   22.4S   36.7W
    2081  Sep  03  09:07:31  160  T   24.6N   53.6E
    2082  Feb  27  14:47:00  162  A    9.4N   47.1W
    2082  Aug  24  01:16:21  163  T   10.3S  151.8E
    2083  Feb  16  18:06:36  164  P   61.6N  154.1W
    2083  Jul  15  00:14:23  165  Pe  64.0N   37.7W
    2083  Aug  13  12:34:41  165  P   62.1S   67.5W
    2084  Jan  07  17:30:24  166  P   64.4S   68.5E
    2084  Jul  03  01:50:26  167  A   75.0N  169.1W
    2084  Dec  27  09:13:48  168  T   47.3S   47.7E
    2085  Jun  22  03:21:16  169  A   26.2N  131.3E
    2085  Dec  16  22:37:48  170  A    7.3S  160.8W
    2086  Jun  11  11:07:14  171  T   23.2S   12.5E
    2086  Dec  06  05:38:55  172  P   67.4N   96.2E
    2087  May  02  18:04:42  173  P   70.3N  127.6E
    2087  Jun  01  01:27:14  173  P   67.8S  165.4E
    2087  Oct  26  11:46:57  174  P   71.0S  130.5W
    2088  Apr  21  10:31:49  175  T   36.0N   15.1E
    2088  Oct  14  14:48:05  177  A   39.7S   56.0W
    2089  Apr  10  22:44:42  178  A   10.2S  154.8W
    2089  Oct  04  01:15:23  179  T    7.4N  162.8E
    2090  Mar  31  03:38:08  180  P   72.1S  156.3W
    2090  Sep  23  16:56:36  181  T   60.7N   40.5W
    2091  Feb  18  09:54:40  182  P   71.2N   17.8W
    2091  Aug  15  00:34:43  183  T   55.6S  150.5E
    2092  Feb  07  15:10:20  184  A    9.9N   48.7W
    2092  Aug  03  09:59:33  185  A    5.6N   30.3E
    2093  Jan  27  03:22:16  186  T   34.1S  136.4E
    2093  Jul  23  12:32:04  187  A   54.6N    1.3E
    2094  Jan  16  18:59:03  189  T   84.8S   10.6W
    2094  Jun  13  00:22:11  190  P   65.3S  163.6W
    2094  Jul  12  13:24:35  190  P   68.0N  152.8E
    2094  Dec  07  20:05:56  191  P   64.7N   95.0W
    2095  Jun  02  10:07:40  192  T   16.7S   37.2E
    2095  Nov  27  01:02:57  193  A    7.2N  169.8E
    2096  May  22  01:37:14  194  T   27.3N  153.4E
    2096  Nov  15  00:36:15  195  A   29.7S  163.3E
    2097  May  11  18:34:31  196  T   67.4N  149.5W
    2097  Nov  04  02:01:25  197  A   65.8S   86.8E
    2098  Apr  01  20:02:31  198  P   61.0S   38.1W
    2098  Sep  25  00:31:16  199  P   61.1N  101.0W
    2098  Oct  24  10:36:11  200  Pb  61.8S   95.5W
    2099  Mar  21  22:54:32  201  A   20.0S  149.0W
    2099  Sep  14  16:57:53  202  T   23.4N   62.8W ''' )


def _get_eclipse_type_from_table_value(
    eclipse_type ):
    '''
    https://eclipse.gsfc.nasa.gov/LEcat5/LEcatkey.html
    https://eclipse.gsfc.nasa.gov/SEcat5/catkey.html
    '''
    if eclipse_type[ 0 ] == 'A':
        _eclipse_type = EclipseType.ANNULAR

    elif eclipse_type[ 0 ] == 'H':
        _eclipse_type = EclipseType.HYBRID

    elif eclipse_type[ 0 ] == 'P':
        _eclipse_type = EclipseType.PARTIAL

    elif eclipse_type[ 0 ] == 'N':
        _eclipse_type = EclipseType.PENUMBRAL

    else: # T
        _eclipse_type = EclipseType.TOTAL

    return _eclipse_type


def _get_eclipse(
    utc_now,
    eclipses ):

    eclipse_information = None
    for line in eclipses.splitlines():
        fields = line.split()

        year = fields[ 0 ]
        month = fields[ 1 ]
        day = fields[ 2 ]
        time_utc = fields[ 3 ]
        delta_t = fields[ 4 ]

        # https://eclipse.gsfc.nasa.gov/LEcat5/deltat.html
        date_time = (
            datetime.datetime.strptime(
                year + ", " + _months[ month ] + ", " + day + ", " + time_utc,
                "%Y, %m, %d, %H:%M:%S" ) )

        date_time = date_time.replace( tzinfo = datetime.timezone.utc )
        date_time = date_time - datetime.timedelta( seconds = int( delta_t ) )

        if utc_now <= date_time:
            latitude = fields[ 6 ]
            longitude = fields[ 7 ]

            latitude_ = str( int( float( latitude[ : -1 ] ) ) )
            if latitude.endswith( 'S' ):
                latitude_ = '-' + latitude_

            longitude_ = str( int( float( longitude[ : -1 ] ) ) )
            if longitude.endswith( 'E' ):
                longitude_ = '-' + longitude_

            eclipse_information = (
                date_time,
                _get_eclipse_type_from_table_value( fields[ 5 ][ 0 ] ),
                latitude_,
                longitude_ )

            break

    return eclipse_information


def get_eclipse_lunar(
    utc_now ):
    '''
    Gets the upcoming lunar eclipse.

    Returns a tuple:
        datetime in UTC with UTC timezone
        EclipseType
        latitude (south is negative)
        longitude (east is negative)

    When no eclipse found, returns None.
    '''
    return _get_eclipse( utc_now, _ECLIPSES_LUNAR )


def get_eclipse_solar(
    utc_now ):
    '''
    Gets the upcoming solar eclipse.

    Returns a tuple:
        datetime in UTC with UTC timezone
        EclipseType
        latitude (south is negative)
        longitude (east is negative)

    When no eclipse found, returns None.
    '''
    return _get_eclipse( utc_now, _ECLIPSES_SOLAR )


def get_eclipse_type_as_text(
    eclipse_type ):
    ''' Returns the translated descriptive text for a given eclipse type. '''
    if eclipse_type == EclipseType.ANNULAR:
        eclipse_type_text = _( "Annular" )

    elif eclipse_type == EclipseType.HYBRID:
        eclipse_type_text = _( "Hybrid (Annular/Total)" )

    elif eclipse_type == EclipseType.PARTIAL:
        eclipse_type_text = _( "Partial" )

    elif eclipse_type == EclipseType.PENUMBRAL:
        eclipse_type_text = _( "Penumbral" )

    else:
        eclipse_type_text = _( "Total" )

    return eclipse_type_text
