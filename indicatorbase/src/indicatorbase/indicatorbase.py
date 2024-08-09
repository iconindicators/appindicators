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
Building wheels for collected packages: cryptography
  Building wheel for cryptography (pyproject.toml) ... error
  error: subprocess-exited-with-error
  
  × Building wheel for cryptography (pyproject.toml) did not run successfully.
  │ exit code: 1
  ╰─> [14 lines of output]
      Running `maturin pep517 build-wheel -i /home/bernard/Programming/Indicators/venv/bin/python3 --compatibility off`
      📦 Including license file "/tmp/pip-install-dyfea59q/cryptography_f4f404043e2242728e2abe7fa83fc3f5/LICENSE"
      📦 Including license file "/tmp/pip-install-dyfea59q/cryptography_f4f404043e2242728e2abe7fa83fc3f5/LICENSE.APACHE"
      📦 Including license file "/tmp/pip-install-dyfea59q/cryptography_f4f404043e2242728e2abe7fa83fc3f5/LICENSE.BSD"
      🍹 Building a mixed python/rust project
      🔗 Found pyo3 bindings with abi3 support for Python ≥ 3.7
      🐍 Not using a specific python interpreter
      📡 Using build options features, locked from pyproject.toml
      error: package `cryptography-key-parsing v0.1.0 (/tmp/pip-install-dyfea59q/cryptography_f4f404043e2242728e2abe7fa83fc3f5/src/rust/cryptography-key-parsing)` cannot be built because it requires rustc 1.65.0 or newer, while the currently active rustc version is 1.63.0
      
      💥 maturin failed
        Caused by: Failed to build a native library through cargo
        Caused by: Cargo build finished with "exit status: 101": `env -u CARGO PYO3_ENVIRONMENT_SIGNATURE="cpython-3.11-64bit" PYO3_PYTHON="/home/bernard/Programming/Indicators/venv/bin/python3" PYTHON_SYS_EXECUTABLE="/home/bernard/Programming/Indicators/venv/bin/python3" "cargo" "rustc" "--features" "pyo3/abi3-py37" "--message-format" "json-render-diagnostics" "--locked" "--manifest-path" "/tmp/pip-install-dyfea59q/cryptography_f4f404043e2242728e2abe7fa83fc3f5/src/rust/Cargo.toml" "--release" "--lib"`
      Error: command ['maturin', 'pep517', 'build-wheel', '-i', '/home/bernard/Programming/Indicators/venv/bin/python3', '--compatibility', 'off'] returned non-zero exit status 1
      [end of output]
  
  note: This error originates from a subprocess, and is likely not a problem with pip.
  ERROR: Failed building wheel for cryptography
Failed to build cryptography
ERROR: ERROR: Failed to build installable wheels for some pyproject.toml based projects (cryptography)
'''
#TODO The above error occurs on Debian 12 32 bit.
# I think 32 bit is no longer supported for the cryptography package.
# Have tried the install instructions (needed curl and then rust something to compile)
# but the rust thing would not work.
#
# So not sure if this is a show stopper.
#
# One thing to try is amend the installation.
# For whatever reason, twine is always installed, which pulls in cryptography.
# So could try to install without the --upgrade option and also specify
# an older version of twine and/or cryptography.
# Perhaps
#   pip install pip twine==5.0.0 cryptography==42.0.8
# Tried above and same error...now what?
#
# Despite the error the indicator actually runs.
# Is it possible to tell pip not install twine or ignore errors?
#
# Does NOT occur on Debian 12 64 bit...so looks to be a 32 bit issue.


#TODO Testing indicatortest on distros/desktops...
#
# Somehow clean this up and keep for posterity...maybe put into build_readme.py as a comment?
#
# Debian 11 - GNOME - No wmctrl, no clipboard.
#                   - Menu stuck on disabled after opening About/Preferences and clicking icon then ESCAPE.
#           - System X11 Default - Menu stuck on disabled after opening About/Preferences and clicking icon then ESCAPE.
#           - GNOME Classic - Menu stuck on disabled after opening About/Preferences and clicking icon then ESCAPE.
#           - GNOME on Xorg - Menu stuck on disabled after opening About/Preferences and clicking icon then ESCAPE.
#
# Debian 12 - GNOME - No wmctrl, no clipboard.
#                   - Menu stuck on disabled after opening About/Preferences and clicking icon then ESCAPE.
#           - GNOME Classic - No wmctrl, no clipboard.
#                           - Menu stuck on disabled after opening About/Preferences and clicking icon then ESCAPE.
#           - GNOME Classic on Xorg - Menu stuck on disabled after opening About/Preferences and clicking icon then ESCAPE.
#           - GNOME on Xorg - Menu stuck on disabled after opening About/Preferences and clicking icon then ESCAPE.
#
# Fedora 38 - GNOME - No wmctrl, no clipboard.
#                   - Menu stuck on disabled after opening About/Preferences and clicking icon then ESCAPE.
#           - GNOME Classic - No wmctrl, no clipboard.
#                           - Menu stuck on disabled after opening About/Preferences and clicking icon then ESCAPE.
#           - GNOME Classic on Xorg - Menu stuck on disabled after opening About/Preferences and clicking icon then ESCAPE.
#           - GNOME on Xorg - Menu stuck on disabled after opening About/Preferences and clicking icon then ESCAPE.
#
# Fedora 39 - GNOME - No wmctrl, no clipboard.
#                   - Menu stuck on disabled after opening About/Preferences and clicking icon then ESCAPE.
#           - GNOME Classic - No wmctrl, no clipboard.
#                           - Menu stuck on disabled after opening About/Preferences and clicking icon then ESCAPE.
#           - GNOME Classic on Xorg - Menu stuck on disabled after opening About/Preferences and clicking icon then ESCAPE.
#           - GNOME on Xorg - Menu stuck on disabled after opening About/Preferences and clicking icon then ESCAPE.
#
# Fedora 40 - GNOME - No wmctrl, no clipboard.
#           - GNOME Classic - No wmctrl, no clipboard.
#           - GNOME Classic on Xorg - All good.
#           - GNOME on Xorg - All good.
#
# Kubuntu 22.04 - Plasma (X11) - no mouse wheel scroll over icon.
# Kubuntu 22.04 - Ubuntu on Xorg - All good.
# Kubuntu 22.04 - Ubuntu - All good.
# Kubuntu 22.04 - Ubuntu on Wayland (Wayland) - No clipboard.     wmctrl WORKS!  I think because of konsole...so using 'wayland' as the session is not good enough.
# Kubuntu 22.04 - Ubuntu (Wayland) - No clipboard.
#
# Linux Mint 21 - Cinnamon (Default) - Tooltip in lieu of label.  No dynamic icon.
#               - Cinnamon (Software Rendering) - Tooltip in lieu of label.  No dynamic icon.
#               - Ubuntu - All good.
#               - Ubuntu on Wayland - No clipboard; no wmctrl; no notify-send/notification.    WHY no notify?
#
# Lubuntu 22.04 - Lubuntu - No label only tooltip which shows the source code name and cannot be changed.
#                         - Cannot change icon.
#                         - Hitting the qterminal problem, so cannot run commands.
#               - LXQt Desktop - No label only tooltip which shows the source code name and cannot be changed.
#                              - Cannot change icon.
#                              - Hitting the qterminal problem, so cannot run commands.
#               - Openbox - Will not boot.
#               - Ubuntu on Xorg - Hitting the qterminal problem, so cannot run commands.
#                                - notify-send does not work.
#               - Ubuntu - Hitting the qterminal problem, so cannot run commands.
#                        - notify-send does not work.
#               - Ubuntu on Wayland (Wayland) - Would not log in. 
#               - Ubuntu (Wayland) - Hitting the qterminal problem, so cannot run commands.
#                                  - notify-send does not work.
#
# Manjaro 22.1 Talos - GNOME - All good.
#                    - GNOME Classic - All good.
# Manjaro 22.1 is already obsolete.  Try perhaps 24.0.0 Wynsdey?
#
# Ubuntu 20.04 - Ubuntu - All good.
# Ubuntu 20.04 - GNOME Classic - Need to Run "Applications - Utilities - Tweaks: Extensions: Enable  Ubuntu appindicators.
# Ubuntu 20.04 - Ubuntu on Wayland - No clipboard; no wmctrl.
#
# openSUSE Tumbleweed - GNOME - No wmctrl, no clipboard.
#                     - GNOME Classic - No wmctrl, no clipboard.
#                     - GNOME Classic on Xorg - All good.
#                     - GNOME on Xorg - No wmctrl, no clipboard.
#                     - IceWM Session - No label/tooltip.  No notify-send / OSD.
#
# Ubuntu 22.04 - Ubuntu - no wmctrl, no clipboard.
# Ubuntu 22.04 - Ubuntu on Xorg - All good.
#
# Ubuntu 24.04 - Ubuntu on Xorg - Fails to log in.  Test from a live USB?  How to install the indicator/packages?
# Ubuntu 24.04 - Ubuntu - no wmctrl, no clipboard.
#                       - Menu stuck on disabled after opening About/Preferences and clicking icon then ESCAPE.
#
# Ubuntu Budgie 22.04 - Budgie Desktop (Default) - All good.
#                     - Ubuntu - All good.
#                     - Ubuntu on Wayland - No clipboard; no wmctrl.
#                     - Ubuntu on Xorg - All good. 
#
# Ubuntu MATE 22.04 - MATE - All good.
#                   - Ubuntu (Default) - All good.
#                   - Ubuntu on Wayland - No clipboard; no wmctrl.
#                   - Ubuntu on Xorg - All good.
#
# Ubuntu Unity 22.04 - Unity (Default) - All good.
#                    - Ubuntu - All good.
#                    - Ubuntu on Wayland - No notify-send. No clipboard; no wmctrl.
#                    - Ubuntu on Xorg - All good.
#
# Xubuntu 22.04 - - No mouse wheel scroll; tooltip in lieu of label.


#TODO There are newer versions of distros to be tested.


#TODO Check the flow of code,
# from init to update loops,
# to about/preferences,
# to interupting an update (if possible or should be allowed),
# to stopping an update and then kicking off later.
#
# When About/Preferences is showing,
# is it possible to click anything else in the indicator menu?
# 
# Seems okay on Ubuntu 20.04.
# Check Debian 12, Febora 39, Fedora 40 and Ubuntu 24.04.
#
# If an update is underway, is it possible for the user to select About/Prefs?
# Hopefully not as the menu should be disabled during the update.
# All good on Ubuntu 20.04...what about Debian et al?


#TODO Run any indicator under Debian 12 and open About dialog.
# Click on the icon and display the menu, the About/Preferences/Quit items are greyed out.
# Clicking the red X on the About dialog (or hitting the escape key)
# closes the dialog but the About/Preferences/Quit items remain greyed out.
# Does not occur on Ubuntu 20.04 / 22.04 / 24.04 et al and NOT on Fedora 40.
# Occurs on Debian 11 on all graphics variants;
# Debian 12 on GNOME, presumably all other graphics variants;
# Fedora 38 / 39; Manjaro 22.1; openSUSE Tumbleweed.
# Happens on Ubuntu 24.04 (Ubuntu session default).  Cannot test on Ubuntu 24.04 Xorg session as it won't boot.
# Check on other distros.
#
# Double check Manjaro 22.1; openSUSE Tumbleweed.
#
# THis also happens on Debian 12 under Xorg.
#
# By doing an update (after the Preferences/About are closed)
#
#    self.request_update()
#
# (and probably only do this "if responseType != Gtk.ResponseType.OK" because when OK
# an update is kicked off any way)
#
# gets around the Debian/Fedora issue when clicking
# the icon when the About/Preferences are open.
# Is this viable...perhaps only do it for Debian 11 / 12 and Fedora 38 / 39?
#
# Maybe call self.set_menu_sensitivity( True ) in a thread 1 sec later? 
#
# Does this issue happen under Debian/Fedora under xorg (rather than default wayland)?
#
# If this is something that only occurs with a range of GTK release versions
# (between Debian 11 and Fedora 39)
# then can we check for that and onl do the update on those?


#TODO Update the PPA description at
#   https://launchpad.net/~thebernmeister/+archive/ubuntu/ppa
# with the following:
#
# This PPA no longer provides releases for indicators.
# Instead, for Ubuntu 20.04 and forward, all releases are made via pip (PyPI).
# 
# Refer to the new URL for each indicator:
# 
# indicator-fortune: https://pypi.org/project/indicatorfortune
# indicator-lunar: https://pypi.org/project/indicatorlunar
# indicator-on-this-day: https://pypi.org/project/indicatoronthisday
# indicator-ppa-download-statistics: https://pypi.org/project/indicatorppadownloadstatistics
# indicator-punycode: https://pypi.org/project/indicatorpunycode
# indicator-script-runner: https://pypi.org/project/indicatorscriptrunner
# indicator-stardate: https://pypi.org/project/indicatorstardate
# indicator-test: https://pypi.org/project/indicatortest
# indicator-tide: https://pypi.org/project/indicatortide
# indicator-virtual-box: https://pypi.org/project/indicatorvirtualbox
# 
# Screenshots for the indicators can be found at https://askubuntu.com/q/30334/67335


#TODO For each indicator at 
#   https://askubuntu.com/questions/30334/what-application-indicators-are-available?answertab=modifieddes
# update the URL at the top with the relevant URL at PyPI.
#
#   https://pypi.org/project/indicatorfortune/
#   https://pypi.org/project/indicatorlunar/
#   https://pypi.org/project/indicatoronthisday/
#   https://pypi.org/project/indicatorppadownloadstatistics/
#   https://pypi.org/project/indicatorpunycode/
#   https://pypi.org/project/indicatorscriptrunner/
#   https://pypi.org/project/indicatorstardate/
#   https://pypi.org/project/indicatortide/
#   https://pypi.org/project/indicatorvirtualbox/


#TODO Is it feasible for an indicator to check, say weekly,
# if there is an update available at its respective PyPI page?
# Can we use 'pip list -o' or something via pip to do the check?
#
# Could use either a list of outdated or uptodate packages:
# https://pip.pypa.io/en/stable/cli/pip_list/
# (see other formatting options too)
#
#	. $HOME/.local/venv_indicatortest/bin/activate && python3 -m pip list -o && deactivate
#	Package    Version Latest Type
#	---------- ------- ------ -----
#	setuptools 44.0.0  69.5.1 wheel
#
#	. $HOME/.local/venv_indicatortest/bin/activate && python3 -m pip list -u && deactivate
#	Package       Version
#	------------- -------
#	indicatortest 1.0.16
#	pip           24.0
#	pycairo       1.26.0
#	PyGObject     3.48.2


# Base class for application indicators.
#
# References:
#   https://lazka.github.io/pgi-docs/AyatanaAppIndicator3-0.1
#   https://github.com/AyatanaIndicators/libayatana-appindicator
#   https://wiki.ayatana-indicators.org/AyatanaIndicatorApplication
#   https://wiki.ubuntu.com/DesktopExperienceTeam/ApplicationIndicators
#   https://askubuntu.com/questions/108035/writing-indicators-with-python-gir-and-gtk3
#   https://python-gtk-3-tutorial.readthedocs.org
#   https://pygobject.gnome.org/guide/threading.html
#   https://stackoverflow.com/q/73665239/2156453
#   https://wiki.ubuntu.com/NotifyOSD
#   https://lazka.github.io/pgi-docs/Gtk-3.0
#   https://pygobject.readthedocs.io/en/latest/getting_started.html
#   https://twine.readthedocs.io/en/latest/
#   https://packaging.python.org/en/latest/tutorials/packaging-projects/
#   https://specifications.freedesktop.org/icon-theme-spec/icon-theme-spec-latest.html
#   https://pypi.org/project/pystray/
#
# Python naming standards:
#   https://peps.python.org/pep-0008/
#   https://docs.python-guide.org/writing/style/
#   https://guicommits.com/organize-python-code-like-a-pro/


import datetime
import email.policy
import gettext
import gi
import inspect
import json
import logging.handlers
import pickle
import shutil
import signal
import subprocess
import sys
import webbrowser

from abc import ABC
from bisect import bisect_right

try:
    gi.require_version( "AyatanaAppIndicator3", "0.1" )
    from gi.repository import AyatanaAppIndicator3 as AppIndicator
except:
    try:
        gi.require_version( "AppIndicator3", "0.1" )
        from gi.repository import AppIndicator3 as AppIndicator # Needed for Fedora.
    except:
        print( "Unable to find either AyatanaAppIndicator3 nor AppIndicator3.")
        sys.exit( 1 )

gi.require_version( "Gdk", "3.0" )
from gi.repository import Gdk

gi.require_version( "GLib", "2.0" )
from gi.repository import GLib

gi.require_version( "Gtk", "3.0" )
from gi.repository import Gtk

try:
    gi.require_version( "Notify", "0.7" )
except ValueError:
    gi.require_version( "Notify", "0.8" )
from gi.repository import Notify

from importlib import metadata
from pathlib import Path
from threading import Lock
from urllib.request import urlopen
from zipfile import ZipFile


class IndicatorBase( ABC ):

    _AUTOSTART_PATH = Path.home() / ".config" / "autostart"

    _CACHE_DATE_TIME_FORMAT_YYYYMMDDHHMMSS = "%Y%m%d%H%M%S"

    _CONFIG_VERSION = "version"

    # Values are the result of calling
    #   echo $XDG_CURRENT_DESKTOP
    #
    # An alternative (with different results) is calling
    #   os.environ.get( "DESKTOP_SESSION" )
    # which gives 'plasma' rather than 'KDE' on 'Plasma (X11)' on Kubuntu.
    _CURRENT_DESKTOP_BUDGIE_GNOME = "Budgie:GNOME"
    _CURRENT_DESKTOP_ICEWM = "ICEWM"
    _CURRENT_DESKTOP_KDE = "KDE"
    _CURRENT_DESKTOP_LXQT = "LXQt"
    _CURRENT_DESKTOP_MATE = "MATE"
    _CURRENT_DESKTOP_UNITY7 = "Unity:Unity7:ubuntu"
    _CURRENT_DESKTOP_X_CINNAMON = "X-Cinnamon"
    _CURRENT_DESKTOP_XFCE = "XFCE"

    _EXTENSION_JSON = ".json"

#TODO Check all terminals on all supported distros.
    _TERMINALS_AND_EXECUTION_FLAGS = [ [ "gnome-terminal", "--" ] ] # ALWAYS list first so as to be the "default".
    _TERMINALS_AND_EXECUTION_FLAGS.extend( [
        [ "konsole", "-e" ],
        [ "lxterminal", "-e" ],
        [ "mate-terminal", "-x" ],
        [ "qterminal", "-e" ],
        [ "tilix", "-e" ],
        [ "xfce4-terminal", "-x" ] ] )

    _UPDATE_PERIOD_IN_SECONDS_DEFAULT = 60

    _X_GNOME_AUTOSTART_ENABLED = "X-GNOME-Autostart-enabled"
    _X_GNOME_AUTOSTART_DELAY = "X-GNOME-Autostart-Delay"

    DIALOG_DEFAULT_HEIGHT = 480
    DIALOG_DEFAULT_WIDTH = 640

    EXTENSION_SVG = ".svg"
    EXTENSION_SVG_SYMBOLIC = "-symbolic.svg"
    EXTENSION_TEXT = ".txt"

    INDENT_WIDGET_LEFT = 25

    # Obtain name of indicator from the call stack and initialise gettext.
    # For a given indicator, indicatorbase MUST be imported FIRST!
    INDICATOR_NAME = None
    for frame_record in inspect.stack():
        found_indicatorbase_import = \
            "from indicatorbase import IndicatorBase" in str( frame_record.code_context ) and \
            Path( frame_record.filename ).stem.startswith( "indicator" )

        if found_indicatorbase_import:
            INDICATOR_NAME = Path( frame_record.filename ).stem

            if INDICATOR_NAME == Path( __file__ ).parent.stem: # Running installed under a virtual environment.
                locale_directory = Path( __file__ ).parent / "locale"

            else:
                # Running in development.
                locale_directory = \
                    Path( __file__ ).parent.parent.parent.parent / INDICATOR_NAME / "src" / INDICATOR_NAME / "locale"

            gettext.install( INDICATOR_NAME, localedir = locale_directory )
            break

    # Commands such as wmctrl do not function under wayland.
    # Need a way to determine whether running under wayland (or say x11).
    # Values are the result of calling
    #   echo $XDG_SESSION_TYPE
    SESSION_TYPE_WAYLAND = "wayland"
    SESSION_TYPE_X11 = "x11"

    URL_TIMEOUT_IN_SECONDS = 20


    # The comments argument is used in two places:
    #
    #   1) The first letter of the comments is capitalised and incorporated
    #      into the Project Description on the PyPI page.
    #
    #   2) The comments is used, as is, in the About dialog.
    def __init__( self, comments, artwork = None, creditz = None, debug = False ):
        if IndicatorBase.INDICATOR_NAME is None:
            self.show_dialog_ok(
                None,
                "Unable to determine indicator name!",
                title = "ERROR",
                message_type = Gtk.MessageType.ERROR )

            sys.exit( 1 )

        self.indicator_name = IndicatorBase.INDICATOR_NAME

        project_metadata, error_message = IndicatorBase.get_project_metadata( self.indicator_name )
        if error_message:
            self.show_dialog_ok(
                None,
                error_message,
                title = self.indicator_name,
                message_type = Gtk.MessageType.ERROR )

            sys.exit( 1 )

        error_message = self._initialise_desktop_file()
        if error_message:
            self.show_dialog_ok(
                None,
                error_message,
                title = self.indicator_name,
                message_type = Gtk.MessageType.ERROR )

            sys.exit( 1 )

        self.comments = comments
        self.artwork = artwork
        self.creditz = creditz
        self.debug = debug

        self.current_desktop = self.process_get( "echo $XDG_CURRENT_DESKTOP" )
        print( "echo $XDG_CURRENT_DESKTOP = " + self.current_desktop )#TODO Test

        self.authors_and_emails = self.get_authors_emails( project_metadata )
        self.version = project_metadata[ "Version" ]
        self.website = project_metadata.get_all( "Project-URL" )[ 0 ].split( ',' )[ 1 ].strip()

        self.log = Path.home() / ( self.indicator_name + ".log" )
        logging.basicConfig(
            format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            level = logging.DEBUG,
            handlers = [ TruncatedFileHandler( self.log ) ] )

        self.lock = Lock()
        self.id = 0 # ID returned when scheduling an update.

        self.lock_update = Lock()
        self.id_update = 0 # ID returned when scheduling an update.

        self.lock_save_config = Lock()
        self.id_save_config = 0 # ID returned when scheduling a config save.

        signal.signal( signal.SIGINT, signal.SIG_DFL ) # Responds to CTRL+C when running from terminal.

        Notify.init( self.indicator_name )

        self.indicator = \
            AppIndicator.Indicator.new(
                self.indicator_name, # ID
                self.get_icon_name(), # Icon name
                AppIndicator.IndicatorCategory.APPLICATION_STATUS )

        self.indicator.set_status( AppIndicator.IndicatorStatus.ACTIVE )

        menu = Gtk.Menu()
        self.create_and_append_menuitem( menu, _( "Initialising..." ) )
        menu.show_all()
        self.indicator.set_menu( menu )

        self._load_config()


    @staticmethod
    def _get_path_to_wheel_in_release( indicator_name ):
        path_release = Path( __file__ ).parent.parent.parent.parent
        path_wheel = path_release / "release" / "wheel" / f"dist_{ indicator_name }"
        return path_wheel


    @staticmethod
    def get_project_metadata( indicator_name ):
        # https://stackoverflow.com/questions/75801738/importlib-metadata-doesnt-appear-to-handle-the-authors-field-from-a-pyproject-t
        # https://stackoverflow.com/questions/76143042/is-there-an-interface-to-access-pyproject-toml-from-python
        try:
            # Obtain pyproject.toml information from pip.
            project_metadata = metadata.metadata( indicator_name )
            error_message = None

        except metadata.PackageNotFoundError:
            # No pip information found; assume in development/testing.
            # Look for a .whl file in the release folder.
            path_wheel = IndicatorBase._get_path_to_wheel_in_release( indicator_name )
            first_wheel = next( path_wheel.glob( "*.whl" ), None )
            if first_wheel is None:
                project_metadata = None
                error_message = f"Unable to locate a .whl in { path_wheel.absolute() }"

            else:
                first_metadata = next( metadata.distributions( path = [ first_wheel ] ), None )
                if first_metadata is None:
                    project_metadata = None
                    error_message = f"No metadata was found in { first_wheel.absolute() }!"

                else:
                    project_metadata = first_metadata.metadata
                    error_message = None

        return project_metadata, error_message


    def _initialise_desktop_file( self ):
        self.desktop_file = self.indicator_name + ".py.desktop"
        self.desktop_file_user_home = IndicatorBase._AUTOSTART_PATH / self.desktop_file

        # This resolves to the .desktop in the virtual environment
        # when running within virtual environment.
        #
        # If running in development, this resolves to a file in
        # indicatorbase which does not exist.
        # To ensure Preferences work under development, extract
        # the .desktop file from the indicator's .whl to /tmp.
        self.desktop_file_virtual_environment = \
            Path( __file__ ).parent / "platform" / "linux" / self.desktop_file

        error_message = None
        if not self.desktop_file_virtual_environment.exists():
            path_wheel = IndicatorBase._get_path_to_wheel_in_release( self.indicator_name )
            first_wheel = next( path_wheel.glob( "*.whl" ), None )
            if first_wheel is None:
                error_message = f"Unable to locate a .whl in { path_wheel.absolute() }"

            else:
                with ZipFile( first_wheel, 'r' ) as z:
                    desktop_file_in_wheel = \
                        self.indicator_name + \
                        "/platform/linux/" + \
                        self.desktop_file

                    if desktop_file_in_wheel not in z.namelist():
                        error_message = \
                            f"Unable to locate { desktop_file_in_wheel } in { first_wheel.absolute() }."

                    else:
                        z.extract( desktop_file_in_wheel, path = "/tmp" )
                        self.desktop_file_virtual_environment = Path( "/tmp" ) / desktop_file_in_wheel
                        if not self.desktop_file_virtual_environment.exists():
                            error_message = f"Unable to locate { self.desktop_file_virtual_environment }!"

                z.close()

        return error_message


    @staticmethod
    def get_authors_emails( project_metadata ):
        # https://stackoverflow.com/a/75803208/2156453
        email_message_object = \
            email.message_from_string(
                f'To: { project_metadata[ "Author-email" ] }',
                policy = email.policy.default, )

        authors_emails = [ ]
        for address in email_message_object[ "to" ].addresses:
            authors_emails.append( [ address.display_name, address.addr_spec ] )

        return authors_emails


    @staticmethod
    def get_year_in_changelog_markdown( changelog_markdown, first_year = True ):
        '''
        If first_year = True, retrieves the first/earliest year from CHANGELOG.md
        otherwise retrieves the most recent year.
        '''
        year = ""
        with open( changelog_markdown, 'r' ) as f:
            lines = f.readlines()
            if first_year:
                lines = reversed( lines )

            for line in lines:
                if line.startswith( "## v" ):
                    left_parenthesis = line.find( '(' )
                    year = line[ left_parenthesis + 1 : left_parenthesis + 1 + 4 ]
                    break

        return year


    @staticmethod
    def get_changelog_markdown_path():
        changelog = Path( __file__ ).parent / "CHANGELOG.md" # Path under virtual environment.
        if not Path( changelog ).exists():
            changelog = Path( '.' ).absolute() / "CHANGELOG.md" # Assume running in development.

        return changelog


    def main( self ):
        self.request_update()
        Gtk.main()


    # The typical flow of events is:
    #   Indicator starts up and kicks off an initial update.
    #
    #   Subsequent updates are scheduled either by:
    #       The indicator returning the amount of seconds from
    #       now until the next update needs to occur.
    #
    #       The user clicks OK in the Preferences.
    #
    #       An indicator experiences and event and requests an update
    #       (for example starting a virtual machine will request an
    #       update to refresh the menu).
    #
    #   If there is a pending (future) update and a request for an update
    #   comes along, need to remove the "old" pending update (referred as self.id).
    def request_update( self, delay = 1 ):
        if self.lock_update.acquire( blocking = False ):
            if self.id_update > 0:
                GLib.source_remove( self.id_update )

            self.id_update = GLib.timeout_add_seconds( delay, self._update )
            self.lock_update.release()

        else:
            self.request_update( IndicatorBase._UPDATE_PERIOD_IN_SECONDS_DEFAULT )


    def _update( self ):
        update_start = datetime.datetime.now()

        self.set_menu_sensitivity( False ) # Menu will be rebuilt as part of the update, so no need to set back to True.

        # The user can nominate any menuitem as a secondary activate target during menu construction.
        # However the secondary activate target can only be set once the menu is built.
        # Therefore, keep a variable for the user to set as needed.
        # Then set the secondary activate target once the menu is built/shown.
        self.secondary_activate_target = None

        menu = Gtk.Menu()
        next_update_in_seconds = self.update( menu ) # Call to implementation in indicator.

        if self.is_debug():
            menu_has_children = len( menu.get_children() ) > 0

            menu.prepend( Gtk.SeparatorMenuItem() )

            if next_update_in_seconds:
                next_update_date_time = datetime.datetime.now() + datetime.timedelta( seconds = next_update_in_seconds )
                label = "Next update: " + str( next_update_date_time ).split( '.' )[ 0 ]
                menu.prepend( Gtk.MenuItem.new_with_label( label ) )

            label = "Time to update: " + str( datetime.datetime.now() - update_start )
            menu.prepend( Gtk.MenuItem.new_with_label( label ) )

            if menu_has_children:
                menu.append( Gtk.SeparatorMenuItem() )

        else:
            if len( menu.get_children() ) > 0:
                menu.append( Gtk.SeparatorMenuItem() )

        titles = ( _( "Preferences" ), _( "About" ), _( "Quit" ) )
        functions = ( self._on_preferences, self._on_about, Gtk.main_quit )
        for title, function in zip( titles, functions ):
            self.create_and_append_menuitem( menu, title, activate_functionandarguments = ( function, ) )

        self.indicator.set_menu( menu )
        menu.show_all()

        self.indicator.set_secondary_activate_target( self.secondary_activate_target )

        self.id_update = 0
        if next_update_in_seconds: # Some indicators don't return a next update time.
            self.request_update( next_update_in_seconds )

        return False


    def set_label( self, text ):
        label_set = False
        if self._is_label_update_supported():
            self.indicator.set_label( text, text )
            self.indicator.set_title( text ) # Needed for Lubuntu/Xubuntu.  #TODO Check this comment.
            label_set = True

        return label_set


    def set_icon( self, icon ):
        icon_set = False
        if self._is_icon_update_supported():
            self.indicator.set_icon_full( icon, "" )
            icon_set = True

        return icon_set


    # Get the name of the icon for the indicator
    # to be passed to the desktop environment for display.
    #
    # GTK will take an icon and display it as expected.
    #
    # The exception is if the icon filename ends with "-symbolic" (before the extension).
    # In this case, GTK will take the colour in the icon (say a generic flat #777777)
    # and replace it with a suitable colour to make the current theme/background/colour.
    # Refer to this discussion:
    #   https://discourse.gnome.org/t/what-colour-to-use-for-a-custom-adwaita-icon/19064
    #
    # If the icon with "-symbolic" cannot be found, it appears the desktop environment as
    # a fallback will look for the icon name without the "-symbolic" which is the hicolor.
    #
    # When updating/replacing an icon, the desktop environment appears to cache.
    # So perhaps first try:
    #   sudo touch $HOME/.local/share/icons/hicolor && sudo gtk-update-icon-cache
    # and if that fails, either log out/in or restart.
    def get_icon_name( self ):
        return self.indicator_name + "-symbolic"


    def is_debug( self ):
        return self.debug


    def show_notification( self, summary, message, icon = None ):
        _icon = icon
        if icon is None:
            _icon = self.get_icon_name()

        Notify.Notification.new( summary, message, _icon ).show()


    def set_secondary_activate_target( self, menuitem ):
        self.secondary_activate_target = menuitem


    # Registers a function (and arguments) to be called on mouse wheel scroll.
    #
    # The function must have the form:
    #
    #   def on_mouse_wheel_scroll( self, indicator, delta, scroll_direction )
    #
    # The name of the function may be any name.
    # The arguments must be present as specified.
    # Additional arguments may be specified.
    def request_mouse_wheel_scroll_events( self, functionandarguments ):
        self.indicator.connect(
            "scroll-event",
            self._on_mouse_wheel_scroll,
            functionandarguments )


    def _on_mouse_wheel_scroll(
            self,
            indicator,
            delta,
            scroll_direction,
            functionandarguments ):

        if self.indicator.get_menu().get_children()[ 0 ].get_sensitive(): # Disable during update/Preferences/About
            if len( functionandarguments ) == 1:
                functionandarguments[ 0 ]( indicator, delta, scroll_direction )

            else:
                functionandarguments[ 0 ]( indicator, delta, scroll_direction, *functionandarguments[ 1 : ] )


    def _on_about( self, menuitem ):
        self.set_menu_sensitivity( False )
        self.indicator.set_secondary_activate_target( None )

        about_dialog = Gtk.AboutDialog()
        about_dialog.set_transient_for( menuitem.get_parent().get_parent() )

        authors_and_websites = [ ]
        for author_and_email in self.authors_and_emails:
            authors_and_websites.append( author_and_email[ 0 ] + " " + self.website )

        about_dialog.set_authors( authors_and_websites )
        about_dialog.set_artists( self.artwork if self.artwork else authors_and_websites )

        about_dialog.set_comments( self.comments )

        changelog_markdown_path = IndicatorBase.get_changelog_markdown_path()

        authors = [ author_and_email[ 0 ] for author_and_email in self.authors_and_emails ]
        about_dialog.set_copyright(
            "Copyright \xa9 " + \
            IndicatorBase.get_year_in_changelog_markdown( changelog_markdown_path ) + \
            '-' + str( datetime.datetime.now().year ) + " " + \
            ' '.join( authors ) )

        about_dialog.set_license_type( Gtk.License.GPL_3_0 )
        about_dialog.set_logo_icon_name( self.get_icon_name() )
        about_dialog.set_program_name( self.indicator_name )
        about_dialog.set_translator_credits( _( "translator-credits" ) )
        about_dialog.set_version( self.version )
        about_dialog.set_website( self.website )
        about_dialog.set_website_label( self.website )

        if self.creditz:
            about_dialog.add_credit_section( _( "Credits" ), self.creditz )

        self._add_hyperlink_label(
            about_dialog,
            changelog_markdown_path,
            _( "View the" ),
            _( "changelog" ),
            _( "text file." ) )

        error_log = Path.home() / ( self.indicator_name + ".log" )
        if error_log.is_file():
            self._add_hyperlink_label(
                about_dialog,
                error_log,
                _( "View the" ),
                _( "error log" ),
                _( "text file." ) )

        about_dialog.run()
        about_dialog.destroy()

        self.set_menu_sensitivity( True )
        self.indicator.set_secondary_activate_target( self.secondary_activate_target )


    def _add_hyperlink_label(
            self,
            about_dialog,
            file_path,
            left_text,
            anchor_text,
            right_text ):

        tooltip = "file://" + str( file_path )
        markup = \
            left_text + \
            " <a href=\'" + "file://" + str( file_path ) + "\' title=\'" + tooltip + "\'>" + \
            anchor_text + "</a> " + \
            right_text

        label = Gtk.Label()
        label.set_markup( markup )
        label.show()
        about_dialog.get_content_area().get_children()[ 0 ].get_children()[ 2 ].get_children()[ 0 ].pack_start( label, False, False, 0 )


    def _on_preferences( self, menuitem ):
        self.set_menu_sensitivity( False )
        self.indicator.set_secondary_activate_target( None )

        dialog = self.create_dialog( menuitem, _( "Preferences" ) )
        response_type = self.on_preferences( dialog ) # Call to implementation in indicator.
        dialog.destroy()

        if response_type == Gtk.ResponseType.OK:
            self.request_save_config()
            self.request_update( 1 ) # Allow one second for the lock to release so the update will proceed.

        self.set_menu_sensitivity( True )
        self.indicator.set_secondary_activate_target( self.secondary_activate_target )


    def set_menu_sensitivity( self, toggle ):
        menuitems = self.indicator.get_menu().get_children()
        if len( menuitems ) > 1: # On the first update, the menu only contains the "initialising" menu item, so ignore.
            for menuitem in self.indicator.get_menu().get_children():
                menuitem.set_sensitive( toggle )


    # Copy text to clipboard or primary.
    def copy_to_selection( self, text, is_primary = False ):
        selection = Gdk.SELECTION_CLIPBOARD
        if is_primary:
            selection = Gdk.SELECTION_PRIMARY

        Gtk.Clipboard.get( selection ).set_text( text, -1 )


    def copy_from_selection_clipboard( self ):
        return Gtk.Clipboard.get( Gdk.SELECTION_CLIPBOARD ).wait_for_text()


    def copy_from_selection_primary( self, clipboard_text_received_functionandarguments ):
        Gtk.Clipboard.get( Gdk.SELECTION_PRIMARY ).request_text(
            *clipboard_text_received_functionandarguments )


    def create_dialog(
            self,
            parent_widget,
            title,
            content_widget = None,
            buttons_responsetypes = ( Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK ),
            default_size = None ):

        dialog = \
            Gtk.Dialog(
                title,
                self._get_parent( parent_widget ),
                Gtk.DialogFlags.MODAL )

        dialog.add_buttons( *buttons_responsetypes )

        if default_size:
            dialog.set_default_size( *default_size )

        if content_widget:
            dialog.get_content_area().pack_start( content_widget, True, True, 0 )

        dialog.set_border_width( 5 )

        return dialog


    def show_dialog_ok_cancel(
            self,
            parent_widget,
            message,
            title = None ):

        return \
            self._show_dialog(
                parent_widget,
                message,
                Gtk.MessageType.QUESTION,
                Gtk.ButtonsType.OK_CANCEL,
                title = title )


    def show_dialog_ok(
            self,
            parent_widget,
            message,
            title = None,
            message_type = Gtk.MessageType.ERROR ):

        return \
            self._show_dialog(
                parent_widget,
                message,
                message_type,
                Gtk.ButtonsType.OK,
                title = title )


    def _show_dialog(
            self,
            parent_widget,
            message,
            message_type,
            buttons_type,
            title = None ):

        dialog = \
            Gtk.MessageDialog(
                self._get_parent( parent_widget ),
                Gtk.DialogFlags.MODAL,
                message_type,
                buttons_type,
                message )

        dialog.set_title( self.indicator_name if title is None else title )

        for child in dialog.get_message_area().get_children():
            if type( child ) is Gtk.Label:
                child.set_selectable( True ) # Allow the label to be highlighted for copy/paste.

        response = dialog.run()
        dialog.destroy()
        return response


    def _get_parent( self, widget ):
        parent = widget # Sometimes the widget itself is a Dialog/Window, so no need to get the parent.
        while( parent is not None ):
            if isinstance( parent, ( Gtk.Dialog, Gtk.Window ) ):
                break

            parent = parent.get_parent()

        return parent


    def create_autostart_checkbox_and_delay_spinner( self ):
        autostart, delay = self.get_autostart_and_delay()

        autostart_checkbox = \
            self.create_checkbutton(
                _( "Autostart" ),
                tooltip_text = _( "Run the indicator automatically." ),
                active = autostart )

        autostart_spinner = \
            self.create_spinbutton(
                delay,
                0,
                1000,
                tooltip_text = _( "Start up delay (seconds)." ),
                sensitive = autostart_checkbox.get_active() )

        autostart_checkbox.connect( "toggled", self.on_radio_or_checkbox, True, autostart_spinner )

        box = \
            self.create_box(
                (
                    ( autostart_checkbox, False ),
                    ( autostart_spinner, False ) ),
                margin_top = 10 )

        return autostart_checkbox, autostart_spinner, box


    # When adding a menuitem to a submenu,
    # under GNOME the menuitem appears in the same menu as the submenu
    # and requires an indent added to look correct.
    #
    # Under Kubuntu et al, menuitems of a submenu appear as a separate,
    # detached menu and so require no indent.
    #
    # The first value of the indent argument refers to the indent for
    # a submenu's menuitems under GNOME and similar layouts.
    # The second value of the indent argument refers to the indent for
    # a submenu's menuitems under Kubuntu and similar layouts.
    def _get_menu_indent_amount( self, indent = ( 0, 0 ) ):
        indent_amount = "      "
        indent_small = \
            self.get_current_desktop() == IndicatorBase._CURRENT_DESKTOP_KDE

        if indent_small:
            indent_amount = "   "

        detatched_submenus = \
            self.get_current_desktop() == IndicatorBase._CURRENT_DESKTOP_BUDGIE_GNOME or \
            self.get_current_desktop() == IndicatorBase._CURRENT_DESKTOP_ICEWM or \
            self.get_current_desktop() == IndicatorBase._CURRENT_DESKTOP_KDE or \
            self.get_current_desktop() == IndicatorBase._CURRENT_DESKTOP_LXQT or \
            self.get_current_desktop() == IndicatorBase._CURRENT_DESKTOP_MATE or \
            self.get_current_desktop() == IndicatorBase._CURRENT_DESKTOP_UNITY7 or \
            self.get_current_desktop() == IndicatorBase._CURRENT_DESKTOP_X_CINNAMON or \
            self.get_current_desktop() == IndicatorBase._CURRENT_DESKTOP_XFCE

        if detatched_submenus:
            indent_amount = indent_amount * indent[ 1 ]

        else:
            indent_amount = indent_amount * indent[ 0 ]

        return indent_amount


    def create_and_append_menuitem(
        self,
        menu,
        label,
        name = None,
        activate_functionandarguments = None,
        indent = ( 0, 0 ), # First element: indent level when adding to a non-detachable menu; Second element: equivalent for a detachable menu.
        is_secondary_activate_target = False ):

        indent_amount = self._get_menu_indent_amount( indent )
        menuitem = Gtk.MenuItem.new_with_label( indent_amount + label )

        if name:
            menuitem.set_name( name )

        if activate_functionandarguments:
            menuitem.connect( "activate", *activate_functionandarguments )

        if is_secondary_activate_target:
            self.secondary_activate_target = menuitem

        menu.append( menuitem )
        return menuitem


    def create_and_insert_menuitem(
        self,
        menu,
        label,
        index,
        name = None,
        activate_functionandarguments = None,
        indent = ( 0, 0 ), # First element: indent level when adding to a non-detachable menu; Second element: equivalent for a detachable menu.
        is_secondary_activate_target = False ):

        menuitem = \
            self.create_and_append_menuitem(
                menu,
                label,
                name = name,
                activate_functionandarguments = activate_functionandarguments,
                indent = indent,
                is_secondary_activate_target = is_secondary_activate_target )

        menu.reorder_child( menuitem, index )
        return menuitem


    # Creates a single (isolated, not part of a group)
    # RadioMenuItem that is enabled/active.
    def create_and_append_radiomenuitem(
        self,
        menu,
        label,
        activate_functionandarguments = None,
        indent = ( 0, 0 ) ): # First element: indent level when adding to a non-detachable menu; Second element: equivalent for a detachable menu.

        indent_amount = self._get_menu_indent_amount( indent )
        menuitem = Gtk.RadioMenuItem.new_with_label( [ ], indent_amount + label )
        menuitem.set_active( True )

        if activate_functionandarguments:
            menuitem.connect( "activate", *activate_functionandarguments )

        menu.append( menuitem )
        return menuitem


    def get_on_click_menuitem_open_browser_function( self ):
        return lambda menuitem: webbrowser.open( menuitem.get_name() )

    
    # Takes a Gtk.TextView and returns the containing text,
    # avoiding the additional calls to get the start/end positions.
    def get_textview_text( self, textview ):
        textview_buffer = textview.get_buffer()
        return \
            textview_buffer.get_text(
                textview_buffer.get_start_iter(),
                textview_buffer.get_end_iter(),
                True )


    # Listens to radio/checkbox "toggled" events and toggles the visibility
    # of the widgets according to the boolean value of 'sense'.
    def on_radio_or_checkbox( self, radio_or_checkbox, sense, *widgets ):
        for widget in widgets:
            widget.set_sensitive( sense and radio_or_checkbox.get_active() )


    # Estimate the number of menu items which will fit into an indicator menu
    # without exceeding the screen height.
    def get_menuitems_guess( self ):
        screen_heights_in_pixels = [ 600, 768, 800, 900, 1024, 1050, 1080 ]
        numbers_of_menuitems = [ 15, 15, 15, 20, 20, 20, 20 ]

        screen_height_in_pixels = Gtk.Window().get_screen().get_height()
        if screen_height_in_pixels < screen_heights_in_pixels[ 0 ]:
            number_of_menuitems = \
                numbers_of_menuitems[ 0 ] * screen_height_in_pixels / screen_heights_in_pixels[ 0 ] # Best guess.

        elif screen_height_in_pixels > screen_heights_in_pixels[ -1 ]:
            number_of_menuitems = \
                numbers_of_menuitems[ -1 ] * screen_height_in_pixels / screen_heights_in_pixels[ -1 ] # Best guess.

        else:
            number_of_menuitems = \
                IndicatorBase.interpolate(
                    screen_heights_in_pixels,
                    numbers_of_menuitems,
                    screen_height_in_pixels )

        return number_of_menuitems


    # Reference: https://stackoverflow.com/a/56233642/2156453
    @staticmethod
    def interpolate( x_values, y_values, x ):
        if not ( x_values[ 0 ] <= x <= x_values[ -1 ] ):
            raise ValueError( "x out of bounds!" )

        if any( y - x <= 0 for x, y in zip( x_values, x_values[ 1 : ] ) ):
            raise ValueError( "xValues must be in strictly ascending order!" )

        intervals = zip( x_values, x_values[ 1 : ], y_values, y_values[ 1 : ] )
        slopes = [ ( y2 - y1 ) / ( x2 - x1 ) for x1, x2, y1, y2 in intervals ]

        if x == x_values[ -1 ]:
            y = y_values[ -1 ]

        else:
            i = bisect_right( x_values, x ) - 1
            y = y_values[ i ] + slopes[ i ] * ( x - x_values[ i ] )

        return y


    def create_grid( self ):
        spacing = 10
        grid = Gtk.Grid()
        grid.set_column_spacing( spacing )
        grid.set_row_spacing( spacing )
        grid.set_margin_left( spacing )
        grid.set_margin_right( spacing )
        grid.set_margin_top( spacing )
        grid.set_margin_bottom( spacing )
        return grid


    def create_scrolledwindow( self, widget ):
        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.set_hexpand( True )
        scrolledwindow.set_vexpand( True )
        scrolledwindow.add( widget )
        return scrolledwindow


    def create_box(
            self,
            widgets_and_expands,
            sensitive = True,
            margin_top = 0,
            margin_left = 0,
            spacing = 6,
            halign = Gtk.Align.FILL,
            homogeneous = False ):

        box = Gtk.Box( spacing = spacing, orientation = Gtk.Orientation.HORIZONTAL )
        box.set_sensitive( sensitive )
        box.set_margin_top( margin_top )
        box.set_margin_left( margin_left )
        box.set_halign( halign )
        box.set_homogeneous( homogeneous )

        for widget, expand in widgets_and_expands:
            box.pack_start( widget, expand, expand, 0 )
            if expand:
                box.set_hexpand( True )

        return box


    def create_buttons_in_box(
            self,
            labels,
            tooltip_texts,
            clicked_functionandarguments ):

        buttons_and_expands = [ ]
        z = zip( labels, tooltip_texts, clicked_functionandarguments )
        for label, tooltip_text, clicked_functionandargument in z:
            button = \
                self.create_button(
                    label,
                    tooltip_text = tooltip_text,
                    clicked_functionandarguments = clicked_functionandargument )

            buttons_and_expands.append( [ button, True ] )

        return \
            self.create_box(
                tuple( buttons_and_expands ),
                halign = Gtk.Align.CENTER,
                homogeneous = True )


    def create_entry(
        self,
        text,
        tooltip_text = "",
        sensitive = True,
        margin_top = 0,
        margin_left = 0,
        editable = True,
        make_longer = False ):

        entry = Gtk.Entry()
        self._set_widget_common_attributes(
            entry,
            tooltip_text = tooltip_text,
            sensitive = sensitive,
            margin_top = margin_top,
            margin_left = margin_left )

        entry.set_text( text )
        entry.set_editable( editable )

        # Give a little more space; sometimes too short due to packing.
        if make_longer and text:
            entry.set_width_chars( len( text ) * 5 / 4 )

        return entry


    def create_comboboxtext(
            self,
            data,
            tooltip_text = "",
            active = -1 ):

        comboboxtext = Gtk.ComboBoxText.new_with_entry()

        for d in data:
            comboboxtext.append_text( d )

        comboboxtext.set_tooltip_text( tooltip_text )
        comboboxtext.set_active( active )
        return comboboxtext


    def create_textview(
            self,
            text = "",
            tooltip_text = "",
            editable = True,
            wrap_mode = Gtk.WrapMode.WORD ):

        textview = Gtk.TextView()
        textview.get_buffer().set_text( text )
        textview.set_tooltip_text( tooltip_text )
        textview.set_editable( editable )
        textview.set_wrap_mode( wrap_mode )
        return textview


    def create_button(
        self,
        label,
        tooltip_text = "",
        sensitive = True,
        margin_top = 0,
        margin_left = 0,
        clicked_functionandarguments = None ): # Must be passed as a tuple https://stackoverflow.com/a/6289656/2156453

        button = Gtk.Button.new_with_label( label )
        self._set_widget_common_attributes(
            button,
            tooltip_text = tooltip_text,
            sensitive = sensitive,
            margin_top = margin_top,
            margin_left = margin_left )

        if clicked_functionandarguments:
            button.connect( "clicked", *clicked_functionandarguments )

        return button


    def create_spinbutton(
        self,
        value,
        lower,
        upper,
        step_increment = 1,
        page_increment = 10,
        tooltip_text = "",
        sensitive = True,
        margin_top = 0,
        margin_left = 0 ):

        spinner = Gtk.SpinButton()
        self._set_widget_common_attributes(
            spinner,
            tooltip_text = tooltip_text,
            sensitive = sensitive,
            margin_top = margin_top,
            margin_left = margin_left )

        spinner.set_adjustment( Gtk.Adjustment.new( value, lower, upper, step_increment, page_increment, 0 ) )
        spinner.set_numeric( True )
        spinner.set_update_policy( Gtk.SpinButtonUpdatePolicy.IF_VALID )
        return spinner


    def create_checkbutton(
        self,
        label,
        tooltip_text = "",
        sensitive = True,
        margin_top = 0,
        margin_left = 0,
        active = True ):

        checkbutton = Gtk.CheckButton.new_with_label( label )
        self._set_widget_common_attributes(
            checkbutton,
            tooltip_text = tooltip_text,
            sensitive = sensitive,
            margin_top = margin_top,
            margin_left = margin_left )

        checkbutton.set_active( active )
        return checkbutton


    def create_radiobutton(
        self,
        radio_group_member,
        label,
        tooltip_text = "",
        sensitive = True,
        margin_top = 0,
        margin_left = 0,
        active = True ):

        radiobutton = Gtk.RadioButton.new_with_label_from_widget( radio_group_member, label )
        self._set_widget_common_attributes(
            radiobutton,
            tooltip_text = tooltip_text,
            sensitive = sensitive,
            margin_top = margin_top,
            margin_left = margin_left )

        radiobutton.set_active( active )
        return radiobutton


    def _set_widget_common_attributes(
        self,
        widget,
        tooltip_text = "",
        sensitive = True,
        margin_top = 0,
        margin_left = 0 ):

        widget.set_tooltip_text( tooltip_text )
        widget.set_sensitive( sensitive )
        widget.set_margin_top( margin_top )
        widget.set_margin_left( margin_left )


    def create_treeview_within_scrolledwindow(
        self,
        treemodel,
        titles,
        renderers_attributes_columnmodelids,
        alignments_columnviewids = None,
        sortcolumnviewids_columnmodelids = None,
        celldatafunctionandarguments_renderers_columnviewids = None,
        clickablecolumnviewids_functionsandarguments = None,
        tooltip_text = "",
        cursorchangedfunctionandarguments = None,
        rowactivatedfunctionandarguments = None ):
        '''
        Creates a Gtk.TreeView encapsulated within a Gtk.ScrolledWindow.

        Parameters:

        treemodel: The Gtk.TreeModel (may be a filter and/or sort).

        titles: Tuple of strings for each column's title.

        renderers_attributes_columnmodelids:
            Tuple of tuples, each of which contains the Gtk.CellRenderer, data type and model column id
            for the column view.
            Columns will not be expanded: treeviewcolumn.pack_start( renderer, False ).
            A tuple (for a given model column id) may contain tuples, each of which is for a different renderer.

        alignments_columnviewids: Tuple of tuples, each of which contains the xalign and view column id.

        sortcolumnviewids_columnmodelids:
            Tuple of tuples, each of which contains the view column id and corresponding model column id.
            The first column will be set as default sorted ascendingly.

        celldatafunctionandarguments_renderers_columnviewids:
            Tuple of tuples, each of which contains a cell data renderer function, parameters to the function,
            a cell data renderer (the SAME renderer passed in to the renderers_attributes_columnmodelids) and
            the view column id.

        clickablecolumnviewids_functionsandarguments:
            Tuple of tuples, each of which contains the view column id and a corresponding function (and parameters)
            to be called on column header click.

        tooltip_text: Tooltip text for the entire TreeView.

        cursorchangedfunctionandarguments: A function (and parameters) to call on row selection.

        rowactivatedfunctionandarguments: A function (and parameters) to call on row double click.      
        '''
        treeview = Gtk.TreeView.new_with_model( treemodel )

        for index, ( title, renderer_attribute_columnmodelid ) in enumerate( zip( titles, renderers_attributes_columnmodelids ) ):
            treeviewcolumn = Gtk.TreeViewColumn( title )

            # Expand the column unless the column contains a single checkbox and no column header title.
            is_checkbox_column = \
                type( renderer_attribute_columnmodelid[ 0 ] ) is Gtk.CellRendererToggle and not title

            treeviewcolumn.set_expand( not is_checkbox_column )

            # Add the renderer / attribute / column model id for each column.
            is_single_tuple = type( renderer_attribute_columnmodelid[ 0 ] ) is not tuple
            if is_single_tuple:
                treeviewcolumn.pack_start( renderer_attribute_columnmodelid[ 0 ], False )
                treeviewcolumn.add_attribute( *renderer_attribute_columnmodelid )

            else: # Assume to be a tuple of tuples of renderer, attribute, column model id.
                for renderer, attribute, columnmodelid in renderer_attribute_columnmodelid:
                    treeviewcolumn.pack_start( renderer, False )
                    treeviewcolumn.add_attribute( renderer, attribute, columnmodelid )

            if alignments_columnviewids:
                alignment = [
                    alignment_columnviewid[ 0 ]
                    for alignment_columnviewid in alignments_columnviewids
                    if alignment_columnviewid[ 1 ] == index ]

                if alignment:
                    treeviewcolumn.set_alignment( alignment[ 0 ] )
                    current_alignment = renderer_attribute_columnmodelid[ 0 ].get_alignment()
                    renderer_attribute_columnmodelid[ 0 ].set_alignment( alignment[ 0 ], current_alignment[ 1 ] )

            treeview.append_column( treeviewcolumn )

        if sortcolumnviewids_columnmodelids:
            for columnviewid, columnmodelid in sortcolumnviewids_columnmodelids:
                for indexcolumn, treeviewcolumn in enumerate( treeview.get_columns() ):
                    if columnviewid == indexcolumn:
                        treeviewcolumn.set_sort_column_id( columnmodelid )
                        if sortcolumnviewids_columnmodelids.index( ( columnviewid, columnmodelid ) ) == 0:
                            treemodel.set_sort_column_id( columnmodelid, Gtk.SortType.ASCENDING ) # Set first sorted column as default ascending.

        if celldatafunctionandarguments_renderers_columnviewids:
            for data_function_and_arguments, renderer, columnviewid in celldatafunctionandarguments_renderers_columnviewids:
                for index, treeviewcolumn in enumerate( treeview.get_columns() ):
                    if columnviewid == index:
                        treeviewcolumn.set_cell_data_func( renderer, *data_function_and_arguments )

        if clickablecolumnviewids_functionsandarguments:
            for columnviewid_functionandarguments in clickablecolumnviewids_functionsandarguments:
                for index, treeviewcolumn in enumerate( treeview.get_columns() ):
                    if columnviewid_functionandarguments[ 0 ] == index:
                        treeviewcolumn.set_clickable( True )
                        treeviewcolumn.connect( "clicked", *columnviewid_functionandarguments[ 1 ] )

        treeview.set_tooltip_text( tooltip_text )
        treeview.get_selection().set_mode( Gtk.SelectionMode.BROWSE )
        treeview.expand_all()
        treeview.set_hexpand( True )
        treeview.set_vexpand( True )

        if cursorchangedfunctionandarguments:
            treeview.connect( "cursor-changed", *cursorchangedfunctionandarguments )

        if rowactivatedfunctionandarguments:
            treeview.connect( "row-activated", *rowactivatedfunctionandarguments )

        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.set_policy( Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC )
        scrolledwindow.add( treeview )
        return treeview, scrolledwindow


    def create_filechooser_dialog(
        self,
        title,
        parent,
        filename,
        action = Gtk.FileChooserAction.OPEN ):

        dialog = \
            Gtk.FileChooserDialog(
                title = title,
                parent = parent,
                action = action )

        dialog.add_buttons( Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK )
        dialog.set_transient_for( parent )
        dialog.set_filename( filename )
        return dialog


    def get_autostart_and_delay( self ):
        autostart = False
        delay = 0
        try:
            if self.desktop_file_user_home.is_file():
                with open( self.desktop_file_user_home, 'r' ) as f:
                    for line in f:
                        if IndicatorBase._X_GNOME_AUTOSTART_ENABLED + "=true" in line:
                            autostart = True

                        if IndicatorBase._X_GNOME_AUTOSTART_DELAY + '=' in line:
                            delay = int( line.split( '=' )[ 1 ].strip() )

        except Exception as e:
            logging.exception( e )
            autostart = False
            delay = 0

        return autostart, delay


    def set_autostart_and_delay( self, is_set, delay ):
        IndicatorBase._AUTOSTART_PATH.mkdir( parents = True, exist_ok = True )

        if not self.desktop_file_user_home.is_file():
            shutil.copy( self.desktop_file_virtual_environment, self.desktop_file_user_home )

        try:
            output = ""
            with open( self.desktop_file_user_home, 'r' ) as f:
                for line in f:
                    if IndicatorBase._X_GNOME_AUTOSTART_DELAY in line:
                        output += IndicatorBase._X_GNOME_AUTOSTART_DELAY + '=' + str( delay ) + '\n'

                    elif IndicatorBase._X_GNOME_AUTOSTART_ENABLED in line:
                        output += IndicatorBase._X_GNOME_AUTOSTART_ENABLED + '=' + str( is_set ).lower() + '\n'

                    else:
                        output += line

            # If the user has an old .desktop file,
            # there may not be an autostart enable field and/or
            # an autostart delay field, so manually add in.
            if IndicatorBase._X_GNOME_AUTOSTART_DELAY not in output:
                output += IndicatorBase._X_GNOME_AUTOSTART_DELAY + '=' + str( delay ) + '\n'

            if IndicatorBase._X_GNOME_AUTOSTART_ENABLED not in output:
                output += IndicatorBase._X_GNOME_AUTOSTART_ENABLED + '=' + str( is_set ).lower() + '\n'

            with open( self.desktop_file_user_home, 'w' ) as f:
                f.write( output )

        except Exception as e:
            logging.exception( e )


    def get_logging( self ):
        return logging


    def is_number( self, number_as_string ):
        try:
            float( number_as_string )
            return True

        except ValueError:
            return False


    def get_current_desktop( self ):
        return self.current_desktop


#TODO UNCHECKED
#TOD Maybe this can go as it is only used below 
# for ubuntu mate 20.04 which is EOL.
    def _is_ubuntu_variant_2004( self ):
        ubuntu_variant_2004 = False
        try:
            ubuntu_variant_2004 = (
                True if self.process_get( "lsb_release -rs" ) == "20.04"
                else False )

        except:
            pass

        return ubuntu_variant_2004


#TODO Check which distros/versions we now support and
# then update this function and comment header
# according to which distros/versions support icon updating.
    # Lubuntu 20.04/22.04 ignores any change to the icon after initialisation.
    # If the icon is changed, the icon is replaced with a strange grey/white circle.
    #
    # Ubuntu MATE 20.04 truncates the icon when changed,
    # despite the icon being fine when clicked.
#TODO UNCHECKED
    def _is_icon_update_supported( self ):
        icon_update_supported = True
        desktop_environment = self.get_current_desktop()

#TODO Tidy up
        if desktop_environment is None or \
           desktop_environment == IndicatorBase._CURRENT_DESKTOP_LXQT or \
           ( desktop_environment == IndicatorBase._CURRENT_DESKTOP_MATE and self._is_ubuntu_variant_2004() ):
            icon_update_supported = False

        return icon_update_supported


#TODO Check which distros/versions we now support and
# then update this function and comment header
# according to which distros/versions support label updating (or even have a label).
#
# Maybe rename to _is_label_or_tooltip_update_supported?
    # Lubuntu 20.04/22.04 ignores any change to the label/tooltip after initialisation.
    def _is_label_update_supported( self ):
        label_update_supported = True
        desktop_environment = self.get_current_desktop()

#TODO Tidy up        
        if desktop_environment is None or \
           desktop_environment == IndicatorBase._CURRENT_DESKTOP_LXQT:
            label_update_supported = False

        return label_update_supported


#TODO Check with latest distro (whichever uses qterminal) if this is still an issue.
    # As a result of
    #   https://github.com/lxqt/qterminal/issues/335
    # provide a way to determine if qterminal is the current terminal.
#TODO UNCHECKED
    def is_terminal_qterminal( self, terminal ):
        return ( terminal is not None ) and ( "qterminal" in terminal )


    # Return the full path and name of the executable for the
    # current terminal and the corresponding execution flag;
    # None otherwise.
    def get_terminal_and_execution_flag( self ):
        terminal = None
        execution_flag = None
        for _terminal, _execution_flag in IndicatorBase._TERMINALS_AND_EXECUTION_FLAGS:
            terminal = self.process_get( "which " + _terminal )
            if terminal is not None:
                execution_flag = _execution_flag
                break

        if terminal:
            terminal = terminal.strip()

        if terminal == "":
            terminal = None
            execution_flag = None

        return terminal, execution_flag


    # Download the contents of the given URL and save to file.
    @staticmethod
    def download( url, filename, logging ):
        downloaded = False
        try:
            response = urlopen( url, timeout = IndicatorBase.URL_TIMEOUT_IN_SECONDS ).read().decode()
            with open( filename, 'w' ) as f_out:
                f_out.write( response )

            downloaded = True

        except Exception as e:
            logging.error( "Error downloading from " + str( url ) )
            logging.exception( e )

        return downloaded


    # Copies .config using the old indicator name format (using hyphens)
    # to the new format, sans hyphens.
    def _copy_config_to_new_directory( self, config_file ):
        mapping = {
            "indicatorfortune":                 "indicator-fortune",
            "indicatorlunar":                   "indicator-lunar",
            "indicatoronthisday":               "indicator-on-this-day",
            "indicatorppadownloadstatistics":   "indicator-ppa-download-statistics",
            "indicatorpunycode":                "indicator-punycode",
            "indicatorscriptrunner":            "indicator-script-runner",
            "indicatorstardate":                "indicator-stardate",
            "indicatortide":                    "indicator-tide",
            "indicatortest":                    "indicator-test",
            "indicatorvirtualbox":              "indicator-virtual-box" }

        config_file_old = str( config_file ).replace( self.indicator_name, mapping[ self.indicator_name ] )
        config_file_old = Path( config_file_old )

        if not config_file.is_file() and config_file_old.is_file():
            shutil.copyfile( config_file_old, config_file )


    # Read a dictionary of configuration from a JSON text file.
    def _load_config( self ):
        config_file = \
            self._get_config_directory() / ( self.indicator_name + IndicatorBase._EXTENSION_JSON )

        self._copy_config_to_new_directory( config_file )

        config = { }
        if config_file.is_file():
            try:
                with open( config_file, 'r' ) as f_in:
                    config = json.load( f_in )

            except Exception as e:
                config = { }
                logging.exception( e )
                logging.error( "Error reading configuration: " + config_file )

        self.load_config( config ) # Call to implementation in indicator.


    def request_save_config( self, delay = 0 ):
        if self.lock_save_config.acquire( blocking = False ):
            if self.id_save_config > 0:
                GLib.source_remove( self.id_save_config )

            self.id_save_config = GLib.timeout_add_seconds( delay, self._save_config )
            self.lock_save_config.release()

        else:
            self.request_save_config( IndicatorBase._UPDATE_PERIOD_IN_SECONDS_DEFAULT )


    # Write a dictionary of user configuration to a JSON text file.
    def _save_config( self ):
        config = self.save_config() # Call to implementation in indicator.
        config[ IndicatorBase._CONFIG_VERSION ] = self.version

        config_file = \
            self._get_config_directory() / ( self.indicator_name + IndicatorBase._EXTENSION_JSON )

        try:
            with open( config_file, 'w' ) as f_out:
                f_out.write( json.dumps( config ) )

        except Exception as e:
            logging.exception( e )
            logging.error( "Error writing configuration: " + config_file )

        self.id_save_config = 0
        return False


    # Return the full directory path to the user config directory for the current indicator.
    def _get_config_directory( self ):
        return self._get_user_directory( ".config", self.indicator_name )


    # Finds the most recent file in the cache with the given basename
    # and if the timestamp is older than the current date/time
    # plus the maximum age, returns True, otherwise False.
    # If no file can be found, returns True.
    def is_cache_stale( self, basename, maximum_age_in_hours ):
        cache_date_time = self.get_cache_date_time( basename )
        if cache_date_time is None:
            stale = True

        else:
            utc_now = datetime.datetime.now( datetime.timezone.utc )
            stale = ( cache_date_time + datetime.timedelta( hours = maximum_age_in_hours ) ) < utc_now

        return stale


    # Find the date/time of the newest file in the cache matching the basename.
    #
    # basename: The text used to form the file name, typically the name of the calling application.
    #
    # Returns the datetime of the newest file in the cache; None if no file can be found.
    def get_cache_date_time( self, basename ):
        expiry = None
        the_file = ""
        for file in self.get_cache_directory().iterdir():
            if file.name.startswith( basename ) and file.name > the_file:
                the_file = file.name

        if the_file: # A value of "" evaluates to False.
            date_time_component = the_file[ len( basename ) : len( basename ) + 14 ] # YYYYMMDDHHMMSS is 14 characters.

            expiry = \
                datetime.datetime.strptime(
                    date_time_component,
                    IndicatorBase._CACHE_DATE_TIME_FORMAT_YYYYMMDDHHMMSS )

            expiry = expiry.replace( tzinfo = datetime.timezone.utc )

        return expiry


    # Create a filename with timestamp and extension to be used to save data to the cache.
    def get_cache_filename_with_timestamp( self, basename, extension = EXTENSION_TEXT ):
        filename = \
            basename + \
            datetime.datetime.now().strftime( IndicatorBase._CACHE_DATE_TIME_FORMAT_YYYYMMDDHHMMSS ) + \
            extension

        return self.get_cache_directory() / filename


    # Search through the cache for all files matching the basename.
    #
    # Returns the newest filename matching the basename on success; None otherwise.
    def get_cache_newest_filename( self, basename ):
        cache_directory = self.get_cache_directory()
        cache_file = ""
        for file in cache_directory.iterdir():
            if file.name.startswith( basename ) and file.name > cache_file:
                cache_file = file.name

        if cache_file:
            cache_file = cache_directory / cache_file

        else:
            cache_file = None

        return cache_file


    # Remove a file from the cache.
    #
    # filename: The file to remove.
    #
    # The file removed will be
    #     ~/.cache/application_base_directory/filename
    def remove_file_from_cache( self, filename ):
        for file in self.get_cache_directory().iterdir():
            if file.name == filename:
                file.unlink()
                break


    # Removes out of date cache files for a given basename.
    #
    # basename: The text used to form the file name, typically the name of the calling application.
    # maximum_age_in_hours: Anything older than the maximum age (hours) is deleted.
    #
    # Any file in the cache directory matching the pattern
    #     ~/.cache/applicationBaseDirectory/basenameCACHE_DATE_TIME_FORMAT_YYYYMMDDHHMMSS
    #
    # and is older than the cache maximum age is discarded.
    #
    # Any file extension is ignored in determining if the file should be deleted or not.
    def flush_cache( self, basename, maximum_age_in_hours ):
        cache_maximum_age_date_time = \
            datetime.datetime.now() - datetime.timedelta( hours = maximum_age_in_hours )

        for file in self.get_cache_directory().iterdir():
            if file.name.startswith( basename ): # Sometimes the base name is shared ("icon-" versus "icon-fullmoon-") so use the date/time to ensure the correct group of files.
                date_time = file.name[ len( basename ) : len( basename ) + 14 ] # len( YYYYMMDDHHMMSS ) = 14.
                if date_time.isdigit():
                    file_date_time = \
                        datetime.datetime.strptime(
                            date_time,
                            IndicatorBase._CACHE_DATE_TIME_FORMAT_YYYYMMDDHHMMSS )

                    if file_date_time < cache_maximum_age_date_time:
                        file.unlink()


    # Read the most recent binary file from the cache.
    #
    # basename: The text used to form the file name, typically the name of the calling application.
    #
    # All files in cache directory are filtered based on the pattern
    #     ~/.cache/applicationBaseDirectory/basenameCACHE_DATE_TIME_FORMAT_YYYYMMDDHHMMSS
    #
    # For example, for an application 'apple', the first file will pass through, whilst the second is filtered out
    #    ~/.cache/fred/apple-20170629174950
    #    ~/.cache/fred/orange-20170629174951
    #
    # Files which pass the filter are sorted by date/time and the most recent file is read.
    #
    # Returns the binary object; None when no suitable cache file exists; None on error and logs.
    def read_cache_binary( self, basename ):
        cache_file = ""
        cache_directory = self.get_cache_directory()
        for file in cache_directory.iterdir():
            if file.name.startswith( basename ) and file.name > cache_file:
                cache_file = file.name

        data = None
        if cache_file: # A value of "" evaluates to False.
            filename = cache_directory / cache_file
            try:
                with open( filename, 'rb' ) as f_in:
                    data = pickle.load( f_in )

            except Exception as e:
                data = None
                logging.exception( e )
                logging.error( "Error reading from cache: " + filename )

        return data


    # Writes an object as a binary file to the cache.
    #
    # binary_data: The object to write.
    # basename: The text used to form the file name, typically the name of the calling application.
    # extension: Added to the end of the basename and date/time.
    #
    # The object will be written to the cache directory using the pattern
    #     ~/.cache/applicationBaseDirectory/basenameCACHE_DATE_TIME_FORMAT_YYYYMMDDHHMMSS
    #
    # Returns filename written on success; None otherwise.
    def write_cache_binary( self, binary_data, basename, extension = "" ):
        filename = \
            basename + \
            datetime.datetime.now().strftime( IndicatorBase._CACHE_DATE_TIME_FORMAT_YYYYMMDDHHMMSS ) + \
            extension

        cache_file = self.get_cache_directory() / filename

        try:
            with open( cache_file, 'wb' ) as f_out:
                pickle.dump( binary_data, f_out )

        except Exception as e:
            logging.exception( e )
            logging.error( "Error writing to cache: " + cache_file )
            cache_file = None

        return cache_file


    # Read the named text file from the cache.
    #
    # filename: The name of the file.
    #
    # Returns the contents of the text file; None on error and logs.
    def read_cache_text_without_timestamp( self, filename ):
        return self._read_cache_text( self.get_cache_directory() / filename )


    # Read the most recent text file from the cache.
    #
    # basename: The text used to form the file name, typically the name of the calling application.
    #
    # All files in cache directory are filtered based on the pattern
    #     ~/.cache/applicationBaseDirectory/basenameCACHE_DATE_TIME_FORMAT_YYYYMMDDHHMMSSextension
    #
    # For example, for an application 'apple', the first file will be caught,
    # whilst the second is filtered out:
    #    ~/.cache/fred/apple-20170629174950
    #    ~/.cache/fred/orange-20170629174951
    #
    # Files which pass the filter are sorted by date/time and the most recent file is read.
    #
    # Returns the contents of the text; None when no suitable cache file exists; None on error and logs.
    def read_cache_text( self, basename ):
        cache_file = ""
        cache_directory = self.get_cache_directory()
        for file in cache_directory.iterdir():
            if file.name.startswith( basename ) and file.name > cache_file:
                cache_file = file.name

        if cache_file:
            cache_file = cache_directory / cache_file

        return self._read_cache_text( cache_file )


    def _read_cache_text( self, cache_file ):
        text = ""
        if cache_file.is_file():
            try:
                with open( cache_file, 'r' ) as f_in:
                    text = f_in.read()

            except Exception as e:
                text = ""
                logging.exception( e )
                logging.error( "Error reading from cache: " + cache_file )

        return text


    # Writes text to a file in the cache.
    #
    # text: The text to write.
    # filename: The name of the file.
    #
    # Returns filename written on success; None otherwise.
    def write_cache_text_without_timestamp( self, text, filename ):
        return self._write_cache_text( text, self.get_cache_directory() / filename )


    # Writes text to a file in the cache.
    #
    # text: The text to write.
    # basename: The text used to form the file name, typically the name of the calling application.
    # extension: Added to the end of the basename and date/time.
    #
    # The text will be written to the cache directory using the pattern
    #     ~/.cache/applicationBaseDirectory/basenameCACHE_DATE_TIME_FORMAT_YYYYMMDDHHMMSSextension
    #
    # Returns filename written on success; None otherwise.
    def write_cache_text( self, text, basename, extension = EXTENSION_TEXT ):
        filename = \
            basename + \
            datetime.datetime.now().strftime( IndicatorBase._CACHE_DATE_TIME_FORMAT_YYYYMMDDHHMMSS ) + \
            extension

        return self._write_cache_text( text, self.get_cache_directory() / filename )


    def _write_cache_text( self, text, cache_file ):
        try:
            with open( cache_file, 'w' ) as f_out:
                f_out.write( text )

        except Exception as e:
            logging.exception( e )
            logging.error( "Error writing to cache: " + cache_file )

        return cache_file


    # Return the full directory path to the user cache directory for the current indicator.
    def get_cache_directory( self ):
        return self._get_user_directory( ".cache", self.indicator_name )


    # Obtain (and create if not present) the directory for configuration, cache or similar.
    #
    # user_base_directory:
    #   The directory name used to hold the configuration/cache.
    # application_base_directory:
    #   The directory name at the end of the final user directory to specify the application.
    #
    # The full directory path will be
    #    ~/user_base_directory/application_base_directory
    def _get_user_directory( self, user_base_directory, application_base_directory ):
        directory = Path.home() / user_base_directory / application_base_directory
        directory.mkdir( parents = True, exist_ok = True )
        return directory


    # Executes the command in a new process.
    # On exception, logs to file.
    def process_call( self, command ):
        try:
            subprocess.call( command, shell = True )

        except subprocess.CalledProcessError as e:
            self.get_logging().error( e )
            if e.stderr:
                self.get_logging().error( e.stderr )


    # Executes the command and returns the result.
    #
    # logNonZeroErrorCode If True, will log any exception arising from a non-zero return code; otherwise will ignore.
    #
    # On exception, logs to file.
    def process_get( self, command, log_non_zero_error_code = False ):
        result = None
        try:
            result = \
                subprocess.run(
                    command,
                    stdout = subprocess.PIPE,
                    stderr = subprocess.PIPE,
                    shell = True,
                    check = log_non_zero_error_code ).stdout.decode()

            if result:
                result = result.strip()

            else:
                result = None

        except subprocess.CalledProcessError as e:
            self.get_logging().error( e )
            if e.stderr:
                self.get_logging().error( e.stderr )

            result = None

        return result


# Log file handler which truncates the file when the file size limit is reached.
#
# References:
#   https://docs.python.org/3/library/logging.handlers.html
#   https://stackoverflow.com/questions/24157278/limit-python-log-file
#   https://github.com/python/cpython/blob/main/Lib/logging/handlers.py
class TruncatedFileHandler( logging.handlers.RotatingFileHandler ):

    def __init__( self, filename, maxBytes = 10000 ):
        super().__init__(
            filename,
            maxBytes = maxBytes,
            delay = True )


    def doRollover( self ):
        if self.stream:
            self.stream.close()

        Path( self.baseFilename ).unlink( missing_ok = True ) # self.baseFilename is defined in parent class.
        self.mode = 'a'
        self.stream = self._open()
