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


''' Convert the project README.md to README.html '''


from pathlib import Path

from . import utils


if __name__ == "__main__":
    current_working_directory = Path.cwd()
    markdown = str( current_working_directory / "README.md" )
    html = str( current_working_directory / "README.html" )
    command = (
        "python3 -c \"import tools._markdown_to_html; "
        "tools._markdown_to_html.markdown_to_html( "
        f"\\\"{ markdown }\\\", \\\"{ html }\\\" )\"" )

    modules_to_install = [
        "pip",
        "readme_renderer[md]" ]

    result = (
        utils.python_run(
            command,
            utils.VENV_BUILD,
            *modules_to_install ) )

    utils.print_stdout_stderr_return_code( *result )
    if result[ 2 ] == 0: # Return code of zero; all is well.
        print( f"\nCreated { html }" )
