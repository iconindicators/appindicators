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
Build a Python3 .whl and .tar.gz for one or more indicators.

To view the contents of a .whl:
   unzip -l indicatortest-1.0.7-py3-none-any.whl

To view the contents of a .tar.gz:
   tar tf indicatortest-1.0.7.tar.gz
'''


from . import utils


if __name__ == "__main__":
    arguments = (
        utils.get_indicators_to_process(
            ( "tag", ),
            ( "The GitHub tag of the release for which this whl/tar.gz is built.", ),
            "Build a Python3 whl/tar.gz for one or more indicators at "
            f"{ utils.RELEASE_DIRECTORY }.",
            "build" ) )

    for indicator in arguments.indicators:
        command = (
            "python3 -c \"import tools.utils_build; "
            f"tools.utils_build.build_wheel( \\\"{ indicator }\\\", \\\"{ arguments.tag }\\\" )\"" )

        modules_to_install = [
            "build",
            "polib",
            utils.get_pygobject(),
            "setuptools",
            "readme_renderer[md]" ]

        result = (
            utils.python_run(
                command,
                utils.VENV_BUILD,
                *modules_to_install ) )

        if not utils.print_stdout_stderr_return_code( *result ):
            break
