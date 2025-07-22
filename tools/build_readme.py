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


''' Build the README.md for the project. '''


from . import utils


if __name__ == "__main__":
    indicators_to_process = (
        utils.get_indicators_to_process(
            "Build a Python3 wheel for one or more indicators at "
            f"{ utils.RELEASE_DIRECTORY }.",
            "build" ) )

    for indicator in indicators_to_process:
        command = (
            "python3 -c \"import tools.utils_build; "
            f"tools.utils_readme.build_readme_for_project()\"" )

        modules_to_install = [
            "readme_renderer[md]" ]

        result = (
            utils.python_run(
                command,
                utils.VENV_BUILD,
                *modules_to_install ) )

        if not utils.print_stdout_stderr_return_code( *result ):
            break
