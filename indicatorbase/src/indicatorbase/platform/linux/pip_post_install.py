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


# Complete the 'pip' installation: copy from the installation directory
# the icon(s), .desktop and run script to the .local directory.


import argparse
from pathlib import Path


'''
mkdir -p $HOME/.local/bin

cp $(ls -d $HOME/.local/venv_indicatortest/lib/python3.* | head -1)/site-packages/indicatortest/platform/linux/indicatortest.sh $HOME/.local/bin

cp $(ls -d $HOME/.local/venv_indicatortest/lib/python3.* | head -1)/site-packages/indicatortest/platform/linux/indicatortest.py.desktop $HOME/.local/share/applications
'''

parser = argparse.ArgumentParser()
parser.add_argument( "indicator" )
args = parser.parse_args()

dot_local_directory = Path( Path.home(), ".local" )

# mkdir -p $HOME/.local/share/icons/hicolor/scalable/apps
icon_directory = Path( dot_local_directory, "share/icons/hicolor/scalable/apps" )
icon_directory.mkdir( parents = True, exist_ok = True )

# cp $(ls -d $HOME/.local/venv_indicatortest/lib/python3.* | head -1)/site-packages/indicatortest/icons/*.svg $HOME/.local/share/icons/hicolor/scalable/apps
python_venv_directory = Path( dot_local_directory, "venv_" + args.indicator, "lib" )
print( python_venv_directory )

python_directories = [ str( x ) for x in python_venv_directory.iterdir() if x.is_dir() ]

# distutils is deprecated and removed in python 3.12
# and need to use packaging.version instead.
# So might have to do an import thing where we try distutils first (or vice versa)
# and catch the exception (like in importing appindicator)
# and import packaging.
#  https://stackoverflow.com/a/1875267/2156453
#  https://snyk.io/advisor/python/packaging/functions/packaging.version
from distutils.version import LooseVersion
versions = ["1.7.0", "1.7.0rc0", "1.11.0"]
print( sorted( python_directories, key = LooseVersion ) )


#TODO What happens when we do the install...and then want to do an upgrade?
# The install will use the default python3, say python3.8.
# Then the upgrade will use the default python3...but what if that python3 is now python3.12?
# So need to check the version number and get the highest because an upgrade might break.
#
# Additionally, if Python3.8 was used to do the install,
# and now the user does an upgrade/update and uses the same instructions/commands
# as the first time around but now has Python3.11 installed.
# The 'ls -d ... | head -1' stuff will find Python3.11 rather than 3.8.
# This will now create two installs...not good.
#
# Can upgrade be done with a script instead?
# Only use PIP page for a clean install?


#TODO Noticed for Ubuntu on the testpypi page that in the apt-get install line
# there is no python3-pip...ensure this gets installed, presumably via python3-venv.
#
# Looking at
    #
    # $ apt rdepends python3-pip
    # python3-pip
    # Reverse Depends:
    #   python3.8-venv
    #   python3.11-venv
    #   indicator-lunar
    #   python3.9-venv
    #   python3.8-venv
    #   thonny
    #   sagemath
    #   duplicity
    #   python3-ryu
    #   python3-pypandoc
    #   python3-pipdeptree
    #   python3-jupyter-core
    #   pipenv
    #   parsero
    #   lektor
    #   gnumed-client
    #   elpa-elpy
    #   dhcpcanon
    #
    # $ apt rdepends python3-venv
    # python3-venv
    # Reverse Depends:
    #   python3.8
    #   python3.9
    #   python3.8
    #   xonsh
    #   thonny
    #   python3
    #
    # $ apt depends python3-pip
    # python3-pip
    #   Depends: ca-certificates
    #   Depends: python3-distutils
    #   Depends: python3-setuptools
    #   Depends: python3-wheel
    #   Depends: python-pip-whl
    #   Depends: <python3:any>
    #     python3:i386
    #     python3
    #   Breaks: <python-pip>
    #   Recommends: build-essential
    #   Recommends: python3-dev
    #   Replaces: <python-pip>
    #
    # $ apt depends python3-venv
    # python3-venv
    #   Depends: python3.8-venv
    #   Depends: python3
    #   Depends: python3-distutils
#
# not sure which depends on which!
#
# I think best to just include both python3-venv and python3-pip for Debian/Ubuntu.
# Check all other distros too!
# Maybe can Google how to create a venv on Manjaro, etc, etc and see what package they install and use that.
# Ditto for installing/running pip.
