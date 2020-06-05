"""Reflexec output plugins module.
"""

from .command import CommandOutputPlugin
from .simple import (
    DefaultOutputPlugin,
    JsonOutputPlugin,
    LoggerOutputPlugin,
    NullOutputPlugin,
    PlainOutputPlugin,
)
from .terminal import ClearTerminalOutputPlugin, ColorTerminalOutputPlugin
from .titlebar import FancyTerminalTitleOutputPlugin, TerminalTitleOutputPlugin

__builtin_plugins__ = [
    ClearTerminalOutputPlugin,
    ColorTerminalOutputPlugin,
    CommandOutputPlugin,
    DefaultOutputPlugin,
    FancyTerminalTitleOutputPlugin,
    JsonOutputPlugin,
    LoggerOutputPlugin,
    NullOutputPlugin,
    PlainOutputPlugin,
    TerminalTitleOutputPlugin,
]
