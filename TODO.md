# Immediate

## Simplify install/update/remove of multiple indicators for the end user.
That is, a single apt-get (or equivalent) along with a pip install listing desired indicators?

Similarly for upgrading...
Is there a way to make it easier for an end user to upgrade all in one go?

Have a wrapper indicator for all?

Maybe have a file in the release called "upgradepath.txt" which contains

  16
  17
  the python venv create/install command

So the indicator knows it is version 16 and there is a new version 17
and only needs to run the command to upgrade.

This could be done also for the OS package changes
(but needs to be per OS now) so

   debian_11=sudo apt-get -y install new_package
   fedora_38=sudo dnf -y install new_package

Maybe don't even need the 16, 17.
Rather if there is an entry say

   debian_11=sudo...
   python venv/install command

then if on Debian 11, the debian_11 command and python command
both apply so show the user.

So how to create this list/file?


Perhaps instead have an update script...?
Not even sure how it works, but would live in the venv directory
and we popup a dialog to let the user know of an available update
rather than an OSD or Preferences message.
Still need to resolve when a user does no upgrade for a few versions
and perhaps needs an OS package installed (rather than just the pip upgrade).

What to name the python/pip project that contains the script/wrapper?


An update requires two parts: OS updates which should be seldom
and Python (and venv) updates which are the typical update.

For each release, need a text file which records any OS packages
which are new since the very first release.

To think about...
- Is there a way to make installing (multiple indicators) easier?
- Is there a way to make updates easier (singular or multiple indicators?

For updating, if an indicator contains in its .whl
a file containing the OS packages required for each distro
which comes from utils_readme.py,
the installed indicator can compare its own file with that
at PyPI (after downloading) and message the user (undecided how)
the OS install command.  This implies only need the latest version.
The PyPI command will always be required for updating,
so only need to check versions.

Maybe need to make a statement in the Installation section
about the name/location of the venv which will be created.
https://stackoverflow.com/questions/34948898/check-whether-directory-is-a-virtualenv
https://stackoverflow.com/questions/47462591/python-how-do-you-check-what-is-in-virtualenv

If installing more than one indicator simultaneously,
split the OS packages into those common to all indicators
(which appear as the first step in the install instructions)
and add a OS install line to the install.sh on a per-indicator
basis for the OS specific packages.  Does this make sense...?
How does this make it easier to install multiple indicators simultaneously?????

If a combined/shared virtual environment is used for all indicators,
need a note on the PyPI page about uninstalling, in that the virtual
environment directory will be deleted because a user might use that
virtual environment for other things.

is it feasible to get the upgrade instructions?
Get from where?  Download the new .whl and extract from the README.md somehow?
Or make a machine readable README.md?


## Autostart with delay fails
On Kubuntu 24.04 and Manjaro 24.0.7, autostart with delay does not work.
Determine if autostart works without delay and if so, make a note in the 
release notes or on the README.md
Could be a KDE/plasma new thing?
- https://docs.kde.org/stable5/en/plasma-workspace/kcontrol/autostart/index.html
- https://www.reddit.com/r/Kubuntu/comments/ya0bb9/autostart_programs_dont_launch_in_kubuntu_2210/
- https://bugs.kde.org/show_bug.cgi?id=433538
- https://www.reddit.com/r/kde/comments/wlmlo1/running_a_command_on_startup/
- https://forum.manjaro.org/t/script-put-in-autostart-doesnt-work/61007/6
- https://askubuntu.com/questions/1490449/how-do-i-autostart-an-application-while-keeping-it-minimized
- https://askubuntu.com/questions/1181813/how-to-get-franz-messaging-app-start-minimized-and-with-window-along-the-right-e
- https://forum.manjaro.org/t/autostart-doesnt-work/121929/6
- https://forum.manjaro.org/t/bash-script-wont-load-on-start/114310
- https://forum.manjaro.org/t/autostart-script-does-not-work/124754

If the autostart works (without delay) on Kubuntu 24.04 and Manjaro 24.0.x
perhaps only show autostart checkbox and not the delay for those distros/versions.

- https://blog.davidedmundson.co.uk/blog/plasma-and-the-systemd-startup/
- https://forum.manjaro.org/t/autostart-doesnt-work/121929
- https://www.reddit.com/r/archlinux/comments/ves6mh/comment/inf2mwq/
- https://forum.manjaro.org/t/autostart-script-does-not-work/124754/6


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

  https://pypi.org/project/indicatorfortune/
  https://pypi.org/project/indicatorlunar/
  https://pypi.org/project/indicatoronthisday/
  https://pypi.org/project/indicatorppadownloadstatistics/
  https://pypi.org/project/indicatorpunycode/
  https://pypi.org/project/indicatorscriptrunner/
  https://pypi.org/project/indicatorstardate/
  https://pypi.org/project/indicatortide/
  https://pypi.org/project/indicatorvirtualbox/



# Long Term

## Migrate to GTK4
May need to continue to run as GTK3 simulataneously.
- https://discourse.gnome.org/t/migrating-gtk3-treestore-to-gtk4-liststore-and-handling-child-rows/12159
- https://stackoverflow.com/questions/73006299/unable-to-get-application-icons-to-display-with-gtk4-under-ubuntu
