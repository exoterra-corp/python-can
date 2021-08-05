#!/usr/bin/env python
"""
Setup script for the `can` package.
Learn more at https://github.com/hardbyte/python-can/
"""

# pylint: disable=invalid-name

from __future__ import absolute_import

from os import listdir, environ
from os.path import isfile, join
import re
import logging
from setuptools import setup, find_packages

logging.basicConfig(level=logging.WARNING)

version="4.0.7"
# #look for the ci_cd env vars
# short_sha = environ.get("CI_COMMIT_SHORT_SHA")
# tag = environ.get("CI_COMMIT_TAG")
# branch_name = environ.get("CI_COMMIT_BRANCH")
#
# #building on tag
# if short_sha is not None and tag is not None:
#     VER = f"{VER}_{tag}_{short_sha}"
# #building on server but not on tag
# elif branch_name is not None:
#     VER = f"{VER}_{branch_name}-dev"
# #building on local machine
# else:
#     VER = f"{VER}-dev"
# print(f"BUILDING: {VER}")
# version = VER

with open("README.rst", "r") as f:
    long_description = f.read()

# Dependencies
extras_require = {
    "seeedstudio": ["pyserial>=3.0"],
    "serial": ["pyserial~=3.0"],
    "neovi": ["filelock", "python-ics>=2.12"],
    "cantact": ["cantact>=0.0.7"],
    "gs_usb": ["gs_usb>=0.2.1"],
    "nixnet": ["nixnet>=0.3.1"],
}

setup(
    # Description
    name="python-can",
    url="https://github.com/hardbyte/python-can",
    description="Controller Area Network interface module for Python",
    long_description=long_description,
    classifiers=[
        # a list of all available ones: https://pypi.org/classifiers/
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Operating System :: MacOS",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Manufacturing",
        "Intended Audience :: Telecommunications Industry",
        "Natural Language :: English",
        "Topic :: System :: Logging",
        "Topic :: System :: Monitoring",
        "Topic :: System :: Networking",
        "Topic :: System :: Hardware :: Hardware Drivers",
        "Topic :: Utilities",
    ],
    version=version,
    packages=find_packages(exclude=["test*", "doc", "scripts", "examples"]),
    scripts=list(filter(isfile, (join("scripts/", f) for f in listdir("scripts/")))),
    author="Python CAN contributors",
    license="LGPL v3",
    package_data={
        "": ["README.rst", "CONTRIBUTORS.txt", "LICENSE.txt", "CHANGELOG.txt"],
        "doc": ["*.*"],
        "examples": ["*.py"],
    },
    # Installation
    # see https://www.python.org/dev/peps/pep-0345/#version-specifiers
    python_requires=">=3.6",
    install_requires=[
        # Note setuptools provides pkg_resources which python-can makes use of,
        # but we assume it is already installed.
        # "setuptools",
        "wrapt~=1.10",
        'windows-curses;platform_system=="Windows"',
        "mypy_extensions>=0.4.0,<0.5.0",
        'pywin32;platform_system=="Windows"',
        'msgpack~=1.0.0;platform_system!="Windows"',
        "crcengine==0.2.0",
    ],
    extras_require=extras_require,
    setup_requires=['wheel'],
)
