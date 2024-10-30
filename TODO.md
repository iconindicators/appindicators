# Immediate

# Calendar not on Manjaro/openSUSE
    indicatoronthisday
        Nothing to do as the indicator readme
        does not provide install instructions
        for Manjaro/openSUSE.
        Maybe make a note however at top of readme?


# Clipboard/primary on Ubuntu 20.04 Wayland
    indicatorfortune
        Should the copy last fortune menu item be hidden,
        or instead show a notification when clicked or
        mouse middle click of icon?
        Show a tooltip in the preferences for radio button mouse
        mouse middle click copy telling the user this won't work
        or hide the radio button?
    indicatoronthisday
        Cannot hide the 'copy' radio button in the preferences
        as it would require making the 'search' radio button
        now a checkbox, or worse/more complicated.
        So maybe add a tooltip?
        When a menu item is checked and preference is to copy,
        do nothing or show a notification?
    indicatorpunycode
        Perhaps don't build the menu (with convert).
        Or show a notification telling the user this will not work
        when convert or mouse click happens?
    indicatortest
        Should the menu copy time to clipboard/primary
        be hidden under Ubuntu 20.04 Wayland,
        or instead show a notification?


# wmctrl on Wayland
    indicatorvirtualbox
        If a vm is selected in the menu but already running,
        should the call to wmcrl be avoided?
        If mouse wheel scroll over icon, avoid calling wmctrl?


# Mouse wheel scroll
What to do when the mouse wheel scroll is invoked but unsupported
on distros Kubuntu 22.04/24.04 and Manjaro 24.0.7?
    indicatorvirtualbox
        If no wmctrl and a vm is selected via menu,
        and vm is running, then do nothing or
        perhaps show a notification to user?


# No autostart on Kubuntu and Manjaro
Given there is no autostart on Kubuntu 24.04 and Manjaro 24.04.7,
should the autostart checkbox and delay spinner be hidden?
If some fix through an OS update appears in the meantime,
will need to release ALL indicators again unhiding checkbox and spinner.
Could have a tooltip...but if the fix comes, don't need to re-release but should.
Otherwise just leave as is...and keep the entry in the changelog.
What to do?


# Change the date in the latest entry in each CHANGELOG.md to date of release.


## When finally released, or at least indicatortest is released, post a note to
  https://github.com/AyatanaIndicators/libayatana-appindicator/issues/76
to help the guy out.


## Update the PPA description at
  https://launchpad.net/~thebernmeister/+archive/ubuntu/ppa
with the following:

This PPA no longer provides releases for indicators.
Instead, for Ubuntu 20.04 and forward, all releases are made via pip (PyPI).

Refer to the new URL for each indicator:

indicator-fortune: https://pypi.org/project/indicatorfortune
indicator-lunar: https://pypi.org/project/indicatorlunar
indicator-on-this-day: https://pypi.org/project/indicatoronthisday
indicator-ppa-download-statistics: https://pypi.org/project/indicatorppadownloadstatistics
indicator-punycode: https://pypi.org/project/indicatorpunycode
indicator-script-runner: https://pypi.org/project/indicatorscriptrunner
indicator-stardate: https://pypi.org/project/indicatorstardate
indicator-test: https://pypi.org/project/indicatortest
indicator-tide: https://pypi.org/project/indicatortide
indicator-virtual-box: https://pypi.org/project/indicatorvirtualbox

Screenshots for the indicators can be found at https://askubuntu.com/q/30334/67335


## For each indicator at
  https://askubuntu.com/questions/30334/what-application-indicators-are-available?answertab=modifieddes
update the URL at the top with the relevant URL at PyPI.

Also update the indicator name (remove the hyphen from the name).


  https://pypi.org/project/indicatorfortune/
  https://pypi.org/project/indicatorlunar/
  https://pypi.org/project/indicatoronthisday/
  https://pypi.org/project/indicatorppadownloadstatistics/
  https://pypi.org/project/indicatorpunycode/
  https://pypi.org/project/indicatorscriptrunner/
  https://pypi.org/project/indicatorstardate/
  https://pypi.org/project/indicatortide/
  https://pypi.org/project/indicatorvirtualbox/


When indicators released to pypi, update description at
  https://sourceforge.net/p/appindicators/admin/overview
to read:


Source code repository for:
 - indicatorfortune
 - indicatorlunar
 - indicatoronthisday
 - indicatorppadownloadstatistics
 - indicatorpunycode
 - indicatorscriptrunner
 - indicatorstardate
 - indicatortest
 - indicatortide
 - indicatorvirtualbox

More details and screenshots:
 -  https://askubuntu.com/q/30334/67335

Releases:
- https://pypi.org/project/indicatorfortune
- https://pypi.org/project/indicatorlunar
- https://pypi.org/project/indicatoronthisday
- https://pypi.org/project/indicatorppadownloadstatistics
- https://pypi.org/project/indicatorpunycode
- https://pypi.org/project/indicatorscriptrunner
- https://pypi.org/project/indicatorstardate
- https://pypi.org/project/indicatortest
- https://pypi.org/project/indicatortide
- https://pypi.org/project/indicatorvirtualbox



# Long Term

# Icons which do not utilise symbolic
Some distros/desktops do not utilise the symbolic icon system as does GNOME.
Determine which distros/desktops these are and if anything can be done.


## Migrate to GTK4
May need to continue to run as GTK3 simulataneously.
- https://discourse.gnome.org/t/migrating-gtk3-treestore-to-gtk4-liststore-and-handling-child-rows/12159
- https://stackoverflow.com/questions/73006299/unable-to-get-application-icons-to-display-with-gtk4-under-ubuntu
