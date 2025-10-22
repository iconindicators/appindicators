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


from pathlib import Path

from . import utils


if __name__ == "__main__":

    # Remove symbolic links to indicatorbase.py to avoid duplicates.
    command_remove_symbolic_links = (
        "for dirs in indicator*; do "
        "if [ -L $dirs/src/$dirs/indicatorbase.py ] ; "
        "then rm $dirs/src/$dirs/indicatorbase.py ; fi ; "
        "done" )

    # Re-enable any check by commenting out the appropriate line.
    pylint_disabled_checks = (
        "--disable=attribute-defined-outside-init "
        "--disable=fixme "
        "--disable=line-too-long "
        "--disable=no-name-in-module "
        "--disable=relative-beyond-top-level "
        "--disable=too-few-public-methods "
        "--disable=too-many-arguments "
        "--disable=too-many-instance-attributes "
        "--disable=too-many-lines "
        "--disable=too-many-locals "
        # "--disable=too-many-positional-arguments " # Does not work on Ubuntu 20.04
        "--disable=too-many-public-methods "
        "--disable=too-many-statements "
        "--disable=undefined-variable "
        "--disable=unused-argument "
        "--disable=unused-variable "
        "--disable=wrong-import-position" )

    command_pylint = (
        "python3 -m pylint "
        "--recursive=y "
        "--ignore=release,venv_build,venv_run,astroskyfield.pymeteorshowertest.py "
        "--output=pylint.txt " 
        f"{ pylint_disabled_checks } "
        f"../{ Path.cwd().stem }" )

    command_sort = (
        "sort --output=pylint.txt -t ':' --key=4,4 --key=1,1 --key=2,2n pylint.txt" )

    # Reinstate symbolic links to indicatorbase.py.
    command_reinstate_symbolic_links = (
        "for dirs in indicator*; do "
        "if [ ! -f $dirs/src/$dirs/indicatorbase.py ]; "
        "then ln -sr indicatorbase/src/indicatorbase/indicatorbase.py "
        "$dirs/src/$dirs/indicatorbase.py; fi ; "
        "done" )

    command = (
        f"{ command_remove_symbolic_links } && "
        f"{ command_pylint } ; " # Must be ; not && otherwise will stop.
        f"{ command_sort } && "
        f"{ command_reinstate_symbolic_links }" )

    modules_to_install = [
        "pylint" ]

    result = (
        utils.python_run(
            command,
            utils.VENV_BUILD,
            *modules_to_install ) )

    utils.print_stdout_stderr_return_code( *result )
