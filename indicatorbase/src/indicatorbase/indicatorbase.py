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


#TODO Got 
#   (indicatortide.py:9968): Gtk-CRITICAL **: 23:05:19.372: gtk_widget_get_scale_factor: assertion 'GTK_IS_WIDGET (widget)' failed
#
# on the laptop...
# Happens when the screen is locked.
# Is this a 32 bit thing?  Test on Debian 12 VM 64 bit.


#TODO On desktop, indicatortide does not run on startup.
# Desktop file, run shell script all have same permissions for other indicators.
# Starts up fine on laptop!
#
# Also on desktop, PPA and Punycode don't autostart...what else...and why?
# They seem to have correct permissions.


#TODO Add changelog entry for each indicator about moving closer to PEP8
# or whatever the Python code standard is?


#TODO Given clipboard and wmctrl don't seem to work under Wayland...
# figure out if this is the case/scenarios...
# then figure out if things like in virtualbox need to handle when middle mouse click
# or mouse wheel scroll is used...is there an issue?


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


#TODO Run any indicator under Debian 12 and open About dialog.
# Click on the icon and display the menu, the About/Preferences/Quit items are greyed out.
# Clicking the red X on the About dialog (or hitting the escape key)
# closes the dialog but the About/Preferences/Quit items remain greyed out.
# Does not occur on Ubuntu 20.04 / 22.04 / 24.04 et al and NOT on Fedora 40.
# Occurs on Debian 11 on all graphics variants;
# Debian 12 on GNOME, presumably all other graphics variants;
# Fedora 38 / 39; Manjaro 22.1; openSUSE Tumbleweed.
# Check on other distros.
#
# Double check Manjaro 22.1; openSUSE Tumbleweed.


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
#


#TODO Before release, perhaps check out:
# Xubuntu, Ubuntu Unity, Ubuntu Budgie, Kubuntu 24.04


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


from abc import ABC
from bisect import bisect_right
import datetime
import email.policy
import gettext
import gi
import sys

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
import inspect
import json
import logging.handlers
import os
from pathlib import Path
import pickle
import re  #TODO No longer used?
import shutil
import signal
import subprocess
from threading import Lock
from urllib.request import urlopen
import webbrowser
from zipfile import ZipFile


class IndicatorBase( ABC ):

    __AUTOSTART_PATH = os.getenv( "HOME" ) + "/.config/autostart/"

    __CACHE_DATE_TIME_FORMAT_YYYYMMDDHHMMSS = "%Y%m%d%H%M%S"

    __CONFIG_VERSION = "version"

#TODO Are these still relevant?
# Check if we need to add others given the variety of distros now supported.
    __DESKTOP_LXQT = "LXQt"
    __DESKTOP_MATE = "MATE"
    __DESKTOP_UNITY7 = "Unity:Unity7:ubuntu"

    __EXTENSION_JSON = ".json"

#TODO Check all terminals on all supported distros.
    __TERMINALS_AND_EXECUTION_FLAGS = [ [ "gnome-terminal", "--" ] ] # ALWAYS list first so as to be the "default".
    __TERMINALS_AND_EXECUTION_FLAGS.extend( [
        [ "konsole", "-e" ],
        [ "lxterminal", "-e" ],
        [ "mate-terminal", "-x" ],
        [ "qterminal", "-e" ],
        [ "tilix", "-e" ],
        [ "xfce4-terminal", "-x" ] ] )

    __UPDATE_PERIOD_IN_SECONDS = 60

    __X_GNOME_AUTOSTART_ENABLED = "X-GNOME-Autostart-enabled"
    __X_GNOME_AUTOSTART_DELAY = "X-GNOME-Autostart-Delay"

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
            locale_directory = str( Path( __file__ ).parent ) + os.sep + "locale"
            gettext.install( INDICATOR_NAME, localedir = locale_directory )
            break

    URL_TIMEOUT_IN_SECONDS = 20


#TODO Check the flow of code, from init to update loops,
# to about/preferences,
# to interupting an update (if possible)
# to stopping an update and then kicking off later.
#
#TODO Check that when About/Preferences is showing,
# is it possible to click anything else in the indicator menu?
# If not, may need to go back to using GLib.idle_add()
# or maybe just disable entire menu?
# 
# On Ubuntu 20.04, does not block when About/Prefs open.
# 
# What about Debian 12?
#
# Run punycode.  Open About dialog.
# Highlight some punycode on a browser page.
# Click convert.  Menu is rebuilt!!!  Not good.
# So maybe have to disable menu...also the secondary menu item and mouse wheel scroll.
#
#Need to guarentee that when a user kicks off Abuot/Prefs that an update is not underway
# and also to prevent an update from happening.
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

        project_metadata, error_message = self._get_project_metadata()
        if error_message:
            self.show_dialog_ok(
                None,
                error_message,
                title = self.indicator_name,
                message_type = Gtk.MessageType.ERROR )

            sys.exit( 1 )

        error_message = self.initialise_desktop_file()
        if error_message:
            self.show_dialog_ok(
                None,
                error_message,
                title = self.indicator_name,
                message_type = Gtk.MessageType.ERROR )

            sys.exit( 1 )

        self.version = project_metadata[ "Version" ]
        self.comments = comments

        # https://stackoverflow.com/a/75803208/2156453
        email_message_object = \
            email.message_from_string(
                f'To: { project_metadata[ "Author-email" ] }',
                policy = email.policy.default, )

        self.copyright_names = [ ]
        for address in email_message_object[ "to" ].addresses:
            self.copyright_names.append( address.display_name )

        self.website = project_metadata.get_all( "Project-URL" )[ 0 ].split( ',' )[ 1 ].strip()

        self.authors = [ ]
        for author in self.copyright_names:
            self.authors.append( author + " " + self.website )

        self.artwork = artwork if artwork else self.authors
        self.creditz = creditz
        self.debug = debug

        self.log = os.getenv( "HOME" ) + '/' + self.indicator_name + ".log"
        logging.basicConfig(
            format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            level = logging.DEBUG,
            handlers = [ TruncatedFileHandler( self.log ) ] )

        self.update_timer_id = None
        self.lock = Lock()
        signal.signal( signal.SIGINT, signal.SIG_DFL ) # Responds to CTRL+C when running from terminal.

        Notify.init( self.indicator_name )

        self.indicator = \
            AppIndicator.Indicator.new(
                self.indicator_name, #ID
                self.get_icon_name(), # Icon name
                AppIndicator.IndicatorCategory.APPLICATION_STATUS )

        self.indicator.set_status( AppIndicator.IndicatorStatus.ACTIVE )

        menu = Gtk.Menu()
        self.create_and_append_menuitem( menu, _( "Initialising..." ) )
        menu.show_all()
        self.indicator.set_menu( menu )

        self.__load_config()


    def _get_project_metadata( self ):
        # https://stackoverflow.com/questions/75801738/importlib-metadata-doesnt-appear-to-handle-the-authors-field-from-a-pyproject-t
        # https://stackoverflow.com/questions/76143042/is-there-an-interface-to-access-pyproject-toml-from-python
        project_metadata = None
        error_message = None
        try:
            # Obtain pyproject.toml information from pip.
            project_metadata = metadata.metadata( self.indicator_name )

        except metadata.PackageNotFoundError:
            # No pip information found; assume in development/testing.
            # Look for a .whl file in the same directory as the indicator.
            first_wheel = next( Path( '.' ).glob( "*.whl" ), None )
            if first_wheel is None:
                error_message = f"Unable to locate a .whl in { os.path.realpath( Path( '.' ) ) }"

            else:
                first_metadata = next( metadata.distributions( path = [ first_wheel ] ), None )
                if first_metadata is None:
                    error_message = f"No metadata was found in { first_wheel.absolute() }!"

                else:
                    project_metadata = first_metadata.metadata

        return project_metadata, error_message


    def initialise_desktop_file( self ):
        # Ensure the .desktop file is present,
        # either in a virtual environment or in development.
        self.desktop_file = self.indicator_name + ".py.desktop"

        self.desktop_file_user_home = \
            IndicatorBase.__AUTOSTART_PATH + \
            self.desktop_file

        self.desktop_file_virtual_environment = \
            str( Path( __file__ ).parent ) + \
            "/platform/linux/" + \
            self.desktop_file

        error_message = None
        if not Path( self.desktop_file_virtual_environment ).exists():
            # Assume running in development; extract the .desktop file
            # from (the first) wheel located in the development folder.
            first_wheel = next( Path( '.' ).glob( "*.whl" ), None )
            if first_wheel is None:
                error_message = f"Unable to locate a .whl in { os.path.realpath( Path( '.' ) ) }"

            else:
                desktop_file_in_wheel = \
                    self.indicator_name + \
                    "/platform/linux/" + \
                    self.indicator_name + ".py.desktop"

                with ZipFile( first_wheel, 'r' ) as z:
                    if desktop_file_in_wheel not in z.namelist():
                        error_message = f"Unable to locate { desktop_file_in_wheel } in { first_wheel }."

                    else:
                        z.extract( desktop_file_in_wheel, path = "/tmp" )
                        self.desktop_file_virtual_environment = \
                            str( Path( "/tmp/" + desktop_file_in_wheel ) )

                        if not Path( self.desktop_file_virtual_environment ).exists():
                            error_message = f"Unable to locate { self.desktop_file_virtual_environment }!"

                z.close()

        return error_message


    @staticmethod
    def get_first_year_or_last_year_in_changelog_markdown( changelog_markdown, first_year = True ):
        first_or_last_year = ""
        with open( changelog_markdown, 'r' ) as f:
            if first_year:
                lines = reversed( f.readlines() )

            else:
                lines = f.readlines()

            for line in lines:
                if line.startswith( "## v" ):
                    left_parenthesis = line.find( '(' )
                    first_or_last_year = line[ left_parenthesis + 1 : left_parenthesis + 1 + 4 ]
                    break

        return first_or_last_year


    @staticmethod
    def get_changelog_markdown_path():
        changelog = str( Path( __file__ ).parent ) + "/CHANGELOG.md" # Path under virtual environment.
        if not Path( changelog ).exists():
            changelog = str( os.path.realpath( Path( '.' ) ) ) + "/CHANGELOG.md" # Assume running in development.

        return changelog


    def main( self ):
        GLib.timeout_add_seconds( 1, self.__update ) # Delay update so that the Gtk main executes to show initialisation.
        Gtk.main()


    def __update( self ):
        if self.lock.acquire( blocking = False ):
            self.set_menu_sensitivity( False )
            GLib.idle_add( self.__update_internal )

        else:
#TODO Test this clause.
            GLib.timeout_add_seconds(
                IndicatorBase.__UPDATE_PERIOD_IN_SECONDS,
                self.__update )
            #TODO This call returns an ID...need to keep it?
            #TODO Keep the About/Prefernces open and see if we keep trying to do an update every 60 seconds.


    def __update_internal( self ):
        update_start = datetime.datetime.now()

        # The user can nominate any menuitem as a secondary activate target during menu construction.
        # However the secondary activate target can only be set once the menu is built.
        # Therefore, keep a variable for the user to set as needed.
        # Then set the secondary activate target once the menu is built/shown.
        self.secondary_activate_target = None

        menu = Gtk.Menu()
        next_update_in_seconds = self.update( menu ) # Call to implementation in indicator.

        if self.is_debug():
            if next_update_in_seconds:
                next_update_date_time = datetime.datetime.now() + datetime.timedelta( seconds = next_update_in_seconds )
                label = "Next update: " + str( next_update_date_time ).split( '.' )[ 0 ]
                menu.prepend( Gtk.MenuItem.new_with_label( label ) )

            label = "Time to update: " + str( datetime.datetime.now() - update_start )
            menu.prepend( Gtk.MenuItem.new_with_label( label ) )

#TODO Ensure this works for indicatortest (with one menu item) and
# indicatorlunar with two menu items.
        if len( menu.get_children() ) > 0:
            menu.append( Gtk.SeparatorMenuItem() )

        titles = ( _( "Preferences" ), _( "About" ), _( "Quit" ) )
        functions = ( self.__on_preferences, self.__on_about, Gtk.main_quit )
        for title, function in zip( titles, functions ):
            self.create_and_append_menuitem( menu, title, activate_functionandarguments = ( function, ) )

        self.indicator.set_menu( menu )
        menu.show_all()

        self.indicator.set_secondary_activate_target( self.secondary_activate_target )

        if next_update_in_seconds: # Some indicators don't return a next update time.
            self.update_timer_id = GLib.timeout_add_seconds( next_update_in_seconds, self.__update )
            # self.nextUpdateTime = datetime.datetime.now() + datetime.timedelta( seconds = next_update_in_seconds ) #TODO Hopefully no longer need self.nextUpdateTime

        self.lock.release()


    def request_update( self, delay = 0 ):
        GLib.timeout_add_seconds( delay, self.__update )  #TODO Should the default delay be 1?  Is 0 too fast?  Could some race condition arise?


    def set_label( self, text ):
        self.indicator.set_label( text, text )
        self.indicator.set_title( text ) # Needed for Lubuntu/Xubuntu.


    def set_icon( self, icon ):
        self.indicator.set_icon_full( icon, "" )


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


#TODO UNCHECKED
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
            self.__on_mouse_wheel_scroll,
            functionandarguments )


    def __on_mouse_wheel_scroll(
            self,
            indicator,
            delta,
            scroll_direction,
            functionandarguments ):

        if not self.lock.locked():
            if len( functionandarguments ) == 1:
                functionandarguments[ 0 ]( indicator, delta, scroll_direction )

            else:
                functionandarguments[ 0 ]( indicator, delta, scroll_direction, *functionandarguments[ 1 : ] )


    def __on_about( self, menuitem ):
        if self.lock.acquire( blocking = False ):
            self.__on_about_internal( menuitem )

        else:
            pass #TODO Show notification to user?  How to tell if we're blocked due to update or Preferences?


    def __on_about_internal( self, menuitem ):
        self.set_menu_sensitivity( False )
        self.indicator.set_secondary_activate_target( None )

        about_dialog = Gtk.AboutDialog()
        about_dialog.set_transient_for( menuitem.get_parent().get_parent() )
        about_dialog.set_artists( self.artwork )
        about_dialog.set_authors( self.authors )
        about_dialog.set_comments( self.comments )

        changelog_markdown_path = IndicatorBase.get_changelog_markdown_path()

        copyright_start_year = \
            IndicatorBase.get_first_year_or_last_year_in_changelog_markdown( changelog_markdown_path )

        about_dialog.set_copyright(
            "Copyright \xa9 " + \
            copyright_start_year + '-' + str( datetime.datetime.now().year ) + " " + \
            ' '.join( self.copyright_names ) )

        about_dialog.set_license_type( Gtk.License.GPL_3_0 )
        about_dialog.set_logo_icon_name( self.get_icon_name() )
        about_dialog.set_program_name( self.indicator_name )
        about_dialog.set_translator_credits( _( "translator-credits" ) )
        about_dialog.set_version( self.version )
        about_dialog.set_website( self.website )
        about_dialog.set_website_label( self.website )

        if self.creditz:
            about_dialog.add_credit_section( _( "Credits" ), self.creditz )

        self.__add_hyperlink_label(
            about_dialog,
            changelog_markdown_path,
            _( "View the" ),
            _( "changelog" ),
            _( "text file." ) )

        error_log = os.getenv( "HOME" ) + '/' + self.indicator_name + ".log"
        if os.path.exists( error_log ):
            self.__add_hyperlink_label(
                about_dialog,
                error_log,
                _( "View the" ),
                _( "error log" ),
                _( "text file." ) )

        about_dialog.run()
        about_dialog.destroy()

        self.set_menu_sensitivity( True )
        self.indicator.set_secondary_activate_target( self.secondary_activate_target )
        self.lock.release()

        #TODO By doing an update gets around the Debian/Fedora issue
        # when clicking the icon when the About/Preferences are open. 
        # Not sure if this should stay...but needs to be only done for Debian 11 / 12 and Fedora 38 / 39.
        #
        # Is there some other way to try?
        # Call self.set_menu_sensitivity( True ) in a thread 1 sec later? 
        #
        #Does this issue happen under Debian/Fedora under xorg (rather than default wayland)?
        # self.request_update()
#TODO May be able to use this to determine the os/platform/distro:
# desktop_environment = os.environ.get('DESKTOP_SESSION')
#         if desktop_environment:
#             if desktop_environment.lower()[:8] == 'cinnamon':
#                 svg = indicator_icon
#             if desktop_environment.lower()[:7] == 'xubuntu':
#                 svg = indicator_icon
#             if desktop_environment.lower()[:4] == 'xfce':
#                 svg = indicator_icon


    def __add_hyperlink_label(
            self,
            about_dialog,
            file_path,
            left_text,
            anchor_text,
            right_text ):

        tooltip = "file://" + file_path
        markup = \
            left_text + \
            " <a href=\'" + "file://" + file_path + "\' title=\'" + tooltip + "\'>" + \
            anchor_text + "</a> " + \
            right_text

        label = Gtk.Label()
        label.set_markup( markup )
        label.show()
        about_dialog.get_content_area().get_children()[ 0 ].get_children()[ 2 ].get_children()[ 0 ].pack_start( label, False, False, 0 )


    def __on_preferences( self, menuitem ):
        if self.lock.acquire( blocking = False ):
            self.__on_preferences_internal( menuitem )

        else:
            pass #TODO Show notification to user?  How to tell if we're blocked due to update or About?


    def __on_preferences_internal( self, menuitem ):
        self.set_menu_sensitivity( False )
        self.indicator.set_secondary_activate_target( None )

        if self.update_timer_id: #TODO If the mutex works...maybe can dispense with the ID stuff.
            GLib.source_remove( self.update_timer_id )
            self.update_timer_id = None

        dialog = self.create_dialog( menuitem, _( "Preferences" ) )
        response_type = self.on_preferences( dialog ) # Call to implementation in indicator.
        dialog.destroy()

#TODO Don't think I need this here...if we OK the Preferences,
# then an update will be kicked off and will disable the menu, 
# so no need to enable the menu.
# If we cancel the Preferences, then enable the menu.
#        self.__setMenuSensitivity( True )

        if response_type == Gtk.ResponseType.OK:
            self.__save_config()
            GLib.timeout_add_seconds( 1, self.__update ) # Allow one second for the lock to release and so the update will proceed.

        #TODO May not need this...If the update keeps trying every minute, then no need for the code below.
        '''
        elif self.nextUpdateTime: # User cancelled and there is a next update time present...
            secondsToNextUpdate = ( self.nextUpdateTime - datetime.datetime.now() ).total_seconds()
            if secondsToNextUpdate > 10: # Scheduled update is still in the future (10 seconds or more), so reschedule...
                GLib.timeout_add_seconds( int( secondsToNextUpdate ), self.__update )

            else: # Scheduled update would have already happened, so kick one off now.
                self.__update()
        '''

        self.set_menu_sensitivity( True )
        self.indicator.set_secondary_activate_target( self.secondary_activate_target )
        self.lock.release()

#        self.request_update() #TODO By doing an update gets around the Debian/Fedora issue
# when clicking the icon when the About/Preferences are open. 
# Not sure if this should stay...but needs to be only done for Debian 11 / 12 and Fedora 38 / 39.
# But...only do this "if responseType != Gtk.ResponseType.OK" because when OK,
# an update is kicked off any way.


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


#TODO Seems Gtk.STOCK_OK et al are deprecated:
#   https://lazka.github.io/pgi-docs/Gtk-3.0/constants.html#Gtk.STOCK_OK
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
                self.__get_parent( parent_widget ),
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
            self.__show_dialog(
                parent_widget,
                message,
                Gtk.MessageType.QUESTION,
                Gtk.ButtonsType.OK_CANCEL,
                title = title )


#TODO UNCHECKED
    def show_dialog_ok(
            self,
            parent_widget,
            message,
            title = None,
            message_type = Gtk.MessageType.ERROR ):

        return \
            self.__show_dialog(
                parent_widget,
                message,
                message_type,
                Gtk.ButtonsType.OK,
                title = title )


    def __show_dialog(
            self,
            parent_widget,
            message,
            message_type,
            buttons_type,
            title = None ):

        dialog = \
            Gtk.MessageDialog(
                self.__get_parent( parent_widget ),
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


    def __get_parent( self, widget ):
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


    def create_and_append_menuitem(
        self,
        menu,
        label,
        name = None,
        activate_functionandarguments = None,
        is_secondary_activate_target = False ):

        menuitem = Gtk.MenuItem.new_with_label( label )

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
        is_secondary_activate_target = False ):

        menuitem = \
            self.create_and_append_menuitem(
                menu,
                label,
                name = name,
                activate_functionandarguments = activate_functionandarguments,
                is_secondary_activate_target = is_secondary_activate_target )

        menu.reorder_child( menuitem, index )
        return menuitem


    # Creates a single (isolated, not part of a group)
    # RadioMenuItem that is enabled/active.
    def create_and_append_radiomenuitem(
        self,
        menu,
        label,
        activate_functionandarguments = None ):

        menuitem = Gtk.RadioMenuItem.new_with_label( [ ], label ) # Always set the group to empty.
        menuitem.set_active( True )

        if activate_functionandarguments:
            menuitem.connect( "activate", *activate_functionandarguments )

        menu.append( menuitem )
        return menuitem


#TODO UNCHECKED
    def get_on_click_menuitem_open_browser_function( self ):
        return lambda menuitem: webbrowser.open( menuitem.get_name() )

    
    # Takes a Gtk.TextView and returns the containing text,
    # avoiding the additional calls to get the start/end positions.
#TODO UNCHECKED
    def get_textview_text( self, textview ):
        textview_buffer = textview.get_buffer()
        return \
            textview_buffer.get_text(
                textview_buffer.get_start_iter(),
                textview_buffer.get_end_iter(),
                True )


    # Listens to radio/checkbox "toggled" events and toggles the visibility
    # of the widgets according to the boolean value of 'sense'.
#TODO UNCHECKED
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


#TODO Not sure if this should be absorbed into create_box
# (but would need to take tooltips and click arguments in the tuple I suppose)
# or if not absorbed and this function stays,
# call create_box internally.
    def create_buttons_in_box(
            self,
            labels,
            tooltip_texts,
            clicked_functionandarguments ):

        box = Gtk.Box( spacing = 6 )
        box.set_homogeneous( True )

        z = zip( labels, tooltip_texts, clicked_functionandarguments )
        for label, tooltip_text, clicked_functionandargument in z:
            box.pack_start(
                self.create_button(
                    label,
                    tooltip_text = tooltip_text,
                    clicked_functionandarguments = clicked_functionandargument ),
                True,
                True,
                0 )

        box.set_halign( Gtk.Align.CENTER )

        return box


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
        self.__set_widget_common_attributes(
            entry,
            tooltip_text = tooltip_text,
            sensitive = sensitive,
            margin_top = margin_top,
            margin_left = margin_left )

        entry.set_text( text )
        entry.set_editable( editable )

#TODO Check this again...
# Check for when doing an 'add' so the entry is empty
# and for doing an 'edit' so the entry has text.
        if make_longer and text:
            # Give a little more space; sometimes too short due to packing.
            entry.set_width_chars( len( text ) * 5 / 4 )

        return entry


#TODO UNCHECKED
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


#TODO UNCHECKED
    def create_textview(
            self,
            text = "",
            tooltip_text = "",
            editable = True,
            wrap_mode = Gtk.WrapMode.WORD ):

        textview = Gtk.TextView()
        textview.get_buffer().set_text( text )
        textview.set_tooltip_text( tooltip_text ) #TODO Test that if a tooltip of "" (or no tooltip) actually shows no tooltip.
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
        self.__set_widget_common_attributes(
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
        self.__set_widget_common_attributes(
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
        self.__set_widget_common_attributes(
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
        self.__set_widget_common_attributes(
            radiobutton,
            tooltip_text = tooltip_text,
            sensitive = sensitive,
            margin_top = margin_top,
            margin_left = margin_left )

        radiobutton.set_active( active )
        return radiobutton


    def __set_widget_common_attributes(
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


#TODO UNCHECKED
    def create_treeview_within_scrolledwindow(
        self,
        treemodel, # Must be a sorted store if columns are to be sorted.
        titles,
        renderers_attributes_columnmodelids, # Columns will not be expanded: treeviewcolumn.pack_start( renderer, False )
        alignments_columnviewids = None,
        sortcolumnviewids_columnmodelids = None, # First column will be set as default sorted ascendingly.
        celldatafunctionandarguments_renderers_columnviewids = None, # Function and arguments must be a nested tuple.
        clickablecolumnviewids_functionsandarguments = None,
        tooltip_text = "",
        cursorchangedfunctionandarguments = None,
        rowactivatedfunctionandarguments = None ):
#TODO Figure out how to do a proper header comment/docstring/whatever it is called...
#...and document each argument...notably the renderers_attributes_columnmodelids
# can be single tuples or a tuple of tuples (as in script runner main treeview).
        treeview = Gtk.TreeView.new_with_model( treemodel )

        for title, renderer_attribute_columnmodelid in zip( titles, renderers_attributes_columnmodelids ):
            treeviewcolumn = Gtk.TreeViewColumn( title )

            # Expand all columns unless the column contains a single checkbox and no column header title.
            is_checkbox_column = \
                type( renderer_attribute_columnmodelid[ 0 ] ) == Gtk.CellRendererToggle and not title

            treeviewcolumn.set_expand( not is_checkbox_column )

            # Add the renderer / attribute / column model id for each column.
            is_single_tuple = not type( renderer_attribute_columnmodelid[ 0 ] ) is tuple
            if is_single_tuple:
                treeviewcolumn.pack_start( renderer_attribute_columnmodelid[ 0 ], False )
                treeviewcolumn.add_attribute( *renderer_attribute_columnmodelid )

            else: # Assume to be a tuple of tuples of renderer, attribute, column model id.
#TODO This clause should happen for script runner when we have interval with two possible renderers...
                for renderer, attribute, columnmodelid in renderer_attribute_columnmodelid:
                    treeviewcolumn.pack_start( renderer, False )
                    treeviewcolumn.add_attribute( renderer, attribute, columnmodelid )

            treeview.append_column( treeviewcolumn )

        if alignments_columnviewids:
            for alignment, columnviewid in alignments_columnviewids:
                for index, treeviewcolumn in enumerate( treeview.get_columns() ):
                    if columnviewid == index:
                        treeviewcolumn.set_alignment( alignment )

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


    def get_menu_indent( self, indent = 1 ):
        indent_amount = "      " * indent
        if self.get_desktop_environment() == IndicatorBase.__DESKTOP_UNITY7:  #TODO What about the Ubuntu Unity OS...what desktop is that?
            indent_amount = "      " * ( indent - 1 )

        return indent_amount


    def get_autostart_and_delay( self ):
        autostart = False
        delay = 0
        try:
            if os.path.exists( self.desktop_file_user_home ):
                with open( self.desktop_file_user_home, 'r' ) as f:
                    for line in f:
                        if IndicatorBase.__X_GNOME_AUTOSTART_ENABLED + "=true" in line:
                            autostart = True

                        if IndicatorBase.__X_GNOME_AUTOSTART_DELAY + '=' in line:
                            delay = int( line.split( '=' )[ 1 ].strip() )

        except Exception as e:
            logging.exception( e )
            autostart = False
            delay = 0

        return autostart, delay


    def set_autostart_and_delay( self, is_set, delay ):
        if not os.path.exists( IndicatorBase.__AUTOSTART_PATH ):
            os.makedirs( IndicatorBase.__AUTOSTART_PATH )

        if not os.path.exists( self.desktop_file_user_home ):
            shutil.copy( self.desktop_file_virtual_environment, self.desktop_file_user_home )

        try:
            output = ""
            with open( self.desktop_file_user_home, 'r' ) as f:
                for line in f:
                    if IndicatorBase.__X_GNOME_AUTOSTART_DELAY in line:
                        output += IndicatorBase.__X_GNOME_AUTOSTART_DELAY + '=' + str( delay ) + '\n'

                    elif IndicatorBase.__X_GNOME_AUTOSTART_ENABLED in line:
                        output += IndicatorBase.__X_GNOME_AUTOSTART_ENABLED + '=' + str( is_set ).lower() + '\n'

                    else:
                        output += line

            # If the user has an old .desktop file,
            # there may not be an autostart enable field and/or
            # an autostart delay field, so manually add in.
            if IndicatorBase.__X_GNOME_AUTOSTART_DELAY not in output:
                output += IndicatorBase.__X_GNOME_AUTOSTART_DELAY + '=' + str( delay ) + '\n'

            if IndicatorBase.__X_GNOME_AUTOSTART_ENABLED not in output:
                output += IndicatorBase.__X_GNOME_AUTOSTART_ENABLED + '=' + str( is_set ).lower() + '\n'

            with open( self.desktop_file_user_home, 'w' ) as f:
                f.write( output )

        except Exception as e:
            logging.exception( e )


    def get_logging( self ):
        return logging


#TODO UNCHECKED
#TODO Who calls this?
    def is_number( self, number_as_string ):
        try:
            float( number_as_string )
            return True

        except ValueError:
            return False


#TODO This returns a \n at the end of the result...should this be trimmed at all...
# and if so, here or by process_get?  Who else calls process_get?
    def get_desktop_environment( self ):
        return self.process_get( "echo $XDG_CURRENT_DESKTOP" ).strip()


#TODO UNCHECKED
    def is_ubuntu_variant_2004( self ):
        ubuntu_variant_2004 = False
        try:
            ubuntu_variant_2004 = (
                True if self.process_get( "lsb_release -rs" ).strip() == "20.04"
                else False )

        except:
            pass

        return ubuntu_variant_2004


    # Lubuntu 20.04/22.04 ignores any change to the icon after initialisation.
    # If the icon is changed, the icon is replaced with a strange grey/white circle.
    #
    # Ubuntu MATE 20.04 truncates the icon when changed,
    # despite the icon being fine when clicked.
#TODO UNCHECKED
    def is_icon_update_supported( self ):
        icon_update_supported = True
        desktop_environment = self.get_desktop_environment()

#TODO Tidy up
        if desktop_environment is None or \
           desktop_environment == IndicatorBase.__DESKTOP_LXQT or \
           ( desktop_environment == IndicatorBase.__DESKTOP_MATE and self.is_ubuntu_variant_2004() ):
            icon_update_supported = False

        return icon_update_supported


    # Lubuntu 20.04/22.04 ignores any change to the label/tooltip after initialisation.
    def is_label_update_supported( self ):
        label_update_supported = True
        desktop_environment = self.get_desktop_environment()

#TODO Tidy up        
        if desktop_environment is None or \
           desktop_environment == IndicatorBase.__DESKTOP_LXQT:
            label_update_supported = False

        return label_update_supported


    # As a result of
    #   https://github.com/lxqt/qterminal/issues/335
    # provide a way to determine if qterminal is the current terminal.
#TODO UNCHECKED
#TODO In indicatortest (maybe elsewhere too)
# first get the terminal and execution flag,
# then call this function (which also calls the get the terminal and execution flag function)...
#...is there a smarter way to do this (maybe pass in the 'terminal' return value)?
    def is_terminal_qterminal( self ):
        terminal_is_qterminal = False
        terminal, terminal_execution_flag = self.get_terminal_and_execution_flag()
        if terminal is not None and "qterminal" in terminal:
            terminal_is_qterminal = True

        return terminal_is_qterminal


    # Return the full path and name of the executable for the
    # current terminal and the corresponding execution flag;
    # None otherwise.
    def get_terminal_and_execution_flag( self ):
        terminal = None
        execution_flag = None
        for _terminal, _execution_flag in IndicatorBase.__TERMINALS_AND_EXECUTION_FLAGS:
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


    # Converts a list of lists to a GTK ListStore.
    #
    # If the list of lists is of the form below,
    # each inner list must be of the same length.
    #
    #    [
    #        [ dataA, dataB, dataC, ... ],
    #        ...
    #        ...
    #        ...
    #        [ dataX, dataY, dataZ, ... ]
    #    ]
    #
    # Corresponding indices of elements of each inner list must be of the same data type:
    #
    #    type( dataA ) == type( dataX ) and type( dataB ) == type( dataY ) and type( dataC ) == type( dataZ ).
    #
    # Each row of the returned ListStore contain one inner list.
#TODO UNCHECKED
    def list_of_lists_to_liststore( self, list_of_lists ): #TODO Check how this function works...if all good, maybe move back into Lunar?
        types = [ ]
        for item in list_of_lists[ 0 ]:
            types.append( type( item[ 0 ] ) )

        liststore = Gtk.ListStore()
        liststore.set_column_types( types )
        for item in list_of_lists:
            liststore.append( item )

        return liststore


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


    def request_save_config( self, delay = 0 ):
        GLib.timeout_add_seconds( delay, self.__save_config, False )


    def __copy_config_to_new_directory( self ):
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

        config_file = self.__get_config_directory() + self.indicator_name + IndicatorBase.__EXTENSION_JSON
        config_file_old = config_file.replace( self.indicator_name, mapping[ self.indicator_name ] )
        if not os.path.isfile( config_file ) and os.path.isfile( config_file_old ):
            shutil.copyfile( config_file_old, config_file )


    # Read a dictionary of configuration from a JSON text file.
    def __load_config( self ):
        self.__copy_config_to_new_directory()
        config_file = self.__get_config_directory() + self.indicator_name + IndicatorBase.__EXTENSION_JSON
        config = { }
        if os.path.isfile( config_file ):
            try:
                with open( config_file, 'r' ) as f_in:
                    config = json.load( f_in )

            except Exception as e:
                config = { }
                logging.exception( e )
                logging.error( "Error reading configuration: " + config_file )

        self.load_config( config ) # Call to implementation in indicator.


    # Write a dictionary of user configuration to a JSON text file.
    #
    # returnStatus If True, will return a boolean indicating success/failure.
    #              If False, no return call is made (useful for calls to GLib idle_add/timeout_add_seconds.
    def __save_config( self, return_status = True ):
        config = self.save_config() # Call to implementation in indicator.
        config[ IndicatorBase.__CONFIG_VERSION ] = self.version
        config_file = \
            self.__get_config_directory() + \
            self.indicator_name + \
            IndicatorBase.__EXTENSION_JSON

        success = True
        try:
            with open( config_file, 'w' ) as f_out:
                f_out.write( json.dumps( config ) )

        except Exception as e:
            logging.exception( e )
            logging.error( "Error writing configuration: " + config_file )
            success = False

        if return_status:
            return success


    # Return the full directory path to the user config directory for the current indicator.
    def __get_config_directory( self ):
        return self.__get_user_directory( "XDG_CONFIG_HOME", ".config", self.indicator_name )


    # Finds the most recent file in the cache with the given basename
    # and if the timestamp is older than the current date/time
    # plus the maximum age, returns True, otherwise False.
    # If no file can be found, returns True.
#TODO UNCHECKED
    def is_cache_stale( self, utc_now, basename, maximum_age_in_hours ):
        cache_date_time = self.get_cache_date_time( basename )
        if cache_date_time is None:
            stale = True

        else:
            stale = ( cache_date_time + datetime.timedelta( hours = maximum_age_in_hours ) ) < utc_now

        return stale


    # Find the date/time of the newest file in the cache matching the basename.
    #
    # basename: The text used to form the file name, typically the name of the calling application.
    #
    # Returns the datetime of the newest file in the cache; None if no file can be found.
#TODO UNCHECKED
    def get_cache_date_time( self, basename ):
        expiry = None
        the_file = ""
        for file in os.listdir( self.get_cache_directory() ):
            if file.startswith( basename ) and file > the_file:
                the_file = file

        if the_file: # A value of "" evaluates to False.
            date_time_component = the_file[ len( basename ) : len( basename ) + 14 ]

            # YYYYMMDDHHMMSS is 14 characters.
            expiry = \
                datetime.datetime.strptime(
                    date_time_component,
                    IndicatorBase.__CACHE_DATE_TIME_FORMAT_YYYYMMDDHHMMSS )

            expiry = expiry.replace( tzinfo = datetime.timezone.utc )

        return expiry


    # Create a filename with timestamp and extension to be used to save data to the cache.
#TODO UNCHECKED
    def get_cache_filename_with_timestamp( self, basename, extension = EXTENSION_TEXT ):
        return \
            self.get_cache_directory() + \
            basename + \
            datetime.datetime.now().strftime( IndicatorBase.__CACHE_DATE_TIME_FORMAT_YYYYMMDDHHMMSS ) + \
            extension


    # Search through the cache for all files matching the basename.
    #
    # Returns the newest filename matching the basename on success; None otherwise.
#TODO UNCHECKED
    def get_cache_newest_filename( self, basename ):
        cache_directory = self.get_cache_directory()
        cache_file = ""
        for file in os.listdir( cache_directory ):
            if file.startswith( basename ) and file > cache_file:
                cache_file = file

        if cache_file:
            cache_file = cache_directory + cache_file

        else:
            cache_file = None

        return cache_file


    # Remove a file from the cache.
    #
    # filename: The file to remove.
    #
    # The file removed will be either
    #     ${XDGKey}/applicationBaseDirectory/fileName
    # or
    #     ~/.cache/applicationBaseDirectory/fileName
    def remove_file_from_cache( self, filename ):
        cache_directory = self.get_cache_directory()
        for file in os.listdir( cache_directory ):
            if file == filename:
                os.remove( cache_directory + file )
                break


    # Removes out of date cache files for a given basename.
    #
    # basename: The text used to form the file name, typically the name of the calling application.
    # maximumAgeInHours: Anything older than the maximum age (hours) is deleted.
    #
    # Any file in the cache directory matching the pattern
    #
    #     ${XDGKey}/applicationBaseDirectory/basenameCACHE_DATE_TIME_FORMAT_YYYYMMDDHHMMSS
    # or
    #     ~/.cache/applicationBaseDirectory/basenameCACHE_DATE_TIME_FORMAT_YYYYMMDDHHMMSS
    #
    # and is older than the cache maximum age is discarded.
    #
    # Any file extension is ignored in determining if the file should be deleted or not.
    def flush_cache( self, basename, maximum_age_in_hours ):
        cache_directory = self.get_cache_directory()
        cache_maximum_age_date_time = datetime.datetime.now() - datetime.timedelta( hours = maximum_age_in_hours )
        for file in os.listdir( cache_directory ):
#TODO Test with something like indicatorlunar to ensure only appropriate files are cleared from the cache.
            if file.startswith( basename ): # Sometimes the base name is shared ("icon-" versus "icon-fullmoon-") so use the date/time to ensure the correct group of files.
                date_time = file[ len( basename ) : len( basename ) + 14 ] # len( YYYYMMDDHHMMSS ) = 14.
                if date_time.isdigit():
                    file_date_time = \
                        datetime.datetime.strptime(
                            date_time,
                            IndicatorBase.__CACHE_DATE_TIME_FORMAT_YYYYMMDDHHMMSS )

                    if file_date_time < cache_maximum_age_date_time:
                        os.remove( cache_directory + file )


    # Read the most recent binary file from the cache.
    #
    # basename: The text used to form the file name, typically the name of the calling application.
    #
    # All files in cache directory are filtered based on the pattern
    #     ${XDGKey}/applicationBaseDirectory/basenameCACHE_DATE_TIME_FORMAT_YYYYMMDDHHMMSS
    # or
    #     ~/.cache/applicationBaseDirectory/basenameCACHE_DATE_TIME_FORMAT_YYYYMMDDHHMMSS
    #
    # For example, for an application 'apple', the first file will pass through, whilst the second is filtered out
    #    ~/.cache/fred/apple-20170629174950
    #    ~/.cache/fred/orange-20170629174951
    #
    # Files which pass the filter are sorted by date/time and the most recent file is read.
    #
    # Returns the binary object; None when no suitable cache file exists; None on error and logs.
#TODO UNCHECKED
    def read_cache_binary( self, basename ):
        data = None
        the_file = ""
        for file in os.listdir( self.get_cache_directory() ):
            if file.startswith( basename ) and file > the_file:
                the_file = file

        if the_file: # A value of "" evaluates to False.
            filename = self.get_cache_directory() + the_file
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
    # binaryData: The object to write.
    # basename: The text used to form the file name, typically the name of the calling application.
    # extension: Added to the end of the basename and date/time.
    #
    # The object will be written to the cache directory using the pattern
    #     ${XDGKey}/applicationBaseDirectory/basenameCACHE_DATE_TIME_FORMAT_YYYYMMDDHHMMSS
    # or
    #     ~/.cache/applicationBaseDirectory/basenameCACHE_DATE_TIME_FORMAT_YYYYMMDDHHMMSS
    #
    # Returns True on success; False otherwise.
#TODO UNCHECKED
    def write_cache_binary( self, binary_data, basename, extension = "" ):
        success = True
        cache_file = \
            self.get_cache_directory() + \
            basename + \
            datetime.datetime.now().strftime( IndicatorBase.__CACHE_DATE_TIME_FORMAT_YYYYMMDDHHMMSS ) + \
            extension

        try:
            with open( cache_file, 'wb' ) as f_out:
                pickle.dump( binary_data, f_out )

        except Exception as e:
            logging.exception( e )
            logging.error( "Error writing to cache: " + cache_file )
            success = False

        return success


    # Read the named text file from the cache.
    #
    # filename: The name of the file.
    #
    # Returns the contents of the text file; None on error and logs.
    def read_cache_text_without_timestamp( self, filename ):
        return self.__read_cache_text( self.get_cache_directory() + filename )


    # Read the most recent text file from the cache.
    #
    # basename: The text used to form the file name, typically the name of the calling application.
    #
    # All files in cache directory are filtered based on the pattern
    #     ${XDGKey}/applicationBaseDirectory/basenameCACHE_DATE_TIME_FORMAT_YYYYMMDDHHMMSSextension
    # or
    #     ~/.cache/applicationBaseDirectory/basenameCACHE_DATE_TIME_FORMAT_YYYYMMDDHHMMSSextension
    #
    # For example, for an application 'apple', the first file will be caught, whilst the second is filtered out:
    #    ~/.cache/fred/apple-20170629174950
    #    ~/.cache/fred/orange-20170629174951
    #
    # Files which pass the filter are sorted by date/time and the most recent file is read.
    #
    # Returns the contents of the text; None when no suitable cache file exists; None on error and logs.
#TODO UNCHECKED
    def read_cache_text( self, basename ):
        cache_directory = self.get_cache_directory()
        cache_file = ""
        for file in os.listdir( cache_directory ):
            if file.startswith( basename ) and file > cache_file:
                cache_file = file

        if cache_file:
            cache_file = cache_directory + cache_file

        return self.__read_cache_text( cache_file )


    def __read_cache_text( self, cache_file ):
        text = ""
        if os.path.isfile( cache_file ):
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
        return self.__write_cache_text( text, self.get_cache_directory() + filename )


    # Writes text to a file in the cache.
    #
    # text: The text to write.
    # basename: The text used to form the file name, typically the name of the calling application.
    # extension: Added to the end of the basename and date/time.
    #
    # The text will be written to the cache directory using the pattern
    #     ${XDGKey}/applicationBaseDirectory/basenameCACHE_DATE_TIME_FORMAT_YYYYMMDDHHMMSSextension
    # or
    #     ~/.cache/applicationBaseDirectory/basenameCACHE_DATE_TIME_FORMAT_YYYYMMDDHHMMSSextension
    #
    # Returns filename written on success; None otherwise.
    def write_cache_text( self, text, basename, extension = EXTENSION_TEXT ):
        cache_file = \
            self.get_cache_directory() + \
            basename + \
            datetime.datetime.now().strftime( IndicatorBase.__CACHE_DATE_TIME_FORMAT_YYYYMMDDHHMMSS ) + \
            extension

        return self.__write_cache_text( text, cache_file )


    def __write_cache_text( self, text, cache_file ):
        try:
            with open( cache_file, 'w' ) as f_out:
                f_out.write( text )

        except Exception as e:
            logging.exception( e )
            logging.error( "Error writing to cache: " + cache_file )
            cache_file = None

        return cache_file


    # Return the full directory path to the user cache directory for the current indicator.
    def get_cache_directory( self ):
        return self.__get_user_directory( "XDG_CACHE_HOME", ".cache", self.indicator_name )


    # Obtain (and create if not present) the directory for configuration, cache or similar.
    #
    # XDGKey: The XDG environment variable used to obtain the base directory of the configuration/cache.
    #         https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html
    # userBaseDirectory: The directory name used to hold the configuration/cache
    #                    (used when the XDGKey is not present in the environment).
    # applicationBaseDirectory: The directory name at the end of the final user directory to specify the application.
    #
    # The full directory path will be either
    #    ${XDGKey}/applicationBaseDirectory
    # or
    #    ~/.userBaseDirectory/applicationBaseDirectory
    def __get_user_directory( self, xdg_key, user_base_directory, application_base_directory ):
        if xdg_key in os.environ:
            directory = \
                os.environ[ xdg_key ] + os.sep + \
                application_base_directory + os.sep

        else:
            directory = \
                os.path.expanduser( '~' ) + os.sep + \
                user_base_directory + os.sep + \
                application_base_directory + os.sep

        if not os.path.isdir( directory ):
            os.mkdir( directory )

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

            if not result:
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
#TODO UNCHECKED
class TruncatedFileHandler( logging.handlers.RotatingFileHandler ):

    def __init__( self, filename, maxBytes = 10000 ):
        super().__init__(
            filename,
            maxBytes = maxBytes,
            delay = True )


    def doRollover( self ):
        if self.stream:
            self.stream.close()

        if os.path.exists( self.baseFilename ): # self.baseFilename is defined in parent class.
            os.remove( self.baseFilename )

        self.mode = 'a'
        self.stream = self._open()
