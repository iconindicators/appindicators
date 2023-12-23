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
# specific to the indicator, drawn from the indicator's CHANGELOG.md and pyproejct.toml.
#
#   https://github.github.com/gfm
#
# When testing/editing, to render out in HTML:
#   python3 -m pip install --upgrade readme_renderer readme_renderer[md]
#   python3 tools/build_readme.py release indicatortest
#   python3 -m readme_renderer release/README.md -o release/README.html


import argparse
import datetime
import re
import sys

from pathlib import Path

sys.path.append( "indicatorbase/src" )
try:
    from indicatorbase import indicatorbase
except ModuleNotFoundError:
    pass # Occurs as the script is run from the incorrect directory and will be caught in main.


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


indicator_dependencies_debian = {
    "indicatorfortune"               : "fortune-mod fortunes python3-notify2", 
    "indicatorlunar"                 : "python3-notify2",
    "indicatoronthisday"             : "calendar python3-notify2",
    "indicatorppadownloadstatistics" : "",
    "indicatorpunycode"              : "python3-notify2",
    "indicatorscriptrunner"          : "libnotify-bin python3-notify2 pulseaudio-utils",
    "indicatorstardate"              : "",
    "indicatortest"                  : "calendar fortune-mod libnotify-bin pulseaudio-utils python3-notify2 wmctrl",
    "indicatortide"                  : "python3-notify2",
    "indicatorvirtualbox"            : "python3-notify2 wmctrl" }


indicator_dependencies_fedora = {
    "indicatorfortune"               : "fortune-mod python3-notify2", 
    "indicatorlunar"                 : "python3-notify2",
    "indicatoronthisday"             : "calendar python3-notify2",
    "indicatorppadownloadstatistics" : "",
    "indicatorpunycode"              : "python3-notify2",
    "indicatorscriptrunner"          : "libnotify-bin python3-notify2 pulseaudio-utils",
    "indicatorstardate"              : "",
    "indicatortest"                  : "calendar fortune-mod libnotify-bin pulseaudio-utils python3-notify2 wmctrl",
    "indicatortide"                  : "python3-notify2",
    "indicatorvirtualbox"            : "python3-notify2 wmctrl" }


def _get_introduction( indicator_name ):
    comments = ""
    pattern_tag = re.compile( f".*comments = _\(.*" )
    for line in open( indicator_name + '/src/' + indicator_name + '/' + indicator_name + ".py" ).readlines():
        matches = pattern_tag.search( line )
        if matches:
            comments = matches.group().split( "\"" )[ 1 ] + '\n\n'
            break

    return comments


def _get_supported_platforms( indicator_name ):
    return (
        f"Supported Platforms\n"
        f"-------------------\n"

        f"`{ indicator_name }` will run on Debian / Ubuntu and Fedora and theoretically, "
        f"any platform which supports the `appindicator` library.\n\n" )


def _get_installation_python_virtual_environment( indicator_name ):
    return (
        f"3. Create a `Python` virtual environment, activate and install the indicator package. Open a `terminal` and...\n"
        f"    ```\n"
        f"    python3 -m venv $HOME/.local/venv_{ indicator_name } && \\\n"
        f"    . $HOME/.local/venv_{ indicator_name }/bin/activate && \\\n"
        f"    python3 -m pip install --upgrade pip { indicator_name } && \\\n"
        f"    deactivate\n"
        f"    ```\n" )


def _get_installation_copy_files( indicator_name ):
    venv_indicator_home = f"$(ls -d $HOME/.local/venv_{ indicator_name }/lib/python3.* | head -1)/site-packages/{ indicator_name }"
    return (
        f"4. Copy icon, run script and desktop file to `$HOME/.local`. Open a `terminal` and...\n"
        f"    ```\n"
        f"    mkdir -p $HOME/.local/share/icons/hicolor/scalable/apps && \\\n"

        f"    cp "
        f"{ venv_indicator_home }/icons/hicolor/{ indicator_name }.svg "
        f"$HOME/.local/share/icons/hicolor/scalable/apps && \\\n"

        f"    mkdir -p $HOME/.local/bin && \\\n"

        f"    cp "
        f"{ venv_indicator_home }/packaging/linux/{ indicator_name }.sh "
        f"$HOME/.local/bin && \\\n"

        f"    cp "
        f"{ venv_indicator_home }/packaging/linux/{ indicator_name }.py.desktop "
        f"$HOME/.local/share/applications\n"

        f"    ```\n\n" )


def _get_installation_debian( indicator_name ):
    return (
        f"<details>"
        f"<summary><b>Debian / Ubuntu</b></summary>\n\n"

        f"1. Install operating system packages. Open a `terminal` and...\n\n"
        f"    ```\n"
        f"    sudo apt-get -y install "
        f"gir1.2-ayatanaappindicator3-0.1 "
        f"libcairo2-dev "
        f"libgirepository1.0-dev "
        f"pkg-config "
        f"python3-dev "
        f"python3-gi "
        f"python3-venv "
        f"{ indicator_dependencies_debian[ indicator_name ] }\n"
        f"    ```\n\n"

        f"2. Install extension:\n\n"

        f"    **Debian:** "
        f"Install the `GNOME Shell` `AppIndicator and KStatusNotifierItem Support` "
        f"[extension](https://extensions.gnome.org/extension/615/appindicator-support).\n\n"

        f"    **Ubuntu:** "
        f"Run `GNOME Tweaks` and enable the `Ubuntu appIndicators` extension.\n\n"

        f"{ _get_installation_python_virtual_environment( indicator_name ) }"

        f"{ _get_installation_copy_files( indicator_name ) }"

        f"</details>\n\n" )


def _get_installation_fedora( indicator_name ):
    return (
        f"<details>"
        f"<summary><b>Fedora</b></summary>\n\n"

        f"1. Install operating system packages. Open a `terminal` and...\n\n"
        f"    ```\n"
        f"    sudo dnf -y install "
        f"libappindicator-gtk3 "
        f"cairo-devel "
        f"pkg-config "
        f"python3-devel "
        f"python3-gobject "
        f"gobject-introspection-devel "
        f"cairo-gobject-devel "
        f"gnome-extensions-app "
        f"gnome-shell-extension-appindicator "
        f"{ indicator_dependencies_fedora[ indicator_name ] }\n"
        f"    ```\n\n"

        f"2. Enable extension:\n\n"
        f"    Run `Extensions` and ensure the extension `AppIndicator and KStatusNotifierItem Support` is enabled.\n\n"

        f"{ _get_installation_python_virtual_environment( indicator_name ) }"

        f"{ _get_installation_copy_files( indicator_name ) }"

        f"</details>\n\n" )


def _get_installation( indicator_name ):

    # Reference on installing some of the operating system packages:    
    #   https://stackoverflow.com/a/61164149/2156453
    return (
        f"Installation\n"
        f"------------\n"

        f"{ _get_installation_debian( indicator_name ) }"

        f"{ _get_installation_fedora( indicator_name ) }" )


def _get_usage( indicator_name ):
    return (
        f"Usage\n"
        f"-----\n"

        f"To run `{ indicator_name }`, press the `Super`/`Windows` key to open the `Show Applications` overlay, "
        f"type `{ indicator_names[ indicator_name ].split( ' ', 1 )[ 1 ].lower() }` "
        f"into the search bar and the icon should be present for you to click.  "
        f"If the icon does not appear, or appears as generic, you may have to log out and log back in (or restart).\n\n"
        f"Under the `Preferences` there is an `autostart` option to run `{ indicator_name }` on start up.\n\n" )


def _get_limitations():
    return (
        f"Limitations\n"
        f"-----------\n"

        f"Distributions/versions with full functionality:\n"
        f"- `Debian 11 / 12`\n"
        f"- `Fedora 38 / 39` on `X.Org`.\n"
        f"- `Ubuntu 20.04 / 22.04`\n"
        f"- `Ubuntu Budgie 22.04`\n"
        f"- `Ubuntu Unity 20.04 / 22.04`\n\n"

        f"Distributions/versions with limited functionality:\n"
        f"- `Fedora 38 / 39` No clipboard on `Wayland`.\n"
        f"- `Kubuntu 20.04 / 22.04` No mouse wheel scroll; tooltip in lieu of label.\n"
        f"- `Linux Mint 21 Cinnamon` Tooltip in lieu of label.\n"
        f"- `Lubuntu 20.04 / 22.04` No label; tooltip is not dynamic; icon is not dynamic.\n"
        f"- `Ubuntu Budgie 20.04` No mouse middle click.\n"
        f"- `Ubuntu MATE 20.04` Dynamic icon is truncated, but fine whilst being clicked.\n"
        f"- `Ubuntu MATE 22.04` Default icon with colour change does not show up; dynamic icon for NEW MOON does not display.\n"
        f"- `Xubuntu 20.04 / 22.04` No mouse wheel scroll; tooltip in lieu of label.\n\n" )


def _get_removal( indicator_name ):
    return (
        f"Removal\n"
        f"-------\n"

        f"Open a `terminal` and...\n"

        f"1. Remove operating system packages:\n\n"

        f"    **Debian / Ubuntu:**\n"
        f"    ```\n"
        f"    sudo apt-get -y remove "
        f"gir1.2-ayatanaappindicator3-0.1 "
        f"libcairo2-dev "
        f"libgirepository1.0-dev "
        f"pkg-config "
        f"python3-dev "
        f"python3-venv \n"
        f"    ```\n\n"

        f"    **Fedora:**\n"
        f"    ```\n"
        f"    sudo dnf -y remove "
        f"libappindicator-gtk3 "
        f"cairo-devel "
        f"pkg-config "
        f"python3-devel "
        f"python3-gobject "
        f"gobject-introspection-devel "
        f"cairo-gobject-devel \n"
        f"    ```\n"

        f"2. Remove `Python` virtual environment and files from `$HOME/.local`:\n"
        f"    ```\n"
        f"    rm -r $HOME/.local/venv_{ indicator_name } && \\\n"
        f"    rm $HOME/.local/share/icons/hicolor/scalable/apps/{ indicator_name }.svg && \\\n"
        f"    rm $HOME/.local/bin/{ indicator_name }.sh && \\\n"
        f"    rm $HOME/.local/share/applications/{ indicator_name }.py.desktop\n"
        f"    ```\n\n" )


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
        f.write( _get_supported_platforms( indicator_name ) )
        f.write( _get_installation( indicator_name ) )
        f.write( _get_usage( indicator_name ) )
        f.write( _get_limitations() )
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
