"""Reflexec keyboard watcher module.
"""

import fcntl
import logging
import os
import sys
import termios

log = logging.getLogger("kbd_watcher")


def watch_kbd(event, pipeline):
    """Keyboard watcher.

    Poll keyboard events. Send keyboard event to pipeline and set threading
    event if any known event (keys R and Q).
    """
    log.debug("Starting keyboard watcher")

    fileno = sys.stdin.fileno()
    oldterm = termios.tcgetattr(fileno)
    newattr = oldterm[:]
    newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
    termios.tcsetattr(fileno, termios.TCSANOW, newattr)

    oldflags = fcntl.fcntl(fileno, fcntl.F_GETFL)
    fcntl.fcntl(fileno, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)

    # clear keyboard buffer
    try:
        while sys.stdin.read(1):
            pass
    except IOError:
        pass

    try:
        while not event.wait(0.1):
            try:
                char = sys.stdin.read(1)
                if char and char in "QqRr":
                    log.debug("Registered keyboard event %r", char)
                    pipeline.put(["KEYBOARD", char.upper()])
                    event.set()
                    break
            except IOError:
                pass
    finally:
        log.debug("Shutting down keyboard watcher")
        termios.tcsetattr(fileno, termios.TCSAFLUSH, oldterm)
        fcntl.fcntl(fileno, fcntl.F_SETFL, oldflags)
