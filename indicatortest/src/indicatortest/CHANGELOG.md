# Indicator Test changelog

## v1.0.16 (2023-12-22)

- Added terminal commands "fortune", "wmctrl", "calendar", "notify-send" and "paplay".
- Distributions/versions with full functionality:
  - Debian 11 / 12 GNOME on Xorg
  - Fedora 38 / 39 GNOME on Xorg
  - Kubuntu 20.04 / 22.04
  - Ubuntu 20.04
  - Ubuntu 22.04 on Xorg
  - Ubuntu Budgie 22.04
  - Ubuntu MATE 22.04
  - Ubuntu Unity 20.04 / 22.04
  - Xubuntu 20.04 / 22.04
- Distributions/versions with limited functionality:
  - Debian 11 / 12 GNOME No clipboard; no wmctrl.
  - Fedora 38 / 39 GNOME No clipboard; no wmctrl.
  - Kubuntu 20.04 / 22.04 No mouse wheel scroll; tooltip in lieu of label.
  - Linux Mint 21 Cinnamon Tooltip in lieu of label.
  - Lubuntu 20.04 / 22.04 No label; tooltip is not dynamic; icon is not dynamic.
  - Manjaro 22.1 GNOME No calendar.
  - openSUSE Tumbleweed No clipboard; no wmctrl; no calendar.
  - openSUSE Tumbleweed GNOME on Xorg No calendar.
  - Ubuntu 22.04 No clipboard; no wmctrl.
  - Ubuntu Budgie 20.04 No mouse middle click.
  - Ubuntu MATE 20.04 Dynamic icon is truncated, but fine whilst being clicked.
  - Ubuntu MATE 22.04 Default icon with colour change does not show up; dynamic icon for NEW MOON does not display.
  - Xubuntu 20.04 / 22.04 No mouse wheel scroll; tooltip in lieu of label.


## v1.0.15 (2023-12-20)

- Corrections made to install and run scripts to avoid globbing paths.  Many thanks to Oleg Moiseichuck!


## v1.0.14 (2023-12-20)

- Updated operating system dependencies.


## v1.0.13 (2023-12-20)

- Still wrestling with differences in Markdown rendering in the README.md and how PyPI interprets things!


## v1.0.12 (2023-12-19)

- Removed URL at end of README.md.
- Added --upgrade to pip install.


## v1.0.11 (2023-12-19)

- Previous build failed quietly which resulted in the README.md not being included.


## v1.0.10 (2023-12-19)

- Dropped the LICENSE.txt file as it should be included by default when specified as a classifer in pyproject.toml.


## v1.0.9 (2023-12-18)

- More work on README.md.


## v1.0.8 (2023-12-18)

- Updated the README.md to render better on PyPI.


## v1.0.7 (2023-12-16)

- Overhaul of all indicators to adhere to the pyproject.toml standard.  Further, indicators are no longer deployed using the .deb format.  Rather, PyPI (pip) is now used, along with commands, to install operating system packages and copy files.  In theory, this allows for indicators to be deployed on any platform which supports both pip and the AppIndicator library.


## v1.0.6 (2022-12-01)

- Lots of changes to support 20.04/22.04 versions of Kubuntu, Lubuntu, Ubuntu, Ubuntu Budgie, Ubuntu MATE, Ubuntu Unity and Xubuntu.


## v1.0.5 (2022-11-16)

- Created a mock indicator which tests all manner of indicator capabilities; OSD, mouse wheel scroll, middle mouse icon click, et al.


## v1.0.4 (2022-06-22)

- Testing debian/control/compat level of 10.


## v1.0.3 (2016-06-13)

- Testing install of pyephem through apt-get.


## v1.0.2 (2016-06-13)

- Testing.


## v1.0.1 (2016-06-12)

- Testing.


## v1.0.0 (2016-06-11)

- Testing.
