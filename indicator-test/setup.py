#!/usr/bin/env python3
# -*- coding: utf-8 -*-


#TODO Setup Tools, setup.py
# https://docs.python.org/3/distutils/introduction.html
# https://setuptools.pypa.io/en/latest/setuptools.html


#TODO As per 
# https://github.com/pypa/sampleproject/blob/db5806e0a3204034c51b1c00dde7d5eb3fa2532e/setup.cfg
# might be able to use a generic setup.py (in IndicatorBase) 
# and the specifics for each indicator are in a setup.cfg in each Indicator's directory.
#
# What is pyproject.toml compared to setup.cfg?
# https://ianhopkinson.org.uk/2022/02/understanding-setup-py-setup-cfg-and-pyproject-toml-in-python/
# http://ivory.idyll.org/blog/2021-transition-to-pyproject.toml-example.html
# https://www.reddit.com/r/learnpython/comments/yqq551/pyprojecttoml_setupcfg_setuppy_whats_the/
# Need to be careful here...
# Looks like toml is the new way to go...replacing setup.py/setup.cfg,
# but does snap accept toml?


#TODO If we switch exclusively to setup, then view the snap and ppa/deb as packages for deployment
# and thus, should be built as needed.
# This implies the debian/changelog should be built from a higher-level/project-level CHANGELOG perhaps.


#TODO The src directory really, according to python,
# have a subdirectory named indicator-test which contains all the src contents.
# Check to see if we can have the '-' there or not.


#TODO Do we need __init__.py?
# Based on this, yes:
#    https://stackoverflow.com/a/48804718/2156453
#
# Also from distutils introduction link above:
#
#    package
#        a module that contains other modules; typically contained in a directory in the filesystem
#        and distinguished from other directories by the presence of a file __init__.py.


#TODO How to handle po and mo files?
# https://stackoverflow.com/questions/22958245/what-is-the-correct-way-to-include-localisation-in-python-packages
# https://stackoverflow.com/questions/53285634/is-there-a-portable-way-to-provide-localization-of-a-package-distributed-on-pypi?noredirect=1&lq=1
# https://github.com/s-ball/mo_installer
# https://stackoverflow.com/questions/55365356/how-to-include-localized-message-in-python-setuptools?noredirect=1&lq=1
# https://stackoverflow.com/questions/34070103/how-to-compile-po-gettext-translations-in-setup-py-python-script


#TODO General setup.py packaging information
# https://python-packaging-tutorial.readthedocs.io/en/latest/setup_py.html
# https://stackoverflow.com/questions/19048732/python-setup-py-develop-vs-install
# https://stackoverflow.com/questions/42411111/why-we-need-python-packaging-e-g-egg
# https://github.com/kennethreitz/setup.py
# https://stackoverflow.com/questions/1471994/what-is-setup-py
# https://godatadriven.com/blog/a-practical-guide-to-using-setup-py/
# https://stackoverflow.com/questions/72627196/modulenotfounderror-when-using-setup-py-install-version-of-package-but-not-loca
# https://stackoverflow.com/questions/64838393/package-dir-in-setup-py-not-working-as-expected
# https://stackoverflow.com/questions/34070103/how-to-compile-po-gettext-translations-in-setup-py-python-script?rq=1
# https://stackoverflow.com/questions/40051076/compile-translation-files-when-calling-setup-py-install?rq=1
#
# https://github.com/thinkle/gourmet/blob/master/setup.py
# https://github.com/PythonOT/POT/blob/master/setup.py
# https://github.com/moinwiki/moin/blob/master/setup.py
# https://github.com/GourmandRecipeManager/gourmand/blob/main/setup.py
#
# https://www.mattlayman.com/blog/2015/i18n/
#
# https://stackoverflow.com/questions/32609248/setuptools-adding-additional-files-outside-package


#TODO What about AppImage?
# https://appimage.org/


#TODO Might be possible to take the setup.py file and create a deb via
#    python3 setup.py bdist_deb
#
# https://unix.stackexchange.com/questions/642948/build-debian-package-using-stdeb
#
# https://stackoverflow.com/questions/7110604/is-there-a-standard-way-to-create-debian-packages-for-distributing-python-progra
# https://the-hitchhikers-guide-to-packaging.readthedocs.io/en/latest/
# https://www.wefearchange.org/2010/05/from-python-package-to-ubuntu-package.html
# https://wiki.debian.org/Python/LibraryStyleGuide


#TODO Something to keep in mind when deciding to do or not to do Flathub
# https://github.com/PlaintextGroup/oss-virtual-incubator/blob/main/proposals/flathub-linux-app-store.md


from setuptools import setup, find_packages
import pathlib


#TODO Maybe remove this stuff?
# But this raises a larger point...
# The changelog and version number (other stuff too?)
# really should be in ONE place (per indicator) and that information is 
# magically pushed to the appropriate places when doing a build.
here = pathlib.Path( __file__ ).parent.resolve()

# Get the long description from the README file
long_description = ( here / "README.md" ).read_text( encoding = "utf-8" )

setup(
    name = "indicator-test",
    version = "1.0.6",
    description = "Testing indicator stuff.", #TODO !!!!!!!!!!!!!!!!!!!!!!  If the long description above is pulled from the README, why not this too?
    long_description = "Tests all aspects/functionality implemented by all other indicators in one place.",
    long_description_content_type = "text/plain",
    url = "https://launchpad.net/~thebernmeister/+archive/ubuntu/ppa",
    author = "Bernard Giannetti",
    author_email = "thebernmeister@hotmail.com",
    classifiers = [
        "Development Status :: 6 - Mature",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Topic :: Desktop Environment:",
    ],
    keywords = "indicator testing",
    package_dir = { "": "src" },
    packages=find_packages( where = "src" ),
    python_requires = ">= 3.6.5",
#    install_requires=["peppercorn"],  #TODO !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!   Add ephem for Indicator Lunar?
    # If there are data files included in your packages that need to be installed, specify them here.
#    package_data = {  # Optional
#        "sample": [ "package_data.dat" ],
#    },#TODO !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!  Indicator Lunar needs planets.bsp and stars.dat.gz under Skyfield 
    entry_points = {
        "console_scripts": [ "indicator-test = indicator-test:main" ],
    },
)
