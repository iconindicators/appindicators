indicatorvirtualbox
---

`indicatorvirtualbox` shows VirtualBox™ virtual machines and allows them to be started.


---
Installation / Updating
-----------------------

<details><summary><b>Debian 12</b></summary>

1. Install operating system packages:

    ```
    sudo apt-get -y install gir1.2-ayatanaappindicator3-0.1 gnome-shell-extension-appindicator libcairo2-dev libgirepository1.0-dev python3-pip python3-venv wmctrl
    ```

2. Create a `Python3` virtual environment at `$HOME/.local/venv_indicators` and install `indicatorvirtualbox`, including icons, .desktop and run script:
    ```
    indicator=indicatorvirtualbox && \
    venv=$HOME/.local/venv_indicators && \
    if [ ! -d ${venv} ]; then python3 -m venv ${venv}; fi && \
    . ${venv}/bin/activate && \
    python3 -m pip install --upgrade PyGObject\<=3.50.0 https://github.com/iconindicators/appindicators/releases/download/1.3/indicatorvirtualbox-1.0.78-py3-none-any.whl && \
    deactivate && \
    . $(ls -d ${venv}/lib/python3.* | head -1)/site-packages/${indicator}/platform/linux/install.sh ${venv}
    ```
3. For the `appindicator` extension to take effect, log out / in (or restart) and in a terminal run:
    ```
    gnome-extensions enable ubuntu-appindicators@ubuntu.com
    ```

</details>

<details><summary><b>Debian 13</b></summary>

1. Install operating system packages:

    ```
    sudo apt-get -y install gir1.2-ayatanaappindicator3-0.1 gnome-shell-extension-appindicator libcairo2-dev libgirepository-2.0-dev python3-pip python3-venv wmctrl
    ```

2. Create a `Python3` virtual environment at `$HOME/.local/venv_indicators` and install `indicatorvirtualbox`, including icons, .desktop and run script:
    ```
    indicator=indicatorvirtualbox && \
    venv=$HOME/.local/venv_indicators && \
    if [ ! -d ${venv} ]; then python3 -m venv ${venv}; fi && \
    . ${venv}/bin/activate && \
    python3 -m pip install --upgrade PyGObject https://github.com/iconindicators/appindicators/releases/download/1.3/indicatorvirtualbox-1.0.78-py3-none-any.whl && \
    deactivate && \
    . $(ls -d ${venv}/lib/python3.* | head -1)/site-packages/${indicator}/platform/linux/install.sh ${venv}
    ```
3. For the `appindicator` extension to take effect, log out / in (or restart) and in a terminal run:
    ```
    gnome-extensions enable ubuntu-appindicators@ubuntu.com
    ```

</details>

<details><summary><b>Fedora 42 | Fedora 43</b></summary>

1. Install operating system packages:

    ```
    sudo dnf -y install cairo-gobject-devel gcc gobject-introspection-devel libappindicator-gtk3 python3-devel python3-pip wmctrl
    ```

2. Create a `Python3` virtual environment at `$HOME/.local/venv_indicators` and install `indicatorvirtualbox`, including icons, .desktop and run script:
    ```
    indicator=indicatorvirtualbox && \
    venv=$HOME/.local/venv_indicators && \
    if [ ! -d ${venv} ]; then python3 -m venv ${venv}; fi && \
    . ${venv}/bin/activate && \
    python3 -m pip install --upgrade PyGObject https://github.com/iconindicators/appindicators/releases/download/1.3/indicatorvirtualbox-1.0.78-py3-none-any.whl && \
    deactivate && \
    . $(ls -d ${venv}/lib/python3.* | head -1)/site-packages/${indicator}/platform/linux/install.sh ${venv}
    ```
3. Install the `GNOME Shell` `AppIndicator and KStatusNotifierItem Support` [extension](https://extensions.gnome.org/extension/615/appindicator-support).

</details>

<details><summary><b>Kubuntu 24.04 | Linux Mint Cinnamon 21 | Linux Mint Cinnamon 22 | Lubuntu 24.04 | Ubuntu 22.04 | Ubuntu 24.04 | Ubuntu Budgie 24.04 | Ubuntu MATE 24.04 | Ubuntu Unity 24.04 | Xubuntu 24.04</b></summary>

1. Install operating system packages:

    ```
    sudo apt-get -y install gir1.2-ayatanaappindicator3-0.1 libcairo2-dev libgirepository1.0-dev python3-pip python3-venv wmctrl
    ```

2. Create a `Python3` virtual environment at `$HOME/.local/venv_indicators` and install `indicatorvirtualbox`, including icons, .desktop and run script:
    ```
    indicator=indicatorvirtualbox && \
    venv=$HOME/.local/venv_indicators && \
    if [ ! -d ${venv} ]; then python3 -m venv ${venv}; fi && \
    . ${venv}/bin/activate && \
    python3 -m pip install --upgrade PyGObject\<=3.50.0 https://github.com/iconindicators/appindicators/releases/download/1.3/indicatorvirtualbox-1.0.78-py3-none-any.whl && \
    deactivate && \
    . $(ls -d ${venv}/lib/python3.* | head -1)/site-packages/${indicator}/platform/linux/install.sh ${venv}
    ```
</details>

<details><summary><b>Manjaro 25</b></summary>

1. Install operating system packages:

    ```
    sudo pacman -S --noconfirm cairo gcc libayatana-appindicator pkgconf wmctrl
    ```

2. Create a `Python3` virtual environment at `$HOME/.local/venv_indicators` and install `indicatorvirtualbox`, including icons, .desktop and run script:
    ```
    indicator=indicatorvirtualbox && \
    venv=$HOME/.local/venv_indicators && \
    if [ ! -d ${venv} ]; then python3 -m venv ${venv}; fi && \
    . ${venv}/bin/activate && \
    python3 -m pip install --upgrade PyGObject https://github.com/iconindicators/appindicators/releases/download/1.3/indicatorvirtualbox-1.0.78-py3-none-any.whl && \
    deactivate && \
    . $(ls -d ${venv}/lib/python3.* | head -1)/site-packages/${indicator}/platform/linux/install.sh ${venv}
    ```
</details>

<details><summary><b>openSUSE Tumbleweed</b></summary>

1. Install operating system packages:

    ```
    sudo zypper install -y cairo-devel gcc gobject-introspection-devel python3-devel typelib-1_0-AyatanaAppIndicator3-0_1
    ```

2. Create a `Python3` virtual environment at `$HOME/.local/venv_indicators` and install `indicatorvirtualbox`, including icons, .desktop and run script:
    ```
    indicator=indicatorvirtualbox && \
    venv=$HOME/.local/venv_indicators && \
    if [ ! -d ${venv} ]; then python3 -m venv ${venv}; fi && \
    . ${venv}/bin/activate && \
    python3 -m pip install --upgrade PyGObject https://github.com/iconindicators/appindicators/releases/download/1.3/indicatorvirtualbox-1.0.78-py3-none-any.whl && \
    deactivate && \
    . $(ls -d ${venv}/lib/python3.* | head -1)/site-packages/${indicator}/platform/linux/install.sh ${venv}
    ```
3. Install the `GNOME Shell` `AppIndicator and KStatusNotifierItem Support` [extension](https://extensions.gnome.org/extension/615/appindicator-support).

</details>



---
Usage
-----

To run `indicatorvirtualbox`, press the `Super` key to show the applications overlay (or similar), type `virtualbox` into the search bar and the icon should be present for you to select.  If the icon does not appear, or appears as generic or broken, you may have to log out / in (or restart).

Alternatively, to run from the terminal:

```. $HOME/.local/bin/indicatorvirtualbox.sh```



---
Config / Log
------------

During the course of normal operation, the indicator may write to the config at `$HOME/.config/indicatorvirtualbox`.

In the event an error occurs, a log file will be written to `$HOME/indicatorvirtualbox.log`.



---
Limitations
-----------

- `ICEWM`: Notifications are unsupported.
- `KDE`: Mouse wheel scroll over icon is unsupported.
- `Kubuntu 24.04`: No autostart.
- `Manjaro 24`: No autostart.
- `Manjaro 25`: No autostart.
- `Wayland`: The command `wmctrl` is unsupported.



---
Uninstall
---------

<details><summary><b>Debian 12</b></summary>

1. Uninstall operating system packages:

    ```
    sudo apt-get -y remove gir1.2-ayatanaappindicator3-0.1 gnome-shell-extension-appindicator libcairo2-dev libgirepository1.0-dev python3-pip python3-venv wmctrl
    ```

2. Uninstall the indicator from the `Python3` virtual environment, including icons, .desktop and run script:
    ```
    indicator=indicatorvirtualbox && \
    venv=$HOME/.local/venv_indicators && \
    $(ls -d ${venv}/lib/python3.* | head -1)/site-packages/${indicator}/platform/linux/uninstall.sh && \
    . ${venv}/bin/activate && \
    python3 -m pip uninstall --yes ${indicator} && \
    count=$(python3 -m pip --disable-pip-version-check list | grep -o "indicator" | wc -l) && \
    deactivate && \
    if [ "$count" -eq "0" ]; then rm -f -r ${venv}; fi 
    ```

    The configuration directory `$HOME/.config/indicatorvirtualbox` will not be deleted.

    The cache directory `$HOME/.cache/indicatorvirtualbox` will be deleted.

    If no other indicators remain installed, the virtual environment will be deleted.

</details>

<details><summary><b>Debian 13</b></summary>

1. Uninstall operating system packages:

    ```
    sudo apt-get -y remove gir1.2-ayatanaappindicator3-0.1 gnome-shell-extension-appindicator libcairo2-dev libgirepository-2.0-dev python3-pip python3-venv wmctrl
    ```

2. Uninstall the indicator from the `Python3` virtual environment, including icons, .desktop and run script:
    ```
    indicator=indicatorvirtualbox && \
    venv=$HOME/.local/venv_indicators && \
    $(ls -d ${venv}/lib/python3.* | head -1)/site-packages/${indicator}/platform/linux/uninstall.sh && \
    . ${venv}/bin/activate && \
    python3 -m pip uninstall --yes ${indicator} && \
    count=$(python3 -m pip --disable-pip-version-check list | grep -o "indicator" | wc -l) && \
    deactivate && \
    if [ "$count" -eq "0" ]; then rm -f -r ${venv}; fi 
    ```

    The configuration directory `$HOME/.config/indicatorvirtualbox` will not be deleted.

    The cache directory `$HOME/.cache/indicatorvirtualbox` will be deleted.

    If no other indicators remain installed, the virtual environment will be deleted.

</details>

<details><summary><b>Fedora 42 | Fedora 43</b></summary>

1. Uninstall operating system packages:

    ```
    sudo dnf -y remove cairo-gobject-devel gcc gobject-introspection-devel libappindicator-gtk3 python3-devel python3-pip wmctrl
    ```

2. Uninstall the indicator from the `Python3` virtual environment, including icons, .desktop and run script:
    ```
    indicator=indicatorvirtualbox && \
    venv=$HOME/.local/venv_indicators && \
    $(ls -d ${venv}/lib/python3.* | head -1)/site-packages/${indicator}/platform/linux/uninstall.sh && \
    . ${venv}/bin/activate && \
    python3 -m pip uninstall --yes ${indicator} && \
    count=$(python3 -m pip --disable-pip-version-check list | grep -o "indicator" | wc -l) && \
    deactivate && \
    if [ "$count" -eq "0" ]; then rm -f -r ${venv}; fi 
    ```

    The configuration directory `$HOME/.config/indicatorvirtualbox` will not be deleted.

    The cache directory `$HOME/.cache/indicatorvirtualbox` will be deleted.

    If no other indicators remain installed, the virtual environment will be deleted.

3. The `GNOME Shell` `AppIndicator and KStatusNotifierItem Support` extension may be turned [off](https://extensions.gnome.org/extension/615/appindicator-support) if no longer in use by other indicators.

</details>

<details><summary><b>Kubuntu 24.04 | Linux Mint Cinnamon 21 | Linux Mint Cinnamon 22 | Lubuntu 24.04 | Ubuntu 22.04 | Ubuntu 24.04 | Ubuntu Budgie 24.04 | Ubuntu MATE 24.04 | Ubuntu Unity 24.04 | Xubuntu 24.04</b></summary>

1. Uninstall operating system packages:

    ```
    sudo apt-get -y remove gir1.2-ayatanaappindicator3-0.1 libcairo2-dev libgirepository1.0-dev python3-pip python3-venv wmctrl
    ```

2. Uninstall the indicator from the `Python3` virtual environment, including icons, .desktop and run script:
    ```
    indicator=indicatorvirtualbox && \
    venv=$HOME/.local/venv_indicators && \
    $(ls -d ${venv}/lib/python3.* | head -1)/site-packages/${indicator}/platform/linux/uninstall.sh && \
    . ${venv}/bin/activate && \
    python3 -m pip uninstall --yes ${indicator} && \
    count=$(python3 -m pip --disable-pip-version-check list | grep -o "indicator" | wc -l) && \
    deactivate && \
    if [ "$count" -eq "0" ]; then rm -f -r ${venv}; fi 
    ```

    The configuration directory `$HOME/.config/indicatorvirtualbox` will not be deleted.

    The cache directory `$HOME/.cache/indicatorvirtualbox` will be deleted.

    If no other indicators remain installed, the virtual environment will be deleted.

</details>

<details><summary><b>Manjaro 25</b></summary>

1. Uninstall operating system packages:

    ```
    sudo pacman -R --noconfirm cairo gcc libayatana-appindicator pkgconf wmctrl
    ```

2. Uninstall the indicator from the `Python3` virtual environment, including icons, .desktop and run script:
    ```
    indicator=indicatorvirtualbox && \
    venv=$HOME/.local/venv_indicators && \
    $(ls -d ${venv}/lib/python3.* | head -1)/site-packages/${indicator}/platform/linux/uninstall.sh && \
    . ${venv}/bin/activate && \
    python3 -m pip uninstall --yes ${indicator} && \
    count=$(python3 -m pip --disable-pip-version-check list | grep -o "indicator" | wc -l) && \
    deactivate && \
    if [ "$count" -eq "0" ]; then rm -f -r ${venv}; fi 
    ```

    The configuration directory `$HOME/.config/indicatorvirtualbox` will not be deleted.

    The cache directory `$HOME/.cache/indicatorvirtualbox` will be deleted.

    If no other indicators remain installed, the virtual environment will be deleted.

</details>

<details><summary><b>openSUSE Tumbleweed</b></summary>

1. Uninstall operating system packages:

    ```
    sudo zypper remove -y cairo-devel gcc gobject-introspection-devel python3-devel typelib-1_0-AyatanaAppIndicator3-0_1
    ```

2. Uninstall the indicator from the `Python3` virtual environment, including icons, .desktop and run script:
    ```
    indicator=indicatorvirtualbox && \
    venv=$HOME/.local/venv_indicators && \
    $(ls -d ${venv}/lib/python3.* | head -1)/site-packages/${indicator}/platform/linux/uninstall.sh && \
    . ${venv}/bin/activate && \
    python3 -m pip uninstall --yes ${indicator} && \
    count=$(python3 -m pip --disable-pip-version-check list | grep -o "indicator" | wc -l) && \
    deactivate && \
    if [ "$count" -eq "0" ]; then rm -f -r ${venv}; fi 
    ```

    The configuration directory `$HOME/.config/indicatorvirtualbox` will not be deleted.

    The cache directory `$HOME/.cache/indicatorvirtualbox` will be deleted.

    If no other indicators remain installed, the virtual environment will be deleted.

3. The `GNOME Shell` `AppIndicator and KStatusNotifierItem Support` extension may be turned [off](https://extensions.gnome.org/extension/615/appindicator-support) if no longer in use by other indicators.

</details>



---
License
-------

This project in its entirety is licensed under the terms of the GNU General Public License v3.0 license.

Copyright 2012-2026 Bernard Giannetti.
