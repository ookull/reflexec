"""Reflexec signal handler module.
"""

import logging
import signal

log = logging.getLogger("reflexec")


class SigQuitException(Exception):
    """Exception to raise on QUIT signal."""


def sigquit_handler(signum, frame):
    """Signal handler for watcher.

    Handles QUIT signal.

    :raise: :py:class:`SigQuitException`
    """
    assert signum == signal.SIGQUIT
    assert frame
    log.debug("Signal handler recieved QUIT signal")
    raise SigQuitException()


def set_quit_signal_handler():
    """Set local handler for QUIT signal."""
    log.debug("Setting QUIT signal handler")
    signal.signal(signal.SIGQUIT, sigquit_handler)
