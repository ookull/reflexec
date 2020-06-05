"""Reflexec ANSI escape codes module for output plugins.

This module generates ANSI character codes to printing colors to terminals.
See: http://en.wikipedia.org/wiki/ANSI_escape_code

Some code is borrowed from `colorama <https://pypi.python.org/pypi/colorama>`_
module (Copyright Jonathan Hartley 2013. BSD 3-Clause license).
"""

#: Control Sequence Introducer
CSI = "\033["
#: Operating System Command
OSC = "\033]"
#: Bell character
BEL = "\007"


def set_title(title):
    """Set terminal title."""
    return "{OSC}2;{title}{BEL}".format(OSC=OSC, title=title, BEL=BEL)


def clear_screen(mode=2):
    """Clear screen."""
    return "{CSI}0;0H{CSI}{mode}J".format(CSI=CSI, mode=mode)


def clear_line(mode=2):
    """Clear current line."""
    return "{CSI}{mode}K".format(CSI=CSI, mode=mode)


def code_to_chars(code):
    """Convert code to ANSI escape sequence."""
    return "{CSI}{code}m".format(CSI=CSI, code=code)


# pylint: disable=too-few-public-methods
class AnsiFore:
    """ANSI foreground color codes."""

    black = code_to_chars(30)
    red = code_to_chars(31)
    green = code_to_chars(32)
    yellow = code_to_chars(33)
    blue = code_to_chars(34)
    magenta = code_to_chars(35)
    cyan = code_to_chars(36)
    white = code_to_chars(37)
    reset = code_to_chars(39)

    # These are fairly well supported, but not part of the standard.
    lightblack = code_to_chars(90)
    lightred = code_to_chars(91)
    lightgreen = code_to_chars(92)
    lightyellow = code_to_chars(93)
    lightblue = code_to_chars(94)
    lightmagenta = code_to_chars(95)
    lightcyan = code_to_chars(96)
    lightwhite = code_to_chars(97)


# pylint: disable=too-few-public-methods
class AnsiBack:
    """ANSI background color codes."""

    black = code_to_chars(40)
    red = code_to_chars(41)
    green = code_to_chars(42)
    yellow = code_to_chars(43)
    blue = code_to_chars(44)
    magenta = code_to_chars(45)
    cyan = code_to_chars(46)
    white = code_to_chars(47)
    reset = code_to_chars(49)

    # These are fairly well supported, but not part of the standard.
    lightblack = code_to_chars(100)
    lightred = code_to_chars(101)
    lightgreen = code_to_chars(102)
    lightyellow = code_to_chars(103)
    lightblue = code_to_chars(104)
    lightmagenta = code_to_chars(105)
    lightcyan = code_to_chars(106)
    lightwhite = code_to_chars(107)


class AnsiStyle:
    """ANSI style codes."""

    bright = code_to_chars(1)
    dim = code_to_chars(2)
    normal = code_to_chars(22)
    reset_all = code_to_chars(0)
