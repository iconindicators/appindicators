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


# Create a README.md for an indicator.


import datetime
import re

from enum import auto, Enum
from pathlib import Path


class Operating_System( Enum ):
    DEBIAN_11_12 = auto() 
    FEDORA_38_39 = auto()
    FEDORA_40 = auto() #TODO After testing on new VMs...can this be absorbed into the above?
    MANJARO_221 = auto()
    OPENSUSE_TUMBLEWEED = auto()
    UBUNTU_2004 = auto()
    UBUNTU_2204_2404 = auto()


class Indicator_Name( Enum ):
    INDICATORFORTUNE = auto()
    INDICATORLUNAR = auto()
    INDICATORONTHISDAY = auto()
    INDICATORPPADOWNLOADSTATISTICS = auto()
    INDICATORPUNYCODE = auto()
    INDICATORSCRIPTRUNNER = auto()
    INDICATORSTARDATE = auto()
    INDICATORTEST = auto()
    INDICATORTIDE = auto()
    INDICATORVIRTUALBOX = auto()


def is_indicator( indicator_name, *indicator_names ):
    is_indicator = False
    for indicator_name_ in indicator_names:
        if indicator_name.upper() == indicator_name_.name:
            is_indicator = True
            break
        
    return is_indicator


def _get_indicator_names_sans_current( indicator_name ):
    indicators = [ str( x ) for x in Path( '.' ).iterdir() if x.is_dir() and str( x ).startswith( "indicator" ) ]
    indicators.remove( indicator_name )
    indicators.remove( "indicatorbase" )
    indicators.sort()
    return indicators


def _get_introduction( indicator_name ):
    pattern_tag = re.compile( f".*comments = _\(.*" )
    for line in open( indicator_name + '/src/' + indicator_name + '/' + indicator_name + ".py" ).readlines():
        matches = pattern_tag.search( line )
        if matches:
            comments = matches.group().split( "\"" )[ 1 ].replace( '\\n', ' ' )[ 0 : -1 ] # Remove \n and drop ending .
            comments = comments[ 0 ].lower() + comments[ 1 : ] # Lower case leading char
            break

    # openSUSE Tumbleweed and Manjaro do not contain the package 'calendar' or equivalent.
    # When creating the README.md for indicatoronthisday, drop references to openSUSE/Manjaro.
    introduction = (
        f"`{ indicator_name }` { comments } on "
        f"`Debian`, `Ubuntu`, `Fedora`" )

    if not is_indicator( indicator_name, Indicator_Name.INDICATORONTHISDAY ):
        introduction += f", `openSUSE`, `Manjaro`"

    introduction += f" and theoretically, any platform which supports the `appindicator` library.\n\n"

    introduction += f"Other indicators in this series are:\n"
    for indicator in _get_indicator_names_sans_current( indicator_name ):
        introduction += f"- [{ indicator }](https://pypi.org/project/{ indicator })\n"

    introduction += '\n'

    return introduction


#TODO Because indicatortest uses Pango,
# which I think pulls in the cairo stuff,
# wonder if I should try installing on a clean (or cleaned) VM
# stardate or punycode which have minimal imports...?
# Will have to do this for all distros.
#
# For indicatorstardate, removed libcairo2-dev from Ubuntu 20.04
# and installed/ran indicatorstardate...all good.
# 
# So only need libcairo2-dev for script runner and test.
def _get_operating_system_dependencies_debian( operating_system, indicator_name ):
    dependencies = [
        "gir1.2-ayatanaappindicator3-0.1",
        "libgirepository1.0-dev",
        "python3-pip",
        "python3-venv" ]

    if indicator_name == Indicator_Name.INDICATORFORTUNE:
        dependencies.append( "fortune-mod" )
        dependencies.append( "fortunes" )

    if indicator_name == Indicator_Name.INDICATORONTHISDAY:
        if operating_system != Operating_System.UBUNTU_2004:
            dependencies.append( "calendar" )

    if indicator_name == Indicator_Name.INDICATORSCRIPTRUNNER:
        dependencies.append( "libcairo2-dev" )
        dependencies.append( "libnotify-bin" )

    if indicator_name == Indicator_Name.INDICATORTEST:
        if operating_system != Operating_System.UBUNTU_2004:
            dependencies.append( "calendar" )

        dependencies.append( "fortune-mod" )
        dependencies.append( "fortunes" )
        dependencies.append( "libcairo2-dev" )
        dependencies.append( "libnotify-bin" )
        dependencies.append( "wmctrl" )

    if indicator_name == Indicator_Name.INDICATORVIRTUALBOX:
        dependencies.append( "wmctrl" )

    return ' '.join( sorted( dependencies ) )


#TODO
# For the old Fedora 38 or 39 or 40 VM,
# grab the history and see how installs happen...that is,
# do we install a package by name and no version number,
# or the package name AND version number?


#TODO Check these...
def _get_operating_system_dependencies_fedora( operating_system, indicator_name ):
    dependencies = [
        "cairo-devel",
        "cairo-gobject-devel",
        "gnome-extensions-app",
        "gnome-shell-extension-appindicator",
        "gobject-introspection-devel",
        "libappindicator-gtk3",
        "pkgconf-pkg-config",
        "python3-devel",
        "python3-gobject",
        "python3-pip" ]

    if indicator_name == Indicator_Name.INDICATORFORTUNE:
        dependencies.append( "fortune-mod" )
        dependencies.append( "python3-notify2" )

    if indicator_name == Indicator_Name.INDICATORLUNAR:
        dependencies.append( "python3-notify2" )

    if indicator_name == Indicator_Name.INDICATORONTHISDAY:
        dependencies.append( "calendar" )
        dependencies.append( "python3-notify2" )

    if indicator_name == Indicator_Name.INDICATORPUNYCODE:
        dependencies.append( "python3-notify2" )

    if indicator_name == Indicator_Name.INDICATORSCRIPTRUNNER:
        dependencies.append( "python3-notify2" )

    if indicator_name == Indicator_Name.INDICATORTEST:
        dependencies.append( "calendar" )
        dependencies.append( "fortune-mod" )
        dependencies.append( "python3-notify2" )
        dependencies.append( "wmctrl" )

    if indicator_name == Indicator_Name.INDICATORTIDE:
        dependencies.append( "python3-notify2" )

    if indicator_name == Indicator_Name.INDICATORVIRTUALBOX:
        dependencies.append( "python3-notify2" )
        dependencies.append( "wmctrl" )

    return ' '.join( sorted( dependencies ) )


#TODO Check these...
def _get_operating_system_dependencies_manjaro( operating_system, indicator_name ):
    dependencies = [
        "cairo",
        "gobject-introspection",
        "gtk3",
        "libayatana-appindicator",
        "pkgconf" ]

    if indicator_name == Indicator_Name.INDICATORFORTUNE:
        dependencies.append( "fortune-mod" )

    if indicator_name == Indicator_Name.INDICATORTEST:
        dependencies.append( "fortune-mod" )
        dependencies.append( "wmctrl" )

    if indicator_name == Indicator_Name.INDICATORVIRTUALBOX:
        dependencies.append( "wmctrl" )

    return ' '.join( sorted( dependencies ) )


#TODO Check these...
def _get_operating_system_dependencies_opensuse( operating_system, indicator_name ):
    dependencies = [
        "cairo-devel",
        "gcc",
        "gobject-introspection-devel",
        "pkg-config",
        "python3-devel",
        "typelib-1_0-AyatanaAppIndicator3-0_1" ]

    if indicator_name == Indicator_Name.INDICATORFORTUNE:
        dependencies.append( "fortune" )

    if indicator_name == Indicator_Name.INDICATORTEST:
        dependencies.append( "fortune" )

    return ' '.join( sorted( dependencies ) )


def _get_extension( operating_system ):
    extension = ''
    if operating_system == Operating_System.DEBIAN_11_12 or \
       operating_system == Operating_System.FEDORA_40 or \
       operating_system == Operating_System.OPENSUSE_TUMBLEWEED:
        extension = (
            f"Install the `GNOME Shell` `AppIndicator and KStatusNotifierItem Support` "
            f"[extension](https://extensions.gnome.org/extension/615/appindicator-support).\n\n" )

    return extension


def _get_installation_python_virtual_environment( indicator_name ):
    return (
        f"Install the indicator into a `Python` virtual environment:\n"
        f"    ```\n"
        f"    if [ ! -d $HOME/.local/venv_{ indicator_name } ]; then python3 -m venv $HOME/.local/venv_{ indicator_name }; fi && \\\n"
        f"    . $HOME/.local/venv_{ indicator_name }/bin/activate && \\\n"
        f"    python3 -m pip install --upgrade --force-reinstall pip { indicator_name } && \\\n"
        f"    deactivate && \\\n"
        f"    . $(ls -d $HOME/.local/venv_{ indicator_name }/lib/python3.* | head -1)/site-packages/{ indicator_name }/platform/linux/post_install.sh\n"
        f"    ```\n" )


def _get_installation_additional_python_modules( indicator_name ):
    message = ''

    common = (
            f"For example if your `Python` script requires the `requests` module:\n"
            f"    ```\n"
            f"    . $HOME/.local/venv_{ indicator_name }/bin/activate && \\\n"
            f"    python3 -m pip install --upgrade requests && \\\n"
            f"    deactivate\n" )

    if indicator_name.upper() == Indicator_Name.INDICATORSCRIPTRUNNER.name:
        message = (
            f"If you have added any `Python` scripts to `{ indicator_name }`,\n"
            f"you may need to install `Python` modules to the virtual environment.\n"
            f"{ common }"
            f"    ```\n" )

    elif indicator_name.upper() == Indicator_Name.INDICATORTIDE.name:
        message = (
            f"You will need to write a `Python` script to retrieve your tidal data.\n"
            f"As such, you may need to install additional `Python` modules to the virtual environment.\n"
            f"{ common }"
            f"    ```\n" )

    return message


def _get_installation_for_operating_system(
        operating_system,
        indicator_name,
        summary,
        install_command,
        _get_operating_system_dependencies_function_name ):

    # openSUSE Tumbleweed does not contain the package 'calendar' or equivalent.
    # When creating the README.md for indicatoronthisday, drop references to openSUSE.
    opensuse_or_manjaro = \
        operating_system == Operating_System.MANJARO_221 or \
        operating_system == Operating_System.OPENSUSE_TUMBLEWEED

    if opensuse_or_manjaro and is_indicator( indicator_name, Indicator_Name.INDICATORONTHISDAY ):
        dependencies = ''

    else:
        operating_system_packages = \
            _get_operating_system_dependencies_function_name(
                operating_system,
                Indicator_Name[ indicator_name.upper() ] )

        # Reference on installing some of the operating system packages:
        #   https://stackoverflow.com/a/61164149/2156453
        dependencies = (
            f"<details>"
            f"<summary><b>{ summary }</b></summary>\n\n"

            f"1. Install operating system packages:\n\n"
            f"    ```\n"
            f"    { install_command } { operating_system_packages }\n"
            f"    ```\n\n" )

        n = 1
        extension = _get_extension( operating_system )
        if extension:
            n += 1
            dependencies += f"{ str( n ) }. { extension }"

        n += 1
        dependencies += f"{ str( n ) }. { _get_installation_python_virtual_environment( indicator_name ) }"

        n += 1
        if is_indicator( indicator_name, Indicator_Name.INDICATORSCRIPTRUNNER, Indicator_Name.INDICATORTIDE ):
            dependencies += f"{ str( n ) }. { _get_installation_additional_python_modules( indicator_name) }"

        dependencies += f"</details>\n\n"

    return dependencies


def _get_installation( indicator_name ):
    install_command_debian = "sudo apt-get -y install"

    return (
        "Installation / Upgrading\n" +
        "------------------------\n\n" +

        _get_installation_for_operating_system(
            Operating_System.DEBIAN_11_12,
            indicator_name,
            "Debian 11 / 12",
            install_command_debian,
            _get_operating_system_dependencies_debian ) +

        _get_installation_for_operating_system(
            Operating_System.FEDORA_38_39,
            indicator_name,
            "Fedora 38 / 39",
            "sudo dnf -y install",
            _get_operating_system_dependencies_fedora ) +

        _get_installation_for_operating_system(
            Operating_System.FEDORA_40,
            indicator_name,
            "Fedora 40",
            "sudo dnf -y install",
            _get_operating_system_dependencies_fedora ) +

        _get_installation_for_operating_system(
            Operating_System.MANJARO_221,
            indicator_name,
            "Manjaro 22.1",
            "sudo pacman -S --noconfirm",
            _get_operating_system_dependencies_manjaro ) +

        _get_installation_for_operating_system(
            Operating_System.OPENSUSE_TUMBLEWEED,
            indicator_name,
            "openSUSE Tumbleweed",
            "sudo zypper install -y",
            _get_operating_system_dependencies_opensuse ) +

        _get_installation_for_operating_system(
            Operating_System.UBUNTU_2004,
            indicator_name,
            "Ubuntu 20.04",
            install_command_debian,
            _get_operating_system_dependencies_debian ) +

        _get_installation_for_operating_system(
            Operating_System.UBUNTU_2204_2404,
            indicator_name,
            "Ubuntu 22.04 / 24.04",
            install_command_debian,
            _get_operating_system_dependencies_debian ) )


def _get_usage( indicator_name, indicator_name_human_readable ):
    # The human readable name is VirtualBox™ and so need to remove '™' below.
    return (
        f"Usage\n"
        f"-----\n\n"

        f"To run `{ indicator_name }`, press the `Super`/`Windows` key to open the `Show Applications` overlay (or similar), "
        f"type `{ indicator_name_human_readable.split( ' ', 1 )[ 1 ].lower().replace( '™', '' ) }` "
        f"into the search bar and the icon should be present for you to select.  "
        f"If the icon does not appear, or appears as generic, you may have to log out and log back in (or restart).\n\n"
        f"Alternatively, to run from the terminal:\n\n"
        f"```\n"
        f"    . $HOME/.local/venv_{ indicator_name }/bin/activate && \\\n"
        f"    python3 $(ls -d $HOME/.local/venv_{ indicator_name }/lib/python3.* | head -1)/site-packages/{ indicator_name }/{ indicator_name }.py && \\\n"
        f"    deactivate\n"
        f"```\n\n" )


#TODO Check these...
def _get_distributions_supported( indicator_name ):
    message_distributions_supported = (
        f"Distributions Supported\n"
        f"-----------------------\n\n"

        f"Distributions/versions:\n"
        f"- `Debian 11+`\n"
        f"- `Fedora 38+`\n"
        f"- `Kubuntu 20.04+`\n"
        f"- `Linux Mint 21`\n"
        f"- `Lubuntu 20.04+`\n"
        f"- `Manjaro 22.1`\n"
        f"- `openSUSE Tumbleweed`.\n"
        f"- `Ubuntu 20.04+`\n"
        f"- `Ubuntu Budgie 22.04+`\n"
        f"- `Ubuntu MATE 20.04+`\n"
        f"- `Ubuntu Unity 20.04+`\n"
        f"- `Xubuntu 20.04+`\n"
        f"\n\n" )

    message_limitations = ""

    if is_indicator(
        indicator_name,
        Indicator_Name.INDICATORFORTUNE,
        Indicator_Name.INDICATORONTHISDAY,
        Indicator_Name.INDICATORPUNYCODE,
        Indicator_Name.INDICATORTEST ):
        message_limitations += (
            f"- `Wayland`: the clipboard does not function.\n" )

    if is_indicator(
        indicator_name,
        Indicator_Name.INDICATORVIRTUALBOX ):
        message_limitations += (
            f"- `Wayland`: the command `wmctrl` does not function "
            f"(used to list windows, uniquely identify and bring to the front).\n" )

    if is_indicator(
        indicator_name,
        Indicator_Name.INDICATORFORTUNE,
        Indicator_Name.INDICATORPPADOWNLOADSTATISTICS,
        Indicator_Name.INDICATORPUNYCODE,
        Indicator_Name.INDICATORSCRIPTRUNNER,
        Indicator_Name.INDICATORTEST,
        Indicator_Name.INDICATORVIRTUALBOX ):
        message_limitations += (
            f"- `Wayland`: middle mouse click does not work.\n" )

    if is_indicator(
        indicator_name,
        Indicator_Name.INDICATORSTARDATE,
        Indicator_Name.INDICATORTEST,
        Indicator_Name.INDICATORVIRTUALBOX ):
        message_limitations += (
            f"- `Plasma (X11) / XFCE`: mouse wheel scroll over icon does not function.\n" )

    if is_indicator(
        indicator_name,
        Indicator_Name.INDICATORLUNAR,
        Indicator_Name.INDICATORSCRIPTRUNNER,
        Indicator_Name.INDICATORSTARDATE,
        Indicator_Name.INDICATORTEST ):
        message_limitations += (
            f"- `Plasma (X11) / XFCE/ Lubuntu / LXQt`: icon label is unsupported.\n" )

    if is_indicator(
        indicator_name,
        Indicator_Name.INDICATORLUNAR,
        Indicator_Name.INDICATORTEST ):
        message_limitations += (
            f"- `Lubuntu / LXQt`: once set, the icon cannot be changed.\n" )

    if is_indicator(
        indicator_name,
        Indicator_Name.INDICATORSCRIPTRUNNER,
        Indicator_Name.INDICATORTEST ):
        message_limitations += (
            f"- `Lubuntu / LXQt 20.04`: arguments are not [preserved]"
            f"(https://github.com/lxqt/qterminal/issues/335) in `qterminal`. "
            f"Alternatively, install `gnome-terminal`.\n" )

    if message_limitations:
        message_limitations = f"Limitations:\n" + message_limitations + f"\n\n"

    return message_distributions_supported + message_limitations


def _get_uninstall_for_operating_system(
        operating_system,
        indicator_name,
        summary,
        uninstall_command,
        _get_operating_system_dependencies_function_name ):

    # openSUSE Tumbleweed does not contain the package 'calendar' or equivalent.
    # When creating the README.md for indicatoronthisday, drop references to openSUSE.
    opensuse_or_manjaro = \
        operating_system == Operating_System.MANJARO_221 or \
        operating_system == Operating_System.OPENSUSE_TUMBLEWEED

    if opensuse_or_manjaro and is_indicator( indicator_name, Indicator_Name.INDICATORONTHISDAY ):
        uninstall = ''

    else:
        uninstall = (
            f"<details>"
            f"<summary><b>{ summary }</b></summary>\n\n"

            f"1. Uninstall operating system packages:\n\n"
            f"    ```\n"
            f"    { uninstall_command } "
            f"{ _get_operating_system_dependencies_function_name( operating_system, Indicator_Name[ indicator_name.upper() ] ) }\n"
            f"    ```\n\n"

            f"2. Uninstall `Python` virtual environment and files:\n"
            f"    ```\n"
            f"    $(ls -d $HOME/.local/venv_{indicator_name}/lib/python3.* | head -1)/site-packages/{indicator_name}/platform/linux/uninstall.sh && \\\n"
            f"    rm -f -r $HOME/.local/venv_{indicator_name}\n"
            f"    ```\n\n"

            f"</details>\n\n" )

    return uninstall


def _get_uninstall( indicator_name ):
    uninstall_command_debian = "sudo apt-get -y remove"

    return (
        "Uninstall\n" +
        "---------\n\n" +

        _get_uninstall_for_operating_system(
            Operating_System.DEBIAN_11_12,
            indicator_name,
            "Debian 11 / 12",
            uninstall_command_debian,
            _get_operating_system_dependencies_debian ) +

        _get_uninstall_for_operating_system(
            Operating_System.FEDORA_38_39,
            indicator_name,
            "Fedora 38 / 39",
            "sudo dnf -y remove",
            _get_operating_system_dependencies_fedora ) +

        _get_uninstall_for_operating_system(
            Operating_System.FEDORA_40,
            indicator_name,
            "Fedora 40",
            "sudo dnf -y remove",
            _get_operating_system_dependencies_fedora ) +

        _get_uninstall_for_operating_system(
            Operating_System.MANJARO_221,
            indicator_name,
            "Manjaro 22.1",
            "sudo pacman -R --noconfirm",
            _get_operating_system_dependencies_manjaro ) +

        _get_uninstall_for_operating_system(
            Operating_System.OPENSUSE_TUMBLEWEED,
            indicator_name,
            "openSUSE Tumbleweed",
            "sudo zypper remove -y",
            _get_operating_system_dependencies_opensuse ) +

        _get_uninstall_for_operating_system(
            Operating_System.UBUNTU_2004,
            indicator_name,
            "Ubuntu 20.04",
            uninstall_command_debian,
            _get_operating_system_dependencies_debian ) +

        _get_uninstall_for_operating_system(
            Operating_System.UBUNTU_2204_2404,
            indicator_name,
            "Ubuntu 22.04 / 24.04",
            uninstall_command_debian,
            _get_operating_system_dependencies_debian ) )


def _get_license( authors_emails, start_year ):
    end_year = datetime.datetime.now( datetime.timezone.utc ).strftime( '%Y' )

    authors = [ author_email[ 0 ] for author_email in authors_emails ]
    authors = ', '.join( authors )

    return (
        f"License\n"
        f"-------\n\n"

        f"This project in its entirety is licensed under the terms of the GNU General Public License v3.0 license.\n\n"
        f"Copyright { start_year }-{ end_year } { authors }.\n" )


def create_readme(
    directory,
    indicator_name,
    indicator_name_human_readable,
    authors_emails,
    start_year ):

    Path( directory ).mkdir( parents = True, exist_ok = True )

    with open( Path( directory, "README.md" ), 'w' ) as f:
        f.write( _get_introduction( indicator_name ) )
        f.write( _get_installation( indicator_name ) )
        f.write( _get_usage( indicator_name, indicator_name_human_readable ) )
        f.write( _get_distributions_supported( indicator_name ) )
        f.write( _get_uninstall( indicator_name ) )
        f.write( _get_license( authors_emails, start_year ) )
