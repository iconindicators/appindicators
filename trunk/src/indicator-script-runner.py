#!/usr/bin/env python3


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


# Application indicator allowing a user to run a terminal command or script.


# TODO Can't run multiple scripts simultaneously (irrespective of the value of terminalOpen).


INDICATOR_NAME = "indicator-script-runner"
import gettext
gettext.install( INDICATOR_NAME )

from gi.repository import AppIndicator3, GLib, Gtk
from script import Info

import copy, json, locale, logging, os, pythonutils, stat, time


class IndicatorScriptRunner:

    AUTHOR = "Bernard Giannetti"
    VERSION = "1.0.0"
    ICON = INDICATOR_NAME
    LOG = os.getenv( "HOME" ) + "/" + INDICATOR_NAME + ".log"
    WEBSITE = "https://launchpad.net/~thebernmeister"

    DESKTOP_FILE = INDICATOR_NAME + ".desktop"

    COMMENTS = _( "Run a terminal command or script from a GUI frontend." )

    SETTINGS_FILE = os.getenv( "HOME" ) + "/." + INDICATOR_NAME + ".json"
    SETTINGS_SCRIPTS = "scripts"


    def __init__( self ):
        filehandler = pythonutils.TruncatedFileHandler( IndicatorScriptRunner.LOG, "a", 10000, None, True )
        logging.basicConfig( format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s", level = logging.DEBUG, handlers = [ filehandler ] )
        self.dialog = None
        self.loadSettings()

#TODO Temporary testing of icon.
#         self.indicator = AppIndicator3.Indicator.new( INDICATOR_NAME, os.path.abspath( "/home/bernard/Programming/IndicatorScriptRunner/icons/ubuntu-mono-dark/" + IndicatorScriptRunner.ICON + ".svg" ), AppIndicator3.IndicatorCategory.APPLICATION_STATUS )
        self.indicator = AppIndicator3.Indicator.new( INDICATOR_NAME, IndicatorScriptRunner.ICON, AppIndicator3.IndicatorCategory.APPLICATION_STATUS )
        self.indicator.set_status( AppIndicator3.IndicatorStatus.ACTIVE )
        self.indicator.set_menu( self.buildMenu() )


    def main( self ): Gtk.main()


#TODO Have an option to put script descriptions into submenus?
    def buildMenu( self ):
        scripts = self.getScriptsGroupedByName()
        menu = Gtk.Menu()
        for scriptName in sorted( scripts.keys(), key = str.lower ):
            menu.append( Gtk.MenuItem( scriptName + "..." ) )
            scripts[ scriptName ].sort( key = lambda script: script.getDescription().lower() )
            for script in scripts[ scriptName ]:
                menuItem = Gtk.MenuItem( "        " + script.getDescription() )
                menuItem.connect( "activate", self.onScript, script )
                menu.append( menuItem )

        pythonutils.createPreferencesAboutQuitMenuItems( menu, len( scripts ) > 0, self.onPreferences, self.onAbout, Gtk.main_quit )
        self.indicator.set_menu( menu )
        menu.show_all()
        return menu


#TODO http://stackoverflow.com/questions/3512055/avoid-gnome-terminal-close-after-script-execution
# http://askubuntu.com/questions/484993/run-command-on-anothernew-terminal-window
# http://stackoverflow.com/questions/11500649/new-terminal-with-multiple-commands-executed
# http://askubuntu.com/questions/351097/passing-multiple-commands-to-gnome-terminal-from-a-script


#TODO Need to test the whole shebang on Lubuntu/Xubuntu...
#Might have to send ALT CTRL T which works on ALL Ubuntu versions...
# http://stackoverflow.com/questions/5714072/simulate-keystroke-in-linux-with-python
# http://askubuntu.com/questions/500972/why-does-man-x-terminal-emulator-return-the-output-of-man-gnome-terminal   
# Xubuntu: x-terminal-emulator default has same arguments as GNOME.
# Lubuntu: x-terminal-emulator default has same arguments as GNOME (but does not have the -x option).
    def onScript( self, widget, script ):
        wrapperScript = ""
        if script.isTerminalOpen():
            wrapperScript = "/tmp/" + str( int ( time.time() ) )
            if os.path.isfile( wrapperScript ):
                os.remove( wrapperScript )

#TODO Is this a security risk leaving the script there?
            with open( wrapperScript, "w" ) as f:
                f.write( "#!/bin/sh\n" )
                f.write( "\"$@\"\n" )
                f.write( "exec \"$SHELL\"\n" )

#TODO Determine which of these permissions are needed or not when the indicator runs as per installed.
            os.chmod( wrapperScript, os.stat( wrapperScript ).st_mode | stat.S_IXUSR )
            os.chmod( wrapperScript, os.stat( wrapperScript ).st_mode | stat.S_IXGRP )
            os.chmod( wrapperScript, os.stat( wrapperScript ).st_mode | stat.S_IXOTH )

        terminalExecutable = "gnome-terminal"
        command = terminalExecutable
        if script.getDirectory() != "":
            command += " --working-directory=" + script.getDirectory()

        command += " -e '" + wrapperScript + " " + script.getCommand() + "'"
        pythonutils.processCall( command )


    def onAbout( self, widget ):
        if self.dialog is None:
            self.dialog = pythonutils.createAboutDialog(
                [ IndicatorScriptRunner.AUTHOR ],
                IndicatorScriptRunner.COMMENTS, 
                [ ],
                "",
                Gtk.License.GPL_3_0,
                IndicatorScriptRunner.ICON,
                INDICATOR_NAME,
                IndicatorScriptRunner.WEBSITE,
                IndicatorScriptRunner.VERSION,
                _( "translator-credits" ),
                _( "View the" ),
                _( "text file." ),
                _( "changelog" ) )

            self.dialog.run()
            self.dialog.destroy()
            self.dialog = None
        else:
            self.dialog.present()


#TODO OPen preferences...was able to kick off a script whilst Prefs are open..that's bad!
#Does this happen in other indicators (and is it of concern)?
    def onPreferences( self, widget ):
        if self.dialog is not None:
            self.dialog.present()
            return

        backup = copy.deepcopy( self.scripts )
        notebook = Gtk.Notebook()

        # User scripts.
        grid = Gtk.Grid()
        grid.set_column_spacing( 10 )
        grid.set_row_spacing( 10 )
        grid.set_margin_left( 10 )
        grid.set_margin_right( 10 )
        grid.set_margin_top( 10 )
        grid.set_margin_bottom( 10 )
        grid.set_row_homogeneous( False )
        grid.set_column_homogeneous( False )

        box = Gtk.Box( spacing = 6 )
        box.set_margin_top( 10 )

        box.pack_start( Gtk.Label( _( "Script Name" ) ), False, False, 0 )

        scriptNameComboBox = Gtk.ComboBoxText()
        scriptNameComboBox.set_tooltip_text( _( "The name of a script object.\n\nMore than one script may\nshare the same name but\nhave a different description." ) )
        scriptNameComboBox.set_entry_text_column( 0 )
        self.populateScriptNameCombo( scriptNameComboBox )

        box.pack_start( scriptNameComboBox, True, True, 0 )
        grid.attach( box, 0, 0, 1, 1 )

        scriptDescriptionListStore = Gtk.ListStore( str, str ) # Script descriptions, tick icon (Gtk.STOCK_APPLY) or None for terminal open.
        scriptDescriptionListStore.set_sort_column_id( 0, Gtk.SortType.ASCENDING )

        scriptDescriptionTreeView = Gtk.TreeView( scriptDescriptionListStore )
        scriptDescriptionTreeView.set_tooltip_text( _( "List of scripts with same name,\nbut different descriptions." ) )
        scriptDescriptionTreeView.set_hexpand( True )
        scriptDescriptionTreeView.set_vexpand( True )
        scriptDescriptionTreeView.get_selection().set_mode( Gtk.SelectionMode.BROWSE )

        treeViewColumn = Gtk.TreeViewColumn( _( "Script Description" ), Gtk.CellRendererText(), text = 0 )
        treeViewColumn.set_expand( True )
        scriptDescriptionTreeView.append_column( treeViewColumn )

        treeViewColumn = Gtk.TreeViewColumn( _( "Terminal Open" ), Gtk.CellRendererPixbuf(), stock_id = 1 )
        treeViewColumn.set_expand( False )
        scriptDescriptionTreeView.append_column( treeViewColumn )

        scrolledWindow = Gtk.ScrolledWindow()
        scrolledWindow.set_policy( Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC )
        scrolledWindow.add( scriptDescriptionTreeView )

        grid.attach( scrolledWindow, 0, 1, 1, 15 )

        box = Gtk.Box( spacing = 6 )
        box.set_margin_top( 10 )

        box.pack_start( Gtk.Label( _( "Directory" ) ), False, False, 0 )

        directoryEntry = Gtk.Entry()
        directoryEntry.set_tooltip_text( _( "The directory from which the\nscript/command is executed." ) )
        directoryEntry.set_editable( False )

        box.pack_start( directoryEntry, True, True, 0 )

        grid.attach( box, 0, 16, 1, 1 )

        box = Gtk.Box( orientation = Gtk.Orientation.VERTICAL, spacing = 6 )
        box.set_margin_top( 10 )

        label = Gtk.Label( _( "Command" ) )
        label.set_halign( Gtk.Align.START )
        box.pack_start( label, False, False, 0 )

        commandTextView = Gtk.TextView()
        commandTextView.set_tooltip_text( _( "The terminal script/command,\nalong with any arguments." ) )
        commandTextView.set_editable( False )
        commandTextView.set_wrap_mode( Gtk.WrapMode.WORD )

        scrolledWindow = Gtk.ScrolledWindow()
        scrolledWindow.add( commandTextView )
        scrolledWindow.set_hexpand( True )
        scrolledWindow.set_vexpand( True )

        box.pack_start( scrolledWindow, True, True, 0 )
        grid.attach( box, 0, 17, 1, 15 )

        box = Gtk.Box( spacing = 6 )
        box.set_margin_top( 10 )
        box.set_homogeneous( True )

        addButton = Gtk.Button( _( "Add" ) )
        addButton.set_tooltip_text( _( "Add a new script." ) )
        addButton.connect( "clicked", self.onScriptAdd, scriptNameComboBox, scriptDescriptionTreeView )

        box.pack_start( addButton, True, True, 0 )

        editButton = Gtk.Button( _( "Edit" ) )
        editButton.set_tooltip_text( _( "Edit the current script." ) )
        editButton.connect( "clicked", self.onScriptEdit, scriptNameComboBox, scriptDescriptionTreeView )
        box.pack_start( editButton, True, True, 0 )

        removeButton = Gtk.Button( _( "Remove" ) )
        removeButton.set_tooltip_text( _( "Remove the selected script." ) )
        removeButton.connect( "clicked", self.onScriptRemove, scriptNameComboBox, scriptDescriptionTreeView, directoryEntry, commandTextView )
        box.pack_start( removeButton, True, True, 0 )

        box.set_halign( Gtk.Align.CENTER )
        grid.attach( box, 0, 32, 1, 1 )

        notebook.append_page( grid, Gtk.Label( _( "Scripts" ) ) )

        # General settings.
        grid = Gtk.Grid()
        grid.set_column_spacing( 10 )
        grid.set_row_spacing( 10 )
        grid.set_margin_left( 10 )
        grid.set_margin_right( 10 )
        grid.set_margin_top( 10 )
        grid.set_margin_bottom( 10 )

        autostartCheckbox = Gtk.CheckButton( _( "Autostart" ) )
        autostartCheckbox.set_tooltip_text( _( "Run the indicator automatically." ) )
        autostartCheckbox.set_active( pythonutils.isAutoStart( IndicatorScriptRunner.DESKTOP_FILE ) )
        autostartCheckbox.set_margin_top( 10 )
        grid.attach( autostartCheckbox, 0, 0, 1, 1 )

        notebook.append_page( grid, Gtk.Label( _( "General" ) ) )

        scriptNameComboBox.connect( "changed", self.onScriptName, scriptDescriptionListStore, scriptDescriptionTreeView )
        scriptDescriptionTreeView.get_selection().connect( "changed", self.onScriptDescription, scriptNameComboBox, directoryEntry, commandTextView )
        scriptNameComboBox.set_active( 0 ) # TODO Test this with NO scripts added.

        self.dialog = Gtk.Dialog( _( "Preferences" ), None, Gtk.DialogFlags.MODAL, ( Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK ) )
        self.dialog.vbox.pack_start( notebook, True, True, 0 )
        self.dialog.set_border_width( 5 )
        self.dialog.set_icon_name( IndicatorScriptRunner.ICON )
        self.dialog.show_all()

        if self.dialog.run() == Gtk.ResponseType.OK:
            self.saveSettings()
            pythonutils.setAutoStart( IndicatorScriptRunner.DESKTOP_FILE, autostartCheckbox.get_active(), logging )
            self.indicator.set_menu( self.buildMenu() )
        else:
            self.scripts = backup

        self.dialog.destroy()
        self.dialog = None


    def onScriptName( self, scriptNameComboBox, scriptDescriptionListStore, scriptDescriptionTreeView ):
        scriptName = scriptNameComboBox.get_active_text()
        scriptDescriptionListStore.clear()

        scriptDescriptions = [ ]
        for script in self.scripts:
            if script.getName() == scriptName:
                scriptDescriptions.append( script.getDescription() )

        scriptDescriptions = sorted( scriptDescriptions, key = str.lower )

        for scriptDescription in scriptDescriptions:
            terminalOpen = None
            if self.getScript( scriptName, scriptDescription ).isTerminalOpen():
                terminalOpen = Gtk.STOCK_APPLY

            scriptDescriptionListStore.append( [ scriptDescription, terminalOpen ] )

        #TODO Test these work with no data in it.
        scriptDescriptionTreeView.get_selection().select_path( 0 )
        scriptDescriptionTreeView.scroll_to_cell( Gtk.TreePath.new_from_string( "0" ) )


#TODO
# Select a script and then a description other than the first.
# Select a different script - we get a selection event for the prior description.  WHy?
    def onScriptDescription( self, scriptDescriptionTreeSelection, scriptNameComboBox, directoryEntry, commandTextView ):
        scriptName = scriptNameComboBox.get_active_text()
        model, treeiter = scriptDescriptionTreeSelection.get_selected()
        if treeiter != None:
            scriptDescription = model[ treeiter ][ 0 ]
            theScript = self.getScript( scriptName, scriptDescription )
            if theScript is not None:
                directoryEntry.set_text( theScript.getDirectory() )
                commandTextView.get_buffer().set_text( theScript.getCommand() )


    def onScriptRemove( self, button, scriptNameComboBox, scriptDescriptionTreeView, directoryEntry, commandTextView ):
        iter = scriptNameComboBox.get_active_iter()
        if iter != None:
            scriptName = scriptNameComboBox.get_model()[ iter ][ 0 ]
            model, treeiter = scriptDescriptionTreeView.get_selection().get_selected()
            if treeiter != None:
                scriptDescription = model[ treeiter ][ 0 ]
                theScript = self.getScript( scriptName, scriptDescription )
                if pythonutils.showOKCancel( None, _( "Remove the selected script?" ), INDICATOR_NAME ) == Gtk.ResponseType.OK:
                    i = 0
                    for script in self.scripts:
                        if script.getName() == scriptName and script.getDescription() == scriptDescription:
                            break

                        i += 1

                    del self.scripts[ i ]
                    self.populateScriptNameCombo( scriptNameComboBox )
                    scriptNameComboBox.set_active( 0 )
                    if len( self.scripts ) == 0:
                        directoryEntry.set_text( "" )
                        commandTextView.get_buffer().set_text( "" )


    def onScriptAdd( self, button, scriptNameComboBox, scriptDescriptionTreeView ):
        self.addEditScript( Info( "", "", "", "", False ), scriptNameComboBox, scriptDescriptionTreeView )


#TODO Handle when no scripts exist and edit is pressed...same as remove. 
    def onScriptEdit( self, button, scriptNameComboBox, scriptDescriptionTreeView ):
        scriptName = scriptNameComboBox.get_active_text() #TODO This is different to remove...check if this works on an empty list of scripts.
        model, treeiter = scriptDescriptionTreeView.get_selection().get_selected()
        if treeiter != None:
            scriptDescription = model[ treeiter ][ 0 ]
            theScript = self.getScript( scriptName, scriptDescription )
            self.addEditScript( theScript, scriptNameComboBox, scriptDescriptionTreeView )


    def addEditScript( self, script, scriptNameComboBox, scriptDescriptionTreeView ):
        grid = Gtk.Grid()
        grid.set_column_spacing( 10 )
        grid.set_row_spacing( 10 )
        grid.set_margin_left( 10 )
        grid.set_margin_right( 10 )
        grid.set_margin_top( 10 )
        grid.set_margin_bottom( 10 )

        box = Gtk.Box( spacing = 6 )
        box.set_margin_top( 10 )

        box.pack_start( Gtk.Label( _( "Script Name" ) ), False, False, 0 )

        scriptNameEntry = Gtk.Entry()
        scriptNameEntry.set_tooltip_text( _( "The name of the script object." ) )
        scriptNameEntry.set_text( script.getName() )

        box.pack_start( scriptNameEntry, True, True, 0 )

        grid.attach( box, 0, 0, 1, 1 )

        box = Gtk.Box( spacing = 6 )
        box.set_margin_top( 10 )

        box.pack_start( Gtk.Label( _( "Script Description" ) ), False, False, 0 )

        scriptDescriptionEntry = Gtk.Entry()
        scriptDescriptionEntry.set_tooltip_text( _( "The description of the script object." ) )
        scriptDescriptionEntry.set_text( script.getDescription() )

        box.pack_start( scriptDescriptionEntry, True, True, 0 )

        grid.attach( box, 0, 1, 1, 1 )

        box = Gtk.Box( spacing = 6 )
        box.set_margin_top( 10 )

        box.pack_start( Gtk.Label( _( "Directory" ) ), False, False, 0 )

        scriptDirectoryEntry = Gtk.Entry()
        scriptDirectoryEntry.set_tooltip_text( _( "The directory from which the\nscript/command is executed." ) )
        scriptDirectoryEntry.set_text( script.getDirectory() )

        box.pack_start( scriptDirectoryEntry, True, True, 0 )

        grid.attach( box, 0, 2, 1, 1 )

        box = Gtk.Box( orientation = Gtk.Orientation.VERTICAL, spacing = 6 )
        box.set_margin_top( 10 )

        label = Gtk.Label( _( "Command" ) )
        label.set_halign( Gtk.Align.START )
        box.pack_start( label, False, False, 0 )

        commandTextView = Gtk.TextView()
        commandTextView.set_tooltip_text( _( "The terminal script/command,\nalong with any arguments." ) )
        commandTextView.set_wrap_mode( Gtk.WrapMode.WORD )
        commandTextView.get_buffer().set_text( script.getCommand() )

        scrolledWindow = Gtk.ScrolledWindow()
        scrolledWindow.add( commandTextView )
        scrolledWindow.set_hexpand( True )
        scrolledWindow.set_vexpand( True )

        box.pack_start( scrolledWindow, True, True, 0 )
        grid.attach( box, 0, 3, 1, 20 )

        terminalOpenCheckbox = Gtk.CheckButton( _( "Terminal Open" ) )
        terminalOpenCheckbox.set_tooltip_text( _( "Leave the terminal open after the script completes." ) )
        terminalOpenCheckbox.set_active( script.isTerminalOpen() )

        grid.attach( terminalOpenCheckbox, 0, 23, 1, 1 )

        title = _( "Edit Script" )
        if script.getName() == "":
            title = _( "Add Script" )

        dialog = Gtk.Dialog( title, self.dialog, Gtk.DialogFlags.MODAL, ( Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK ) )
        dialog.vbox.pack_start( grid, True, True, 0 )
        dialog.set_border_width( 5 )
        dialog.set_icon_name( IndicatorScriptRunner.ICON )

        while True:
            dialog.show_all()
            if dialog.run() == Gtk.ResponseType.OK:

                if scriptNameEntry.get_text().strip() == "":
                    pythonutils.showMessage( dialog, Gtk.MessageType.ERROR, _( "The script name cannot be empty." ), INDICATOR_NAME )
                    scriptNameEntry.grab_focus()
                    continue

                if scriptDescriptionEntry.get_text().strip() == "":
                    pythonutils.showMessage( dialog, Gtk.MessageType.ERROR, _( "The script description cannot be empty." ), INDICATOR_NAME )
                    scriptNameEntry.grab_focus()
                    continue

                if pythonutils.getTextViewText( commandTextView ).strip() == "":
                    pythonutils.showMessage( dialog, Gtk.MessageType.ERROR, _( "The script command cannot be empty." ), INDICATOR_NAME )
                    scriptNameEntry.grab_focus()
                    continue

                if script.getName() == "": # Adding a new script - check for duplicate.
                    if self.getScript( script.getName(), script.getDescription() ) is not None:
                        pythonutils.showMessage( dialog, Gtk.MessageType.ERROR, _( "A script of the same name and description already exists." ), INDICATOR_NAME )
                        scriptNameEntry.grab_focus()
                        continue

                else: # Editing an existing script.
                    if scriptNameEntry.get_text().strip() == script.getName() and scriptDescriptionEntry.get_text().strip() == script.getDescription(): # Script name and description have not changed, so need nothing to do.
                        break

                    duplicate = False
                    for scriptInList in self.scripts:
                        if scriptNameEntry.get_text().strip() == scriptInList.getName() and scriptDescriptionEntry.get_text().strip() == scriptInList.getDescription():
                            duplicate = True
                            break

                    if duplicate:
                        pythonutils.showMessage( dialog, Gtk.MessageType.ERROR, _( "A script of the same name and description already exists." ), INDICATOR_NAME )
                        scriptNameEntry.grab_focus()
                        continue

                    # Remove the existing script...a new script containing the edits will be added later.
                    i = 0
                    for scriptInList in self.scripts:
                        if script.getName() == scriptInList.getName() and script.getDescription() == scriptInList.getDescription():
                            break

                        i += 1

                    del self.scripts[ i ]

                # Either the new script or the edit.
                newScript = Info( scriptNameEntry.get_text(),
                                  scriptDescriptionEntry.get_text(), 
                                  scriptDirectoryEntry.get_text(),
                                  pythonutils.getTextViewText( commandTextView ),
                                  terminalOpenCheckbox.get_active() )

                self.scripts.append( newScript )

                # Refresh the script name combo, select the script name and then the description.
                self.populateScriptNameCombo( scriptNameComboBox )
                iter = scriptNameComboBox.get_model().get_iter_first()
                i = 0
                while iter != None:
                    if scriptNameComboBox.get_model().get_value( iter, 0 ) == newScript.getName():
                        scriptNameComboBox.set_active( i )
                        iter = scriptDescriptionTreeView.get_model().get_iter_first()
                        i = 0
                        while iter != None:
                            if scriptDescriptionTreeView.get_model().get_value( iter, 0 ) == newScript.getDescription():
                                scriptDescriptionTreeView.get_selection().select_path( i )
                                scriptDescriptionTreeView.scroll_to_cell( Gtk.TreePath.new_from_string( str( i ) ) )
                                break

                            iter = scriptDescriptionTreeView.get_model().iter_next( iter )
                            i += 1

                    iter = scriptNameComboBox.get_model().iter_next( iter )
                    i += 1

            break

        dialog.destroy()


    def populateScriptNameCombo( self, scriptNameComboBox ):
        scriptNameComboBox.remove_all()
        scripts = self.getScriptsGroupedByName()
        for scriptName in sorted( scripts, key = str.lower ):
            scriptNameComboBox.append_text( scriptName )


    def getScript( self, scriptName, scriptDescription ):
        theScript = None
        for script in self.scripts:
            if script.getName() == scriptName and script.getDescription() == scriptDescription:
                theScript = script
                break

        return theScript


    def getScriptsGroupedByName( self ):
        scripts = { }
        for script in self.scripts:
            if script.getName() not in scripts:
                scripts[ script.getName() ] = [ ]

            scripts[ script.getName() ].append( script )

        return scripts


    def loadSettings( self ):
        self.scripts = [ ]
        if os.path.isfile( IndicatorScriptRunner.SETTINGS_FILE ):
            try:
                with open( IndicatorScriptRunner.SETTINGS_FILE, "r" ) as f:
                    settings = json.load( f )

                scripts = settings.get( IndicatorScriptRunner.SETTINGS_SCRIPTS, [ ] )
                for script in scripts:
                    self.scripts.append( Info( script[ 0 ], script[ 1 ], script[ 2 ], script[ 3 ], bool( script[ 4 ] ) ) )

            except Exception as e:
                logging.exception( e )
                logging.error( "Error reading settings: " + IndicatorScriptRunner.SETTINGS_FILE )
        else:
            self.scripts = [ ]
            self.scripts.append( Info( "Ping", "Google", "", "ping -c 5 www.google.com", False ) )
            self.scripts.append( Info( "Ping", "Ubuntu", "", "ping -c 5 www.ubuntu.com", False ) )
            self.scripts.append( Info( "List Files", "Contents of /usr/bin", "/usr/bin", "ls", True ) )
            self.scripts.append( Info( "List Files", "Contents of /bin", "/bin", "ls", True ) )

#TODO This prompts for the password but seems to only do the autoclean...not the rest.           
            self.scripts.append( Info( "Update", "autoclean | autoremove | update | dist-upgrade", "", "sudo apt-get autoclean && sudo apt-get -y autoremove && sudo apt-get update && sudo apt-get -y dist-upgrade", True ) )


    def saveSettings( self ):
        try:
            scripts = [ ]
            for script in self.scripts:
                scripts.append( [ script.getName(), script.getDescription(), script.getDirectory(), script.getCommand(), script.isTerminalOpen() ] )

            settings = { IndicatorScriptRunner.SETTINGS_SCRIPTS: scripts }
            with open( IndicatorScriptRunner.SETTINGS_FILE, "w" ) as f:
                f.write( json.dumps( settings ) )

        except Exception as e:
            logging.exception( e )
            logging.error( "Error writing settings: " + IndicatorScriptRunner.SETTINGS_FILE )


if __name__ == "__main__": IndicatorScriptRunner().main()