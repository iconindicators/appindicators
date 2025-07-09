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
Create a README.md for an indicator.

References:
    https://pygobject.gnome.org/getting_started.html
    https://stackoverflow.com/q/70508775/2156453
    https://stackoverflow.com/q/60779139/2156453
'''


#TODO Consider testing on Fedora 42.


#TODO Consider testing on newest Manjaro.
#    MANJARO_25 = auto()
# Check that calendar still does not exist.
# Check that autostart still does not function.
# In messages to user about Manjaro, maybe change "Manjaro 24" to just
# "Manjaro" or "Manjaro 24/25".


#TODO Test on Linux Mint 20 first, then delete, then 21.
# 21 is NOT backed up.


#TODO Candidates for removal of VM from backup after testing...
# EOL Dates:
#   Fedora 38 2024 05
#   Debian 11 2024 08
#   Fedora 39 2024 11
#   Kubuntu 22.04 2025 04
#   Linux Mint 20 2025 04
#   Lubuntu 22.04 2025 04
#   Fedora 40 2025 05
#   Ubuntu Unity 22.04 2025 04
#   Manjaro 24 now replaced by 25


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
    FEDORA_38 = auto()
    FEDORA_39 = auto()
    FEDORA_40 = auto()
    KUBUNTU_2204 = auto()
    KUBUNTU_2404 = auto()
    LINUX_MINT_CINNAMON_20 = auto()
    LINUX_MINT_CINNAMON_21 = auto()
    LINUX_MINT_CINNAMON_22 = auto()
    LUBUNTU_2204 = auto()
    LUBUNTU_2404 = auto()
    MANJARO_24 = auto()
    OPENSUSE_TUMBLEWEED = auto()
    UBUNTU_2004 = auto()
    UBUNTU_2204 = auto()
    UBUNTU_2404 = auto()
    UBUNTU_BUDGIE_2404 = auto()
    UBUNTU_MATE_2404 = auto()
    UBUNTU_UNITY_2204 = auto()
    UBUNTU_UNITY_2404 = auto()
    XUBUNTU_2404 = auto()


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

    is_indicator = False
    for indicator_ in indicators:
        if indicator == indicator_.name.lower():
            is_indicator = True
            break

    return is_indicator


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
        f"`{ indicator }` { comments } on "
        "`Debian`, `Ubuntu`, `Fedora`" )

    # openSUSE Tumbleweed and Manjaro do not contain the 'calendar' package.
    #
    # For indicatoronthisday, drop references to openSUSE/Manjaro.
    #
    # Keep indicatortest as `calendar` is only a small part of the overall
    # functionality.
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


def _get_indicator_names_sans_current(
    indicator ):

    indicators = [
        str( x )
        for x in Path( '.' ).iterdir()
        if x.is_dir() and str( x ).startswith( "indicator" ) ]

    indicators.remove( indicator )
    indicators.remove( "indicatorbase" )
    indicators.sort()
    return indicators


def _get_install_uninstall(
    indicator,
    install = True ):

    if install:
        function = _get_install_for_operating_system
        command_debian = "sudo apt-get -y install"
        command_fedora = "sudo dnf -y install"

        additional_text = ""
        if _is_indicator( indicator, IndicatorName.INDICATORSCRIPTRUNNER ):
            additional_text = (
                f"3. Any `Python` scripts you add to `{ indicator }` may "
                "require additional modules installed to the virtual "
                f"environment at `{ utils.VENV_INSTALL }`.\n" )

        if _is_indicator( indicator, IndicatorName.INDICATORTIDE ):
            additional_text = (
                "3. You will need to write a `Python` script to retrieve your "
                "tidal data.  In addition, your `Python` script may require "
                "additional modules installed to the virtual environment at "
                f"`{ utils.VENV_INSTALL }`.\n" )

        title = (
            "Installation / Updating\n"
            "-----------------------\n\n"
            "Installation and updating follow the same process:\n"
            "1. Install operating system packages.\n"
            f"2. Install `{ indicator }` to a `Python3` virtual "
            f"environment at `{ utils.VENV_INSTALL }`.\n"
            f"{ additional_text }\n\n" )

    else:
        function = _get_uninstall_for_operating_system
        command_debian = "sudo apt-get -y remove"
        command_fedora = "sudo dnf -y remove"
        title = (
            "Uninstall\n"
            "---------\n\n" )

    return (
        title +

        function(
            {
                OperatingSystem.DEBIAN_11,
                OperatingSystem.DEBIAN_12 },
            indicator,
            command_debian,
            _get_operating_system_dependencies_debian ) +

        function(
            { OperatingSystem.FEDORA_38 },
            indicator,
            command_fedora,
            _get_operating_system_dependencies_fedora ) +

        function(
            {
                OperatingSystem.FEDORA_39,
                OperatingSystem.FEDORA_40 },
            indicator,
            command_fedora,
            _get_operating_system_dependencies_fedora ) +

        function(
            { OperatingSystem.MANJARO_24 },
            indicator,
            "sudo pacman -S --noconfirm"
            if install else
            "sudo pacman -R --noconfirm",
            _get_operating_system_dependencies_manjaro ) +

        function(
            { OperatingSystem.OPENSUSE_TUMBLEWEED },
            indicator,
            "sudo zypper install -y"
            if install else
            "sudo zypper remove -y",
            _get_operating_system_dependencies_opensuse ) +

        function(
            {
                OperatingSystem.LINUX_MINT_CINNAMON_20,
                OperatingSystem.UBUNTU_2004 },
            indicator,
            command_debian,
            _get_operating_system_dependencies_debian ) +

        function(
            {
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
                OperatingSystem.XUBUNTU_2404 },
            indicator,
            command_debian,
            _get_operating_system_dependencies_debian ) )


def _os_has_no_calendar( operating_systems ):
    '''
    openSUSE Tumbleweed and Manjaro do not contain the package 'calendar'.
    '''
    return (
        { OperatingSystem.MANJARO_24 }.issubset( operating_systems ) or
        { OperatingSystem.OPENSUSE_TUMBLEWEED }.issubset( operating_systems ) )


def _get_install_for_operating_system(
    operating_systems,
    indicator,
    install_command,
    _get_operating_system_dependencies_function ):

    calendar_vital_to_indicator = (
        _is_indicator(
            indicator,
            IndicatorName.INDICATORONTHISDAY ) )

    if calendar_vital_to_indicator and _os_has_no_calendar( operating_systems ):
        installation = ''

    else:
        summary = _get_summary( operating_systems )

        # Installing operating system packages:
        #   https://stackoverflow.com/a/61164149/2156453
        #   https://pygobject.gnome.org/getting_started.html
        operating_system_dependencies = (
            _get_operating_system_dependencies_function(
                operating_systems,
                IndicatorName[ indicator.upper() ] ) )

        installation = (
            "<details>"
            f"<summary><b>{ summary }</b></summary>\n\n"

            "1. Install operating system packages:\n\n"
            "    ```\n"
            f"    { install_command } { operating_system_dependencies }\n"
            "    ```\n"
            f"    { _get_extension( operating_systems ) }\n\n" )

        python_virtual_environment = (
            _get_installation_python_virtual_environment(
                indicator, operating_systems ) )

        installation += f"2. { python_virtual_environment }"

        additional_python_modules = (
            _get_installation_additional_python_modules( indicator ) )

        if additional_python_modules:
            installation += f"3. { additional_python_modules }"

        installation += "</details>\n\n"

    return installation


def _get_extension(
    operating_systems ):

    extension = ''

    needs_extension = (
        { OperatingSystem.DEBIAN_11 }.issubset( operating_systems ) or
        { OperatingSystem.DEBIAN_12 }.issubset( operating_systems ) )

    if needs_extension:
        extension = (
            "For the `appindicator` extension to take effect, log out / in "
            "(or restart) and in a terminal run:\n"
            "    ```\n"
            "    gnome-extensions enable ubuntu-appindicators@ubuntu.com\n"
            "    ```\n" )

    needs_extension = (
        { OperatingSystem.FEDORA_38 }.issubset( operating_systems ) or
        { OperatingSystem.FEDORA_39 }.issubset( operating_systems ) or
        { OperatingSystem.FEDORA_40 }.issubset( operating_systems ) or
        { OperatingSystem.KUBUNTU_2204 }.issubset( operating_systems ) or
        { OperatingSystem.OPENSUSE_TUMBLEWEED }.issubset( operating_systems ) )

    if needs_extension:
        url = "https://extensions.gnome.org/extension/615/appindicator-support"
        extension = (
            "Install the `GNOME Shell` "
            "`AppIndicator and KStatusNotifierItem Support` "
            f"[extension]({ url }).\n\n" )

    return extension


def _get_installation_python_virtual_environment(
    indicator,
    operating_systems ):

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
    pygobject_needs_to_be_pinned = (
        { OperatingSystem.DEBIAN_11 }.issubset( operating_systems ) or
        { OperatingSystem.DEBIAN_12 }.issubset( operating_systems ) or
        { OperatingSystem.KUBUNTU_2204 }.issubset( operating_systems ) or
        { OperatingSystem.KUBUNTU_2404 }.issubset( operating_systems ) or
        { OperatingSystem.LINUX_MINT_CINNAMON_20 }.issubset( operating_systems ) or
        { OperatingSystem.LINUX_MINT_CINNAMON_21 }.issubset( operating_systems ) or
        { OperatingSystem.LINUX_MINT_CINNAMON_22 }.issubset( operating_systems ) or
        { OperatingSystem.LUBUNTU_2204 }.issubset( operating_systems ) or
        { OperatingSystem.LUBUNTU_2404 }.issubset( operating_systems ) or
        { OperatingSystem.UBUNTU_2004 }.issubset( operating_systems ) or
        { OperatingSystem.UBUNTU_2204 }.issubset( operating_systems ) or
        { OperatingSystem.UBUNTU_2404 }.issubset( operating_systems ) or
        { OperatingSystem.UBUNTU_BUDGIE_2404 }.issubset( operating_systems ) or
        { OperatingSystem.UBUNTU_MATE_2404 }.issubset( operating_systems ) or
        { OperatingSystem.UBUNTU_UNITY_2204 }.issubset( operating_systems ) or
        { OperatingSystem.UBUNTU_UNITY_2404 }.issubset( operating_systems ) or
        { OperatingSystem.XUBUNTU_2404 }.issubset( operating_systems ) )

    pygobject = "PyGObject"
    if pygobject_needs_to_be_pinned:
        pygobject = "PyGObject\<=3.50.0"

    message = (
        f"Install `{ indicator }`, including icons, .desktop and run "
        "script, to the `Python3` virtual environment:\n"
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

    return message


def _get_installation_additional_python_modules(
    indicator ):

    message = ''

    common = (
        "For example, to install the `requests` module:\n"
        "    ```\n"
        f"    . { utils.VENV_INSTALL }/bin/activate && \\\n"
        "    python3 -m pip install --upgrade requests && \\\n"
        "    deactivate\n"
        "    ```\n" )

    if _is_indicator( indicator, IndicatorName.INDICATORSCRIPTRUNNER ):
        message += (
            f"If you have added any `Python` scripts to `{ indicator }`, "
            f"you may need to install additional `Python` modules. { common }" )

    if _is_indicator( indicator, IndicatorName.INDICATORTIDE ):
        message += (
            "Your `Python` script which retrieves tidal data may require "
            f"additional `Python` modules. { common }" )

    return message


def _get_uninstall_for_operating_system(
    operating_systems,
    indicator,
    uninstall_command,
    _get_operating_system_dependencies_function ):

    calendar_vital_to_indicator = (
        _is_indicator( indicator, IndicatorName.INDICATORONTHISDAY ) )

    if calendar_vital_to_indicator and _os_has_no_calendar( operating_systems ):
        uninstall = ''

    else:
        summary = _get_summary( operating_systems )

        operating_system_dependencies = (
            _get_operating_system_dependencies_function(
                operating_systems, IndicatorName[ indicator.upper() ] ) )

        # Ideally, an extension which was installed should be uninstalled.
        #
        # In reality, perhaps unwise to try to specify how to do this as it
        # depends on the distribution and version of the distribution.
        # Leave the extension in place; should not present a major drama!
        uninstall = (
            "<details>"
            f"<summary><b>{ summary }</b></summary>\n\n"

            "1. Uninstall operating system packages:\n\n"
            "    ```\n"
            f"    { uninstall_command } { operating_system_dependencies }\n"
            "    ```\n\n"

            "2. Uninstall the indicator from virtual environment:\n"
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
            "    If no other indicators remain installed, the virtual "
            "environment will be deleted.\n\n"
            "</details>\n\n" )

    return uninstall


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


def _get_operating_system_dependencies_debian(
    operating_systems,
    indicator ):

    dependencies = [
        "gir1.2-ayatanaappindicator3-0.1",
        "libcairo2-dev",
        "libgirepository1.0-dev",
        "python3-pip",
        "python3-venv" ]

    needs_gnome_shell_extension_appindicator = (
        { OperatingSystem.DEBIAN_11 }.issubset( operating_systems ) or
        { OperatingSystem.DEBIAN_12 }.issubset( operating_systems ) )

    if needs_gnome_shell_extension_appindicator:
        dependencies.append( "gnome-shell-extension-appindicator" )

    if indicator == IndicatorName.INDICATORFORTUNE:
        dependencies.append( "fortune-mod" )
        dependencies.append( "fortunes" )
        dependencies.append( "wl-clipboard" )

    needs_calendar = (
        { OperatingSystem.DEBIAN_11 }.issubset( operating_systems ) or
        { OperatingSystem.DEBIAN_12 }.issubset( operating_systems ) or
        { OperatingSystem.KUBUNTU_2204 }.issubset( operating_systems ) or
        { OperatingSystem.KUBUNTU_2404 }.issubset( operating_systems ) or
        { OperatingSystem.LINUX_MINT_CINNAMON_21 }.issubset( operating_systems ) or
        { OperatingSystem.LINUX_MINT_CINNAMON_22 }.issubset( operating_systems ) or
        { OperatingSystem.LUBUNTU_2204 }.issubset( operating_systems ) or
        { OperatingSystem.LUBUNTU_2404 }.issubset( operating_systems ) or
        { OperatingSystem.UBUNTU_2204 }.issubset( operating_systems ) or
        { OperatingSystem.UBUNTU_2404 }.issubset( operating_systems ) or
        { OperatingSystem.UBUNTU_BUDGIE_2404 }.issubset( operating_systems ) or
        { OperatingSystem.UBUNTU_MATE_2404 }.issubset( operating_systems ) or
        { OperatingSystem.UBUNTU_UNITY_2204 }.issubset( operating_systems ) or
        { OperatingSystem.UBUNTU_UNITY_2404 }.issubset( operating_systems ) or
        { OperatingSystem.XUBUNTU_2404 }.issubset( operating_systems ) )

    if indicator == IndicatorName.INDICATORONTHISDAY:
        dependencies.append( "wl-clipboard" )
        if needs_calendar:
            dependencies.append( "calendar" )

    if indicator == IndicatorName.INDICATORPUNYCODE:
        dependencies.append( "wl-clipboard" )

    if indicator == IndicatorName.INDICATORSCRIPTRUNNER:
        dependencies.append( "libnotify-bin" )
        dependencies.append( "pulseaudio-utils" )

    if indicator == IndicatorName.INDICATORTEST:
        dependencies.append( "fortune-mod" )
        dependencies.append( "fortunes" )
        dependencies.append( "libnotify-bin" )
        dependencies.append( "pulseaudio-utils" )
        dependencies.append( "wl-clipboard" )
        dependencies.append( "wmctrl" )
        if needs_calendar:
            dependencies.append( "calendar" )

    if indicator == IndicatorName.INDICATORVIRTUALBOX:
        dependencies.append( "wmctrl" )

    return ' '.join( sorted( dependencies ) )


def _get_operating_system_dependencies_fedora(
    operating_systems,
    indicator ):

    dependencies = [
        "cairo-gobject-devel",
        "gcc",
        "gobject-introspection-devel",
        "libappindicator-gtk3",
        "python3-devel",
        "python3-pip" ]

    if indicator == IndicatorName.INDICATORFORTUNE:
        dependencies.append( "fortune-mod" )
        dependencies.append( "wl-clipboard" )

    if indicator == IndicatorName.INDICATORONTHISDAY:
        dependencies.append( "calendar" )
        dependencies.append( "wl-clipboard" )

    if indicator == IndicatorName.INDICATORPUNYCODE:
        dependencies.append( "wl-clipboard" )

    needs_pulseaudio = (
        { OperatingSystem.FEDORA_39 }.issubset( operating_systems ) or
        { OperatingSystem.FEDORA_40 }.issubset( operating_systems ) )

    if indicator == IndicatorName.INDICATORSCRIPTRUNNER:
        if needs_pulseaudio:
            dependencies.append( "pulseaudio-utils" )

    if indicator == IndicatorName.INDICATORTEST:
        dependencies.append( "calendar" )
        dependencies.append( "fortune-mod" )
        dependencies.append( "wl-clipboard" )
        dependencies.append( "wmctrl" )

        if needs_pulseaudio:
            dependencies.append( "pulseaudio-utils" )

    if indicator == IndicatorName.INDICATORVIRTUALBOX:
        dependencies.append( "wmctrl" )

    return ' '.join( sorted( dependencies ) )


def _get_operating_system_dependencies_manjaro(
    operating_systems,
    indicator ):

    dependencies = [
        "cairo",
        "gcc",
        "libayatana-appindicator",
        "pkgconf" ]

    if indicator == IndicatorName.INDICATORFORTUNE:
        dependencies.append( "fortune-mod" )
        dependencies.append( "wl-clipboard" )

    if indicator == IndicatorName.INDICATORONTHISDAY:
        dependencies.append( "wl-clipboard" )

    if indicator == IndicatorName.INDICATORPUNYCODE:
        dependencies.append( "wl-clipboard" )

    if indicator == IndicatorName.INDICATORTEST:
        dependencies.append( "fortune-mod" )
        dependencies.append( "wl-clipboard" )
        dependencies.append( "wmctrl" )

    if indicator == IndicatorName.INDICATORVIRTUALBOX:
        dependencies.append( "wmctrl" )

    return ' '.join( sorted( dependencies ) )


def _get_operating_system_dependencies_opensuse(
    operating_systems,
    indicator ):

    dependencies = [
        "cairo-devel",
        "gcc",
        "gobject-introspection-devel",
        "python3-devel",
        "typelib-1_0-AyatanaAppIndicator3-0_1" ]

    if indicator == IndicatorName.INDICATORFORTUNE:
        dependencies.append( "fortune" )
        dependencies.append( "wl-clipboard" )

    if indicator == IndicatorName.INDICATORONTHISDAY:
        dependencies.append( "wl-clipboard" )

    if indicator == IndicatorName.INDICATORPUNYCODE:
        dependencies.append( "wl-clipboard" )

    if indicator == IndicatorName.INDICATORTEST:
        dependencies.append( "fortune" )
        dependencies.append( "wl-clipboard" )

    return ' '.join( sorted( dependencies ) )


def _get_usage(
    indicator,
    indicator_human_readable ):

    return (
        "Usage\n"
        "-----\n\n"

        f"To run `{ indicator }`, press the `Super` key to show the "
        "applications overlay (or similar), type "
        f"`{ indicator_human_readable.split( ' ', 1 )[ 1 ].lower().replace( '™', '' ) }` " # Removes the ™ from VirtualBox™.
        "into the search bar and the icon should be present for you to select.  "
        "If the icon does not appear, or appears as generic or broken, you may have to "
        "log out / in (or restart).\n\n"
        "Alternatively, to run from the terminal:\n\n"
        f"```. $HOME/.local/bin/{ indicator }.sh```\n\n" )


def _get_limitations(
    indicator ):

    messages = [ ]

    if _is_indicator(
        indicator,
        IndicatorName.INDICATORTEST,
        IndicatorName.INDICATORVIRTUALBOX ):
        messages.append(
            "- `Wayland`: The command `wmctrl` is unsupported.\n" )

    # Kubuntu 22.04     KDE     No mouse wheel scroll.
    # Kubuntu 24.04     KDE     No mouse wheel scroll.
    # Manjaro 24.0.7    KDE     No mouse wheel scroll.
    if _is_indicator(
        indicator,
        IndicatorName.INDICATORSTARDATE,
        IndicatorName.INDICATORTEST,
        IndicatorName.INDICATORVIRTUALBOX ):
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
    # openSUSE Tumbleweed   ICEWM       No label/tooltip.
    # Xubuntu 24.04         XFCE        Tooltip in lieu of label.
    if _is_indicator(
        indicator,
        IndicatorName.INDICATORLUNAR,
        IndicatorName.INDICATORSCRIPTRUNNER,
        IndicatorName.INDICATORSTARDATE,
        IndicatorName.INDICATORTEST ):
        messages.append(
            "- `KDE`: The icon label is unsupported; "
            "the icon tooltip is used in lieu.\n" )
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
    if _is_indicator(
        indicator,
        IndicatorName.INDICATORLUNAR,
        IndicatorName.INDICATORTEST ):
        messages.append(
            "- `LXQt`: The icon cannot be changed once set.\n" )
        messages.append(
            "- `X-Cinnamon`: The icon disappears when changed from that "
            "originally set, leaving a blank space.\n" )

    # Lubuntu 22.04     LXQt    Default terminal (qterminal) does not work.
    # Lubuntu 24.04     LXQt    Default terminal (qterminal) all good.
    if _is_indicator(
        indicator,
        IndicatorName.INDICATORSCRIPTRUNNER,
        IndicatorName.INDICATORTEST ):
        messages.append(
            "- `LXQt`: Commands cannot be sent to `qterminal` with version < `1.2.0`"
            " as the arguments are not "
            "[preserved](https://github.com/lxqt/qterminal/issues/335). "
            "Install `gnome-terminal` as a workaround.\n" )

    # Manjaro 24            No `calendar` command.
    # openSUSE Tumbleweed   No `calendar` command.
    if _is_indicator(
        indicator,
        IndicatorName.INDICATORTEST ):
        messages.append(
            "- `Manjaro 24`: Does not contain the `calendar` command.\n" )
        messages.append(
            "- `openSUSE Tumbleweed`: Does not contain the `calendar` command.\n" )

    # openSUSE Tumbleweed    ICEWM      No notifications.
    if _is_indicator(
        indicator,
        IndicatorName.INDICATORFORTUNE,
        IndicatorName.INDICATORLUNAR,
        IndicatorName.INDICATORONTHISDAY,
        IndicatorName.INDICATORPUNYCODE,
        IndicatorName.INDICATORSCRIPTRUNNER,
        IndicatorName.INDICATORTEST,
        IndicatorName.INDICATORTIDE,
        IndicatorName.INDICATORVIRTUALBOX ):
        messages.append(
            "- `ICEWM`: Notifications are unsupported.\n" )

    # Kubuntu 24.04     No autostart.
    messages.append(
        "- `Kubuntu 24.04`: No autostart.\n" )

    # Manjaro 24.04.7   No autostart.
    # As indicatoronthisday is unsupported on Manjaro (and openSUSE) as there
    # is no calendar package, only flag that that autostart does not work for
    # all the indicators other than indicatoronthisday.
    if not _is_indicator(
        indicator,
        IndicatorName.INDICATORONTHISDAY ):
        messages.append(
            "- `Manjaro 24`: No autostart.\n" )

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


def create_readme(
    directory,
    indicator,
    indicator_human_readable,
    authors_emails,
    start_year ):

    Path( directory ).mkdir( parents = True, exist_ok = True )

    with open( Path( directory, "README.md" ), 'w', encoding = "utf-8" ) as f:
        f.write( _get_introduction( indicator ) )
        f.write( _get_install_uninstall( indicator ) )
        f.write( _get_usage( indicator, indicator_human_readable ) )
        f.write( _get_limitations( indicator ) )
        f.write( _get_install_uninstall( indicator, install = False ) )
        f.write( _get_license( authors_emails, start_year ) )
