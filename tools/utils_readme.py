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


#TODO Try again with Manjaro?


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


#TODO
#   Linux Mint Cinnamon 22 is same install as Ubuntu 24.04
#   Lubuntu 22.04 is same install as Ubuntu 22.04
#   Ubuntu Budgie 24.04 is same install as Ubuntu 24.04
#   Ubuntu MATE 24.04 is same install as Ubuntu 24.04
#   Ubuntu Unity 22.04 is same install as Ubuntu 22.04
#   Xubuntu 24.04 is same install as Ubuntu 24.04
#
# Given the above all share identical OS package and extension (no extension) text,
# do we really want a long list, or can we combine these into one?
#
# Thinking to split all OS into singles.
# Can then pass a tuple of OS which have a common install or extension
# along with a new function to allow for checking of an OS present in the tuple.
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
    OPENSUSE_TUMBLEWEED = auto()
    UBUNTU_2004 = auto()
    UBUNTU_2204 = auto()
    UBUNTU_2404 = auto()
    UBUNTU_BUDGIE_2404 = auto()
    UBUNTU_MATE_2404 = auto()
    UBUNTU_UNITY_2204 = auto()
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
                if "MATE" == part:
                    human_readable_operating_system += ' ' + part

                elif "OPENSUSE" == part:
                    human_readable_operating_system += ' ' + "openSUSE"

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

    # openSUSE Tumbleweed does not contain the package 'calendar' or equivalent.
    # When creating the README.md for indicatoronthisday, drop references to openSUSE.
    # Want to still have indicatortest for openSUSE!
    if not is_indicator( indicator_name, Indicator_Name.INDICATORONTHISDAY ):
        introduction += f", `openSUSE`"

    introduction += f" and theoretically, any platform which supports the `appindicator` library.\n\n"

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
            Operating_System.UBUNTU_2204,
            Operating_System.UBUNTU_2404,
            Operating_System.UBUNTU_BUDGIE_2404,
            Operating_System.UBUNTU_MATE_2404,
            Operating_System.UBUNTU_UNITY_2204,
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
            Operating_System.UBUNTU_2204,
            Operating_System.UBUNTU_2404,
            Operating_System.UBUNTU_BUDGIE_2404,
            Operating_System.UBUNTU_MATE_2404,
            Operating_System.UBUNTU_UNITY_2204,
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
#TODO See above command...
# Is it possible once the extension is installed via apt-get to call something
# which will refresh the list of extensions and so no need to log out/in?
#
# OR, maybe check again that with Debian 11 and Debian 12
# it is possible to instead use the browser extension.

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

    # openSUSE Tumbleweed does not contain the package 'calendar' or equivalent.
    # When creating the README.md for indicatoronthisday, drop references to openSUSE.
    os_has_no_calendar = operating_system.issubset( { Operating_System.OPENSUSE_TUMBLEWEED } )
    indicator_uses_calendar = is_indicator( indicator_name, Indicator_Name.INDICATORONTHISDAY )
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


#TODO Remove after some testing!
def _get_installation( indicator_name ):
    install_command_debian = "sudo apt-get -y install"
    install_command_fedora = "sudo dnf -y install"

    return (
        "Installation / Upgrading\n" +
        "------------------------\n\n" +

        _get_installation_for_operating_system(
            {
                Operating_System.DEBIAN_11,
                Operating_System.DEBIAN_12 },
            indicator_name,
            install_command_debian,
            _get_operating_system_dependencies_debian ) +

        _get_installation_for_operating_system(
            { Operating_System.FEDORA_38 },
            indicator_name,
            install_command_fedora,
            _get_operating_system_dependencies_fedora ) +

        _get_installation_for_operating_system(
            {
                Operating_System.FEDORA_39,
                Operating_System.FEDORA_40 },
            indicator_name,
            install_command_fedora,
            _get_operating_system_dependencies_fedora ) +

        _get_installation_for_operating_system(
            { Operating_System.OPENSUSE_TUMBLEWEED },
            indicator_name,
            "sudo zypper install -y",
            _get_operating_system_dependencies_opensuse ) +

        _get_installation_for_operating_system(
            { Operating_System.UBUNTU_2004 },
            indicator_name,
            install_command_debian,
            _get_operating_system_dependencies_debian ) +

        _get_installation_for_operating_system(
            {
                Operating_System.KUBUNTU_2204,
                Operating_System.KUBUNTU_2404,
                Operating_System.LINUX_MINT_CINNAMON_22,
                Operating_System.LUBUNTU_2204,
                Operating_System.UBUNTU_2204,
                Operating_System.UBUNTU_2404,
                Operating_System.UBUNTU_BUDGIE_2404,
                Operating_System.UBUNTU_MATE_2404,
                Operating_System.UBUNTU_UNITY_2204,
                Operating_System.XUBUNTU_2404 },
            indicator_name,
            install_command_debian,
            _get_operating_system_dependencies_debian ) )


def _get_usage( indicator_name, indicator_name_human_readable ):
    # Remove the '™' from the human readable name VirtualBox™ below.
    return (
        f"Usage\n"
        f"-----\n\n"

        f"To run `{ indicator_name }`, press the `Super` key to open the `Show Applications` overlay (or similar), "
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
#
#TODO Maybe remove the list of supported distirbutions as these are listed in the install?
# If so, rename this function to _get_limitations or _get_known_knowns or ...?
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
        uninstall_command,
        _get_operating_system_dependencies_function_name ):

    # openSUSE Tumbleweed does not contain the package 'calendar' or equivalent.
    # When creating the README.md for indicatoronthisday, drop references to openSUSE.
    os_has_no_calendar = operating_system.issubset( { Operating_System.OPENSUSE_TUMBLEWEED } )
    indicator_uses_calendar = is_indicator( indicator_name, Indicator_Name.INDICATORONTHISDAY )
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


#TODO Remove after some testing!
def _get_uninstall( indicator_name ):
    uninstall_command_debian = "sudo apt-get -y remove"
    uninstall_command_fedora = "sudo dnf -y remove"

    return (
        "Uninstall\n" +
        "---------\n\n" +

        _get_uninstall_for_operating_system(
            {
                Operating_System.DEBIAN_11,
                Operating_System.DEBIAN_12 },
            indicator_name,
            uninstall_command_debian,
            _get_operating_system_dependencies_debian ) +

        _get_uninstall_for_operating_system(
            { Operating_System.FEDORA_38 },
            indicator_name,
            uninstall_command_fedora,
            _get_operating_system_dependencies_fedora ) +

        _get_uninstall_for_operating_system(
            {
                Operating_System.FEDORA_39,
                Operating_System.FEDORA_40 },
            indicator_name,
            uninstall_command_fedora,
            _get_operating_system_dependencies_fedora ) +

        _get_uninstall_for_operating_system(
            { Operating_System.OPENSUSE_TUMBLEWEED },
            indicator_name,
            "sudo zypper remove -y",
            _get_operating_system_dependencies_opensuse ) +

        _get_uninstall_for_operating_system(
            { Operating_System.UBUNTU_2004 },
            indicator_name,
            uninstall_command_debian,
            _get_operating_system_dependencies_debian ) +

        _get_uninstall_for_operating_system(
            {
                Operating_System.KUBUNTU_2204,
                Operating_System.KUBUNTU_2404,
                Operating_System.LINUX_MINT_CINNAMON_22,
                Operating_System.LUBUNTU_2204,
                Operating_System.UBUNTU_2204,
                Operating_System.UBUNTU_2404,
                Operating_System.UBUNTU_BUDGIE_2404,
                Operating_System.UBUNTU_MATE_2404,
                Operating_System.UBUNTU_UNITY_2204,
                Operating_System.XUBUNTU_2404 },
            indicator_name,
            uninstall_command_debian,
            _get_operating_system_dependencies_debian ) )


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
                Operating_System.UBUNTU_2204,
                Operating_System.UBUNTU_2404,
                Operating_System.UBUNTU_BUDGIE_2404,
                Operating_System.UBUNTU_MATE_2404,
                Operating_System.UBUNTU_UNITY_2204,
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
        f.write( _get_distributions_supported( indicator_name ) )
        f.write( _get_install_uninstall( indicator_name, install = False ) )
        f.write( _get_license( authors_emails, start_year ) )
