# python-can

[![Latest Version on PyPi](https://img.shields.io/pypi/v/python-can.svg)](https://pypi.python.org/pypi/python-can/)
[![Downloads on PePy](https://pepy.tech/badge/python-can)](https://pepy.tech/project/python-can)
[![Monthly downloads on PePy](https://pepy.tech/badge/python-can/month)](https://pepy.tech/project/python-can/month)
[![This project uses the black formatter.](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)

[![Documentation](https://readthedocs.org/projects/python-can/badge/?version=stable)](https://python-can.readthedocs.io/en/stable/)
[![Travis CI Server for develop branch](https://img.shields.io/travis/hardbyte/python-can/develop.svg?label=Travis%20CI)](https://travis-ci.org/hardbyte/python-can/branches)
[![AppVeyor CI Server for develop branch](https://img.shields.io/appveyor/ci/hardbyte/python-can/develop.svg?label=AppVeyor)](https://ci.appveyor.com/project/hardbyte/python-can/history)
[![Test coverage reports on Codecov.io](https://codecov.io/gh/hardbyte/python-can/branch/develop/graph/badge.svg)](https://codecov.io/gh/hardbyte/python-can/branch/develop)

[![Mergify Status](https://img.shields.io/endpoint.svg?url=https://gh.mergify.io/badges/hardbyte/python-can&style=flat)](https://mergify.io)

The **C**ontroller **A**rea **N**etwork is a bus standard designed to
allow microcontrollers and devices to communicate with each other. It
has priority based bus arbitration and reliable deterministic
communication. It is used in cars, trucks, boats, wheelchairs and more.

The `can` package provides controller area network support for Python
developers; providing common abstractions to different hardware devices,
and a suite of utilities for sending and receiving messages on a can
bus.

The library currently supports Python 3.6+ as well as PyPy 3 and runs on
Mac, Linux and Windows.

+--------------------------------+------------+
| Library Version                | Python     |
+================================+============+
| > 2.x                          | 2.6+, 3.4+ |
+--------------------------------+------------+
| > 3.x                          | 2.7+, 3.5+ |
+--------------------------------+------------+
| > 4.x *(currently on develop)* | 3.6+       |
+--------------------------------+------------+

## Features

-   common abstractions for CAN communication
-   support for many different backends (see the
    [docs](https://python-can.readthedocs.io/en/stable/interfaces.html))
-   receiving, sending, and periodically sending messages
-   normal and extended arbitration IDs
-   limited [CAN FD](https://en.wikipedia.org/wiki/CAN_FD) support
-   many different loggers and readers supporting playback: ASC
    (CANalyzer format), BLF (Binary Logging Format by Vector), CSV,
    SQLite and Canutils log
-   efficient in-kernel or in-hardware filtering of messages on
    supported interfaces
-   bus configuration reading from file or environment variables
-   CLI tools for working with CAN buses (see the
    [docs](https://python-can.readthedocs.io/en/stable/scripts.html))
-   more

## Example usage

``` python
# import the library
import can

# create a bus instance
# many other interfaces are supported as well (see below)
bus = can.Bus(interface='socketcan',
              channel='vcan0',
              receive_own_messages=True)

# send a message
message = can.Message(arbitration_id=123, is_extended_id=True,
                      data=[0x11, 0x22, 0x33])
bus.send(message, timeout=0.2)

# iterate over received messages
for msg in bus:
    print("{:X}: {}".format(msg.arbitration_id, msg.data))

# or use an asynchronous notifier
notifier = can.Notifier(bus, [can.Logger("recorded.log"), can.Printer()])
```

You can find more information in the documentation, online at
[python-can.readthedocs.org](https://python-can.readthedocs.org/en/stable/).

## Discussion

If you run into bugs, you can file them in our [issue
tracker](https://github.com/hardbyte/python-can/issues) on GitHub.

There is also a
[python-can](https://groups.google.com/forum/#!forum/python-can) mailing
list for development discussion.

[Stackoverflow](https://stackoverflow.com/questions/tagged/can+python)
has several questions and answers tagged with `python+can`.

Wherever we interact, we strive to follow the [Python Community Code of
Conduct](https://www.python.org/psf/codeofconduct/).

## Contributing

See [doc/development.rst](doc/development.rst) for getting started.
