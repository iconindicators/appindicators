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


#TODO If this script method of install works,
# need to amend the readme such that the OS packages of python3-venv and python3-pip
# (or equivalent for each distro/version) are installed by the user up front.


#TODO For an upgrade, consider a whole new script
# which is used to do full upgrade, rather than running any 
# of the original install instructions.
# How much of this post_install script can be reused?
#
# I think the upgrade needs to be a combination of kick off a pip upgrade
# and then run a post-upgrade script
# (the post-upgrade script could be updated so not a good idea to run a script 
# that does an update that wants to update the script itself).



#TODO What is the difference between install and upgrade and removal:
#
# INSTALL
#   sudo apt-get -y install fortune-mod fortunes gir1.2-ayatanaappindicator3-0.1 gir1.2-gtk-3.0 gnome-shell-extension-appindicator libcairo2-dev libgirepository1.0-dev pkg-config python3-dev python3-gi python3-gi-cairo python3-notify2 python3-venv wmctrl
#
#   python3 -m venv $HOME/.local/venv_indicatortest && \
#   . $HOME/.local/venv_indicatortest/bin/activate && \
#   python3 -m pip install --upgrade pip indicatortest && \
#   deactivate
#
#   mkdir -p $HOME/.local/share/icons/hicolor/scalable/apps && \
#   cp $(ls -d $HOME/.local/venv_indicatortest/lib/python3.* | head -1)/site-packages/indicatortest/icons/*.svg $HOME/.local/share/icons/hicolor/scalable/apps && \
#   mkdir -p $HOME/.local/bin && \
#   cp $(ls -d $HOME/.local/venv_indicatortest/lib/python3.* | head -1)/site-packages/indicatortest/platform/linux/indicatortest.sh $HOME/.local/bin && \
#   cp $(ls -d $HOME/.local/venv_indicatortest/lib/python3.* | head -1)/site-packages/indicatortest/platform/linux/indicatortest.py.desktop $HOME/.local/share/applications
#
# UPGRADE
#   sudo apt-get -y install <a new package required by a change to an indicator; remove a package no longer used>
#
#   . $HOME/.local/venv_indicatortest/bin/activate && \       <no need to create the venv>
#   python3 -m pip install --upgrade pip indicatortest && \
#   deactivate
#
#   mkdir -p $HOME/.local/share/icons/hicolor/scalable/apps && \   <new/upgraded icons or a change to the .desktop.sh>
#   cp $(ls -d $HOME/.local/venv_indicatortest/lib/python3.* | head -1)/site-packages/indicatortest/icons/*.svg $HOME/.local/share/icons/hicolor/scalable/apps && \
#   mkdir -p $HOME/.local/bin && \
#   cp $(ls -d $HOME/.local/venv_indicatortest/lib/python3.* | head -1)/site-packages/indicatortest/platform/linux/indicatortest.sh $HOME/.local/bin && \
#   cp $(ls -d $HOME/.local/venv_indicatortest/lib/python3.* | head -1)/site-packages/indicatortest/platform/linux/indicatortest.py.desktop $HOME/.local/share/applications
#
# REMOVE
#   sudo apt-get -y remove fortune-mod fortunes gir1.2-ayatanaappindicator3-0.1 gir1.2-gtk-3.0 gnome-shell-extension-appindicator libcairo2-dev libgirepository1.0-dev pkg-config python3-dev python3-gi python3-gi-cairo python3-notify2 python3-venv wmctrl
#
#   rm $HOME/.local/share/icons/hicolor/scalable/apps/<icons for the indicator...maybe get that list from the indicator directory>
#   rm $HOME/.local/bin/indicatortest.sh
#   rm $HOME/.local/share/applications/indicatortest.py.desktop
#   rm -r $HOME/.local/venv_indicatortest
# What about .cache, .config and any log files?
   

#TODO TO RUN FROM TERMINAL:
#   python3 $(ls -d $HOME/.local/venv_indicatortest/lib/python3.* | head -1)/site-packages/indicatortest/platform/linux/pip_post_install.py


# import argparse
from enum import auto, Enum
import os
from pathlib import Path
import platform
import shutil
import subprocess


class Operating_System( Enum ):
    DEBIAN_11_DEBIAN_12 = auto()
    FEDORA_38_FEDORA_39 = auto()
    MANJARO_221 = auto()
    OPENSUSE_TUMBLEWEED = auto()
    UBUNTU_2004 = auto()
    UBUNTU_2204 = auto()


indicator_names = [
    "indicatorbase", #TODO Remove...only used for testing.
    "indicatorfortune",
    "indicatorlunar",
    "indicatoronthisday",
    "indicatorppadownloadstatistics",
    "indicatorpunycode",
    "indicatorscriptrunner",
    "indicatorstardate",
    "indicatortest",
    "indicatortide",
    "indicatorvirtualbox" ]


def copy_files():
    indicator_directory = Path( os.path.realpath( __file__ ) ).parents[ 2 ]
    indicator_name = indicator_directory.name

    dot_local_directory = Path( Path.home(), ".local" )

    # mkdir -p $HOME/.local/share/icons/hicolor/scalable/apps
    # Create the icons directory.
    dot_local_icon_directory = Path( dot_local_directory, "share/icons/hicolor/scalable/apps" )
    dot_local_icon_directory.mkdir( parents = True, exist_ok = True )

    # cp $(ls -d $HOME/.local/venv_indicatortest/lib/python3.* | head -1)/site-packages/indicatortest/icons/*.svg $HOME/.local/share/icons/hicolor/scalable/apps
    # Copy icons from indicator installation to icons directory.
    indicator_icon_directory = Path( indicator_directory, "icons" )
    shutil.copytree( indicator_icon_directory, dot_local_icon_directory, dirs_exist_ok = True ) #TODO Need to overwrite if already there?  

    # mkdir -p $HOME/.local/bin
    # Create the bin directory.
    dot_local_bin_directory = Path( dot_local_directory, "bin" )
    dot_local_bin_directory.mkdir( parents = True, exist_ok = True )

    # cp $(ls -d $HOME/.local/venv_indicatortest/lib/python3.* | head -1)/site-packages/indicatortest/platform/linux/indicatortest.sh $HOME/.local/bin
    # Copy indicator run script from indicator installation to bin directory.
#TODO Why check for the existence of the run script (and also the .desktop below)
# but we don't check for the existence of the icons?
# If this is a fresh install, no need to check.
# If there is a pre-existing install, this script will work (except for the icons already existing and not checking first).
# Maybe also check for the icons and then this script (or in part) can be used for the upgrade.
    if not Path( dot_local_bin_directory, indicator_name + ".sh" ).is_file():
        shutil.copyfile(
            str( Path( indicator_directory, "platform/linux/" + indicator_name + ".sh" ) ),
            str( Path( dot_local_bin_directory, indicator_name + ".sh" ) ) )

    # mkdir -p $HOME/.local/share/applications
    dot_local_applications_directory = Path( dot_local_directory, "share/applications" )
    # Create the applications directory.
    dot_local_applications_directory.mkdir( parents = True, exist_ok = True )

    # cp $(ls -d $HOME/.local/venv_indicatortest/lib/python3.* | head -1)/site-packages/indicatortest/platform/linux/indicatortest.py.desktop $HOME/.local/share/applications
    # Copy indicator .desktop from indicator installation to applications directory.
    if not Path( dot_local_applications_directory, indicator_name + ".py.desktop" ).is_file():
        shutil.copyfile(
            str( Path( indicator_directory, "platform/linux/" + indicator_name + ".py.desktop" ) ),
            str( Path( dot_local_applications_directory, indicator_name + ".py.desktop" ) ) )


#TODO This needs to take into account the indicator too...
# See the build_readme script.
# Either use that code to determine packages for each distro/version/indicator combination
# or come up with something else.
distribution_names_and_versions_to_operating_sytem_packages = {
    "ubuntu2004" : "sudo apt-get -y install fortune-mod fortunes gir1.2-ayatanaappindicator3-0.1 gir1.2-gtk-3.0 gnome-shell-extension-appindicator libcairo2-dev libgirepository1.0-dev pkg-config python3-dev python3-gi python3-gi-cairo python3-notify2 wmctrl"
}


def install_operating_system_packages( operating_system, indicator_name ):
    print( f"Installing operating system packages for { indicator_name } on { operating_system.name }...")
#TODO For each distro/version run something like:
#   sudo apt-get -y install calendar fortune-mod fortunes gir1.2-ayatanaappindicator3-0.1 gir1.2-gtk-3.0 gnome-shell-extension-appindicator libcairo2-dev libgirepository1.0-dev pkg-config python3-dev python3-gi python3-gi-cairo python3-notify2 python3-venv wmctrl
    command = "cat /etc/os-release"
    '''
    result = subprocess.run(
                command,
                stdout = subprocess.PIPE,
                stderr = subprocess.PIPE,
                shell = True ).stdout.decode()
    '''

    if operating_system == Operating_System.UBUNTU_2004:
        print( "TODO Return apt get install for ubuntu 20.04 and relevent indicator" )

    elif operating_system == Operating_System.DEBIAN_11_DEBIAN_12:
        print( "TODO Return apt get install for debian 11/12 and relevent indicator" )


# https://www.freedesktop.org/software/systemd/man/latest/os-release.html
# https://github.com/stejskalleos/os_release
def get_operating_system():
    operating_system = None
    command = "cat /etc/os-release"
    result = subprocess.run(
                command,
                stdout = subprocess.PIPE,
                stderr = subprocess.PIPE,
                shell = True ).stdout.decode()

    if "ID=debian" in result and ( "VERSION_ID=\"11\"" in result or "VERSION_ID=\"12\"" in result ):
        operating_system = Operating_System.DEBIAN_11_DEBIAN_12

    elif "ID=ubuntu" in result and "VERSION_ID=\"20.04\"" in result:
        operating_system = Operating_System.UBUNTU_2004

#TODO Add rest of supported distributions/versions.

    return operating_system


def get_indicator_directory():
    return Path( os.path.realpath( __file__ ) ).parents[ 2 ]


def get_indicator_name():
    return get_indicator_directory().name


indicator_name = get_indicator_name()
operating_system = get_operating_system()
if indicator_name not in indicator_names:
    print( f"TODO Indicator { indicator_name } is invalid.  Please contact the author." )

elif operating_system is None:
    print( f"TODO Unknown/unsupported distribution/version.  Please contact the author." )

else:
    # print( indicator_name )
    # print( operating_system )
    # print( "Good to install...!" )
    install_operating_system_packages( operating_system, indicator_name )
#TODO Is there a way to see if the packages were installed and if so, continue; if not, message user?
    # copy_files()





#   https://stackoverflow.com/questions/4256107/running-bash-commands-in-python
# To run as sudo:
#   sudo python3 pip_post_install.py
# import subprocess
# cmd = "sudo apt update"
# results = subprocess.run( cmd, shell = True, universal_newlines = True, check = True )
# print( results.stdout )






#OLD STUFF BELOW....NOT SURE IF ANY IS VALID BUT CHECK ANYWAY.


# python_venv_directory = Path( dot_local_directory, "venv_" + args.indicator, "lib" )
# print( python_venv_directory )



# python_directories = [ str( x ) for x in python_venv_directory.iterdir() if x.is_dir() ]

# distutils is deprecated and removed in python 3.12
# and need to use packaging.version instead.
# So might have to do an import thing where we try distutils first (or vice versa)
# and catch the exception (like in importing appindicator)
# and import packaging.
#  https://stackoverflow.com/a/1875267/2156453
#  https://snyk.io/advisor/python/packaging/functions/packaging.version
#from distutils.version import LooseVersion
#versions = ["1.7.0", "1.7.0rc0", "1.11.0"]
#print( sorted( python_directories, key = LooseVersion ) )

# This selects the correct version of python...at least on Debian 12.
# Guess need to check/test on all other supported distros!
# ls -d $HOME/.local/venv_indicatortest/lib/python3.* | sort --version-sort | tail -1



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
