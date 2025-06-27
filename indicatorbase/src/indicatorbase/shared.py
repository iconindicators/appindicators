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


'''Functions shared between indicators and development tools. '''


import subprocess


#TODO Hopefully can go if I get everything back into IndicatorBase.
# def get_year_in_changelog_markdown(
#     changelog_markdown,
#     first_year = True ):
#     '''
#     If first_year = True, retrieves the first/earliest year from
#     CHANGELOG.md otherwise retrieves the most recent year.
#     '''
#     year = ""
#     with open( changelog_markdown, 'r', encoding = "utf-8" ) as f:
#         lines = f.readlines()
#         if first_year:
#             lines = reversed( lines )
#
#         for line in lines:
#             if line.startswith( "## v" ):
#                 left_parenthesis = line.find( '(' )
#                 year = (
#                     line[ left_parenthesis + 1 : left_parenthesis + 1 + 4 ] )
#
#                 break
#
#     return year


#TODO Hopefully can go if I get everything back into IndicatorBase.
# def get_etc_os_release():
#     '''
#     Return the result of calling
#         cat /etc/os-release
#     '''
#     return process_run( "cat /etc/os-release" )[ 0 ]


#TODO Hopefully can go if I get everything back into IndicatorBase.
# def process_run(
#     command,
#     capture_output = True,
#     print_ = False,
#     logging = None ):  #TODO Handle logging...will (SHOULD) exist for calls from indicators, but not from tools.
#     '''
#     Executes the command, returning the tuple:
#         stdout
#         stderr
#         return code
#
# #TODO Why not ALWAYS capture output?
#     If capture_output is True, stdout and stderr are captured;
#     otherwise, stdout and stderr are set to "".
#
# #TODO Is this needed? If end user wants the result, up to end user to sift stdout from stderr.
#     If print_ is True, prints stdout and stderr to the console.
#
#     On stderr or exception, logs to a file, if logging was previously
#     initialised.
#     '''
#     try:
#         result = (
#             subprocess.run(
#                 command,
#                 shell = True,
#                 capture_output = capture_output ) )
# #TODO Used to have check = True, but that throws an exception for grep when grep
# # finds no result but returns a 1 (which is not 0 and thus an exception is thrown).
# # Who/when might need check = True?
#
#         if capture_output:
#             stdout_ = result.stdout.decode().strip()
#             stderr_ = result.stderr.decode()
#             # if stderr_ and IndicatorBase._LOGGING_INITIALISED:
#             #     IndicatorBase.get_logging().error( stderr_ )
#
#         else:
#             stdout_ = ""
#             stderr_ = ""
#
#         return_code = result.returncode
#
#     except subprocess.CalledProcessError as e:
#         print( "EXCEPTION" ) #TODO Testing
#         # if logging:# TODO Need this but what about below?
#         # if IndicatorBase._LOGGING_INITIALISED:
#         #     print("----") #TODO Testing
#         #     print( e.stdout )
#         #     print("----")
#         #     print( e.stderr )
#         #     print("----")
#         #     print( e.returncode )
#         #     print("----")
#         #     IndicatorBase.get_logging().error( e.stderr.decode() )
#
# #TODO Find a way to trigger this exception and determine what happens when
# # capture_output is True (stdout/stderr should be defined so decode is okay) and
# # when capture_output is False (stdout/stderr should be not be defined so decode is unsafe).
# # Can trigger the exception on grep but no result but get a return code of 1
# # but need to set check = True in the call to subprocess.run().
#         stdout_ = e.stdout.decode()
#         stderr_ = e.stderr.decode()
#         return_code = e.returncode
#
#     if print_:
#         if stdout_:
#             print( stdout_ )
#
#         elif stderr_:
#             print( stderr_ )
#
#         if return_code != 0:
#             print( f"return code: { return_code }" )
#
#     return stdout_, stderr_, return_code
