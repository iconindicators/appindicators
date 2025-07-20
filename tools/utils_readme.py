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


#TODO Compare all code against original /home/bernard/utils_readme.py


'''
Create a README.md for an indicator.

References:
    https://pygobject.gnome.org/getting_started.html
    https://stackoverflow.com/q/70508775/2156453
    https://stackoverflow.com/q/60779139/2156453
'''


import datetime
import re
import sys

from enum import auto, Enum
from pathlib import Path

if "../" not in sys.path:
    sys.path.insert( 0, "../" )

from indicatorbase.src.indicatorbase import indicatorbase

from . import utils


class OperatingSystem( Enum ):
    ''' Supported operating systems. '''
    DEBIAN_11 = auto()
    DEBIAN_12 = auto()
    FEDORA_40 = auto()
    FEDORA_41 = auto()
    FEDORA_42 = auto()
    KUBUNTU_2204 = auto()
    KUBUNTU_2404 = auto()
    LINUX_MINT_CINNAMON_20 = auto()
    LINUX_MINT_CINNAMON_21 = auto()
    LINUX_MINT_CINNAMON_22 = auto()
    LUBUNTU_2204 = auto()
    LUBUNTU_2404 = auto()
    MANJARO_24 = auto()
    MANJARO_25 = auto()
    OPENSUSE_TUMBLEWEED = auto()
    UBUNTU_2004 = auto()
    UBUNTU_2204 = auto()
    UBUNTU_2404 = auto()
    UBUNTU_BUDGIE_2404 = auto()
    UBUNTU_MATE_2404 = auto()
    UBUNTU_UNITY_2204 = auto()
    UBUNTU_UNITY_2404 = auto()
    XUBUNTU_2404 = auto()


OPERATING_SYSTEMS_DEBIAN_BASED = {
    OperatingSystem.DEBIAN_11,
    OperatingSystem.DEBIAN_12,
    OperatingSystem.KUBUNTU_2204,
    OperatingSystem.KUBUNTU_2404,
    OperatingSystem.LINUX_MINT_CINNAMON_20,
    OperatingSystem.LINUX_MINT_CINNAMON_21,
    OperatingSystem.LINUX_MINT_CINNAMON_22,
    OperatingSystem.LUBUNTU_2204,
    OperatingSystem.LUBUNTU_2404,
    OperatingSystem.UBUNTU_2004,
    OperatingSystem.UBUNTU_2204,
    OperatingSystem.UBUNTU_2404,
    OperatingSystem.UBUNTU_BUDGIE_2404,
    OperatingSystem.UBUNTU_MATE_2404,
    OperatingSystem.UBUNTU_UNITY_2204,
    OperatingSystem.UBUNTU_UNITY_2404,
    OperatingSystem.XUBUNTU_2404 }


OPERATING_SYSTEMS_FEDORA_BASED = {
    OperatingSystem.FEDORA_40,
    OperatingSystem.FEDORA_41,
    OperatingSystem.FEDORA_42 }


OPERATING_SYSTEMS_MANJARO_BASED = {
    OperatingSystem.MANJARO_24,
    OperatingSystem.MANJARO_25 }


OPERATING_SYSTEMS_OPENSUSE_BASED = {
    OperatingSystem.OPENSUSE_TUMBLEWEED }


class IndicatorName( Enum ):
    ''' Indicators. '''
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


def _is_indicator(
    indicator,
    *indicators ):

    return { IndicatorName[ indicator.upper() ] }.issubset( { *indicators } )


def _is_operating_system(
    operating_system,
    *operating_systems ):

    return { operating_system }.issubset( { *operating_systems } )


def _get_indicator_names_sans_current(
    indicator ):

    indicator_as_enum = IndicatorName[ indicator.upper() ]

    indicators = [ ]
    for indicator_name in IndicatorName:
        if indicator_name == indicator_as_enum:
            continue

        indicators.append( indicator_name.name.lower() )

    return indicators


def _get_introduction(
    indicator ):

    pattern_tag = re.compile( r".*comments = _\(.*" )
    filename = indicator + '/src/' + indicator + '/' + indicator + ".py"
    lines = indicatorbase.IndicatorBase.read_text_file( filename )
    for line in lines:
        matches = pattern_tag.search( line )
        if matches:
            # Remove \n and drop ending.
            comments = matches.group().split( "\"" )[ 1 ].replace( '\\n', ' ' )[ 0 : -1 ]

            # Lower case leading character.
            comments = comments[ 0 ].lower() + comments[ 1 : ]

            break

    introduction = (
        f"`{ indicator }` { comments } on `Debian`, `Ubuntu`, `Fedora`" )

    # Manjaro and openSUSE Tumbleweed do not contain the 'calendar' package.
    #
    # For indicatoronthisday, drop references to Manjaro/openSUSE.
    #
    # For indicatortest, the calendar test is hidden and the remainder of the
    # indicator works, so leave in the reference to openSUSE/Manjaro.
    if not _is_indicator( indicator, IndicatorName.INDICATORONTHISDAY ):
        introduction += ", `openSUSE`, `Manjaro`"

    introduction += (
        " and theoretically, any platform which supports the "
        "`AyatanaAppIndicator3` / `AppIndicator3` library.\n\n" )

    introduction += "Other indicators in this series are:\n"
    for indicator_ in _get_indicator_names_sans_current( indicator ):
        introduction += f"- [{ indicator_ }](https://pypi.org/project/{ indicator_ })\n"

    introduction += '\n'

    return introduction


def _get_install_uninstall(
    indicator,
    content_heading,
    content_install_uninstall_operating_system_packages,
    install_uninstall_command_debian,
    install_uninstall_command_fedora,
    install_uninstall_command_manjaro,
    install_uninstall_command_opensuse,
    get_python_virtual_environment_install_uninstall_function,
    get_extension_install_uninstall_function ):

    operating_system_to_content = { }
    for operating_system in OperatingSystem:
        if _is_operating_system( operating_system, *OPERATING_SYSTEMS_DEBIAN_BASED ):
            install_uninstall_command = install_uninstall_command_debian
            _get_operating_system_packages_function = _get_operating_system_packages_debian

        elif _is_operating_system( operating_system, *OPERATING_SYSTEMS_FEDORA_BASED ):
            install_uninstall_command = install_uninstall_command_fedora
            _get_operating_system_packages_function = _get_operating_system_packages_fedora

        elif _is_operating_system( operating_system, *OPERATING_SYSTEMS_MANJARO_BASED ):
            install_uninstall_command = install_uninstall_command_manjaro
            _get_operating_system_packages_function = _get_operating_system_packages_manjaro

        elif _is_operating_system( operating_system, *OPERATING_SYSTEMS_OPENSUSE_BASED ):
            install_uninstall_command = install_uninstall_command_opensuse
            _get_operating_system_packages_function = _get_operating_system_packages_opensuse

        else:
            raise ValueError( f"Unknown operating system : { operating_system }" )

        operating_system_packages = (
            _get_operating_system_packages_function(
                indicator,
                operating_system ) )

        operating_system_to_content[ operating_system ] = (
            f"1. { content_install_uninstall_operating_system_packages }"
            "    ```\n"
            f"    { install_uninstall_command + ' ' }"
            f"{ ' '.join( sorted( operating_system_packages ) ) }\n"
            "    ```\n\n" )

        python_install_uninstall = (
            get_python_virtual_environment_install_uninstall_function(
                indicator,
                operating_system ) )

        operating_system_to_content[ operating_system ] += (
            f"2. { python_install_uninstall }" )

        extension = get_extension_install_uninstall_function( operating_system )
        if extension:
            operating_system_to_content[ operating_system ] += (
                f"3. { extension }" )

    # Group by operating systems with identical content.
    content_to_operating_systems = { }
    for operating_system, content in operating_system_to_content.items():
        content_to_operating_systems.setdefault( content, set() ).add( operating_system )

    # Sort within each group of operating systems.
    for content, operating_systems in content_to_operating_systems.items():
        content_to_operating_systems[ content ] = (
            tuple( sorted( operating_systems, key = lambda key_: key_.name ) ) )

    # Swap content with sorted groups of operating systems.
    operating_systems_to_content = { }
    for content, operating_systems in content_to_operating_systems.items():
        operating_systems_to_content.setdefault( operating_systems, set() ).add( content )

    content = content_heading

    # Generate content for group of operating systems,
    # sorted by the first operating system of each group.
    operating_system_groups = (
        sorted(
            operating_systems_to_content.keys(),
            key = lambda key_: key_[ 0 ].name ) )

    for operating_systems in operating_system_groups:
        content += (
            "<details>"
            f"<summary><b>{ _get_summary( operating_systems ) }</b></summary>\n\n"
            f"{ operating_system_to_content[ operating_systems[ 0 ] ] }"  #TODO I dn't understand the zero here.
            "</details>\n\n" )

    return content


def _get_install(
    indicator ):

    return (
        _get_install_uninstall(
            indicator,

            "Installation / Updating\n"
            "------------------------\n\n",

            "Install operating system packages:\n\n",

            "sudo apt-get -y install",
            "sudo dnf -y install",
            "sudo pacman -S --noconfirm",
            "sudo zypper install -y",
            
             _get_python_virtual_environment_install,

             _get_extension_install )  )


def _get_uninstall(
    indicator ):

    return (
        _get_install_uninstall(
            indicator,

            "Uninstall\n"
            "---------\n\n",

            "Uninstall operating system packages:\n\n",

            "sudo apt-get -y remove",
            "sudo dnf -y remove",
            "sudo pacman -R --noconfirm",
            "sudo zypper remove -y",

             _get_python_virtual_environment_uninstall,

             _get_extension_uninstall ) )


def _get_python_virtual_environment_install(
    indicator,
    operating_system ):

#TODO Need to ensure that the correct libgirepository 1 or 2 is in the packages
# section.
#
# For below, consider Ubuntu 24 to use libgirep 2
    # On Debian based distributions, the latest version of PyGObject requires
    # libgirepository-2.0-dev which is only available on Debian 13+ and
    # Ubuntu 24.04+.
    #
    # Ubuntu 24.04 has both libgirepository-2.0-dev and libgirepository1.0-dev
    # and things seem to work just fine with libgirepository1.0-dev.
    #
    # Consequently, For Debian 11/12 and Ubuntu 20.04/22.04/24.04 PyGObject is
    # pinned to 3.50.0 which is compatible with libgirepository1.0-dev.
    #
    # This issue does not seem to affect Fedora, Manjaro nor openSUSE.
    #
    # References:
    #   https://gitlab.gnome.org/GNOME/pygobject/-/blob/main/NEWS
    #   https://pygobject.gnome.org/getting_started.html
    #   https://github.com/beeware/toga/issues/3143#issuecomment-2727905226
    pygobject_pinned_to_3_50_0 = (
        _is_operating_system(
            operating_system,
            OperatingSystem.DEBIAN_11,
            OperatingSystem.DEBIAN_12,
            OperatingSystem.KUBUNTU_2204,
            OperatingSystem.KUBUNTU_2404,
            OperatingSystem.LINUX_MINT_CINNAMON_20,
            OperatingSystem.LINUX_MINT_CINNAMON_21,
            OperatingSystem.LINUX_MINT_CINNAMON_22,
            OperatingSystem.LUBUNTU_2204,
            OperatingSystem.LUBUNTU_2404,
            OperatingSystem.UBUNTU_2004,
            OperatingSystem.UBUNTU_2204,
            OperatingSystem.UBUNTU_2404,
            OperatingSystem.UBUNTU_BUDGIE_2404,
            OperatingSystem.UBUNTU_MATE_2404,
            OperatingSystem.UBUNTU_UNITY_2204,
            OperatingSystem.UBUNTU_UNITY_2404,
            OperatingSystem.XUBUNTU_2404 ) )

    pygobject = "PyGObject"
    if pygobject_pinned_to_3_50_0:
        pygobject = r"PyGObject\<=3.50.0"

    return (
        f"Create a `Python3` virtual environment at `{ utils.VENV_INSTALL }` "
        f"and install `{ indicator }`, including icons, .desktop and run "
        " script:\n"
        "    ```\n"
        f"    indicator={ indicator } && \\\n"
        f"    venv={ utils.VENV_INSTALL } && \\\n"
        f"    if [ ! -d ${{venv}} ]; then python3 -m venv ${{venv}}; fi && \\\n"
        f"    . ${{venv}}/bin/activate && \\\n"
        f"    python3 -m pip install --upgrade { pygobject } ${{indicator}} && \\\n"
        "    deactivate && \\\n"
        f"    . $(ls -d ${{venv}}/lib/python3.* | head -1)/"
        f"site-packages/${{indicator}}/platform/linux/install.sh\n"
        "    ```\n" )


def _get_python_virtual_environment_uninstall(
    indicator,
    operating_system ):

    return (
        "Uninstall the indicator from the `Python3` virtual environment, "
        "including icons, .desktop and run script:\n"
        "    ```\n"
        f"    indicator={ indicator } && \\\n"
        f"    venv={ utils.VENV_INSTALL } && \\\n"
        f"    $(ls -d ${{venv}}/lib/python3.* | head -1)/"
        f"site-packages/${{indicator}}/platform/linux/uninstall.sh && \\\n"
        f"    . ${{venv}}/bin/activate && \\\n"
        f"    python3 -m pip uninstall --yes ${{indicator}} && \\\n"
        "    count=$(python3 -m pip --disable-pip-version-check list | grep -o \"indicator\" | wc -l) && \\\n"
        "    deactivate && \\\n"
        f"    if [ \"$count\" -eq \"0\" ]; then rm -f -r ${{venv}}; fi \n"
        "    ```\n\n"
        f"    The configuration directory `$HOME/.config/{ indicator }` "
        "will not be deleted.\n\n"
        f"    The cache directory `$HOME/.cache/{ indicator }` "
        "will be deleted.\n\n"
        "    If no other indicators remain installed, the virtual "
        "environment will be deleted.\n\n" )


def _get_extension_install(
    operating_system ):

    extension = ""

#TODO Check this list.
    if (
        { operating_system }.issubset( {
            OperatingSystem.DEBIAN_11,
            OperatingSystem.DEBIAN_12 } ) ):

        extension = (
            "For the `appindicator` extension to take effect, log out / in "
            "(or restart) and in a terminal run:\n"
            "    ```\n"
            "    gnome-extensions enable ubuntu-appindicators@ubuntu.com\n"
            "    ```\n\n" )

#TODO Check this list
    if (
        { operating_system }.issubset( {
            OperatingSystem.FEDORA_40,
            OperatingSystem.FEDORA_41,
            OperatingSystem.FEDORA_42,
            OperatingSystem.KUBUNTU_2204,
            OperatingSystem.OPENSUSE_TUMBLEWEED } ) ):

        url = "https://extensions.gnome.org/extension/615/appindicator-support"
        extension = (
            "Install the "
            "`GNOME Shell` `AppIndicator and KStatusNotifierItem Support` "
            f"[extension]({ url }).\n\n" )

    return extension


def _get_extension_uninstall(
    operating_system ):

    return "" #TODO Should write something...


def _get_summary(
    operating_systems ):

    summary = [ ]
    for operating_system in operating_systems:
        human_readable_operating_system = ""
        for part in operating_system.name.split( '_' ):
            if part.isnumeric():
                if len( part ) == 2:
                    human_readable_operating_system += ' ' + part

                elif len( part ) == 4:
                    human_readable_operating_system += (
                        ' ' + part[ 0 : 2 ] + '.' + part[ 2 : ] )

                else:
                    print( f"UNHANDLED PART '{ part }' for OPERATING SYSTEM '{ operating_system }'" )

            else:
                if human_readable_operating_system.endswith( "Manjaro" ):
                    human_readable_operating_system += (
                        ' ' + part[ 0 : 2 ] + '.' + part[ 2 : 3 ] + '.' + part[ 3 ].lower() )

                elif "MATE" == part:
                    human_readable_operating_system += ' ' + part # Keep capitalised.

                elif "OPENSUSE" == part:
                    human_readable_operating_system += ' ' + "openSUSE" # Keep partially capitalised.

                else:
                    human_readable_operating_system += ' ' + part.title()

        summary.append( human_readable_operating_system.strip() )

    return " | ".join( sorted( summary ) )


def _get_operating_system_packages_debian(
    indicator,
    operating_system ):

    packages = [
        "gir1.2-ayatanaappindicator3-0.1",
        "libcairo2-dev",
        "libgirepository1.0-dev",  #TODO I think need to move this out of here
        # as it will not apply for Debian 13 and Ubuntu 26.04 and possibly
        # 24.04 as they want version 2
        "python3-pip",
        "python3-venv" ]

    needs_gnome_shell_extension_appindicator = (
        _is_operating_system(
            operating_system,
            OperatingSystem.DEBIAN_11,
            OperatingSystem.DEBIAN_12 ) )

    if needs_gnome_shell_extension_appindicator:
        packages.append( "gnome-shell-extension-appindicator" )

    needs_calendar = (
        _is_operating_system(
            operating_system,
            OperatingSystem.DEBIAN_11,
            OperatingSystem.DEBIAN_12,
            OperatingSystem.KUBUNTU_2204,
            OperatingSystem.KUBUNTU_2404,
            OperatingSystem.LINUX_MINT_CINNAMON_21,
            OperatingSystem.LINUX_MINT_CINNAMON_22,
            OperatingSystem.LUBUNTU_2204,
            OperatingSystem.LUBUNTU_2404,
            OperatingSystem.UBUNTU_2204,
            OperatingSystem.UBUNTU_2404,
            OperatingSystem.UBUNTU_BUDGIE_2404,
            OperatingSystem.UBUNTU_MATE_2404,
            OperatingSystem.UBUNTU_UNITY_2204,
            OperatingSystem.UBUNTU_UNITY_2404,
            OperatingSystem.XUBUNTU_2404 ) )

    if _is_indicator( indicator, IndicatorName.INDICATORFORTUNE ):
        packages.append( "fortune-mod" )
        packages.append( "fortunes" )
        packages.append( "wl-clipboard" )

    if _is_indicator( indicator, IndicatorName.INDICATORONTHISDAY ):
        packages.append( "wl-clipboard" )

        if needs_calendar:
            packages.append( "calendar" )

    if _is_indicator( indicator, IndicatorName.INDICATORPUNYCODE ):
        packages.append( "wl-clipboard" )

    if _is_indicator( indicator, IndicatorName.INDICATORSCRIPTRUNNER ):
        packages.append( "libnotify-bin" )
        packages.append( "pulseaudio-utils" )

    if _is_indicator( indicator, IndicatorName.INDICATORTEST ):
        packages.append( "fortune-mod" )
        packages.append( "fortunes" )
        packages.append( "libnotify-bin" )
        packages.append( "pulseaudio-utils" )
        packages.append( "wl-clipboard" )
        packages.append( "wmctrl" )

        if needs_calendar:
            packages.append( "calendar" )

    if _is_indicator( indicator, IndicatorName.INDICATORVIRTUALBOX ):
        packages.append( "wmctrl" )

    return packages


def _get_operating_system_packages_fedora(
    indicator,
    operating_system ):

    packages = [
        "cairo-gobject-devel",
        "gcc",
        "gobject-introspection-devel",
        "libappindicator-gtk3",
        "python3-devel",
        "python3-pip" ]

    if _is_indicator( indicator, IndicatorName.INDICATORFORTUNE ):
        packages.append( "fortune-mod" )
        packages.append( "wl-clipboard" )

    if _is_indicator( indicator, IndicatorName.INDICATORONTHISDAY ):
        packages.append( "calendar" )
        packages.append( "wl-clipboard" )

    if _is_indicator( indicator, IndicatorName.INDICATORPUNYCODE ):
        packages.append( "wl-clipboard" )

    # Fedora 42 uses pw-play so pulseaudio is not required.
    needs_pulseaudio = (
        _is_operating_system(
            operating_system,
            OperatingSystem.FEDORA_40,
            OperatingSystem.FEDORA_41 ) )

    if _is_indicator( indicator, IndicatorName.INDICATORSCRIPTRUNNER ):
        if needs_pulseaudio:
            packages.append( "pulseaudio-utils" )

    if _is_indicator( indicator, IndicatorName.INDICATORTEST ):
        packages.append( "calendar" )
        packages.append( "fortune-mod" )
        packages.append( "wl-clipboard" )
        packages.append( "wmctrl" )

        if needs_pulseaudio:
            packages.append( "pulseaudio-utils" )

    if _is_indicator( indicator, IndicatorName.INDICATORVIRTUALBOX ):
        packages.append( "wmctrl" )

    return packages


def _get_operating_system_packages_manjaro(
    indicator,
    operating_system ):

    packages = [
        "cairo",
        "gcc",
        "libayatana-appindicator",
        "pkgconf" ]

    if _is_indicator( indicator, IndicatorName.INDICATORFORTUNE ):
        packages.append( "fortune-mod" )
        packages.append( "wl-clipboard" )

    if _is_indicator( indicator, IndicatorName.INDICATORONTHISDAY ):
        packages.append( "wl-clipboard" )

    if _is_indicator( indicator, IndicatorName.INDICATORPUNYCODE ):
        packages.append( "wl-clipboard" )

    if _is_indicator( indicator, IndicatorName.INDICATORTEST ):
        packages.append( "fortune-mod" )
        packages.append( "wl-clipboard" )
        packages.append( "wmctrl" )

    if _is_indicator( indicator, IndicatorName.INDICATORVIRTUALBOX ):
        packages.append( "wmctrl" )

    return packages


def _get_operating_system_packages_opensuse(
    indicator,
    operating_system ):

    packages = [
        "cairo-devel",
        "gcc",
        "gobject-introspection-devel",
        "python3-devel",
        "typelib-1_0-AyatanaAppIndicator3-0_1" ]

    if _is_indicator( indicator, IndicatorName.INDICATORFORTUNE ):
        packages.append( "fortune" )
        packages.append( "wl-clipboard" )

    if _is_indicator( indicator, IndicatorName.INDICATORONTHISDAY ):
        packages.append( "wl-clipboard" )

    if _is_indicator( indicator, IndicatorName.INDICATORPUNYCODE ):
        packages.append( "wl-clipboard" )

    if _is_indicator( indicator, IndicatorName.INDICATORTEST ):
        packages.append( "fortune" )
        packages.append( "wl-clipboard" )

    return packages


def _get_usage(
    indicator,
    indicator_human_readable ):

    # Remove the ™ from VirtualBox™.
    indicator_human_readable_cleaned = (
        indicator_human_readable.split( ' ', 1 )[ 1 ].lower().replace( '™', '' ) )

    usage = (
        "Usage\n"
        "-----\n\n"

        f"To run `{ indicator }`, press the `Super` key to show the "
        "applications overlay (or similar), type "
        f"`{ indicator_human_readable_cleaned }` into the search bar and the "
        "icon should be present for you to select.  "
        "If the icon does not appear, or appears as generic or broken, you may "
        "have to log out / in (or restart).\n\n"
        "Alternatively, to run from the terminal:\n\n"
        f"```. $HOME/.local/bin/{ indicator }.sh```\n\n" )

    if _is_indicator( indicator, IndicatorName.INDICATORSCRIPTRUNNER ):
        usage += (
            f"Note that any `Python3` scripts you add to `{ indicator }` may "
            "require additional modules installed to the virtual environment at"
            f" `{ utils.VENV_INSTALL }`.\n\n" )

    if _is_indicator( indicator, IndicatorName.INDICATORTIDE ):
        usage += (
            "Note that you will need to write a `Python3` script to retrieve "
            "your tidal data.  In addition, your `Python` script may require "
            "additional modules installed to the virtual environment at "
            f"`{ utils.VENV_INSTALL }`.\n\n" )

    return usage


def _get_limitations(
    indicator ):

    messages = [ ]

    if (
        _is_indicator(
            indicator,
            IndicatorName.INDICATORTEST,
            IndicatorName.INDICATORVIRTUALBOX ) ):
        messages.append(
            "- `Wayland`: The command `wmctrl` is unsupported.\n" )

    # Kubuntu 22.04     KDE     No mouse wheel scroll.
    # Kubuntu 24.04     KDE     No mouse wheel scroll.
    # Manjaro 24.0.7    KDE     No mouse wheel scroll.
    # Manjaro 25.0.5    KDE     No mouse wheel scroll.
    if (
        _is_indicator(
            indicator,
            IndicatorName.INDICATORSTARDATE,
            IndicatorName.INDICATORTEST,
            IndicatorName.INDICATORVIRTUALBOX ) ):
        messages.append(
            "- `KDE`: Mouse wheel scroll over icon is unsupported.\n" )

    # Kubuntu 22.04         KDE         Tooltip in lieu of label.
    # Kubuntu 24.04         KDE         Tooltip in lieu of label.
    # Linux Mint 20         X-Cinnamon  Tooltip in lieu of label.
    # Linux Mint 21         X-Cinnamon  Tooltip in lieu of label.
    # Linux Mint 22         X-Cinnamon  Tooltip in lieu of label.
    # Lubuntu 22.04         LXQt        No label; tooltip is indicator filename.
    # Lubuntu 24.04         LXQt        No label; tooltip is indicator filename.
    # Manjaro 24.0.7        KDE         Tooltip in lieu of label.
    # Manjaro 25.0.5        KDE         No label/tooltip.
    # openSUSE Tumbleweed   ICEWM       No label/tooltip.
    # Xubuntu 24.04         XFCE        Tooltip in lieu of label.
    if (
        _is_indicator(
            indicator,
            IndicatorName.INDICATORLUNAR,
            IndicatorName.INDICATORSCRIPTRUNNER,
            IndicatorName.INDICATORSTARDATE,
            IndicatorName.INDICATORTEST ) ):
        messages.append(
            "- `KDE`: The icon label is unsupported; "
            "the icon tooltip is used in lieu where available.\n" )
        messages.append(
            "- `X-Cinnamon`: The icon label is unsupported; "
            "the icon tooltip is used in lieu.\n" )
        messages.append(
            "- `XFCE`: The icon label is unsupported; "
            "the icon tooltip is used in lieu.\n" )
        messages.append(
            "- `LXQt`: The icon label is unsupported; icon tooltip shows the "
            "indicator filename (effectively unsupported).\n" )
        messages.append(
            "- `ICEWM`: The icon label and icon tooltip are unsupported.\n" )

    # Linux Mint 20     X-Cinnamon  When icon is changed, it disappears.
    # Linux Mint 21     X-Cinnamon  When icon is changed, it disappears.
    # Linux Mint 22     X-Cinnamon  When icon is changed, it disappears.
    # Lubuntu 22.04     LXQt        Cannot change the icon once initially set.
    # Lubuntu 24.04     LXQt        Cannot change the icon once initially set.
    if (
        _is_indicator(
            indicator,
            IndicatorName.INDICATORLUNAR,
            IndicatorName.INDICATORTEST ) ):
        messages.append(
            "- `LXQt`: The icon cannot be changed once set.\n" )
        messages.append(
            "- `X-Cinnamon`: The icon disappears when changed from that "
            "originally set, leaving a blank space.\n" )

    # Lubuntu 22.04     LXQt    Default terminal (qterminal) does not work.
    # Lubuntu 24.04     LXQt    Default terminal (qterminal) all good.
    if (
        _is_indicator(
            indicator,
            IndicatorName.INDICATORSCRIPTRUNNER,
            IndicatorName.INDICATORTEST ) ):
        messages.append(
            "- `LXQt`: Commands cannot be sent to `qterminal` with version < `1.2.0`"
            " as the arguments are not "
            "[preserved](https://github.com/lxqt/qterminal/issues/335). "
            "Install `gnome-terminal` as a workaround.\n" )

    # Manjaro 24            No `calendar` command.
    # Manjaro 25            No `calendar` command.
    # openSUSE Tumbleweed   No `calendar` command.
    if (
        _is_indicator(
            indicator,
            IndicatorName.INDICATORTEST ) ):
        messages.append(
            "- `Manjaro 24`: Does not contain the `calendar` command.\n" )
        messages.append(
            "- `Manjaro 25`: Does not contain the `calendar` command.\n" )
        messages.append(
            "- `openSUSE Tumbleweed`: Does not contain the `calendar` command.\n" )

    # openSUSE Tumbleweed    ICEWM      No notifications.
    if (
        _is_indicator(
            indicator,
            IndicatorName.INDICATORFORTUNE,
            IndicatorName.INDICATORLUNAR,
            IndicatorName.INDICATORONTHISDAY,
            IndicatorName.INDICATORPUNYCODE,
            IndicatorName.INDICATORSCRIPTRUNNER,
            IndicatorName.INDICATORTEST,
            IndicatorName.INDICATORTIDE,
            IndicatorName.INDICATORVIRTUALBOX )  ):
        messages.append(
            "- `ICEWM`: Notifications are unsupported.\n" )

    # Kubuntu 24.04     No autostart.
    messages.append(
        "- `Kubuntu 24.04`: No autostart.\n" )

    # Manjaro 24.0.7   No autostart.
    # Manjaro 25.0.5   No autostart.
    # As indicatoronthisday is unsupported on Manjaro (and openSUSE) as there
    # is no calendar package, only flag that that autostart does not work for
    # all the indicators other than indicatoronthisday.
    if not (
        _is_indicator(
            indicator,
            IndicatorName.INDICATORONTHISDAY ) ):
        messages.append(
            "- `Manjaro 24`: No autostart.\n" )
        messages.append(
            "- `Manjaro 25`: No autostart.\n" )

    message = ""
    if messages:
        message = (
            "Limitations\n"
            "-----------\n\n"
            f"{ ''.join( sorted( messages, key = str.casefold ) ) }\n\n" )

    return message


def _get_license(
    authors_emails,
    start_year ):

    end_year = datetime.datetime.now( datetime.timezone.utc ).strftime( '%Y' )
    authors = [ author_email[ 0 ] for author_email in authors_emails ]

    return (
        "License\n"
        "-------\n\n"
        "This project in its entirety is licensed under the terms of the "
        "GNU General Public License v3.0 license.\n\n"
        f"Copyright { start_year }-{ end_year } { ', '.join( authors ) }.\n" )


def build_readme(
    directory,
    indicator,
    indicator_human_readable,
    authors_emails,
    start_year ):
    '''
    Build the README.md file for the indicator.
    '''
    Path( directory ).mkdir( parents = True, exist_ok = True )

    content = (
        _get_introduction( indicator ) +
        _get_install( indicator ) +
        _get_usage( indicator, indicator_human_readable ) +
        _get_limitations( indicator ) +
        _get_uninstall( indicator ) +
        _get_license( authors_emails, start_year ) )

    indicatorbase.IndicatorBase.write_text_file(
        Path( directory, "README.md" ),
        content )
