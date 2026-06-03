# Medium Term

### Test Upcoming Releases
- Debian 14
- Fedora 45
- Manjaro 27
- Ubuntu 28.04


# Long Term

### Deprecation of libayatana-appindicator
When running on Debian 13 and Manjaro 25 (using libgirepository-2.0-dev) get the following:

    libayatana-appindicator-WARNING **:
        libayatana-appindicator is deprecated.
        Please use libayatana-appindicator-glib in newly written code.

There is presently no available package and some searching suggests that perhaps the deprecation message is quite early and package managers for ALL distros are yet to upgrade.

Will need to eventually swap over each distro as it is released with libayatana-appindicator-glib and update the install instructions.


### Non-symbolic icons
Some distros/desktops do not utilise the GNOME symbolic icon mechanism. Determine which distros/desktops these are and if anything can be done.


### Replacement for wmctrl for indicatorvirtualbox on Wayland
- https://git.sr.ht/~brocellous/wlrctl

  Installed in Debian 13; get the error message "error message: Foreign Toplevel Management interface not found!" when using to list windows or find a window by name.

- https://github.com/CZ-NIC/run-or-raise

  GNOME extension; maybe could be used but only works on GNOME presumably.

- https://github.com/ickyicky/window-calls

  GNOME extension; maybe could be used but only works on GNOME presumably.

- Activate Window By Title
  
  https://unix.stackexchange.com/questions/688583/focus-window-by-title-in-gnome-shell-41-under-wayland

  https://extensions.gnome.org/extension/5021/activate-window-by-title/

- https://unix.stackexchange.com/questions/702236/how-to-list-all-object-paths-under-a-dbus-service-only-usign-dbus-command-line-u

- https://unix.stackexchange.com/questions/656729/wmctrl-like-tool-or-alternative-for-kde-wayland

- https://unix.stackexchange.com/questions/684461/fedora-36-wmctrl-does-not-work-at-all

- https://unix.stackexchange.com/questions/706477/is-there-a-way-to-get-list-of-windows-on-kde-wayland

- https://bbs.archlinux.org/viewtopic.php?id=306439

- https://github.com/jinliu/kdotool


### Release astroskyfield for indicatorlunar

There is still some work to be done to clean up and finalise astroskyfield in regards to satellites, comets, and minor planets.  For the most part, astroskyfield could be released as it runs accurately and fast enough on a good system.

However, Debian 12 32 bit, I was unable to install both numpy and pandas, both required for skyfield.  I was able to achieve this on a virtual machine running 32 bit Debian 12 on a physical 64 bit host, so I don't know if there was a specific issue with the laptop installation or somehow the virtual machine installation seemed to be treated as 64 bit or something else again.

When installing on the laptop I pinned the versions of pandas/numpy back to quite old levels in an attempt to install what should be a 32 bit equivalent, but that didn't work.

Until installing pandas/numpy on 32 bit is resolved and given astroskyfield still needs tidying up, defer the release of astroskyfield for now.

One option is to clean up astroskyfield for release but release both astroskyfield and astropyphem.  The Python pip install instructions will have to include a bash command to determine if 32 bit (so install ephem) or 64 bit (so install skyfield and pandas/numpy).  In indicatorlunar, internally switch between astropyephem and astroskyfield if on 32 bit or 64 bit respectively.


### Access Data at Runtime
Reading
    https://setuptools.pypa.io/en/latest/userguide/datafiles.html#accessing-data-files-at-runtime
it appears that data files which are part of the installation should be accessed via importlib.resources which is available since Python 3.10.
Applies to locale (which works fine as is) and stars.dat / planets.bsp for astroskyfield.
Consider this once Ubuntu 20.04 / Debian 11 (et al) are no longer supported.


### Migrate to GTK4
May need to continue to run as GTK3 simulataneously.
- https://discourse.gnome.org/t/migrating-gtk3-treestore-to-gtk4-liststore-and-handling-child-rows/12159
- https://stackoverflow.com/questions/73006299/unable-to-get-application-icons-to-display-with-gtk4-under-ubuntu
