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
Base class for application indicators.

References
    https://lazka.github.io/pgi-docs/AyatanaAppIndicator3-0.1
    https://github.com/AyatanaIndicators/libayatana-appindicator
    https://wiki.ayatana-indicators.org/AyatanaIndicatorApplication
    https://wiki.ubuntu.com/DesktopExperienceTeam/ApplicationIndicators
    https://askubuntu.com/q/108035/67335
    https://python-gtk-3-tutorial.readthedocs.org
    https://pygobject.gnome.org/guide/threading.html
    https://stackoverflow.com/q/73665239/2156453
    https://wiki.ubuntu.com/NotifyOSD
    https://lazka.github.io/pgi-docs/Gtk-3.0
    https://pygobject.readthedocs.io/en/latest/getting_started.html
    https://twine.readthedocs.io/en/latest/
    https://packaging.python.org/en/latest/tutorials/packaging-projects/
    https://specifications.freedesktop.org/icon-theme-spec/latest/
    https://pypi.org/project/pystray/
    https://peps.python.org/pep-0008/
    https://docs.python-guide.org/writing/style/
    https://guicommits.com/organize-python-code-like-a-pro/
'''


import datetime
import email.policy
import gettext
import inspect
import json
import logging.handlers
import pickle
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import threading
import webbrowser

from abc import ABC, abstractmethod
from bisect import bisect_right
from importlib import metadata
from pathlib import Path, PosixPath
from threading import Lock
from urllib.error import HTTPError, URLError
from urllib.request import urlopen
from zipfile import ZipFile

import gi

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

try:
    gi.require_version( "AyatanaAppIndicator3", "0.1" )
    from gi.repository import AyatanaAppIndicator3 as AppIndicator
except ValueError:
    try:
        gi.require_version( "AppIndicator3", "0.1" )
        from gi.repository import AppIndicator3 as AppIndicator # For Fedora.
    except ValueError:
        print( "Unable to find neither AyatanaAppIndicator3 nor AppIndicator3.")
        sys.exit( 1 )


class IndicatorBase( ABC ):
    '''
    Base class from which all indicators inherit.
    '''

    _CACHE_DATE_TIME_FORMAT_YYYYMMDDHHMMSS = "%Y%m%d%H%M%S"

    _CONFIG_CHECK_LATEST_VERSION = "checklatestversion"
    _CONFIG_VERSION = "version"

    # Supported desktops; values are the result of calling
    #   echo $XDG_CURRENT_DESKTOP
    #
    # Different results come from calling
    #   os.environ.get( "DESKTOP_SESSION" )
    # giving 'plasma' rather than 'KDE' on 'Plasma (X11)' on Kubuntu.
    _DESKTOP_BUDGIE_GNOME = "Budgie:GNOME"
    _DESKTOP_ICEWM = "ICEWM"
    _DESKTOP_KDE = "KDE"
    _DESKTOP_LXQT = "LXQt"
    _DESKTOP_MATE = "MATE"
    _DESKTOP_UNITY7 = "Unity:Unity7:ubuntu"
    _DESKTOP_X_CINNAMON = "X-Cinnamon"
    _DESKTOP_XFCE = "XFCE"

    _DOT_DESKTOP_AUTOSTART_DELAY = "X-GNOME-Autostart-Delay" # Not on Debian.
    _DOT_DESKTOP_AUTOSTART_ENABLED = "X-GNOME-Autostart-enabled"
    _DOT_DESKTOP_EXEC = "Exec"
    _DOT_DESKTOP_TERMINAL = "Terminal"

    _EXTENSION_JSON = ".json"

    _TERMINALS_AND_EXECUTION_FLAGS = [ [ "gnome-terminal", "--" ] ]
    _TERMINALS_AND_EXECUTION_FLAGS.extend( [
        [ "konsole", "-e" ],
        [ "lxterminal", "-e" ],
        [ "mate-terminal", "-x" ],
        [ "qterminal", "-e" ],
        [ "tilix", "-e" ],
        [ "xfce4-terminal", "-x" ] ] )

    _UPDATE_PERIOD_IN_SECONDS_DEFAULT = 60

    DIALOG_DEFAULT_HEIGHT = 480
    DIALOG_DEFAULT_WIDTH = 640

    EXTENSION_SVG = ".svg"
    EXTENSION_SVG_SYMBOLIC = "-symbolic.svg"
    EXTENSION_TEXT = ".txt"

    INDENT_WIDGET_LEFT = 25
    INDENT_WIDGET_TOP = 10

    # Commands such as wmctrl and the clipboard do not function under Wayland.
    # Need a way to determine whether running under Wayland versus x11.
    # Values are the result of calling
    #   echo $XDG_SESSION_TYPE
    SESSION_TYPE_WAYLAND = "wayland"
    SESSION_TYPE_X11 = "x11"

    TIMEOUT_IN_SECONDS = 10

    # Obtain name of indicator from the call stack and initialise gettext.
    INDICATOR_NAME = None
    for frame_record in inspect.stack():
        in_indicator_source = (
            "from indicatorbase import IndicatorBase"
            in
            str( frame_record.code_context ) )

        if in_indicator_source:
            INDICATOR_NAME = Path( frame_record.filename ).stem
            if INDICATOR_NAME == Path( __file__ ).parent.stem:
                # Running installed under a virtual environment.
                locale_directory = Path( __file__ ).parent / "locale"

            else:
#TODO When running under development,
# check this works under Eclipse, Visual Studio Code and via a terminal.
                # Running in development.
                locale_directory = (
                    Path( __file__ ).parent.parent.parent.parent / INDICATOR_NAME / "src" / INDICATOR_NAME / "locale" )

            gettext.install( INDICATOR_NAME, localedir = locale_directory )
            break


    def __init__(
        self,
        comments,
        artwork = None,
        creditz = None,
        debug = False ):
        '''
        The comments argument is used in two places:
            1) The comments are passed directly to the About dialog.

            2) The first letter of the comments is capitalised and
               incorporated into the Project Description on the PyPI page.
        '''

        if IndicatorBase.INDICATOR_NAME is None:
            self.show_dialog_ok(
                None,
                "Unable to determine indicator name!",
                title = "ERROR",
                message_type = Gtk.MessageType.ERROR )

            sys.exit( 1 )

        self.indicator_name = IndicatorBase.INDICATOR_NAME

        project_metadata, error_message = (
            IndicatorBase.get_project_metadata( self.indicator_name ) )

        if error_message:
            self.show_dialog_ok(
                None,
                error_message,
                title = self.indicator_name,
                message_type = Gtk.MessageType.ERROR )

            sys.exit( 1 )

        error_message = self._initialise_desktop_file_in_user_home()
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

        self.authors_and_emails = self.get_authors_emails( project_metadata )
        self.version = project_metadata[ "Version" ]

        self.website = (
            project_metadata.get_all( "Project-URL" )[ 0 ].split( ',' )[ 1 ].strip() )

        self.log = Path.home() / ( self.indicator_name + ".log" )
        logging.basicConfig(
            format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            level = logging.DEBUG,
            handlers = [ TruncatedFileHandler( self.log ) ] )

        self.lock_update = Lock()
        self.id_update = 0 # ID returned when scheduling an update.

        self.lock_save_config = Lock()
        self.id_save_config = 0 # ID returned when scheduling a config save.

        # Respond to CTRL+C when running from terminal.
        signal.signal( signal.SIGINT, signal.SIG_DFL )

        Notify.init( self.indicator_name )

        self.indicator = (
            AppIndicator.Indicator.new(
                self.indicator_name, # ID
                self.get_icon_name(), # Icon name
                AppIndicator.IndicatorCategory.APPLICATION_STATUS ) )

        self.indicator.set_status( AppIndicator.IndicatorStatus.ACTIVE )

        menu = Gtk.Menu()
        self.create_and_append_menuitem( menu, _( "Initialising..." ) )
        menu.show_all()
        self.indicator.set_menu( menu )

        self._load_config()

        self.new_version_available = False
        if self.check_latest_version:
            threading.Thread( target = self._check_for_newer_version ).start()


    def _check_for_newer_version( self ):
        url = f"https://pypi.org/pypi/{ self.indicator_name }/json"
        message = _( "Refer to the Preferences for details." )
        summary = _(
            "New version of {0} available..." ).format( self.indicator_name )

        data_json, error_network, error_timeout = self.get_json( url )
        if data_json:
            version_latest = data_json[ "info" ][ "version" ]
            if version_latest != str( self.version ):
                self.new_version_available = True
                self.show_notification( summary, message )


    def get_json(
        self,
        url ):
        '''
        Retrieves the JSON content from a URL.

        On success, returns a tuple of the JSON and two booleans set to false.

        On exception (timeout, network error) returns a tuple with None for the
        JSON followed by two booleans, one of which will be set to True.
        The first boolean indicates a network error and the second boolean
        indicates a timeout.

        https://stackoverflow.com/q/72388829/2156453
        https://stackoverflow.com/q/8763451/2156453
        '''
        error_network = False
        error_timeout = False
        try:
            with urlopen( url, timeout = IndicatorBase.TIMEOUT_IN_SECONDS ) as f:
                json_ = json.loads( f.read().decode( "utf8" ) )

        except ( HTTPError, URLError ) as e:
            if isinstance( e.reason, socket.timeout ):
                error_timeout = True
            else:
                error_network = True

            self.get_logging().error( f"Problem with { url }" )  #TODO URL is underscored...an error/warning?  What does pylint say?
            self.get_logging().exception( e )
            json_ = None

        except socket.timeout as e:
            error_timeout = True
            self.get_logging().error( f"Problem with { url }" )  #TODO URL is underscored...an error/warning?  What does pylint say?
            self.get_logging().exception( e )
            json_ = None

        return json_, error_network, error_timeout


    @staticmethod
    def _get_wheel_in_release( indicator_name ):
        error_message = None
        path_release = Path( __file__ ).parent.parent.parent.parent
        path_wheel = (
            path_release / "release" / "wheel" / f"dist_{ indicator_name }" )

        first_wheel = next( path_wheel.glob( "*.whl" ), None )
        if first_wheel is None:
            error_message = (
                f"Unable to locate a .whl in { path_wheel.absolute() }" )

        return first_wheel, error_message


    @staticmethod
    def get_project_metadata( indicator_name ):
        '''
        Read in the project metadata,
            either via pip if the indicator is installed,
            or parsing a .whl in the release folder running under development.

        https://stackoverflow.com/q/75801738/2156453
        https://stackoverflow.com/q/76143042/2156453
        '''
        try:
            # Obtain pyproject.toml information from pip.
            project_metadata = metadata.metadata( indicator_name )
            error_message = None

        except metadata.PackageNotFoundError:
            # No pip information found; assume running in development;
            # look for a .whl file in the release folder.
            wheel_in_release, error_message = (
                IndicatorBase._get_wheel_in_release( indicator_name ) )

            if wheel_in_release is None:
                project_metadata = None

            else:
                first_metadata = (
                    next(
                        metadata.distributions(
                            path = [ wheel_in_release ] ), None ) )

                if first_metadata is None:
                    project_metadata = None
                    error_message = (
                        f"No metadata was found in " +
                        "{ wheel_in_release.absolute() }!" )

                else:
                    project_metadata = first_metadata.metadata

        return project_metadata, error_message


    def _initialise_desktop_file_in_user_home( self ):
        autostart_path = Path.home() / ".config" / "autostart"
        autostart_path.mkdir( parents = True, exist_ok = True )

        desktop_file = self.indicator_name + ".py.desktop"
        self.desktop_file_user_home = autostart_path / desktop_file
        desktop_file_virtual_environment = (
            Path( __file__ ).parent / "platform" / "linux" / desktop_file )

        error_message = None
        if self.desktop_file_user_home.is_file():
            self._process_existing_dot_desktop_file_to_home_config_autostart(
                desktop_file_virtual_environment )

        else:
            error_message = (
                self._copy_dot_desktop_file_to_home_config_autostart(
                    desktop_file_virtual_environment, desktop_file ) )

        return error_message


    def _process_existing_dot_desktop_file_to_home_config_autostart(
        self,
        desktop_file_virtual_environment ):

        # The .desktop may be an older version with an Exec without a sleep,
        # or tags no longer used such as X-GNOME-Autostart-Delay.
        # Comment out unused tags and get the delay if present.
        output = ""
        delay = ""
        autostart_enabled_present = False
        exec_with_sleep_present = False
        terminal_present = False
        made_a_change = False
        with open( self.desktop_file_user_home, 'r', encoding = "utf-8" ) as f:
            for line in f:
                starts_with_autostart_enabled = (
                    line.startswith(
                        IndicatorBase._DOT_DESKTOP_AUTOSTART_ENABLED + '=' ) )

                starts_with_autostart_delay = (
                    line.startswith(
                        IndicatorBase._DOT_DESKTOP_AUTOSTART_DELAY + '=' ) )

                starts_with_desktop_exec = (
                    line.startswith(
                        IndicatorBase._DOT_DESKTOP_EXEC + '=' ) )

                starts_with_desktop_terminal = (
                    line.startswith(
                        IndicatorBase._DOT_DESKTOP_TERMINAL + '=' ) )

                if starts_with_autostart_enabled:
                    output += line
                    autostart_enabled_present = True

                elif starts_with_autostart_delay:
                    # Does not work in Debian et al.
                    # Capture the delay and comment out the line.
                    delay = line.split( '=' )[ 1 ].strip()
                    output += '#' + line
                    made_a_change = True

                elif starts_with_desktop_exec:
                    if "sleep" in line:
                        # Assume to be part of the install and not user created.
                        output += line
                        exec_with_sleep_present = True

                    else:
                        # Comment out and eventually replace with sleep version.
                        output += '#' + line
                        made_a_change = True

                elif starts_with_desktop_terminal:
                    output += line
                    terminal_present = True

                else:
                    output += line

#TODO Make shorter
        if not autostart_enabled_present or not exec_with_sleep_present or not terminal_present:
            # Extract the Exec (with sleep) line and X-GNOME-Autostart-enabled
            # line from the original .desktop file (production or development).
            if desktop_file_virtual_environment.exists():
                desktop_file_original = desktop_file_virtual_environment

            else:
                desktop_file_original = (
                    Path( __file__ ).parent / "platform" / "linux" / "indicatorbase.py.desktop" )

            with open( desktop_file_original, 'r', encoding = "utf-8" ) as f:
                for line in f:
                    if line.startswith( IndicatorBase._DOT_DESKTOP_AUTOSTART_ENABLED ) and not autostart_enabled_present:
                        output += line
                        made_a_change = True

                    elif line.startswith( IndicatorBase._DOT_DESKTOP_EXEC ) and not exec_with_sleep_present:
                        if delay:
                            output += line.replace( "{indicator_name}", self.indicator_name ).replace( '0', delay )

                        else:
                            output += line.replace( "{indicator_name}", self.indicator_name )

                        made_a_change = True

                    elif line.startswith( IndicatorBase._DOT_DESKTOP_TERMINAL ) and not terminal_present:
                        output += line
                        made_a_change = True

        if made_a_change:
#TODO Make shorter
            with open( self.desktop_file_user_home, 'w', encoding = "utf-8" ) as f:
                f.write( output )


    def _copy_dot_desktop_file_to_home_config_autostart(
        self,
        desktop_file_virtual_environment,
        desktop_file ):
        '''
        The .desktop file is not present in $HOME/.config/autostart
        so copy from the virtual environment (when running in production)
        or a .whl from the release directory (when running in development).
        '''
        if desktop_file_virtual_environment.exists():
            shutil.copy(
                desktop_file_virtual_environment,
                self.desktop_file_user_home )

            error_message = None

        else:
            wheel_in_release, error_message = (
                IndicatorBase._get_wheel_in_release( self.indicator_name ) )

            if wheel_in_release:
                with ZipFile( wheel_in_release, 'r' ) as z:
                    desktop_file_in_wheel = (
                        self.indicator_name +
                        "/platform/linux/" +
                        desktop_file )

                    if desktop_file_in_wheel in z.namelist():
                        desktop_file_in_tmp = (
                            z.extract( desktop_file_in_wheel, path = "/tmp" ) )

                        shutil.copy(
                            desktop_file_in_tmp,
                            self.desktop_file_user_home )

                    else:
                        error_message = (
                            f"Unable to locate { desktop_file_in_wheel } in " +
                            "{ wheel_in_release.absolute() }." )

                z.close()

        return error_message


    @staticmethod
    def get_authors_emails( project_metadata ):
        '''
        Extract the authors (and emails) from the project metadata.
        https://stackoverflow.com/a/75803208/2156453
        '''
        email_message_object = (
            email.message_from_string(
                f'To: { project_metadata[ "Author-email" ] }',
                policy = email.policy.default, ) )

        authors_emails = [ ]
        for address in email_message_object[ "to" ].addresses:
            authors_emails.append( [ address.display_name, address.addr_spec ] )

        return authors_emails


    @staticmethod
    def get_year_in_changelog_markdown(
        changelog_markdown,
        first_year = True ):
        '''
        If first_year = True, retrieves the first/earliest year from
        CHANGELOG.md otherwise retrieves the most recent year.
        '''
        year = ""
        with open( changelog_markdown, 'r', encoding = "utf-8" ) as f:
            lines = f.readlines()
            if first_year:
                lines = reversed( lines )

            for line in lines:
                if line.startswith( "## v" ):
                    left_parenthesis = line.find( '(' )
                    year = (
                        line[ left_parenthesis + 1 : left_parenthesis + 1 + 4 ] )

                    break

        return year


    @staticmethod
    def get_changelog_markdown_path():
        # Path under virtual environment.
        changelog = Path( __file__ ).parent / "CHANGELOG.md"

        if not Path( changelog ).exists():
            # Assume running in development.
            changelog = Path( '.' ).absolute() / "CHANGELOG.md"

        return changelog


    def main( self ):
        self.request_update()
        Gtk.main()


    def request_update(
        self,
        delay = 1 ):
        '''
        The typical flow of events is:
            Indicator starts up and kicks off an initial update.

            Subsequent updates are scheduled either by:
                The indicator returning the amount of seconds from now until
                the next update needs to occur.

                The user clicks OK in the Preferences.

                An indicator experiences and event and requests an update.
                For example, starting a virtual machine will request an update
                to refresh the menu.

            If there is a pending (future) update and a request for an update
            comes along, need to remove the "old" pending update.
        '''
        if self.lock_update.acquire( blocking = False ):
            if self.id_update > 0:
                GLib.source_remove( self.id_update )

            self.id_update = GLib.timeout_add_seconds( delay, self._update )
            self.lock_update.release()

        else:
            self.request_update(
                IndicatorBase._UPDATE_PERIOD_IN_SECONDS_DEFAULT )


    @abstractmethod
    def update(
        self,
        menu ):
        raise NotImplementedError()


    def _update( self ):
        update_start = datetime.datetime.now()

        # Disable the menu to prevent the user interacting and wreaking havoc.
        # The menu will be rebuilt as part of the update so there is no need to
        # set back to True.
        self.set_menu_sensitivity( False )

        # The user can nominate any menuitem as a secondary activate target
        # during menu construction.  However the secondary activate target can
        # only be set once the menu is built.  Therefore, keep a variable for
        # the user to set as needed.  Then set the secondary activate target
        # once the menu is built/shown.
        self.secondary_activate_target = None

        menu = Gtk.Menu()

        # Call to implementation in indicator.
        next_update_in_seconds = self.update( menu )

        if self.is_debug():
            menu_has_children = len( menu.get_children() ) > 0

            menu.prepend( Gtk.SeparatorMenuItem() )

            if next_update_in_seconds:
                next_update_date_time = (
                    datetime.datetime.now() + datetime.timedelta( seconds = next_update_in_seconds ) )

                label = (
                    "Next update: " +
                    str( next_update_date_time ).split( '.', maxsplit = 1 )[ 0 ] )

                menu.prepend( Gtk.MenuItem.new_with_label( label ) )

            label = (
                "Time to update: " +
                str( datetime.datetime.now() - update_start ) )

            menu.prepend( Gtk.MenuItem.new_with_label( label ) )

            if menu_has_children:
                menu.append( Gtk.SeparatorMenuItem() )

        else:
            if len( menu.get_children() ) > 0:
                menu.append( Gtk.SeparatorMenuItem() )

        titles = ( _( "Preferences" ), _( "About" ), _( "Quit" ) )
        functions = ( self._on_preferences, self._on_about, Gtk.main_quit )
        for title, function in zip( titles, functions ):
            self.create_and_append_menuitem(
                menu,
                title,
                activate_functionandarguments = ( function, ) )

        self.indicator.set_menu( menu )
        menu.show_all()

        self.indicator.set_secondary_activate_target(
            self.secondary_activate_target )

        self.id_update = 0
        if next_update_in_seconds:
            # Some indicators don't return a next update time.
            self.request_update( next_update_in_seconds )

        return False


    def set_label_or_tooltip(
        self,
        text ):
        '''
        Sets the label and tooltip assuming this is supported.
        Returns True if the operation is supported; False otherwise.
        For example, on Lubuntu 22.04 LXQt, there is no icon label and the
        tooltip contains the indicator source filename and so would return a
        False value.
        '''
        label_or_tooltip_update_supported = (
            self._is_label_or_tooltip_update_supported() )

        if label_or_tooltip_update_supported:
            self.indicator.set_label( text, text )
            self.indicator.set_title( text )

        return label_or_tooltip_update_supported


    def set_icon(
        self,
        icon ):
        '''
        Sets the icon assuming this is supported.
        Returns True if the operation is supported; False otherwise.
        For example, on Lubuntu 22.04 LXQt, the icon cannot be changed once set
        and so would return a False value.
        '''
        icon_update_supported = self._is_icon_update_supported()
        if icon_update_supported:
            self.indicator.set_icon_full( icon, "" )

        return icon_update_supported


    def get_icon_name( self ):
        '''
        Get the name of the icon for the indicator to be passed to the desktop
        environment for display.

        GTK will take an icon and display it as expected.

        The exception is if the icon filename ends with "-symbolic" (before the
        extension).

        In this case, GTK will take the colour in the icon (say a generic flat
        #777777) and replace it with a suitable colour to make the current
        theme/background/colour.

        Refer to this discussion:
            https://discourse.gnome.org/t/what-colour-to-use-for-a-custom-adwaita-icon/19064

        If the icon with "-symbolic" cannot be found, it appears the desktop
        environment as a fallback will look for the icon name without the
        "-symbolic" which is the hicolor.

        When updating/replacing an icon, the desktop environment appears to
        cache.  So perhaps first try:

            sudo touch $HOME/.local/share/icons/hicolor && sudo gtk-update-icon-cache

        and if that fails, either log out/in or restart.
        '''
        return self.indicator_name + "-symbolic"


    def is_debug( self ):
        return self.debug


    def show_notification(
        self,
        summary,
        message,
        icon = None ):

        _icon = icon
        if icon is None:
            _icon = self.get_icon_name()

        if isinstance( _icon, PosixPath ):
            _icon = str( _icon )

        Notify.Notification.new( summary, message, _icon ).show()


    def set_secondary_activate_target(
        self,
        menuitem ):

        self.secondary_activate_target = menuitem


    def request_mouse_wheel_scroll_events(
        self,
        functionandarguments ):
        '''
        Registers a function (and arguments) to be called on mouse wheel scroll.

        The function must have the form:

            def on_mouse_wheel_scroll(
                self, indicator, delta, scroll_direction )

        The name of the function may be any name.
        The arguments must be present as specified.
        Additional arguments may be specified.
        '''
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

        if self.indicator.get_menu().get_children()[ 0 ].get_sensitive():
#TODO Check this comment...correct working and placement?
            # Disabled during update/Preferences/About
            if len( functionandarguments ) == 1:
                functionandarguments[ 0 ]( indicator, delta, scroll_direction )

            else:
                functionandarguments[ 0 ](
                    indicator,
                    delta,
                    scroll_direction,
                    *functionandarguments[ 1 : ] )


    def get_session_type( self ):
        return self.process_get( "echo $XDG_SESSION_TYPE" )


    def is_session_type_wayland( self ):
        return self.get_session_type() == IndicatorBase.SESSION_TYPE_WAYLAND


    def is_session_type_x11( self ):
        return self.get_session_type() == IndicatorBase.SESSION_TYPE_X11


    def _on_about(
        self,
        menuitem ):

        self.set_menu_sensitivity( False )
        self.indicator.set_secondary_activate_target( None )

        about_dialog = Gtk.AboutDialog()
        about_dialog.set_transient_for( menuitem.get_parent().get_parent() )

        authors_and_websites = [ ]
        for author_and_email in self.authors_and_emails:
            authors_and_websites.append(
                author_and_email[ 0 ] + " " + self.website )

        about_dialog.set_authors( authors_and_websites )
        about_dialog.set_artists(
            self.artwork if self.artwork else authors_and_websites )

        about_dialog.set_comments( self.comments )

        changelog_markdown_path = IndicatorBase.get_changelog_markdown_path()

        authors = [
                author_and_email[ 0 ]
                for author_and_email in self.authors_and_emails ]

        about_dialog.set_copyright(
            "Copyright \xa9 "
            +
            IndicatorBase.get_year_in_changelog_markdown(
                changelog_markdown_path )
            +
            '-'
            +
            str( datetime.datetime.now().year )
            +
            " "
            +
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
        self.indicator.set_secondary_activate_target(
            self.secondary_activate_target )


    def _add_hyperlink_label(
        self,
        about_dialog,
        file_path,
        left_text,
        anchor_text,
        right_text ):

        file_ = f"\'file://{ str( file_path ) }\'"
        title = f"title=\'file://{ str( file_path ) }\'>"

        markup = (
            f"{ left_text }" +
            f" <a href={ file_ } { title }{ anchor_text }</a> " +
            f"{ right_text }" )

        label = Gtk.Label()
        label.set_markup( markup )
        label.show()
        about_dialog.get_content_area().get_children()[
            0 ].get_children()[
                2 ].get_children()[
                    0 ].pack_start( label, False, False, 0 )


    @abstractmethod
    def on_preferences(
        self,
        dialog ):

        raise NotImplementedError()


    def _on_preferences(
        self,
        menuitem ):

        self.set_menu_sensitivity( False )
        self.indicator.set_secondary_activate_target( None )

        dialog = self.create_dialog( menuitem, _( "Preferences" ) )

        # Call to implementation in indicator.
        response_type = self.on_preferences( dialog )
        dialog.destroy()

        if response_type == Gtk.ResponseType.OK:
            self.request_save_config()

            # Allow a second for the lock to release so the update will proceed.
            self.request_update( 1 )

        else:
            self.set_menu_sensitivity( True )
            self.indicator.set_secondary_activate_target(
                self.secondary_activate_target )


    def set_menu_sensitivity(
        self,
        toggle ):

        menuitems = self.indicator.get_menu().get_children()
        # On the first update, the menu only contains the "initialising"
        # menu item, so ignore.
        if len( menuitems ) > 1:
            for menuitem in self.indicator.get_menu().get_children():
                menuitem.set_sensitive( toggle )


    def is_calendar_supported( self ):
        '''
        The calendar package is unavailable on some distributions.
        '''
        etc_os_release = self.process_get( "cat /etc/os-release" )

        is_manjaro = "NAME=\"Manjaro Linux\"" in etc_os_release

        is_opensuse_tumbleweed = (
            "NAME=\"openSUSE Tumbleweed\"" in etc_os_release )

        return not is_manjaro and not is_opensuse_tumbleweed


#TODO Where is clipboard used?
# indicatorfortune
# indicatoronthisday
# indicatorpunycode
# indicatortest
#
# Clipboard should now work on X11 and Wayland, so no issue here.
#
# EXCEPT: Under Ubuntu 20.04 Wayland, clipboard causes a logout.
# So test clipboard on Wayland for all other distros.
# Note in readme the bad distros.
# What else to do?  Block the call to clipboard for these distros?
# Tell the user in a tooltip?
# Show a notification?
# Hide the option/functionality from the user?
#
# Works on both X11 and Wayland for distro...
#   Debian 11
#   Debian 12
#   Fedora 38
#   Fedora 39
#   Fedora 40
#   Manjaro KDE
#   openSUSE
#   Ubuntu 22.04
#   Ubuntu 24.04
#
#   Ubuntu 20.04  Works on X11 but logs out on Wayland.
#
#
# Seems to also be an issue on Debian 12 32 bit wayland.

    def is_clipboard_supported( self ):
        '''
        On Ubuntu 20.04 when calling wl-copy/wl-paste under Wayland, due to a
        bug in GNOME, the destkop session crashes:

            https://gitlab.gnome.org/GNOME/mutter/-/issues/1690

        Unfortunately this issue never got fixed for the version of GNOME used
        in Ubuntu 20.04.
        '''
        clipboard_supported = True
        if self.is_session_type_wayland():
            etc_os_release = self.process_get( "cat /etc/os-release" )
            clipboard_supported = (
                "ID=ubuntu" in etc_os_release
                and
                "VERSION_ID=\"20.04\"" in etc_os_release )

        return clipboard_supported


    def copy_to_selection(
        self,
        text,
        is_primary = False ):
        '''
        Send text to the clipboard or primary.
        '''
        if self.is_clipboard_supported():
            if self.is_session_type_wayland():
#TODO Make shorter
                with tempfile.NamedTemporaryFile( mode = 'w', delete = False ) as temporary_named_file:
                    temporary_named_file.write( text )

                command = "wl-copy "
                if is_primary:
                    command += "--primary "

                command += "< "

                self.process_call( command + temporary_named_file.name )
                Path( temporary_named_file.name ).unlink( missing_ok = True )

            else:
                selection = Gdk.SELECTION_CLIPBOARD
                if is_primary:
                    selection = Gdk.SELECTION_PRIMARY

                Gtk.Clipboard.get( selection ).set_text( text, -1 )


    def copy_from_selection_clipboard( self ):
        '''
        Obtains text from the clipboard.
        If there was no text copied or an error occurred, None is returned.
        '''
        text_in_clipboard = None
        if self.is_clipboard_supported():
            if self.is_session_type_wayland():
                text_in_clipboard = self.process_get( "wl-paste" )

            else:
                text_in_clipboard = (
                    Gtk.Clipboard.get(
                        Gdk.SELECTION_CLIPBOARD ).wait_for_text() )

        return text_in_clipboard


    def copy_from_selection_primary(
        self,
        primary_received_callback_function ):
        '''
        To receive the text from the primary input, a callback function
        is required, the simplest of which for example is:

            def primary_received_callback_function( text ):
                print( text )

        On success, the text parameter to the callback function
        will contain the primary text; otherwise None.
        '''
        if self.is_clipboard_supported():
            if self.is_session_type_wayland():
                # GTK interacts with the X11 clipboard mechanism via a user
                # callback function to receive the selection, whereas under
                # Wayland, this is not the case.
                #
                # There is presently no GTK method for accessing the clipboard
                # under Wayland.  Instead, the package wl-clipboard is used
                # directly via a terminal, requiring no callback function.
                #
                # To shield the user from having to know whether Wayland or X11
                # is in use, access to the primary is wrapped within a callback
                # function.
                primary_received_callback_function(
                    self.process_get( "wl-paste --primary" ) )

            else:
                Gtk.Clipboard.get( Gdk.SELECTION_PRIMARY ).request_text(
                    self._clipboard_text_received_function,
                    primary_received_callback_function )


    def _clipboard_text_received_function(
        self,
        clipboard,
        text,
        primary_received_callback_function ):
        '''
        A callback function is required by GTK to obtain text from the primary
        when running under X11:

            https://lazka.github.io/pgi-docs/#Gtk-3.0/classes/Clipboard.html#Gtk.Clipboard.request_text

        When running under Wayland, the package wl-paste is called directly
        and no callback is required.

        However, so that a user can retrieve the text from the primary without
        having to know whether running under X11 or Wayland, the Wayland method
        also uses the same callback mechanism.
        '''
        primary_received_callback_function( text )


    def get_play_sound_complete_command( self ):
        return "paplay /usr/share/sounds/freedesktop/stereo/complete.oga"


    def create_dialog(
        self,
        parent_widget,
        title,
        content_widget = None,
        buttons_responsetypes = (
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OK, Gtk.ResponseType.OK ),
        default_size = None ):

        dialog = (
            Gtk.Dialog(
                title,
                self._get_parent( parent_widget ),
                Gtk.DialogFlags.MODAL ) )

        dialog.add_buttons( *buttons_responsetypes )

        if default_size:
            dialog.set_default_size( *default_size )

        if content_widget:
            dialog.get_content_area().pack_start(
                content_widget, True, True, 0 )

        dialog.set_border_width( 5 )

        return dialog


    def show_dialog_ok_cancel(
        self,
        parent_widget,
        message,
        title = None ):

        return (
            self._show_dialog(
                parent_widget,
                message,
                Gtk.MessageType.QUESTION,
                Gtk.ButtonsType.OK_CANCEL,
                title = title ) )


    def show_dialog_ok(
        self,
        parent_widget,
        message,
        title = None,
        message_type = Gtk.MessageType.ERROR ):

        return (
            self._show_dialog(
                parent_widget,
                message,
                message_type,
                Gtk.ButtonsType.OK,
                title = title ) )


    def _show_dialog(
        self,
        parent_widget,
        message,
        message_type,
        buttons_type,
        title = None ):

        dialog = (
            Gtk.MessageDialog(
                self._get_parent( parent_widget ),
                Gtk.DialogFlags.MODAL,
                message_type,
                buttons_type,
                message ) )

        dialog.set_title( self.indicator_name if title is None else title )

        for child in dialog.get_message_area().get_children():
            if isinstance( child, Gtk.Label ):
                # Allow the label to be highlighted for copy/paste.
                child.set_selectable( True )

        response = dialog.run()
        dialog.destroy()
        return response


    def _get_parent(
        self,
        widget ):

        parent = widget
        while parent is not None:
            if isinstance( parent, ( Gtk.Dialog, Gtk.Window ) ):
                # Stop when the widget is a Dialog/Window.
                break

            parent = parent.get_parent()

        return parent


    def create_preferences_common_widgets( self ):
        autostart = False
        delay = 0
        with open( self.desktop_file_user_home, 'r', encoding = "utf-8" ) as f:
            autostart_enable_equals_true = (
                IndicatorBase._DOT_DESKTOP_AUTOSTART_ENABLED + "=true" )

            for line in f:
                if line.startswith( autostart_enable_equals_true ):
                    autostart = True

                starts_with_dot_desktop_exec = (
                    line.startswith( IndicatorBase._DOT_DESKTOP_EXEC ) )

                if starts_with_dot_desktop_exec and "sleep" in line:
                    delay = int(
                        line.split( "sleep" )[ 1 ].split( "&&" )[ 0 ].strip() )

        autostart_checkbox = (
            self.create_checkbutton(
                _( "Autostart" ),
                tooltip_text = _( "Run the indicator automatically." ),
                active = autostart ) )

        autostart_spinner = (
            self.create_spinbutton(
                delay,
                0,
                1000,
                tooltip_text = _( "Start up delay (seconds)." ),
                sensitive = autostart_checkbox.get_active() ) )

        autostart_checkbox.connect(
            "toggled",
            self.on_radio_or_checkbox,
            True,
            autostart_spinner )

        box_autostart = (
            self.create_box(
                (
                    ( autostart_checkbox, False ),
                    ( autostart_spinner, False ) ),
                margin_top = IndicatorBase.INDENT_WIDGET_TOP ) )

        latest_version_checkbox = (
            self.create_checkbutton(
                _( "Check Latest Version" ),
                tooltip_text = _(
                    "Check for the latest version " +
                    "of the indicator on start up." ),
                active = self.check_latest_version ) )

        box_latest_version = (
            self.create_box(
                ( ( latest_version_checkbox, False ), ),
                margin_top = IndicatorBase.INDENT_WIDGET_TOP ) )

        if self.new_version_available and self.check_latest_version:
            url = f"https://pypi.org/project/{ self.indicator_name }"
            label = Gtk.Label.new()
            label.set_markup( _(
                "An update is available at " +
                "<a href=\"{0}\">{1}</a>." ).format( url, url ) )

            box_new_version = (
                self.create_box(
                    ( ( label, False ), ),
                    orientation = Gtk.Orientation.VERTICAL ) )

            boxes = (
                ( ( box_autostart, False ),
                  ( box_latest_version, False ),
                  ( box_new_version, False ) ) )

        else:
            boxes = (
                ( ( box_autostart, False ),
                  ( box_latest_version, False ) ) )

        box = self.create_box( boxes, orientation = Gtk.Orientation.VERTICAL )

        return (
            autostart_checkbox,
            autostart_spinner,
            latest_version_checkbox,
            box )


    def create_and_append_menuitem(
        self,
        menu,
        label,
        name = None,
        activate_functionandarguments = None,
        indent = ( 0, 0 ),
        is_secondary_activate_target = False ):
        '''
        indent:
            First element: indent level when adding to a non-detachable menu.
            Second element: equivalent for a detachable menu.
        '''

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
        indent = ( 0, 0 ),
        is_secondary_activate_target = False ):
        '''
        indent:
            First element: indent level when adding to a non-detachable menu.
            Second element: equivalent for a detachable menu.
        '''

        menuitem = (
            self.create_and_append_menuitem(
                menu,
                label,
                name = name,
                activate_functionandarguments = activate_functionandarguments,
                indent = indent,
                is_secondary_activate_target = is_secondary_activate_target ) )

        menu.reorder_child( menuitem, index )
        return menuitem


    def create_and_append_radiomenuitem(
        self,
        menu,
        label,
        activate_functionandarguments = None,
        indent = ( 0, 0 ) ):
        '''
        Creates a single (isolated, not part of a group) RadioMenuItem that is
        enabled/active.

        indent:
            First element: indent level when adding to a non-detachable menu.
            Second element: equivalent for a detachable menu.
        '''

        indent_amount = self._get_menu_indent_amount( indent )
        menuitem = (
            Gtk.RadioMenuItem.new_with_label( [ ], indent_amount + label ) )

        menuitem.set_active( True )

        if activate_functionandarguments:
            menuitem.connect( "activate", *activate_functionandarguments )

        menu.append( menuitem )
        return menuitem


    def _get_menu_indent_amount(
        self,
        indent = ( 0, 0 ) ):
        '''
        When adding a menuitem to a submenu,
        under GNOME the menuitem appears in the same menu as the submenu
        and requires an indent added to look correct.

        Under Kubuntu et al, menuitems of a submenu appear as a separate,
        detached menu and so require no indent.

        The first value of the indent argument refers to the indent for
        a submenu's menuitems under GNOME and similar layouts.
        The second value of the indent argument refers to the indent for
        a submenu's menuitems under Kubuntu and similar layouts.
        '''

        indent_amount = "      "
        indent_small = (
            self.get_current_desktop() == IndicatorBase._DESKTOP_KDE )

        if indent_small:
            indent_amount = "   "

        detatched_submenus = (
            self.get_current_desktop() == IndicatorBase._DESKTOP_BUDGIE_GNOME or
            self.get_current_desktop() == IndicatorBase._DESKTOP_ICEWM or
            self.get_current_desktop() == IndicatorBase._DESKTOP_KDE or
            self.get_current_desktop() == IndicatorBase._DESKTOP_LXQT or
            self.get_current_desktop() == IndicatorBase._DESKTOP_MATE or
            self.get_current_desktop() == IndicatorBase._DESKTOP_UNITY7 or
            self.get_current_desktop() == IndicatorBase._DESKTOP_X_CINNAMON or
            self.get_current_desktop() == IndicatorBase._DESKTOP_XFCE )

        if detatched_submenus:
            indent_amount = indent_amount * indent[ 1 ]

        else:
            indent_amount = indent_amount * indent[ 0 ]

        return indent_amount


    def get_on_click_menuitem_open_browser_function( self ):
        return lambda menuitem: webbrowser.open( menuitem.get_name() )


    def get_textview_text(
        self,
        textview ):
        '''
        Takes a Gtk.TextView and returns the containing text, avoiding the
        additional calls to get the start/end positions.
        '''
        textview_buffer = textview.get_buffer()
        return (
            textview_buffer.get_text(
                textview_buffer.get_start_iter(),
                textview_buffer.get_end_iter(),
                True ) )


    def on_radio_or_checkbox(
        self,
        radio_or_checkbox,
        sense,
        *widgets ):
        '''
        Listens to radio/checkbox "toggled" events and toggles the visibility
        of the widgets according to the boolean value of 'sense'.
        '''
        for widget in widgets:
            widget.set_sensitive( sense and radio_or_checkbox.get_active() )


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


    def create_scrolledwindow(
        self,
        widget ):

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
        orientation = Gtk.Orientation.HORIZONTAL,
        halign = Gtk.Align.FILL,
        homogeneous = False ):

        box = Gtk.Box( spacing = spacing, orientation = orientation )
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
        '''
        TODO Explain return values
        '''

        buttons_and_expands = [ ]
        z = zip( labels, tooltip_texts, clicked_functionandarguments )
        for label, tooltip_text, clicked_functionandargument in z:
            button = (
                self.create_button(
                    label,
                    tooltip_text = tooltip_text,
                    clicked_functionandarguments =
                        clicked_functionandargument ) )

            buttons_and_expands.append( [ button, True ] )

        buttons = [
            button_and_expand[ 0 ]
            for button_and_expand in buttons_and_expands ]

        return (
            self.create_box(
                tuple( buttons_and_expands ),
                halign = Gtk.Align.CENTER,
                homogeneous = True ),
            *buttons )


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
        active = -1,
        editable = False ):

        if editable:
            comboboxtext = Gtk.ComboBoxText.new_with_entry()

        else:
            comboboxtext = Gtk.ComboBoxText.new()

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
        clicked_functionandarguments = None ):
        '''
        clicked_functionandarguments:
            Must be passed as a tuple.
            https://stackoverflow.com/a/6289656/2156453
       '''

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

        spinner.set_adjustment(
            Gtk.Adjustment.new(
                value, lower, upper, step_increment, page_increment, 0 ) )

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

        radiobutton = (
            Gtk.RadioButton.new_with_label_from_widget(
                radio_group_member, label ) )

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
        default_sort_func = None,
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
            Tuple of tuples, each contains the Gtk.CellRenderer,
            data type and model column id for the column view.
            Columns will not be expanded as if calling
                treeviewcolumn.pack_start( renderer, False ).
            A tuple (for a given model column id) may contain tuples,
            each of which is for a different renderer.

        alignments_columnviewids:
            Tuple of tuples, each contains the xalign and view column id.

        default_sort_func:
            Name of a comparison function to sort rows.

        sortcolumnviewids_columnmodelids:
            Tuple of tuples, each of which contains the view column id and
            corresponding model column id.
            The first column will be set as default sorted ascending.

        celldatafunctionandarguments_renderers_columnviewids:
            Tuple of tuples, each contains a cell data renderer function,
            parameters to the function, a cell data renderer (the SAME renderer
            passed in to the renderers_attributes_columnmodelids) and the view
            column id.

        clickablecolumnviewids_functionsandarguments:
            Tuple of tuples, each contains the view column id and a
            corresponding function (and parameters) to be called on column
            header click.

        tooltip_text: Tooltip text for the entire TreeView.

        cursorchangedfunctionandarguments:
            A function (and parameters) to call on row selection.

        rowactivatedfunctionandarguments:
            A function (and parameters) to call on row double click.
        '''
        treeview = Gtk.TreeView.new_with_model( treemodel )

        z = zip( titles, renderers_attributes_columnmodelids )
        for index, ( title, renderer_attribute_columnmodelid ) in enumerate( z ):
            treeviewcolumn = Gtk.TreeViewColumn( title )

            # Expand the column unless the column contains a single checkbox
            # and no column header title.
            is_checkbox_column = (
                isinstance(
                    renderer_attribute_columnmodelid[ 0 ],
                    Gtk.CellRendererToggle )
                and
                not title )

            treeviewcolumn.set_expand( not is_checkbox_column )

            # Add the renderer / attribute / column model id for each column.
            is_single_tuple = (
                not isinstance( renderer_attribute_columnmodelid[ 0 ], tuple ) )

            if is_single_tuple:
                treeviewcolumn.pack_start(
                    renderer_attribute_columnmodelid[ 0 ], False )

                treeviewcolumn.add_attribute(
                    *renderer_attribute_columnmodelid )

            else:
                # Assume a tuple of tuples of
                #   renderer, attribute, column model id.
#TODO Make shorter
                for renderer, attribute, columnmodelid in renderer_attribute_columnmodelid:
                    treeviewcolumn.pack_start( renderer, False )
                    treeviewcolumn.add_attribute(
                        renderer, attribute, columnmodelid )

            if alignments_columnviewids:
                alignment = [
                    alignment_columnviewid[ 0 ]
                    for alignment_columnviewid in alignments_columnviewids
                    if alignment_columnviewid[ 1 ] == index ]

                if alignment:
                    treeviewcolumn.set_alignment( alignment[ 0 ] )
                    current_alignment = (
                        renderer_attribute_columnmodelid[ 0 ].get_alignment() )

                    renderer_attribute_columnmodelid[ 0 ].set_alignment(
                        alignment[ 0 ],
                        current_alignment[ 1 ] )

            treeview.append_column( treeviewcolumn )

        if default_sort_func:
            treemodel.set_default_sort_func( default_sort_func, None )
            treemodel.set_sort_column_id(
                Gtk.TREE_SORTABLE_DEFAULT_SORT_COLUMN_ID,
                Gtk.SortType.ASCENDING )

#TODO Need to look at sorting again...
# Not sure what the difference is between
#    treeviewcolumn.set_sort_column_id
# and
#    treemodel.set_sort_column_id
#...and how does it relate or not to clickable column view ids below?
# https://python-gtk-3-tutorial.readthedocs.io/en/latest/treeview.html
# https://lazka.github.io/pgi-docs/Gtk-3.0/classes/TreeSortable.html#Gtk.TreeSortable.set_sort_column_id
# https://lazka.github.io/pgi-docs/Gtk-3.0/classes/TreeViewColumn.html#Gtk.TreeViewColumn.set_sort_column_id
# https://stackoverflow.com/questions/18954160/sort-a-column-in-a-treeview-by-default-or-programmatically
# https://stackoverflow.com/questions/55167884/python-gtk-3-sorting-a-treeview-by-clicking-on-column
# https://stackoverflow.com/questions/53158803/gtk-tree-view-with-filter-and-sorting
# https://stackoverflow.com/questions/18234513/python-sort-a-gtk-treeview
# https://stackoverflow.com/questions/55167884/python-gtk-3-sorting-a-treeview-by-clicking-on-column/70108852
# https://stackoverflow.com/questions/12368059/a-sorted-and-filtered-treemodel-in-python-gtk3
# https://stackoverflow.com/questions/9194588/how-to-programmatically-sort-treeview
# https://python-gtk-3-tutorial.readthedocs.io/en/latest/treeview.html
#
# I think this is now okay...better check with ALL tables in all indicators.
#
# TODO I think this is only used in lunar for the icon text values and satellites.
        if sortcolumnviewids_columnmodelids:
            for columnviewid, columnmodelid in sortcolumnviewids_columnmodelids:
                for indexcolumn, treeviewcolumn in enumerate( treeview.get_columns() ):
                    if columnviewid == indexcolumn:
                        treeviewcolumn.set_sort_column_id( columnmodelid )
                        if sortcolumnviewids_columnmodelids.index( ( columnviewid, columnmodelid ) ) == 0:
                            # Set first sorted column as default ascending.
                            treemodel.set_sort_column_id(
                                columnmodelid,
                                Gtk.SortType.ASCENDING )

        if celldatafunctionandarguments_renderers_columnviewids:
#TODO Make shorter
            for data_function_and_arguments, renderer, columnviewid in celldatafunctionandarguments_renderers_columnviewids:
                for index, treeviewcolumn in enumerate( treeview.get_columns() ):
                    if columnviewid == index:
                        treeviewcolumn.set_cell_data_func(
                            renderer,
                            *data_function_and_arguments )

        if clickablecolumnviewids_functionsandarguments:
#TODO Make shorter
            for columnviewid_functionandarguments in clickablecolumnviewids_functionsandarguments:
                for index, treeviewcolumn in enumerate( treeview.get_columns() ):
                    if columnviewid_functionandarguments[ 0 ] == index:
                        treeviewcolumn.set_clickable( True )
                        treeviewcolumn.connect(
                            "clicked",
                            *columnviewid_functionandarguments[ 1 ] )

        treeview.set_tooltip_text( tooltip_text )
        treeview.get_selection().set_mode( Gtk.SelectionMode.BROWSE )
        treeview.expand_all()
        treeview.set_hexpand( True )
        treeview.set_vexpand( True )

        if cursorchangedfunctionandarguments:
            treeview.connect(
                "cursor-changed", *cursorchangedfunctionandarguments )

        if rowactivatedfunctionandarguments:
            treeview.connect(
                "row-activated", *rowactivatedfunctionandarguments )

        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.set_policy(
            Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC )

        scrolledwindow.add( treeview )

        return treeview, scrolledwindow


    def create_filechooser_dialog(
        self,
        title,
        parent,
        filename,
        action = Gtk.FileChooserAction.OPEN ):

        dialog = (
            Gtk.FileChooserDialog(
                title = title,
                parent = parent,
                action = action ) )

        dialog.add_buttons(
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN,
            Gtk.ResponseType.OK )

        dialog.set_transient_for( parent )
        dialog.set_filename( filename )
        return dialog


    def set_preferences_common_attributes(
        self,
        is_set,
        delay,
        check_latest_version ):

        self.check_latest_version = check_latest_version

        output = ""
        with open( self.desktop_file_user_home, 'r', encoding = "utf-8" ) as f:
            for line in f:
                line_starts_with_dot_desktop_autostart_enabled = (
                    line.startswith(
                        IndicatorBase._DOT_DESKTOP_AUTOSTART_ENABLED ) )

                if line_starts_with_dot_desktop_autostart_enabled:
                    output += (
                        IndicatorBase._DOT_DESKTOP_AUTOSTART_ENABLED +
                        '=' +
                        str( is_set ).lower() +
                        '\n' )

                elif line.startswith( IndicatorBase._DOT_DESKTOP_EXEC ):
                    parts = line.split( "sleep" )
                    right = parts[ 1 ].split( "&&" )[ 1 ]
                    output += (
                        parts[ 0 ] +
                        "sleep " + str( delay ) +
                        " &&" +
                        right +
                        '\n' )

                else:
                    output += line

        with open( self.desktop_file_user_home, 'w', encoding = "utf-8" ) as f:
            f.write( output )


    @staticmethod
    def get_menuitems_guess():
        '''
        Estimate the number of menu items which will fit into an indicator menu
        without exceeding the screen height.
        '''

        screen_heights_in_pixels = [ 600, 768, 800, 900, 1024, 1050, 1080 ]
        numbers_of_menuitems = [ 15, 15, 15, 20, 20, 20, 20 ]

        screen_height_in_pixels = Gtk.Window().get_screen().get_height()
        if screen_height_in_pixels < screen_heights_in_pixels[ 0 ]:
            number_of_menuitems = (
                numbers_of_menuitems[ 0 ]
                *
                screen_height_in_pixels
                /
                screen_heights_in_pixels[ 0 ] ) # Best guess.

        elif screen_height_in_pixels > screen_heights_in_pixels[ -1 ]:
            number_of_menuitems = (
                numbers_of_menuitems[ -1 ]
                *
                screen_height_in_pixels
                /
                screen_heights_in_pixels[ -1 ] ) # Best guess.

        else:
            number_of_menuitems = (
                IndicatorBase.interpolate(
                    screen_heights_in_pixels,
                    numbers_of_menuitems,
                    screen_height_in_pixels ) )

        return number_of_menuitems


    @staticmethod
    def interpolate(
        x_values,
        y_values,
        x ):
        '''
        Reference: https://stackoverflow.com/a/56233642/2156453
        '''
        if not x_values[ 0 ] <= x <= x_values[ -1 ]:
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


    def get_logging( self ):
        return logging


    def is_number(
        self,
        number_as_string ):

        try:
            float( number_as_string )
            return True

        except ValueError:
            return False


    def get_current_desktop( self ):
        return self.current_desktop


    def _is_label_or_tooltip_update_supported( self ):
        '''
        Lubuntu 20.04/22.04 does not support setting/updating of icon
        label/tooltip.
        '''
        desktop_environment = self.get_current_desktop()
        label_or_tooltip_update_unsupported = (
            desktop_environment is None
            or
            desktop_environment == IndicatorBase._DESKTOP_ICEWM
            or
            desktop_environment == IndicatorBase._DESKTOP_LXQT )

        return not label_or_tooltip_update_unsupported


    def _is_icon_update_supported( self ):
        ''' Lubuntu 20.04/22.04 does not support updating of icon once set. '''
        desktop_environment = self.get_current_desktop()
        icon_update_unsupported = (
            desktop_environment is None
            or
            desktop_environment == IndicatorBase._DESKTOP_LXQT )

        return not icon_update_unsupported


    def is_qterminal_and_broken(
        self,
        terminal ):
        '''
        As a result of
            https://github.com/lxqt/qterminal/issues/335
        determine if qterminal is the current terminal and of a broken version.
        Fixed in version 1.2.0
            https://github.com/lxqt/qterminal/releases
        '''
        is_qterminal_and_broken_ = False
        if "qterminal" in terminal:
            is_qterminal_and_broken_ = (
                self.process_get( "qterminal --version" ) < "1.2.0" )

        return is_qterminal_and_broken_


    def get_terminal_and_execution_flag( self ):
        '''
        Return the full path and name of the executable for the current terminal
        and the corresponding execution flag; None otherwise.
        '''
        terminal = None
        execution_flag = None
#TODO Make shorter
        for _terminal, _execution_flag in IndicatorBase._TERMINALS_AND_EXECUTION_FLAGS:
            terminal = self.process_get( "which " + _terminal )
            if terminal:
                execution_flag = _execution_flag
                break

        return terminal, execution_flag


    @staticmethod
    def download(
        url,
        filename,
        logging_ ):
        ''' Download the contents of the given URL and save to file. '''
        downloaded = False
        try:
#TODO Make shorter
            with urlopen( url, timeout = IndicatorBase.TIMEOUT_IN_SECONDS ) as f_in:
                with open( filename, 'w', encoding = "utf-8" ) as f_out:
                    f_out.write( f_in.read().decode() )

            downloaded = True

        except URLError as e:
            logging_.error( "Error downloading from " + str( url ) )
            logging_.exception( e )

        return downloaded


    @abstractmethod
    def load_config(
        self,
        config ):

        raise NotImplementedError()


    def _load_config( self ):
        ''' Read a dictionary of configuration from a JSON text file. '''
        config_file = (
            self._get_config_directory() / ( self.indicator_name + IndicatorBase._EXTENSION_JSON ) )

        self._copy_config_to_new_directory( config_file )

        config = { }
        if config_file.is_file():
            with open( config_file, 'r', encoding = "utf-8" ) as f_in:
                config = json.load( f_in )

        self.load_config( config ) # Call to implementation in indicator.

        if IndicatorBase._CONFIG_CHECK_LATEST_VERSION not in config:
            config[ IndicatorBase._CONFIG_CHECK_LATEST_VERSION ] = False

        self.check_latest_version = (
            config[ IndicatorBase._CONFIG_CHECK_LATEST_VERSION ] )


    def _copy_config_to_new_directory(
        self,
        config_file ):
        '''
        Copies .config using the old indicator name format (using hyphens)
        to the new format, sans hyphens.
        '''
        mapping = {
            "indicatorfortune":               "indicator-fortune",
            "indicatorlunar":                 "indicator-lunar",
            "indicatoronthisday":             "indicator-on-this-day",
            "indicatorppadownloadstatistics": "indicator-ppa-download-statistics",
            "indicatorpunycode":              "indicator-punycode",
            "indicatorscriptrunner":          "indicator-script-runner",
            "indicatorstardate":              "indicator-stardate",
            "indicatortide":                  "indicator-tide",
            "indicatortest":                  "indicator-test",
            "indicatorvirtualbox":            "indicator-virtual-box" }

        config_file_old = (
            str( config_file ).replace(
                self.indicator_name, mapping[ self.indicator_name ] ) )

        config_file_old = Path( config_file_old )

        if not config_file.is_file() and config_file_old.is_file():
            shutil.copyfile( config_file_old, config_file )


    def request_save_config(
        self,
        delay = 0 ):

        if self.lock_save_config.acquire( blocking = False ):
            if self.id_save_config > 0:
                GLib.source_remove( self.id_save_config )

            self.id_save_config = (
                GLib.timeout_add_seconds( delay, self._save_config ) )

            self.lock_save_config.release()

        else:
            self.request_save_config(
                IndicatorBase._UPDATE_PERIOD_IN_SECONDS_DEFAULT )


    @abstractmethod
    def save_config( self ):
        raise NotImplementedError()


    def _save_config( self ):
        ''' Write a dictionary of user configuration to a JSON text file. '''
        config = self.save_config() # Call to implementation in indicator.
        config[ IndicatorBase._CONFIG_VERSION ] = self.version
        config[ IndicatorBase._CONFIG_CHECK_LATEST_VERSION ] = (
            self.check_latest_version )

        config_file = (
            self._get_config_directory() / ( self.indicator_name + IndicatorBase._EXTENSION_JSON ) )

        with open( config_file, 'w', encoding = "utf-8" ) as f_out:
            f_out.write( json.dumps( config ) )

        self.id_save_config = 0
        return False


    def _get_config_directory( self ):
        '''
        Return the full directory path to the user config directory for the
        current indicator.
        '''
        return self._get_user_directory( ".config", self.indicator_name )


    def is_cache_stale(
        self,
        basename,
        maximum_age_in_hours ):
        '''
        Finds the most recent file in the cache with the given basename and if
        the timestamp is older than the current date/time plus the maximum age,
        returns True, otherwise False. If no file can be found, returns True.
        '''
        cache_date_time = self.get_cache_date_time( basename )
        if cache_date_time is None:
            stale = True

        else:
            cache_date_time_plus_maximum_age = (
                cache_date_time +
                datetime.timedelta( hours = maximum_age_in_hours ) )

            utc_now = datetime.datetime.now( datetime.timezone.utc )

            stale = cache_date_time_plus_maximum_age < utc_now

        return stale


    def get_cache_date_time(
        self,
        basename ):
        '''
        Find the date/time of the newest file in the cache matching the
        basename, where the basename is the text used to form the file name,
        typically the name of the calling application.
        Returns the datetime of the newest file in the cache;
        None if no file can be found.
        '''
        expiry = None
        the_file = ""
        for file in self.get_cache_directory().iterdir():
            if file.name.startswith( basename ) and file.name > the_file:
                the_file = file.name

        if the_file: # A value of "" evaluates to False.
            # YYYYMMDDHHMMSS is 14 characters.
            date_time_component = (
                    the_file[ len( basename ) : len( basename ) + 14 ] )

            expiry = (
                datetime.datetime.strptime(
                    date_time_component,
                    IndicatorBase._CACHE_DATE_TIME_FORMAT_YYYYMMDDHHMMSS ) )

            expiry = expiry.replace( tzinfo = datetime.timezone.utc )

        return expiry


    def get_cache_filename_with_timestamp(
        self,
        basename,
        extension = EXTENSION_TEXT ):
        '''
        Create a filename with timestamp and extension to be used to save data
        to the cache.
        '''
        filename = (
            basename
            +
            datetime.datetime.now().strftime(
                IndicatorBase._CACHE_DATE_TIME_FORMAT_YYYYMMDDHHMMSS )
            +
            extension )

        return self.get_cache_directory() / filename


    def get_cache_newest_filename(
        self,
        basename ):
        '''
        Search through the cache for all files matching the basename.
        Returns the newest filename matching the basename on success;
        None otherwise.
        '''
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


    def remove_file_from_cache(
        self,
        filename ):
        '''
        The file removed will be
            ~/.cache/application_base_directory/filename
        '''
        for file in self.get_cache_directory().iterdir():
            if file.name == filename:
                file.unlink()
                break


    def flush_cache(
        self,
        basename,
        maximum_age_in_hours ):
        '''
        Removes out of date cache files for a given basename.

        basename:
            The text used to form the file name, typically the name of the
            calling application.
        maximum_age_in_hours:
            Anything older than the maximum age (hours) is deleted.

        Any file in the cache directory matching the pattern
            ~/.cache/applicationBaseDirectory/basenameCACHE_DATE_TIME_FORMAT_YYYYMMDDHHMMSS

        and is older than the cache maximum age is discarded.

        Any file extension is ignored in determining if the file should be
        deleted or not.
        '''
        cache_maximum_age_date_time = (
            datetime.datetime.now()
            -
            datetime.timedelta( hours = maximum_age_in_hours ) )

        for file in self.get_cache_directory().iterdir():
            # Sometimes the base name is shared
            # ("icon-" versus "icon-fullmoon-")
            # so use the date/time to ensure the correct group of files.
            if file.name.startswith( basename ):
                # len( YYYYMMDDHHMMSS ) = 14.
                date_time = (
                    file.name[ len( basename ) : len( basename ) + 14 ] )

                if date_time.isdigit():
                    file_date_time = (
                        datetime.datetime.strptime(
                            date_time,
                            IndicatorBase._CACHE_DATE_TIME_FORMAT_YYYYMMDDHHMMSS ) )

                    if file_date_time < cache_maximum_age_date_time:
                        file.unlink()


    def read_cache_binary(
        self,
        basename ):
        '''
        Read the most recent binary file from the cache.

        basename:
            The text used to form the file name, typically the name of the
            calling application.

        All files in cache directory are filtered based on the pattern
            ~/.cache/applicationBaseDirectory/basenameCACHE_DATE_TIME_FORMAT_YYYYMMDDHHMMSS

        For example, for an application 'apple', the first file will pass
        through, whilst the second is filtered out
            ~/.cache/fred/apple-20170629174950
            ~/.cache/fred/orange-20170629174951

        Files which pass the filter are sorted by date/time and the most recent
        file is read.

        Returns the binary object; None when no suitable cache file exists;
        None on error and logs.
        '''
        cache_file = ""
        cache_directory = self.get_cache_directory()
        for file in cache_directory.iterdir():
            if file.name.startswith( basename ) and file.name > cache_file:
                cache_file = file.name

        data = None
        if cache_file: # A value of "" evaluates to False.
            filename = cache_directory / cache_file
            with open( filename, 'rb' ) as f_in:
                data = pickle.load( f_in )

        return data


    def write_cache_binary(
        self,
        binary_data,
        basename,
        extension = "" ):
        '''
        Writes an object as a binary file to the cache.

        binary_data:
            The object to write.
        basename:
        The text used to form the file name, typically the name of the
        calling application.
        extension:
            Added to the end of the basename and date/time.

        The object will be written to the cache directory using the pattern
            ~/.cache/applicationBaseDirectory/basenameCACHE_DATE_TIME_FORMAT_YYYYMMDDHHMMSS

        Returns filename written on success; None otherwise.
        '''
        filename = (
            basename
            +
            datetime.datetime.now().strftime(
                IndicatorBase._CACHE_DATE_TIME_FORMAT_YYYYMMDDHHMMSS )  #TODO Look to see where this is used...seems to be used to create the same filename over and over...or am I dreaming?
            +
            extension )

        cache_file = self.get_cache_directory() / filename
        with open( cache_file, 'wb' ) as f_out:
            pickle.dump( binary_data, f_out )

        return cache_file


    def read_cache_text_without_timestamp(
        self,
        filename ):
        '''
        Read the named text file from the cache.

        filename: The name of the file.

        Returns the contents of the text file; None on error and logs.
        '''
        return self._read_cache_text( self.get_cache_directory() / filename )


    def read_cache_text(
        self,
        basename ):
        '''
        Read the most recent text file from the cache.

        basename:
            The text used to form the file name, typically the name of the
            calling application.

        All files in cache directory are filtered based on the pattern
            ~/.cache/applicationBaseDirectory/basenameCACHE_DATE_TIME_FORMAT_YYYYMMDDHHMMSSextension

        For example, for an application 'apple', the first file will be caught,
        whilst the second is filtered out:
            ~/.cache/fred/apple-20170629174950
            ~/.cache/fred/orange-20170629174951

        Files which pass the filter are sorted by date/time and the most
        recent file is read.

        Returns the contents of the text; None when no suitable cache
        file exists; None on error and logs.
        '''
        cache_file = ""
        cache_directory = self.get_cache_directory()
        for file in cache_directory.iterdir():
            if file.name.startswith( basename ) and file.name > cache_file:
                cache_file = file.name

        if cache_file:
            cache_file = cache_directory / cache_file

        return self._read_cache_text( cache_file )


    def _read_cache_text(
        self,
        cache_file ):
        text = ""
        if cache_file.is_file():
            with open( cache_file, 'r', encoding = "utf-8" ) as f_in:
                text = f_in.read()

        return text


    def write_cache_text_without_timestamp(
        self,
        text,
        filename ):
        '''
        Writes text to a file in the cache.

        text: The text to write.
        filename: The name of the file.

        Returns filename written on success; None otherwise.
        '''
        return (
            self._write_cache_text(
                text, self.get_cache_directory() / filename ) )


    def write_cache_text(
        self,
        text,
        basename,
        extension = EXTENSION_TEXT ):
        '''
        Writes text to a file in the cache.

        text:
            The text to write.
        basename:
            The text used to form the file name, typically the name of the
            calling application.
        extension:
            Added to the end of the basename and date/time.

        The text will be written to the cache directory using the pattern
            ~/.cache/applicationBaseDirectory/basenameCACHE_DATE_TIME_FORMAT_YYYYMMDDHHMMSSextension

        Returns filename written on success; None otherwise.
        '''
        filename = (
            basename
            +
            datetime.datetime.now().strftime(
                IndicatorBase._CACHE_DATE_TIME_FORMAT_YYYYMMDDHHMMSS )
            +
            extension )

        return (
            self._write_cache_text(
                text, self.get_cache_directory() / filename ) )


    def _write_cache_text(
        self,
        text,
        cache_file ):

        with open( cache_file, 'w', encoding = "utf-8" ) as f_out:
            f_out.write( text )

        return cache_file


    def get_cache_directory( self ):
        '''
        Return the full directory path to the user cache directory for
        the current indicator.
        '''
        return self._get_user_directory( ".cache", self.indicator_name )


    def _get_user_directory(
        self,
        user_base_directory,
        application_base_directory ):
        '''
        Obtain (and create if not present) the directory for configuration,
        cache or similar.

        user_base_directory:
            The directory name used to hold the configuration/cache.
        application_base_directory:
            The directory name at the end of the final user directory to specify
            the application.

        The full directory path will be
            ~/user_base_directory/application_base_directory
        '''
        directory = Path.home() / user_base_directory / application_base_directory
        directory.mkdir( parents = True, exist_ok = True )
        return directory


    def process_call(
        self,
        command ):
        '''
        Executes the command in a new process.
        On exception, logs to file.
        '''
        try:
            subprocess.call( command, shell = True )

        except subprocess.CalledProcessError as e:
            logging.error( e )
            if e.stderr:
                logging.error( e.stderr )


#TODO Check every function which calls this...the function no longer returns None but rather "".
# Do we need to return the result and stderr?
    def process_get(
        self,
        command,
        log_non_zero_error_code = False ):
        '''
        Executes the command and returns the result.
        The result of executing the command may indeed be "" which does not
        necessarily indicate an error condition.

        logNonZeroErrorCode:
            If True, will log any exception arising from a non-zero return code;
            otherwise will ignore.

        On failure/exception, logs to file and returns "".
        '''
        try:
            result = (
                subprocess.run(
                    command,
                    stdout = subprocess.PIPE,
                    stderr = subprocess.PIPE,
                    shell = True,
                    check = log_non_zero_error_code ) )

            stderr_ = result.stderr.decode()
            if stderr_:
                result = ""
                logging.error( stderr_ )

            else:
                result = result.stdout.decode().strip()

        except subprocess.CalledProcessError as e:
            logging.error( e )
            if e.stderr:
                logging.error( e.stderr )

            result = ""

        return result


class TruncatedFileHandler( logging.handlers.RotatingFileHandler ):
    '''
    Log file handler which truncates the file when the file size limit
    (in bytes) has been reached.

    References:
        https://docs.python.org/3/library/logging.handlers.html
        https://stackoverflow.com/questions/24157278/limit-python-log-file
        https://github.com/python/cpython/blob/main/Lib/logging/handlers.py
    '''

    def __init__(
        self,
        filename,
        maxBytes = 10000 ):

        super().__init__(
            filename,
            maxBytes = maxBytes,
            delay = True )


    def doRollover( self ):
        if self.stream:
            self.stream.close()

        # self.baseFilename is defined in the parent class.
        Path( self.baseFilename ).unlink( missing_ok = True )
        self.mode = 'a'
        self.stream = self._open()
