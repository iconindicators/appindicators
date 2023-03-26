#!/usr/bin/env python3
# -*- coding: utf-8 -*-


#TODO Current thinking/plan for creating snaps...
#
# To create a snap, need to have a well-behaved/formed Python project with a setup.py
# Based on reading, but still need to verify via official documentation,
#    https://docs.python.org/3/distutils/setupscript.html
#    https://packaging.python.org/en/latest/
#    https://github.com/pypa/sampleproject/tree/db5806e0a3204034c51b1c00dde7d5eb3fa2532e
# other files may or may not be required to get to the snap build stage such as
# setup.cfg, README*, MANIFEST* and others.
#
# To create the Python default source distribution use
#
#    python setup.py sdist
#
# To create the snap, assuming the snap-specific configuration .yaml file is created
# (and possibly other stuff), must be able to create a Python wheel successfully.
#
# May be possible to then create a source DEB release based on the ability to create an RPM
#
#    python setup.py bdist_rpm
#
# See
#
#    python setup.py bdist --help-formats
# 
# which could then replace hopefully the dedicated shell script to build the DEB source file.
#
# HOWEVER, Python is deprecating setup.py in some capacity.
# Unsure if that means setup.py will be completely dropped, but it certainly seems in the next year or so
# some major change is afoot.
#
# The new way for a Python project to be built/configured is to use pyproject.toml.
# Unfortunately, the snap build does not support pyproject.toml
#
# For now, get the simplest setup.py working to get a snap built.
# If/when the time comes, migrated to pyproject.toml assuming either
# snap supports pyproject.toml or there is a way to make snap build using a
# pyproject.toml converted to a setup.py
#
# Ideally, want a well-behaved/formed Python project from the outset using pyproject.toml
# and from that all other builds (DEB source for LaunchPad, snap, et al) come from that.
#
# For further consideration...
#
#    Can/should the current changelog file be changed to the Python format
#    and then part of the build for DEB source takes the Python format changelog
#    and converts to the DEB format?
#
#    Is it possible to have a single version number location?
#    Ideally should be in the setup.py (or perhaps setup.cfg).
#    Look into this as would need to removed the version number from say
#    each indicator's main .py file and be replaced at build time.
#    https://packaging.python.org/en/latest/guides/single-sourcing-package-version/
#
# ALL TODOS BELOW MAY OR MAY NOT NO LONGER APPLY!


#TODO Setup Tools, setup.py
# https://docs.python.org/3/distutils/introduction.html
# https://setuptools.pypa.io/en/latest/setuptools.html
# https://packaging.python.org/en/latest/
# https://pypa-build.readthedocs.io/en/stable/
# https://peps.python.org/pep-0517/
#
# https://chriswarrick.com/blog/2023/01/15/how-to-improve-python-packaging/
#
# https://forum.snapcraft.io/
# https://blog.ganssle.io/articles/2021/10/setup-py-deprecated.html
#
# https://sinoroc.gitlab.io/kb/python/package_data.html
# https://discuss.python.org/t/how-to-package-translation-files-po-mo-in-a-future-proof-way/20096


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


# https://forum.snapcraft.io/t/parse-info-on-pythonpart-utilizing-pyproject-toml/33294
# https://forum.snapcraft.io/t/building-a-core20-python-snap-using-pyproject-toml/22028
# https://stackoverflow.com/questions/73310069/should-i-be-using-only-pyproject-toml
# https://stackoverflow.com/questions/72352801/migration-from-setup-py-to-pyproject-toml-how-to-specify-package-name
# https://stackoverflow.com/questions/71193095/questions-on-pyproject-toml-vs-setup-py
# https://stackoverflow.com/questions/62983756/what-is-pyproject-toml-file-for
# https://setuptools.pypa.io/en/latest/userguide/pyproject_config.html





#TODO Examples from
# https://docs.python.org/3/distutils/setupscript.html
#
#
# from distutils.core import setup
# setup(name='foo',
#       version='1.0',
#       py_modules=['foo'],
#       )
#
#
#
#
# from distutils.core import setup
#
# setup(name='Distutils',
#       version='1.0',
#       description='Python Distribution Utilities',
#       author='Greg Ward',
#       author_email='gward@python.net',
#       url='https://www.python.org/sigs/distutils-sig/',
#       packages=['distutils', 'distutils.command'],
#      )




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
