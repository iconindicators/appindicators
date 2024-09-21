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
#
# References:
#   https://pygobject.gnome.org/getting_started.html
#   https://stackoverflow.com/questions/70508775/error-could-not-build-wheels-for-pycairo-which-is-required-to-install-pyprojec
#   https://stackoverflow.com/questions/60779139/trouble-installing-pycairo-any-suggestions-on-what-to-try-next


import datetime
import re

from enum import auto, Enum
from pathlib import Path


class Operating_System( Enum ):
    DEBIAN_11 = auto() 
    DEBIAN_12 = auto() 
    FEDORA_38 = auto()
    FEDORA_39 = auto()
    FEDORA_40 = auto()
    KUBUNTU_2204 = auto()
    KUBUNTU_2404 = auto()
    LINUX_MINT_CINNAMON_22 = auto()
    LUBUNTU_2204 = auto()
    LUBUNTU_2404 = auto()
    MANJARO_240X = auto()
    OPENSUSE_TUMBLEWEED = auto()
    UBUNTU_2004 = auto()
    UBUNTU_2204 = auto()
    UBUNTU_2404 = auto()
    UBUNTU_BUDGIE_2404 = auto()
    UBUNTU_MATE_2404 = auto()
    UBUNTU_UNITY_2204 = auto()
    UBUNTU_UNITY_2404 = auto()
    XUBUNTU_2404 = auto()


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


def _get_summary( operating_system ):
    summary = [ ]
    for operating_system_ in operating_system:
        human_readable_operating_system = ""
        for part in operating_system_.name.split( '_' ):
            if part.isnumeric():
                if len( part ) == 2:
                    human_readable_operating_system += ' ' + part

                elif len( part ) == 4:
                    human_readable_operating_system += ' ' + part[ 0 : 2 ] + '.' + part[ 2 : ]

                else:
                    print( f"UNHANDLED PART '{ part }' for OPERATING SYSTEM '{ operating_system_ }'" )

            else:
                if human_readable_operating_system.endswith( "Manjaro" ):
                    human_readable_operating_system += ' ' + part[ 0 : 2 ] + '.' + part[ 2 : 3 ] + '.' + part[ 3 ].lower()

                elif "MATE" == part:
                    human_readable_operating_system += ' ' + part # Keep capitalised.

                elif "OPENSUSE" == part:
                    human_readable_operating_system += ' ' + "openSUSE" # Keep partially capitalised.

                else:
                    human_readable_operating_system += ' ' + part.title()

        summary.append( human_readable_operating_system.strip() )

    return " | ".join( sorted( summary ) )


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
            comments = matches.group().split( "\"" )[ 1 ].replace( '\\n', ' ' )[ 0 : -1 ] # Remove \n and drop ending.
            comments = comments[ 0 ].lower() + comments[ 1 : ] # Lower case leading character.
            break

    introduction = (
        f"`{ indicator_name }` { comments } on "
        f"`Debian`, `Ubuntu`, `Fedora`" )

    # openSUSE Tumbleweed and Manjaro do not contain the package 'calendar' or equivalent.
    # When creating the README.md for indicatoronthisday, drop references to openSUSE/Manjaro.
    # Want to still have indicatortest for openSUSE/Manjaro!
    if not is_indicator( indicator_name, Indicator_Name.INDICATORONTHISDAY ):
        introduction += f", `openSUSE`, `Manjaro`"

    introduction += f" and theoretically, any platform which supports the `AyatanaAppIndicator3` / `AppIndicator3` library.\n\n"

    introduction += f"Other indicators in this series are:\n"
    for indicator in _get_indicator_names_sans_current( indicator_name ):
        introduction += f"- [{ indicator }](https://pypi.org/project/{ indicator })\n"

    introduction += '\n'

    return introduction


def _get_operating_system_dependencies_debian( operating_system, indicator_name ):
    dependencies = [
        "gir1.2-ayatanaappindicator3-0.1",
        "libcairo2-dev",
        "libgirepository1.0-dev",
        "python3-pip",
        "python3-venv" ]

    applicable_operating_systems = {
        Operating_System.DEBIAN_11,
        Operating_System.DEBIAN_12 }

    if operating_system.issubset( applicable_operating_systems ):
        dependencies.append( "gnome-shell-extension-appindicator" )

    if indicator_name == Indicator_Name.INDICATORFORTUNE:
        dependencies.append( "fortune-mod" )
        dependencies.append( "fortunes" )

    if indicator_name == Indicator_Name.INDICATORONTHISDAY:
        applicable_operating_systems = {
            Operating_System.DEBIAN_11,
            Operating_System.DEBIAN_12,
            Operating_System.KUBUNTU_2204,
            Operating_System.KUBUNTU_2404,
            Operating_System.LINUX_MINT_CINNAMON_22,
            Operating_System.LUBUNTU_2204,
            Operating_System.LUBUNTU_2404,
            Operating_System.UBUNTU_2204,
            Operating_System.UBUNTU_2404,
            Operating_System.UBUNTU_BUDGIE_2404,
            Operating_System.UBUNTU_MATE_2404,
            Operating_System.UBUNTU_UNITY_2204,
            Operating_System.UBUNTU_UNITY_2404,
            Operating_System.XUBUNTU_2404 }

        if operating_system.issubset( applicable_operating_systems ):
            dependencies.append( "calendar" )

    if indicator_name == Indicator_Name.INDICATORSCRIPTRUNNER:
        dependencies.append( "libnotify-bin" )
        dependencies.append( "pulseaudio-utils" )

    if indicator_name == Indicator_Name.INDICATORTEST:
        dependencies.append( "fortune-mod" )
        dependencies.append( "fortunes" )
        dependencies.append( "libnotify-bin" )
        dependencies.append( "pulseaudio-utils" )
        dependencies.append( "wmctrl" )

        applicable_operating_systems = {
            Operating_System.DEBIAN_11,
            Operating_System.DEBIAN_12,
            Operating_System.KUBUNTU_2204,
            Operating_System.KUBUNTU_2404,
            Operating_System.LINUX_MINT_CINNAMON_22,
            Operating_System.LUBUNTU_2204,
            Operating_System.LUBUNTU_2404,
            Operating_System.UBUNTU_2204,
            Operating_System.UBUNTU_2404,
            Operating_System.UBUNTU_BUDGIE_2404,
            Operating_System.UBUNTU_MATE_2404,
            Operating_System.UBUNTU_UNITY_2204,
            Operating_System.UBUNTU_UNITY_2404,
            Operating_System.XUBUNTU_2404 }

        if operating_system.issubset( applicable_operating_systems ):
            dependencies.append( "calendar" )

    if indicator_name == Indicator_Name.INDICATORVIRTUALBOX:
        dependencies.append( "wmctrl" )

    return ' '.join( sorted( dependencies ) )


def _get_operating_system_dependencies_fedora( operating_system, indicator_name ):
    dependencies = [
        "cairo-gobject-devel",
        "gcc",
        "gobject-introspection-devel",
        "libappindicator-gtk3",
        "python3-devel",
        "python3-pip" ]

    if indicator_name == Indicator_Name.INDICATORFORTUNE:
        dependencies.append( "fortune-mod" )

    if indicator_name == Indicator_Name.INDICATORONTHISDAY:
        dependencies.append( "calendar" )

    if indicator_name == Indicator_Name.INDICATORSCRIPTRUNNER:
        applicable_operating_systems = {
            Operating_System.FEDORA_39, 
            Operating_System.FEDORA_40 }

        if operating_system.issubset( applicable_operating_systems ):
            dependencies.append( "pulseaudio-utils" )

    if indicator_name == Indicator_Name.INDICATORTEST:
        dependencies.append( "calendar" )
        dependencies.append( "fortune-mod" )
        dependencies.append( "wmctrl" )

        applicable_operating_systems = {
            Operating_System.FEDORA_39, 
            Operating_System.FEDORA_40 }

        if operating_system.issubset( applicable_operating_systems ):
            dependencies.append( "pulseaudio-utils" )

    if indicator_name == Indicator_Name.INDICATORVIRTUALBOX:
        dependencies.append( "wmctrl" )

    return ' '.join( sorted( dependencies ) )


def _get_operating_system_dependencies_manjaro( operating_system, indicator_name ):
    dependencies = [
        "cairo",
        "gcc",
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
        "python3-devel",
        "typelib-1_0-AyatanaAppIndicator3-0_1" ]

    if indicator_name == Indicator_Name.INDICATORFORTUNE:
        dependencies.append( "fortune" )

    if indicator_name == Indicator_Name.INDICATORTEST:
        dependencies.append( "fortune" )

    return ' '.join( sorted( dependencies ) )


def _get_extension( operating_system ):
    extension = ''

    applicable_operating_systems = {
        Operating_System.DEBIAN_11,
        Operating_System.DEBIAN_12 }

    if operating_system.issubset( applicable_operating_systems ):
        extension = (
            f"For the `appindicator` extension to take effect, log out then log in "
            f"(or restart) and in a terminal run:"
            f"    `gnome-extensions enable ubuntu-appindicators@ubuntu.com`\n\n" )

    applicable_operating_systems = {
        Operating_System.FEDORA_38,
        Operating_System.FEDORA_39,
        Operating_System.KUBUNTU_2204,
        Operating_System.FEDORA_40,
        Operating_System.OPENSUSE_TUMBLEWEED }

    if operating_system.issubset( applicable_operating_systems ):
        extension = (
            f"Install the `GNOME Shell` `AppIndicator and KStatusNotifierItem Support` "
            f"[extension](https://extensions.gnome.org/extension/615/appindicator-support).\n\n" )

    return extension


def _get_installation_python_virtual_environment( indicator_name ):
    return (
        f"Install the indicator into a `Python` virtual environment:\n"
        f"    ```\n"
        f"    indicatorname={ indicator_name } && \\\n"
        f"    if [ ! -d $HOME/.local/venv_${{indicatorname}} ]; then python3 -m venv $HOME/.local/venv_${{indicatorname}}; fi && \\\n"
        f"    . $HOME/.local/venv_${{indicatorname}}/bin/activate && \\\n"
        f"    python3 -m pip install --upgrade --force-reinstall pip ${{indicatorname}} && \\\n"
        f"    deactivate && \\\n"
        f"    . $(ls -d $HOME/.local/venv_${{indicatorname}}/lib/python3.* | head -1)/site-packages/${{indicatorname}}/platform/linux/install.sh\n"
        f"    ```\n" )


def _get_installation_additional_python_modules( indicator_name ):
    message = ''

#TODO Perhaps remove the --upgrade from below?
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

    if indicator_name.upper() == Indicator_Name.INDICATORTIDE.name:
        message = (
            f"You will need to write a `Python` script to retrieve your tidal data.\n"
            f"As such, you may need to install additional `Python` modules to the virtual environment.\n"
            f"{ common }"
            f"    ```\n" )

    return message


def _get_installation_for_operating_system(
        operating_system,
        indicator_name,
        install_command,
        _get_operating_system_dependencies_function_name ):

    # openSUSE Tumbleweed and Manjaro do not contain the package 'calendar' or equivalent.
    # When creating the README.md for indicatoronthisday, drop references to openSUSE/Manjaro.
    os_has_no_calendar = \
        operating_system.issubset( {
            Operating_System.MANJARO_240X,
            Operating_System.OPENSUSE_TUMBLEWEED } )

    indicator_uses_calendar = \
        is_indicator(
            indicator_name,
            Indicator_Name.INDICATORONTHISDAY )

    if indicator_uses_calendar and os_has_no_calendar:
        dependencies = ''

    else:
        operating_system_packages = \
            _get_operating_system_dependencies_function_name(
                operating_system,
                Indicator_Name[ indicator_name.upper() ] )

        n = 1 # Dynamically number each section.

        # Reference on installing some of the operating system packages:
        #   https://stackoverflow.com/a/61164149/2156453
        #   https://pygobject.gnome.org/getting_started.html
        dependencies = (
            f"<details>"
            f"<summary><b>{ _get_summary( operating_system ) }</b></summary>\n\n"

            f"{ str( n ) }. Install operating system packages:\n\n"
            f"    ```\n"
            f"    { install_command } { operating_system_packages }\n"
            f"    ```\n\n" )

        n += 1

        extension = _get_extension( operating_system )
        if extension:
            dependencies += f"{ str( n ) }. { extension }"
            n += 1

        dependencies += f"{ str( n ) }. { _get_installation_python_virtual_environment( indicator_name ) }"
        n += 1

        if is_indicator( indicator_name, Indicator_Name.INDICATORSCRIPTRUNNER, Indicator_Name.INDICATORTIDE ):
            dependencies += f"{ str( n ) }. { _get_installation_additional_python_modules( indicator_name) }"

        dependencies += f"</details>\n\n"

    return dependencies


def _get_usage( indicator_name, indicator_name_human_readable ):
    # Remove the '™' from the human readable name VirtualBox™ below.
    return (
        f"Usage\n"
        f"-----\n\n"

        f"To run `{ indicator_name }`, press the `Super` key to show the applications overlay or similar "
        f"and type `{ indicator_name_human_readable.split( ' ', 1 )[ 1 ].lower().replace( '™', '' ) }` "
        f"into the search bar and the icon should be present for you to select.  "
        f"If the icon does not appear, or appears as generic, you may have to log out and log back in (or restart).\n\n"
        f"Alternatively, to run from the terminal:\n\n"
        f"```\n"
        f". $HOME/.local/venv_{ indicator_name }/bin/activate && \\\n"
        f"python3 $(ls -d $HOME/.local/venv_{ indicator_name }/lib/python3.* | head -1)/site-packages/{ indicator_name }/{ indicator_name }.py && \\\n"
        f"deactivate\n"
        f"```\n\n" )


def _get_limitations( indicator_name ):
    messages = [ ]

    if is_indicator(
        indicator_name,
        Indicator_Name.INDICATORPUNYCODE ):
        messages.append(
            f"- `Wayland`: Clipboard/Primary input and output function intermittently at best; effectively unsupported.\n" )

    if is_indicator(
        indicator_name,
        Indicator_Name.INDICATORFORTUNE,
        Indicator_Name.INDICATORONTHISDAY,
        Indicator_Name.INDICATORTEST ):
        messages.append(
            f"- `Wayland`: Clipboard copy/paste is unsupported.\n" )

    if is_indicator(
        indicator_name,
        Indicator_Name.INDICATORTEST,
        Indicator_Name.INDICATORVIRTUALBOX ):
        messages.append(
            f"- `Wayland`: The command `wmctrl` is unsupported.\n" )

    if is_indicator(
        indicator_name,
        Indicator_Name.INDICATORSTARDATE,
        Indicator_Name.INDICATORTEST,
        Indicator_Name.INDICATORVIRTUALBOX ):
        messages.append(
            f"- `KDE`: Mouse wheel scroll over icon is unsupported.\n" )
# Kubuntu 22.04  KDE   No mouse wheel scroll.            
# Kubuntu 24.04  KDE   No mouse wheel scroll.            
# Manjaro 24.0.7 KDE   No mouse wheel scroll.            

    if is_indicator(
        indicator_name,
        Indicator_Name.INDICATORLUNAR,
        Indicator_Name.INDICATORSCRIPTRUNNER,
        Indicator_Name.INDICATORSTARDATE,
        Indicator_Name.INDICATORTEST ):
        messages.append(
            f"- `KDE`  |  `X-Cinnamon`  |  `XFCE`: The icon label is unsupported; the icon tooltip is used in lieu.\n" )
        messages.append(
            f"- `LXQt`: The icon label is unsupported; icon tooltip shows the indicator filename (effectively unsupported).\n" )
        messages.append(
            f"- `ICEWM`: The icon label and icon tooltip are unsupported.\n" )
# Kubuntu 22.04          KDE         Tooltip in lieu of label.
# Kubuntu 24.04          KDE         Tooltip in lieu of label.
# Linux Mint 22          X-Cinnamon  Tooltip in lieu of label.
# Lubuntu 22.04          LXQt        No label; tooltip is indicator filename.
# Lubuntu 24.04          LXQt        No label; tooltip is indicator filename.
# Manjaro 24.0.7         KDE         Tooltip in lieu of label.
#### openSUSE Tumbleweed    ICEWM  No label/tooltip.
# Xubuntu 24.04          XFCE        Tooltip in lieu of label.

    if is_indicator(
        indicator_name,
        Indicator_Name.INDICATORLUNAR,
        Indicator_Name.INDICATORTEST ):
        messages.append(
            f"- `LXQt`: The icon cannot be changed once set.\n" )
        messages.append(
            f"- `X-Cinnamon`: The icon disappears when changed from that originally set, leaving a blank space.\n" )
# Linux Mint 22     X-Cinnamon  When icon is changed, it disappears.
# Lubuntu 22.04     LXQt        Cannot change the icon once initially set.
# Lubuntu 24.04     LXQt        Cannot change the icon once initially set.

    if is_indicator(
        indicator_name,
        Indicator_Name.INDICATORSCRIPTRUNNER,
        Indicator_Name.INDICATORTEST ):
        messages.append(
            f"- `LXQt`: Commands cannot be sent to `qterminal` with version < `1.2.0` as the "
            f"arguments are not [preserved](https://github.com/lxqt/qterminal/issues/335). "
            f"Install `gnome-terminal` as a workaround.\n" )
# Lubuntu 22.04     LXQt    Default terminal (qterminal) does not work.
# Lubuntu 24.04     LXQt    Default terminal (qterminal) all good.

    if is_indicator(
        indicator_name,
        Indicator_Name.INDICATORTEST ):
        messages.append(
            f"- `openSUSE Tumbleweed`: Does not contain the `calendar` command.\n" )
# openSUSE Tumbleweed does not have the `calendar` command. 

    if is_indicator(
        indicator_name,
        Indicator_Name.INDICATORFORTUNE,
        Indicator_Name.INDICATORLUNAR,
        Indicator_Name.INDICATORONTHISDAY,
        Indicator_Name.INDICATORPUNYCODE,
        Indicator_Name.INDICATORSCRIPTRUNNER,
        Indicator_Name.INDICATORTEST,
        Indicator_Name.INDICATORTIDE,
        Indicator_Name.INDICATORVIRTUALBOX ):
        messages.append(
            f"- `ICEWM`: Notifications are unsupported.\n" )
#### openSUSE Tumbleweed    ICEWM    No notifications.

    message = ""
    if messages:
        message = (
            f"Limitations\n"
            f"-----------\n\n"
            f"{ ''.join( sorted( messages, key = str.casefold ) ) }\n\n" )

    return message


def _get_uninstall_for_operating_system(
        operating_system,
        indicator_name,
        uninstall_command,
        _get_operating_system_dependencies_function_name ):

    # openSUSE Tumbleweed and Manjaro do not contain the package 'calendar' or equivalent.
    # When creating the README.md for indicatoronthisday, drop references to openSUSE/Manjaro.
    os_has_no_calendar = \
        operating_system.issubset( {
            Operating_System.MANJARO_240X,
            Operating_System.OPENSUSE_TUMBLEWEED } )

    indicator_uses_calendar = \
        is_indicator(
            indicator_name,
            Indicator_Name.INDICATORONTHISDAY )

    if indicator_uses_calendar and os_has_no_calendar:
        uninstall = ''

    else:
        uninstall = (
            f"<details>"
            f"<summary><b>{ _get_summary( operating_system ) }</b></summary>\n\n"

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


def _get_install_uninstall( indicator_name, install = True ):
    if install:
        function = _get_installation_for_operating_system
        command_debian = "sudo apt-get -y install"
        command_fedora = "sudo dnf -y install"
        title = \
            "Installation / Upgrading\n" + \
            "------------------------\n\n"

    else:
        function = _get_uninstall_for_operating_system
        command_debian = "sudo apt-get -y remove"
        command_fedora = "sudo dnf -y remove"
        title = \
            "Uninstall\n" + \
            "---------\n\n"

    return (
        title +

        function(
            {
                Operating_System.DEBIAN_11,
                Operating_System.DEBIAN_12 },
            indicator_name,
            command_debian,
            _get_operating_system_dependencies_debian ) +

        function(
            { Operating_System.FEDORA_38 },
            indicator_name,
            command_fedora,
            _get_operating_system_dependencies_fedora ) +

        function(
            {
                Operating_System.FEDORA_39,
                Operating_System.FEDORA_40 },
            indicator_name,
            command_fedora,
            _get_operating_system_dependencies_fedora ) +

        function(
            { Operating_System.MANJARO_240X },
            indicator_name,
            "sudo pacman -S --noconfirm" if install else "sudo pacman -R --noconfirm",
            _get_operating_system_dependencies_manjaro ) +

        function(
            { Operating_System.OPENSUSE_TUMBLEWEED },
            indicator_name,
            "sudo zypper install -y" if install else "sudo zypper remove -y",
            _get_operating_system_dependencies_opensuse ) +

        function(
            { Operating_System.UBUNTU_2004 },
            indicator_name,
            command_debian,
            _get_operating_system_dependencies_debian ) +

        function(
            {
                Operating_System.KUBUNTU_2204,
                Operating_System.KUBUNTU_2404,
                Operating_System.LINUX_MINT_CINNAMON_22,
                Operating_System.LUBUNTU_2204,
                Operating_System.LUBUNTU_2404,
                Operating_System.UBUNTU_2204,
                Operating_System.UBUNTU_2404,
                Operating_System.UBUNTU_BUDGIE_2404,
                Operating_System.UBUNTU_MATE_2404,
                Operating_System.UBUNTU_UNITY_2204,
                Operating_System.UBUNTU_UNITY_2404,
                Operating_System.XUBUNTU_2404 },
            indicator_name,
            command_debian,
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
        f.write( _get_install_uninstall( indicator_name ) )
        f.write( _get_usage( indicator_name, indicator_name_human_readable ) )
        f.write( _get_limitations( indicator_name ) )
        f.write( _get_install_uninstall( indicator_name, install = False ) )
        f.write( _get_license( authors_emails, start_year ) )
