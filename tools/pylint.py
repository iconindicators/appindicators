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


''' Run Pylint '''


from . import utils


if __name__ == "__main__":
    command = (
        "python3 -m pylint --recursive=y --ignore=release,venv_build,venv_run "
        "../Indicators --output=pylint.txt ; "
        "sort --output=pylint.txt -t ':' --key=4,4 --key=1,1 --key=2,2n pylint.txt" )

    modules_to_install = [
        "pylint" ]

    result = (
        utils.python_run(
            command,
            utils.VENV_BUILD,
            *modules_to_install ) )

    utils.print_stdout_stderr_return_code( *result )
