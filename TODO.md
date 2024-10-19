# Immediate


# What about stardatesystemtray and worldtimesystemtray?
Should these two projects also be under git/github?
Perhaps the github organisation could be called indicators or icon-indicators.
For the appindicators, call that repository appindicators or python-appindicators.
For stardatesystemtray and worldtimesystemtray, call the repository perhaps java-system-tray-icons
Need to look into what version of Java and/or Windows to support.
Windows XP is no longer supported and neither is Java 6.
So maybe look at supporting only Windows 10/11 (check for the EOL dates),
along with the versions of Java supported for those versions of Windows.
Consider also one or more versions prior to Windows 10 and whatever version of Java was last supported.

Windows EOL
	Vista 2017
	7 2020
	8 2016
	8.1 2023
	10 2025
	11 ...?
	
Java EOL
	1.6 2013
	1.7 2015
	8 2019...2026
	9 2018
	10 2018
	11 2019...2027
	12 2019
	13 2020
	14 2020
	15 2021
	16 2021
	17 2024...2027
	18 2022
	19 2023
	20 2023
	21 2028...2029
	22 2024
	23 2025
	24 2025
	25 2030

Downloaded Java for Windows 11; was recommended by the Oracle website to download Java 8.
Installed Java 8.
Installed Stardate System Tray.
Installed World Time System Tray.
Both work!
Check if built for Java 6 or Java 8 or Java 11 and update each page's description.

Consider renaming project to change the wrld to world?
https://sourceforge.net/p/forge/site-support/new/




# Check if Autostart without delay on Kubuntu 24.04 works
Document to the user (along with the status of not working with a delay).


# Check if Autostart without delay on Manjaro 24.0.7 works
Document to the user (along with the status of not working with a delay).


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

## Migrate to GTK4
May need to continue to run as GTK3 simulataneously.
- https://discourse.gnome.org/t/migrating-gtk3-treestore-to-gtk4-liststore-and-handling-child-rows/12159
- https://stackoverflow.com/questions/73006299/unable-to-get-application-icons-to-display-with-gtk4-under-ubuntu
