#!/usr/bin/env python3
from debian import changelog


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
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


# Application indicator which displays the current Star Trek™ stardate.


# References:
#  http://developer.gnome.org/pygobject
#  http://developer.gnome.org/gtk3
#  http://python-gtk-3-tutorial.readthedocs.org
#  http://developer.ubuntu.com/api/ubuntu-12.10/python/AppIndicator3-0.1.html


try:
    from gi.repository import AppIndicator3 as appindicator
except:
    pass

from gi.repository import GLib, Gtk

import datetime, gzip, json, logging, os, re, shutil, stardate, sys


class IndicatorStardate:

    AUTHOR = "Bernard Giannetti"
    NAME = "indicator-stardate"
    VERSION = "1.0.16"
    ICON = NAME
    LICENSE = "Distributed under the GNU General Public License, version 3.\nhttp://www.opensource.org/licenses/GPL-3.0"
    LOG = os.getenv( "HOME" ) + "/" + NAME + ".log"
    WEBSITE = "https://launchpad.net/~thebernmeister"

    AUTOSTART_PATH = os.getenv( "HOME" ) + "/.config/autostart/"
    DESKTOP_PATH = "/usr/share/applications/"
    DESKTOP_FILE = NAME + ".desktop"

    COMMENTS = "Shows the current Star Trek™ stardate."
    CREDITS = [ "Based on STARDATES IN STAR TREK FAQ V1.6 by Andrew Main." ]

    SETTINGS_FILE = os.getenv( "HOME" ) + "/." + NAME + ".json"
    SETTINGS_SHOW_CLASSIC = "showClassic"
    SETTINGS_SHOW_ISSUE = "showIssue"


    def __init__( self ):
        filehandler = logging.FileHandler( filename = IndicatorStardate.LOG, mode = "a", delay = True )
        logging.basicConfig( format = "%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s", 
                             datefmt = "%H:%M:%S", level = logging.DEBUG,
                             handlers = [ filehandler ] )

        self.dialog = None
        self.loadSettings()

        try:
            self.appindicatorImported = True
            self.indicator = appindicator.Indicator.new( IndicatorStardate.NAME, IndicatorStardate.ICON, appindicator.IndicatorCategory.APPLICATION_STATUS )
            self.indicator.set_status( appindicator.IndicatorStatus.ACTIVE )
            self.buildMenu()
            self.indicator.set_menu( self.menu )
        except:
            self.appindicatorImported = False            
            self.buildMenu()
            self.statusicon = Gtk.StatusIcon()
            self.statusicon.set_from_icon_name( IndicatorStardate.ICON )
            self.statusicon.connect( "popup-menu", self.handleRightClick )
            self.statusicon.connect( "activate", self.handleLeftClick )


    def buildMenu( self ):
        self.menu = Gtk.Menu()

        if self.appindicatorImported == False:
            image = Gtk.Image()
            image.set_from_icon_name( IndicatorStardate.ICON, Gtk.IconSize.MENU )
            self.stardateMenuItem = Gtk.ImageMenuItem()
            self.stardateMenuItem.set_image( image )
            self.menu.append( self.stardateMenuItem )
            self.menu.append( Gtk.SeparatorMenuItem() )

        preferencesMenuItem = Gtk.ImageMenuItem.new_from_stock( Gtk.STOCK_PREFERENCES, None )
        preferencesMenuItem.connect( "activate", self.onPreferences )
        self.menu.append( preferencesMenuItem )

        aboutMenuItem = Gtk.ImageMenuItem.new_from_stock( Gtk.STOCK_ABOUT, None )
        aboutMenuItem.connect( "activate", self.onAbout )
        self.menu.append( aboutMenuItem )

        quitMenuItem = Gtk.ImageMenuItem.new_from_stock( Gtk.STOCK_QUIT, None )
        quitMenuItem.connect( "activate", Gtk.main_quit )
        self.menu.append( quitMenuItem )

        self.menu.show_all()


    def main( self ):
        self.stardate = stardate.Stardate()
        self.update()

        # Use the stardate update period to set a refresh timer.
        # The stardate calculation and WHEN the stardate changes are not synchronised,
        # so update at ten times speed (but no less than once per second).
        period = int( self.stardate.getStardateFractionalPeriod() / 10 ) 
        if period < 1:
            period = 1

        GLib.timeout_add_seconds( period, self.update )
        Gtk.main()


    def update( self ):
        self.stardate.setClassic( self.showClassic )
        self.stardate.setGregorian( datetime.datetime.now() )
        s = self.stardate.toStardateString( self.showIssue )

        if self.appindicatorImported == True:
            self.indicator.set_label( s, "" ) # Second parameter is a guide for how wide the text could get (see label-guide in http://developer.ubuntu.com/api/ubuntu-12.10/python/AppIndicator3-0.1.html).
        else:
            self.statusicon.set_tooltip_text( "Stardate: " + s )
            self.stardateMenuItem.set_label( "Stardate: " + s )

        return True # Needed so the timer continues!


    def handleLeftClick( self, icon ):
        self.menu.popup( None, None, Gtk.StatusIcon.position_menu, self.statusicon, 1, Gtk.get_current_event_time() )


    def handleRightClick( self, icon, button, time ):
        self.menu.popup( None, None, Gtk.StatusIcon.position_menu, self.statusicon, button, time )


    def onAbout( self, widget ):
        if self.dialog is not None:
            self.dialog.present()
            return

        self.dialog = AboutDialogWithChangeLog( 
               IndicatorStardate.NAME,
               IndicatorStardate.COMMENTS, 
               IndicatorStardate.WEBSITE, 
               IndicatorStardate.WEBSITE, 
               IndicatorStardate.VERSION, 
               Gtk.License.GPL_3_0, 
               IndicatorStardate.ICON,
               [ IndicatorStardate.AUTHOR ],
                IndicatorStardate.CREDITS,
                "Credits",
               self.getChangeLog() )

        self.dialog.run()
        self.dialog.destroy()
        self.dialog = None


    def onPreferences( self, widget ):
        if self.dialog is not None:
            self.dialog.present()
            return

        grid = Gtk.Grid()
        grid.set_column_spacing( 10 )
        grid.set_row_spacing( 10 )
        grid.set_margin_left( 10 )
        grid.set_margin_right( 10 )
        grid.set_margin_top( 10 )
        grid.set_margin_bottom( 10 )

        showClassicCheckbox = Gtk.CheckButton( "Use 'classic' conversion" )
        showClassicCheckbox.set_active( self.showClassic )
        showClassicCheckbox.set_tooltip_text( "Stardate 'classic' is based on STARDATES IN STAR TREK FAQ V1.6 by Andrew Main.\n\nOtherwise the 2009 revised conversion is used (http://en.wikipedia.org/wiki/Stardate)." )
        grid.attach( showClassicCheckbox, 0, 0, 2, 1 )

        showIssueCheckbox = Gtk.CheckButton( "Show ISSUE" )
        showIssueCheckbox.set_active( self.showIssue )
        showIssueCheckbox.set_sensitive( showClassicCheckbox.get_active() )
        showIssueCheckbox.set_margin_left( 15 )
        showIssueCheckbox.set_tooltip_text( "Show the ISSUE of the stardate (only applies to 'classic')" )
        grid.attach( showIssueCheckbox, 0, 1, 1, 1 )

        showClassicCheckbox.connect( "toggled", self.onShowClassicCheckbox, showIssueCheckbox )

        autostartCheckbox = Gtk.CheckButton( "Autostart" )
        autostartCheckbox.set_active( os.path.exists( IndicatorStardate.AUTOSTART_PATH + IndicatorStardate.DESKTOP_FILE ) )
        grid.attach( autostartCheckbox, 0, 2, 2, 1 )

        self.dialog = Gtk.Dialog( "Preferences", None, 0, ( Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK ) )
        self.dialog.vbox.pack_start( grid, True, True, 0 )
        self.dialog.set_border_width( 5 )
        self.dialog.set_icon_name( IndicatorStardate.ICON )
        self.dialog.show_all()

        response = self.dialog.run()
        if response == Gtk.ResponseType.OK:
            self.showClassic = showClassicCheckbox.get_active()
            self.showIssue = showIssueCheckbox.get_active()
            self.saveSettings()

            if not os.path.exists( IndicatorStardate.AUTOSTART_PATH ):
                os.makedirs( IndicatorStardate.AUTOSTART_PATH )

            if autostartCheckbox.get_active():
                try:
                    shutil.copy( IndicatorStardate.DESKTOP_PATH + IndicatorStardate.DESKTOP_FILE, IndicatorStardate.AUTOSTART_PATH + IndicatorStardate.DESKTOP_FILE )
                except Exception as e:
                    logging.exception( e )
            else:
                try:
                    os.remove( IndicatorStardate.AUTOSTART_PATH + IndicatorStardate.DESKTOP_FILE )
                except: pass

            self.update()

        self.dialog.destroy()
        self.dialog = None


    def onShowClassicCheckbox( self, source, showIssueCheckbox ):
        showIssueCheckbox.set_sensitive( source.get_active() )


    def loadSettings( self ):
        self.showClassic = True
        self.showIssue = True

        if os.path.isfile( IndicatorStardate.SETTINGS_FILE ):
            try:
                with open( IndicatorStardate.SETTINGS_FILE, "r" ) as f:
                    settings = json.load( f )

                self.showIssue = settings.get( IndicatorStardate.SETTINGS_SHOW_ISSUE, self.showIssue )

            except Exception as e:
                logging.exception( e )
                logging.error( "Error reading settings: " + IndicatorStardate.SETTINGS_FILE )


    def saveSettings( self ):
        try:
            settings = {
                IndicatorStardate.SETTINGS_SHOW_ISSUE: self.showClassic,
                IndicatorStardate.SETTINGS_SHOW_ISSUE: self.showIssue
            }
            with open( IndicatorStardate.SETTINGS_FILE, "w" ) as f:
                f.write( json.dumps( settings ) )

        except Exception as e:
            logging.exception( e )
            logging.error( "Error writing settings: " + IndicatorStardate.SETTINGS_FILE )


    # Assumes a typical format for a Debian changelog file.
    def getChangeLog( self ):
        contents = None
        changeLog = "/usr/share/doc/" + IndicatorStardate.NAME + "/changelog.Debian.gz"
        if os.path.exists( changeLog ):
            try:
                with gzip.open( changeLog, 'rb' ) as f:
                    changeLogContents = re.split( "\n\n\n", f.read().decode() )

                    contents = ""
                    for changeLogEntry in changeLogContents:
                        changeLogEntry = changeLogEntry.split( "\n" )

                        version = changeLogEntry[ 0 ].split( "(" )[ 1 ].split( "-1)" )[ 0 ]
                        dateTime = changeLogEntry[ len( changeLogEntry ) - 1 ].split( ">" )[ 1 ].split( "+" )[ 0 ].strip()
                        changes = "\n".join( changeLogEntry[ 2 : len( changeLogEntry ) - 2 ] )

                        contents += "Version " + version + " (" + dateTime + ")\n" + changes + "\n\n"

                    contents = contents.strip()

            except Exception as e:
                logging.exception( e )
                logging.error( "Error reading changelog: " + changeLog )
                contents = None

        return contents


class AboutDialogWithChangeLog( Gtk.AboutDialog ):

    CHANGELOG_BUTTON_NAME = "Change _Log"


    # If there are no credits, set both credits/creditsLabel to "".
    # Changelog can be set to None...if that's the case, use a GtkAboutDialog.
    def __init__( self, programName, comments, website, websiteLabel, version, licenseType, logoIconName, authors, credits, creditsLabel, changeLog ):
        super( AboutDialogWithChangeLog, self ).__init__()

        self.add_credit_section( creditsLabel, credits )
        self.set_authors( authors )
        self.set_comments( comments )
        self.set_license_type( licenseType )
        self.set_logo_icon_name( logoIconName )
        self.set_program_name( programName )
        self.set_version( version )
        self.set_website( website )
        self.set_website_label( websiteLabel )
        self.set_position( Gtk.WindowPosition.CENTER_ALWAYS )

        if changeLog is None: return

        notebook = self.get_content_area().get_children()[ 0 ].get_children()[ 2 ]

        textView = Gtk.TextView()
        textView.set_editable( False )
        textBuffer = textView.get_buffer()
        textBuffer.set_text( changeLog )

        # Reference https://gitorious.org/ghelp/gtk/raw/5c4f2ef0c1e658827091aadf4fc3c4d5f5964785:gtk/gtkaboutdialog.c
        scrolledWindow = Gtk.ScrolledWindow()
        scrolledWindow.set_shadow_type( Gtk.ShadowType.IN );
        scrolledWindow.set_policy( Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC )
        scrolledWindow.set_hexpand( True )
        scrolledWindow.set_vexpand( True )
        scrolledWindow.add( textView )
        scrolledWindow.show_all()

        changeLogTabIndex = notebook.append_page( scrolledWindow, Gtk.Label( "" ) ) # The tab is hidden so the label contents are irrelevant.

        changeLogButton = Gtk.ToggleButton( AboutDialogWithChangeLog.CHANGELOG_BUTTON_NAME )
        changeLogButton.set_use_underline( True )
        changeLogButton.show()

        buttonBox = self.get_content_area().get_children()[ 1 ]
        buttonBox.pack_start( changeLogButton, True, True, 0 )
        buttonBox.set_child_secondary( changeLogButton, True )

        buttons = buttonBox.get_children()
        buttonsForToggle = [ ]
        for button in buttons:
            if button.get_label() != AboutDialogWithChangeLog.CHANGELOG_BUTTON_NAME and button.get_label() != "gtk-close":
                buttonsForToggle.append( button )
                button.connect( "toggled", self.onOtherToggledButtons, changeLogButton )

        changeLogButton.connect( "toggled", self.onChangeLogButtonToggled, notebook, changeLogTabIndex, buttonsForToggle )


    def onChangeLogButtonToggled( self, changeLogButton, notebook, changeLogTabIndex, buttonsForToggle ):
        if changeLogButton.get_active():
            if notebook.get_current_page() != 0:
                for button in buttonsForToggle:
                    button.set_active( False )

            notebook.set_current_page( changeLogTabIndex )
        else:
            if notebook.get_current_page() == changeLogTabIndex:
                notebook.set_current_page( 0 )


    def onOtherToggledButtons( self, toggleButton, changeLogButton ):
        if toggleButton.get_active() and changeLogButton.get_active():
            changeLogButton.set_active( False )


if __name__ == "__main__": IndicatorStardate().main()