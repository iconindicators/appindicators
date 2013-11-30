#!/usr/bin/python
# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
### BEGIN LICENSE
# Copyright (C) 2011 Andrea Azzarone admin@ubuntusecrets.it
# This program is free software: you can redistribute it and/or modify it 
# under the terms of the GNU General Public License version 3, as published 
# by the Free Software Foundation.
# 
# This program is distributed in the hope that it will be useful, but 
# WITHOUT ANY WARRANTY; without even the implied warranties of 
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR 
# PURPOSE.  See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along 
# with this program.  If not, see <http://www.gnu.org/licenses/>.
### END LICENSE

"""Code to add AppIndicator."""

import gtk

from fortune_indicator.helpers import get_media_file

import gettext
from gettext import gettext as _
gettext.textdomain('fortune-indicator')

from xdg import BaseDirectory as xdg
import os
import glib
import subprocess
import appindicator
import gobject
import datetime
import pynotify
from commands import *

from fortune_indicator import (
    AboutFortuneIndicatorDialog, PreferencesFortuneIndicatorDialog)
from fortune_indicator.helpers import get_builder

class Indicator:
    def __init__(self):
        self.indicator = appindicator.Indicator('fortune-indicator','distributor-logo', appindicator.CATEGORY_APPLICATION_STATUS)
        self.indicator.set_status(appindicator.STATUS_ACTIVE)
    
        #Can use self.icon once appindicator python api supports custom icons.
        icon = get_media_file("icon.png")
        icon = icon.replace ("file:///", "")
        self.indicator.set_icon(icon)
 
        #Uncomment and choose an icon for attention state. 
        #self.indicator.set_attention_icon("ICON-NAME")
        
        self.menu = gtk.Menu()

        # Add items to Menu and connect signals. 
        
        #Adding "Show one cookie" button
        self.showOneCookie = gtk.MenuItem("Show one cookie")
        self.showOneCookie.connect("activate", self.next_cookie)
        self.showOneCookie.show()
        self.menu.append(self.showOneCookie)
        
        #Adding "Disable auto refresh" checkbox
        self.disable = gtk.CheckMenuItem("Disable auto refresh")
        self.disable.connect("activate", self.on_disable_activate)
        self.disable.show()
        self.menu.append(self.disable)
        
        #Add a separator
        separator = gtk.SeparatorMenuItem()
        separator.show()
        self.menu.append(separator)
        
        #Adding "Copy last cookie" button
        self.copy = gtk.MenuItem("Copy last cookie")
        self.copy.connect("activate", self.copy_last_cookie)
        self.copy.show()
        self.menu.append(self.copy)
        
        #Adding "Share last cookie" button
        self.share = gtk.MenuItem("Share...")
        self.share.connect("activate", self.share_last_cookie)
        self.can_share = has_accounts_in_sqlite() and os.path.exists("/usr/bin/gwibber-poster")
        self.share.set_sensitive(False) #Until the first cookie we can share nothing
        self.share.show()
        self.menu.append(self.share)
        
        #Add a separator
        separator = gtk.SeparatorMenuItem()
        separator.show()
        self.menu.append(separator)
        
        #Adding preferences button 
        self.preferences = gtk.MenuItem("Preferences")
        self.preferences.connect("activate",self.preferencesDialog)
        self.preferences.show()
        self.menu.append(self.preferences)
        
        #Adding about button 
        self.about = gtk.MenuItem("About")
        self.about.connect("activate",self.aboutDialog)
        self.about.show()
        self.menu.append(self.about)
        
        #Add a separator
        separator = gtk.SeparatorMenuItem()
        separator.show()
        self.menu.append(separator)

        #Adding quit button 
        self.quit = gtk.MenuItem("Quit")
        self.quit.connect("activate",gtk.main_quit)
        self.quit.show()
        self.menu.append(self.quit)                    

        self.menu.show()
        self.indicator.set_menu(self.menu)
        
        # run after init
        self.after_init()
        
    def preferencesDialog(self, widget, data=None):
        """Display the preferences window for fortune-indicator."""
        if self.prefs_showed == True:
            return
        
        self.prefs = PreferencesFortuneIndicatorDialog.PreferencesFortuneIndicatorDialog()
        self.prefs_showed = True
        response = self.prefs.run()
        self.prefs_showed = False
        
        if response == gtk.RESPONSE_OK:
            # Make any updates based on changed preferences here.
            # Reset the timer if the timeout change
            if self.isDisable() == False and self.TimePeriod <> self.prefs._preferences["timeout"]:
                gobject.source_remove(self.source_event)
                self.timer()
        
        self.prefs.destroy()

    def aboutDialog(self, widget, data=None):
        """Display the about box for fortune-indicator."""
        response = self.about.run()
        self.about.hide()

    def after_init(self):
        """The function that is called after the init function"""
        self.prefs = PreferencesFortuneIndicatorDialog.PreferencesFortuneIndicatorDialog()
        self.about = AboutFortuneIndicatorDialog.AboutFortuneIndicatorDialog()
        
        self.prefs_showed = False
        self.body = "" #if share_last_cookie is called before show_cookie, self.body is not declared
        
        # get the clipboard
        self.clipboard = gtk.clipboard_get()
        
        self.timer()
        
        
    def isDisable (self):
        return self.disable.get_active()
        
    def on_disable_activate(self, *arg):
        """Returns the Checkbox status"""
        if True == self.isDisable():
            gobject.source_remove(self.source_event)
        else:
            self.timer()
        
    def show_cookie(self):
        """Shows a cookie without waiting timer handler"""
        self.cookie = getoutput('/usr/games/fortune -s')
        title = "Fortune Cookie"
        self.body = self.cookie
        icon = ""
        notif = pynotify.Notification(title, self.body, icon);
        notif.show()
        
        self.share.set_sensitive(self.can_share)
        

    def timer_handler(self):
        """Timer handler"""
        self.next_cookie()
        self.start_timer = datetime.datetime.today()
        return True
        
    def timer(self):
        """Shows next cookie after the time period"""
        self.TimePeriod = self.prefs._preferences["timeout"]
        self.time = int(self.TimePeriod*60)
        self.source_event = gobject.timeout_add_seconds(self.time, self.timer_handler)
        self.start_timer = datetime.datetime.today()
        
    def next_cookie(self, *arg):
        """Show next cookie if Checkbox is disable"""
        self.show_cookie()
        
        if self.isDisable() == False:
            gobject.source_remove(self.source_event)
            self.timer()
    
    def copy_last_cookie(self, *arg):
        self.clipboard.set_text(self.body)
        
    def share_last_cookie(self, *arg):
        p = subprocess.Popen(["gwibber-poster", "-w", "-m", self.body])
        # setup timeout handler to avoid zombies
        glib.timeout_add_seconds(1, lambda p: p.poll() is None, p)
   
#from ubuntu-software-centre     
def has_accounts_in_sqlite():
    """ return if there are accounts for gwibber in sqlite """
    # don't use dbus, triggers a gwibber start each time we call this
    import sqlite3
    dbpath = "%s/gwibber/gwibber.sqlite" % xdg.xdg_config_home
    if not os.path.exists(dbpath):
        return False
    with sqlite3.connect(dbpath) as db:
        results = db.execute("SELECT data FROM accounts")
        if len(results.fetchall()) > 0:
            return True
    return False
    
def new_application_indicator():
    ind = Indicator()
    return ind.indicator
