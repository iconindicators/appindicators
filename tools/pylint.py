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


''' Run Pylint, with several checks disabled. '''


from . import utils


if __name__ == "__main__":
    # To enable any disabled check below, comment out that line.
    command = (
        "python3 -m pylint "
        "--disable=line-too-long "
        "--disable=missing-function-docstring "
        "--disable=too-many-lines "
        "--disable=wrong-import-position "
        "--disable=import-error "
        "--disable=undefined-variable "
        "--disable=no-name-in-module "
        "--disable=no-member "
        "--disable=too-many-instance-attributes "
        "--disable=too-many-branches "
        "--disable=too-many-arguments "
        "--disable=too-many-locals "
        "--disable=too-many-statements "
        "--disable=too-many-boolean-expressions "
        "--disable=too-many-nested-blocks "
        "--disable=attribute-defined-outside-init "
        "--disable=unused-argument "
        "--disable=f-string-without-interpolation "
        "--disable=too-few-public-methods "
        "--disable=too-many-public-methods "
        "--disable=unused-variable "
        "--disable=fixme "
        "--recursive=y "
        "--ignore=release,venv_build,venv_run,indicatorfortune/src/indicator/fortune/indicatorbase.py "
        "../Indicators "
        "--output=pylint.txt ; "
        "sort --output=pylint.txt -t ':' --key=4,4 --key=1,1 --key=2,2n pylint.txt" )

    modules_to_install = [
        "pylint" ]

    result = (
        utils.python_run(
            command,
            utils.VENV_BUILD,
            *modules_to_install ) )

    utils.print_stdout_stderr_return_code( *result )
