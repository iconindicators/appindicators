# Indicator Test changelog

## v1.0.19 (2025-11-25)

- Ignore a failure to connect to `GitHub` when checking for a new release.


## v1.0.18 (2025-11-21)

- Bug fix: the build resulted in erroneous hard coding of `indicatortest` in the install script for all indicators.


## v1.0.17 (2025-10-18)

- Consolidated menu options.
- Updated README.md.
- Now includes an opt-in check during start up for the latest version at GitHub.
- Deployment using the .deb format is superceded; pip is used with operating system packages and file copy.


## v1.0.16 (2023-12-22)

- Added terminal commands "fortune", "wmctrl", "calendar", "notify-send" and "paplay".
- Now includes a symbolic icon allowing the colour to be adjusted for the current theme.


## v1.0.15 (2023-12-20)

- Corrections made to install and run scripts to avoid globbing paths. Many thanks to Oleg Moiseichuck!


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

- Overhauled to adhere to the pyproject.toml standard.
- Deployment using the .deb format is superceded; PyPI (pip) is used with operating system packages and file copy.


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
