"""
The ``can`` package provides controller area network support for
Python developers; providing common abstractions to
different hardware devices, and a suite of utilities for sending and receiving
messages on a can bus.
"""

import logging
from os import environ
from typing import Dict, Any

VER="4.0.5"
#look for the ci_cd env vars
short_sha = environ.get("CI_COMMIT_SHORT_SHA")  
tag = environ.get("CI_COMMIT_TAG")
branch_name = environ.get("CI_COMMIT_BRANCH")

#building on tag
if short_sha is not None and tag is not None:
    VER = f"{VER}_{tag}_{short_sha}"
#building on server but not on tag
elif branch_name is not None:
    VER = f"{VER}_{branch_name}-dev"
#building on local machine
else:
    VER = f"{VER}-dev"
print(f"BUILDING: {VER}")
__version__ = VER

log = logging.getLogger("can")

rc: Dict[str, Any] = dict()

class CanError(IOError):
    """Indicates an error with the CAN network.

    """


from .listener import Listener, BufferedReader, RedirectReader, AsyncBufferedReader

from .io import Logger, SizedRotatingLogger, Printer, LogReader, MessageSync
from .io import ASCWriter, ASCReader
from .io import BLFReader, BLFWriter
from .io import CanutilsLogReader, CanutilsLogWriter
from .io import CSVWriter, CSVReader
from .io import SqliteWriter, SqliteReader

from .util import set_logging_level

from .message import Message
from.exomessage import ExoMessage
from .bus import BusABC, BusState
from .thread_safe_bus import ThreadSafeBus
from .notifier import Notifier
from .interfaces import VALID_INTERFACES
from . import interface
from .interface import Bus, detect_available_configs
from .bit_timing import BitTiming

from .broadcastmanager import (
    CyclicSendTaskABC,
    LimitedDurationCyclicSendTaskABC,
    ModifiableCyclicTaskABC,
    MultiRateCyclicSendTaskABC,
    RestartableCyclicTaskABC,
)
