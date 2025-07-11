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
    command = (
        # Remove symbolic links to indicatorbase.py to avoid duplicates.
        "for dirs in indicator*; do "
        "if [ -L $dirs/src/$dirs/indicatorbase.py ] ; "
        "then rm $dirs/src/$dirs/indicatorbase.py ; fi ; "
        "done && "

        # Uncomment any line below to disable the check.
        "python3 -m pylint "
        "--disable=attribute-defined-outside-init "
        # "--disable=f-string-without-interpolation "
        "--disable=fixme "
        # "--disable=import-error "
        "--disable=line-too-long "
        # "--disable=missing-function-docstring "
        # "--disable=no-member "
        "--disable=no-name-in-module "
        "--disable=relative-beyond-top-level "
        "--disable=too-few-public-methods "
        "--disable=too-many-arguments "
        # "--disable=too-many-boolean-expressions "
        # "--disable=too-many-branches "
        "--disable=too-many-instance-attributes "
        "--disable=too-many-lines "
        "--disable=too-many-locals "
        # "--disable=too-many-nested-blocks "
        # "--disable=too-many-positional-arguments " # Does not work on Ubuntu 20.04
        "--disable=too-many-public-methods "
        "--disable=too-many-statements "
        "--disable=undefined-variable "
        "--disable=unused-argument "
        "--disable=unused-variable "
        "--disable=wrong-import-position "

        "--recursive=y "
        "--ignore=release,venv_build,venv_run,meteorshowertest.py "
        "../Indicators "
        "--output=pylint.txt ; " # Must be ; not && otherwise will stop.

        "sort --output=pylint.txt -t ':' --key=4,4 --key=1,1 --key=2,2n pylint.txt && "

        # Reinstate symbolic links to indicatorbase.py.
        "for dirs in indicator*; do "
        "if [ ! -f $dirs/src/$dirs/indicatorbase.py ]; "
        "then ln -sr indicatorbase/src/indicatorbase/indicatorbase.py "
        "$dirs/src/$dirs/indicatorbase.py; fi ; "
        "done" )

    modules_to_install = [
        "pylint" ]

    result = (
        utils.python_run(
            command,
            utils.VENV_BUILD,
            *modules_to_install ) )

    utils.print_stdout_stderr_return_code( *result )
