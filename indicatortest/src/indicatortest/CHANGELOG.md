# Indicator Test changelog

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
