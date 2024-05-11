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


# Create a README.md for an indicator from text common to all indicators and text
# specific to the indicator, drawn from the indicator's CHANGELOG.md and pyproject.toml.
#
#   https://github.github.com/gfm
#
# When testing/editing, to render out in HTML:
#   python3 -m pip install --upgrade readme_renderer readme_renderer[md]
#   python3 tools/build_readme.py release indicatortest
#   python3 -m readme_renderer release/README.md -o release/README.html
#
# References
#   https://pycairo.readthedocs.io
#   https://pygobject.readthedocs.io


import argparse
import datetime
import re
import sys

from enum import auto, Enum
from pathlib import Path

sys.path.append( "indicatorbase/src" )
try:
    from indicatorbase import indicatorbase
except ModuleNotFoundError:
    pass # Occurs as the script is run from the incorrect directory and will be caught in main.


class Operating_System( Enum ):
    DEBIAN_11_DEBIAN_12 = auto()
    FEDORA_38_FEDORA_39 = auto()
    MANJARO_221 = auto()
    OPENSUSE_TUMBLEWEED = auto()
    UBUNTU_2004 = auto()
    UBUNTU_2204 = auto()


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


indicator_names = {
    "indicatorfortune"               : "Indicator Fortune",
    "indicatorlunar"                 : "Indicator Lunar",
    "indicatoronthisday"             : "Indicator On This Day",
    "indicatorppadownloadstatistics" : "Indicator PPA Download Statistics",
    "indicatorpunycode"              : "Indicator Punycode",
    "indicatorscriptrunner"          : "Indicator Script Runner",
    "indicatorstardate"              : "Indicator Stardate",
    "indicatortest"                  : "Indicator Test",
    "indicatortide"                  : "Indicator Tide",
    "indicatorvirtualbox"            : "Indicator VirtualBox™" }


def _get_introduction( indicator_name ):
    pattern_tag = re.compile( f".*comments = _\(.*" )
    for line in open( indicator_name + '/src/' + indicator_name + '/' + indicator_name + ".py" ).readlines():
        matches = pattern_tag.search( line )
        if matches:
            comments = matches.group().split( "\"" )[ 1 ].split( ' ' )
            comments[ 0 ] = comments[ 0 ].lower()
            break

    # openSUSE Tumbleweed and Manjaro do not contain the package 'calendar' or equivalent.
    # When creating the README.md for indicatoronthisday, drop references to openSUSE/Manjaro.
    introduction = (
        f"`{ indicator_name }` { ' '.join( comments )[ 0 : -1 ] } on "
        f"`Debian`, `Ubuntu`, `Fedora`" )

    if indicator_name.upper() != Indicator_Name.INDICATORONTHISDAY.name:
        introduction += f", `openSUSE`, `Manjaro` "

    introduction += f" and theoretically, any platform which supports the `appindicator` library.\n\n"

    introduction += f"Other indicators in this series are:\n"
    indicators = ( list( indicator_names.keys() ) )
    indicators.remove( indicator_name )
    introduction += "- `" + '`\n- `'.join( indicators ) + "`\n\n"

    return introduction


def _get_operating_system_dependencies_debian( operating_system, indicator_name ):
    dependencies = [
        "gir1.2-ayatanaappindicator3-0.1",
        "gir1.2-gtk-3.0",
        "libcairo2-dev",
        "libgirepository1.0-dev",
        "pkg-config",
        "python3-dev",
        "python3-gi",
        "python3-gi-cairo",
        "python3-pip",
        "python3-venv" ]

    if operating_system == Operating_System.UBUNTU_2004 or \
       operating_system == Operating_System.UBUNTU_2204:
        dependencies.append( "gnome-shell-extension-appindicator" )

    if indicator_name == Indicator_Name.INDICATORFORTUNE:
        dependencies.append( "fortune-mod" )
        dependencies.append( "fortunes" )
        dependencies.append( "python3-notify2" )

    if indicator_name == Indicator_Name.INDICATORLUNAR:
        dependencies.append( "python3-notify2" )

    if indicator_name == Indicator_Name.INDICATORONTHISDAY:
        dependencies.append( "python3-notify2" )

        if operating_system == Operating_System.DEBIAN_11_DEBIAN_12 or \
           operating_system == Operating_System.UBUNTU_2204:
            dependencies.append( "calendar" )

    if indicator_name == Indicator_Name.INDICATORPUNYCODE:
        dependencies.append( "python3-notify2" )

    if indicator_name == Indicator_Name.INDICATORSCRIPTRUNNER:
        dependencies.append( "libnotify-bin" )
        dependencies.append( "python3-notify2" )

    if indicator_name == Indicator_Name.INDICATORTEST:
        dependencies.append( "fortune-mod" )
        dependencies.append( "fortunes" )
        dependencies.append( "python3-notify2" )
        dependencies.append( "wmctrl" )

        if operating_system == Operating_System.DEBIAN_11_DEBIAN_12 or \
           operating_system == Operating_System.UBUNTU_2204:
            dependencies.append( "calendar" )

    if indicator_name == Indicator_Name.INDICATORTIDE:
        dependencies.append( "python3-notify2" )

    if indicator_name == Indicator_Name.INDICATORVIRTUALBOX:
        dependencies.append( "python3-notify2" )
        dependencies.append( "wmctrl" )

    return ' '.join( sorted( dependencies ) )


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
    if operating_system == Operating_System.DEBIAN_11_DEBIAN_12 or \
       operating_system == Operating_System.OPENSUSE_TUMBLEWEED:
        extension = (
            f"Install the `GNOME Shell` `AppIndicator and KStatusNotifierItem Support` "
            f"[extension](https://extensions.gnome.org/extension/615/appindicator-support).\n\n" )

    return extension


def _get_installation_python_virtual_environment( indicator_name ):
    return (
        f"Create a `Python` virtual environment, activate and install the indicator package:\n"
        f"    ```\n"
        f"    if [ ! -d $HOME/.local/venv_{ indicator_name } ]; then python3 -m venv $HOME/.local/venv_{ indicator_name }; fi && \\\n"
        f"    . $HOME/.local/venv_{ indicator_name }/bin/activate && \\\n"
        f"    python3 -m pip install --upgrade pip { indicator_name } && \\\n"
        f"    deactivate\n"
        f"    ```\n" )


def _get_installation_copy_files( indicator_name ):
    venv_indicator_home = \
        f"$(ls -d $HOME/.local/venv_{ indicator_name }/lib/python3.* | head -1)/site-packages/{ indicator_name }"

    return (
        f"Copy icon, run script and desktop file to `$HOME/.local`:\n"
        f"    ```\n"

        f"    mkdir -p $HOME/.local/bin && \\\n"

        f"    cp "
        f"{ venv_indicator_home }/platform/linux/{ indicator_name }.sh "
        f"$HOME/.local/bin && \\\n"

        f"    mkdir -p $HOME/.local/share/applications && \\\n"

        f"    cp "
        f"{ venv_indicator_home }/platform/linux/{ indicator_name }.py.desktop "
        f"$HOME/.local/share/applications\n"

        f"    mkdir -p $HOME/.local/share/icons/hicolor/scalable/apps && \\\n"

        f"    cp "
        f"{ venv_indicator_home }/icons/*.svg "
        f"$HOME/.local/share/icons/hicolor/scalable/apps && \\\n"

        f"    ```\n\n" )


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

    if opensuse_or_manjaro and indicator_name.upper() == Indicator_Name.INDICATORONTHISDAY.name:
        dependencies = ''

    else:
        operating_system_packages = _get_operating_system_dependencies_function_name(
                                        operating_system, Indicator_Name[ indicator_name.upper() ] )

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
        dependencies += f"{ str( n ) }. { _get_installation_copy_files( indicator_name ) }"

        n += 1
        if indicator_name.upper() == Indicator_Name.INDICATORSCRIPTRUNNER.name or \
           indicator_name.upper() == Indicator_Name.INDICATORTIDE.name:
            dependencies += f"{ str( n ) }. { _get_installation_additional_python_modules( indicator_name) }"

        dependencies += f"</details>\n\n"

    return dependencies


def _get_installation( indicator_name ):
    install_command_debian = "sudo apt-get -y install"

    return (
        "Installation / Upgrading\n" +
        "------------------------\n" +

        _get_installation_for_operating_system(
            Operating_System.DEBIAN_11_DEBIAN_12,
            indicator_name,
            "Debian 11 / 12",
            install_command_debian,
            _get_operating_system_dependencies_debian ) +

        _get_installation_for_operating_system(
            Operating_System.FEDORA_38_FEDORA_39,
            indicator_name,
            "Fedora 38 / 39",
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
            Operating_System.UBUNTU_2204,
            indicator_name,
            "Ubuntu 22.04",
            install_command_debian,
            _get_operating_system_dependencies_debian ) )


def _get_usage( indicator_name ):
    return (
        f"Usage\n"
        f"-----\n"

        f"To run `{ indicator_name }`, press the `Super`/`Windows` key to open the `Show Applications` overlay (or similar), "
        f"type `{ indicator_names[ indicator_name ].split( ' ', 1 )[ 1 ].lower() }` "
        f"into the search bar and the icon should be present for you to click.  "
        f"If the icon does not appear, or appears as generic, you may have to log out and log back in (or restart).\n\n"
        f"Alternatively, to run from the terminal:\n\n"
        f"```\n"
        f"    . $HOME/.local/venv_{ indicator_name }/bin/activate && \\\n"
        f"    python3 $(ls -d $HOME/.local/venv_{ indicator_name }/lib/python3.* | head -1)/site-packages/{ indicator_name }/{ indicator_name }.py && \\\n"
        f"    deactivate\n"
        f"```\n\n" )



def _get_distributions_tested():
    return (
        f"Distributions Tested\n"
        f"--------------------\n"

        f"Distributions/versions with full functionality:\n"
        f"- `Debian 11 / 12 GNOME on Xorg`\n"
        f"- `Fedora 38 / 39 GNOME on Xorg`\n"
        f"- `Kubuntu 20.04 / 22.04`\n"
        f"- `Ubuntu 20.04`\n"
        f"- `Ubuntu 22.04 on Xorg`\n"
        f"- `Ubuntu Budgie 22.04`\n"
        f"- `Ubuntu Unity 20.04 / 22.04`\n"
        f"- `Xubuntu 20.04 / 22.04`\n\n"

        f"Distributions/versions with limited functionality:\n"
        f"- `Debian 11 / 12 GNOME` No clipboard; no `wmctrl`.\n"
        f"- `Fedora 38 / 39 GNOME` No clipboard; no `wmctrl`.\n"
        f"- `Kubuntu 20.04 / 22.04` No mouse wheel scroll; tooltip in lieu of label.\n"
        f"- `Linux Mint 21 Cinnamon` Tooltip in lieu of label.\n"
        f"- `Lubuntu 20.04 / 22.04` No label; tooltip is not dynamic; icon is not dynamic.\n"
        f"- `Manjaro 22.1 GNOME` No `calendar`.\n"
        f"- `openSUSE Tumbleweed` No clipboard; no `wmctrl`; no `calendar`.\n"
        f"- `openSUSE Tumbleweed GNOME on Xorg` No `calendar`.\n"
        f"- `Ubuntu 22.04` No clipboard; no `wmctrl`.\n"
        f"- `Ubuntu Budgie 20.04` No mouse middle click.\n"
        f"- `Ubuntu MATE 20.04` Dynamic icon is truncated, but fine whilst being clicked.\n"
        f"- `Ubuntu MATE 22.04` Dynamic icon for NEW MOON is truncated.\n"
        f"- `Xubuntu 20.04 / 22.04` No mouse wheel scroll; tooltip in lieu of label.\n\n" )


def _get_removal_for_operating_system(
        operating_system,
        indicator_name,
        summary,
        remove_command,
        _get_operating_system_dependencies_function_name ):

    # openSUSE Tumbleweed does not contain the package 'calendar' or equivalent.
    # When creating the README.md for indicatoronthisday, drop references to openSUSE.
    opensuse_or_manjaro = \
        operating_system == Operating_System.MANJARO_221 or \
        operating_system == Operating_System.OPENSUSE_TUMBLEWEED

    if opensuse_or_manjaro and indicator_name.upper() == Indicator_Name.INDICATORONTHISDAY.name:
        removal = ''

    else:
        removal = (
            f"<details>"
            f"<summary><b>{ summary }</b></summary>\n\n"

            f"1. Remove operating system packages:\n\n"
            f"    ```\n"
            f"    { remove_command } "
            f"{ _get_operating_system_dependencies_function_name( operating_system, Indicator_Name[ indicator_name.upper() ] ) }\n"
            f"    ```\n\n"

            f"2. Remove `Python` virtual environment and support files:\n"
            f"    ```\n"
            f"    rm -f $HOME/.local/bin/{ indicator_name }.sh && \\\n"
            f"    rm -f $HOME/.local/share/applications/{ indicator_name }.py.desktop && \\\n"
            f"    rm -f $HOME/.local/share/icons/hicolor/scalable/apps/{ indicator_name }*.svg && \\\n"
            f"    rm -f -r $HOME/.local/venv_{ indicator_name } && \\\n"
            f"    rm -f -r $HOME/.cache/{ indicator_name } && \\\n"
            f"    rm -f -r $HOME/.config/{ indicator_name }\n"
            f"    ```\n\n"

            f"</details>\n\n" )

    return removal


def _get_removal( indicator_name ):
    remove_command_debian = "sudo apt-get -y remove"

    return (
        "Removal\n" +
        "-------\n" +

        _get_removal_for_operating_system(
            Operating_System.DEBIAN_11_DEBIAN_12,
            indicator_name,
            "Debian 11 / 12",
            remove_command_debian,
            _get_operating_system_dependencies_debian ) +

        _get_removal_for_operating_system(
            Operating_System.FEDORA_38_FEDORA_39,
            indicator_name,
            "Fedora 38 / 39",
            "sudo dnf -y remove",
            _get_operating_system_dependencies_fedora ) +

        _get_removal_for_operating_system(
            Operating_System.MANJARO_221,
            indicator_name,
            "Manjaro 22.1",
            "sudo pacman -R --noconfirm",
            _get_operating_system_dependencies_manjaro ) +

        _get_removal_for_operating_system(
            Operating_System.OPENSUSE_TUMBLEWEED,
            indicator_name,
            "openSUSE Tumbleweed",
            "sudo zypper remove -y",
            _get_operating_system_dependencies_opensuse ) +

        _get_removal_for_operating_system(
            Operating_System.UBUNTU_2004,
            indicator_name,
            "Ubuntu 20.04",
            remove_command_debian,
            _get_operating_system_dependencies_debian ) +

        _get_removal_for_operating_system(
            Operating_System.UBUNTU_2204,
            indicator_name,
            "Ubuntu 22.04",
            remove_command_debian,
            _get_operating_system_dependencies_debian ) )


def _get_license( indicator_name ):
    start_year = \
        indicatorbase.IndicatorBase.get_first_year_or_last_year_in_changelog_markdown(
            indicator_name + '/src/' + indicator_name + '/CHANGELOG.md' )

    end_year = datetime.datetime.now( datetime.timezone.utc ).strftime( '%Y' )

    return (
        f"License\n"
        f"-------\n"

        f"This project in its entirety is licensed under the terms of the GNU General Public License v3.0 license.\n\n"
        f"Copyright { start_year }-{ end_year } Bernard Giannetti.\n" )


def _create_readme( directory_out, indicator_name ):
    if not Path( directory_out ).exists():
        Path( directory_out ).mkdir( parents = True )

    with open( Path( directory_out, "README.md" ), 'w' ) as f:
        f.write( _get_introduction( indicator_name ) )
        f.write( _get_installation( indicator_name ) )
        f.write( _get_usage( indicator_name ) )
        f.write( _get_distributions_tested() )
        f.write( _get_removal( indicator_name ) )
        f.write( _get_license( indicator_name ) )


def _initialise_parser():
    parser = argparse.ArgumentParser(
        description = "Create README.md for an indicator." )

    parser.add_argument(
        "directory_out",
        help = "The output directory for the README.md." )

    parser.add_argument(
        "indicator_name",
        help = "The name of the indicator." )

    return parser


if __name__ == "__main__":
    parser = _initialise_parser()
    script_path_and_name = "tools/build_readme.py"
    if Path( script_path_and_name ).exists():
        args = parser.parse_args()
        _create_readme( args.directory_out, args.indicator_name )

    else:
        print(
            f"The script must be run from the top level directory (one above utils).\n"
            f"For example:\n"
            f"\tpython3 { script_path_and_name } release indicatorfortune" )
