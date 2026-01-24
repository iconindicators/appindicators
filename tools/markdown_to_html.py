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


''' Convert a file in markdown to html. '''


from pathlib import Path

from . import utils


if __name__ == "__main__":
    arguments = (
        utils.get_arguments(
            "Convert a file in markdown to html.",
            ( "markdown", ) ) )

    f_in = Path( arguments.markdown )
    if f_in.is_file():
        f_out = f_in.parent / ( f_in.stem + ".html" )

        command = f"python3 -m readme_renderer { f_in } -o { f_out }"

        modules_to_install = [
            "readme_renderer[md]" ]

        result = (
            utils.python_run(
                command,
                utils.VENV_BUILD,
                *modules_to_install ) )

        if utils.print_stdout_stderr_return_code( *result ):
            print( f"\nCreated { f_out }" )

    else:
        print( f"{ f_in } is not a file." )
