## Introduction

This project contains application indicators written in `Python3` for `Ubuntu 20.04` or equivalent as follows:

- `indicator-fortune` displays the `fortune` cookie in the on-screen notification.

- `indicator-lunar` displays lunar, solar, planetary, minor planet, star and satellite information.

- `indicator-on-this-day` displays calendar/history events for today and future dates.

- `indicator-ppa-download-statistics` displays the download counts for packages in a `Launchpad PPA`.

- `indicator-punycode` converts domain names between Unicode and ASCII.

- `indicator-script-runner` allows a user to run a terminal command or script from the indicator menu, optionally showing the output in the icon label.

- `indicator-stardate` displays the current Star Trek™ stardate.

- `indicator-tide` displays tidal information.

- `indicator-virtual-box` displays VirtualBox™ `virtual machines` allowing for manual or automatic start.


## Requirements
- For `Ubuntu`, you must enable the `Ubuntu appIndicators` extension using `GNOME Tweaks`.

- For `Debian 12 (bookworm)` you must [install](https://extensions.gnome.org/extension/615/appindicator-support/) the `GNOME Shell` extension `AppIndicator and KStatusNotifierItem Support`. 


## Installation
#### Ubuntu
Open a `terminal` and add the `Personal Package Archive`:
```
sudo add-apt-repository ppa:thebernmeister/ppa
sudo apt update
```
then install the indicator of your choice:
```
sudo apt install indicator-fortune
```

#### Debian
Download the `.deb` for the indicator you want to install from [LaunchPad](https://launchpad.net/~thebernmeister/+archive/ubuntu/ppa/+packages).

For example, for`indicator-fortune`, the `.deb` most current, as of this writing, is  `indicator-fortune_1.0.41-1_all.deb`.  Choose any `.deb` for the particular indicator you want; the `series` is irrelevant.

In a `terminal`:
```
sudo dpkg -i indicator-fortune_1.0.41-1_all.deb && sudo apt install -f
```

## Usage
To run `indicator-fortune` for example, press the `Super`/`Windows` key to open the `Show Applications` overlay, type `fortune` into the search bar and the icon should be present for you to click.


## Limitations
Distributions/versions with full functionality:
- `Ubuntu 20.04`
- `Ubuntu 22.04`
- `Ubuntu Budgie 22.04`
- `Ubuntu Unity 20.04`
- `Ubuntu Unity 22.04`

Distributions/versions with limited functionality:
- `Kubuntu 20.04` No mouse wheel scroll; tooltip in lieu of label.
- `Kubuntu 22.04` No mouse wheel scroll; tooltip in lieu of label.
- `Lubuntu 20.04` No label; tooltip is not dynamic; icon is not dynamic.
- `Lubuntu 22.04` No label; tooltip is not dynamic; icon is not dynamic.
- `Ubuntu Budgie 20.04` No mouse middle click.
- `Ubuntu MATE 20.04` Dynamic icon is truncated, but fine whilst being clicked.
- `Ubuntu MATE 22.04` Default icon with colour change does not show up; dynamic icon for NEW MOON does not display.
- `Xubuntu 20.04` No mouse wheel scroll; tooltip in lieu of label.
- `Xubuntu 22.04` No mouse wheel scroll; tooltip in lieu of label.


## License
This project in its entirety is licensed under the terms of the GNU General Public License v3.0 license. 
Copyright 2012-2023 Bernard Giannetti.
https://launchpad.net/~thebernmeister/+archive/ubuntu/ppa
