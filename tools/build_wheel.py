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
    indicators_to_process = (
        utils.get_indicators_to_process(
            "Build a Python3 wheel for one or more indicators at "
            f"{ utils.RELEASE_DIRECTORY }.",
            "build" ) )

    for indicator in indicators_to_process:
        utils.python_run(
            "python3 -c \"import tools._build_wheel; "
            f"tools._build_wheel.build_wheel( \\\"{ indicator }\\\" )\"",
            utils.VENV_BUILD,
            "build",
            "pip",
            "polib",
            utils.get_pygobject(),
            "readme_renderer[md]" )
