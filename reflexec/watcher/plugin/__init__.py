"""Reflexec watcher plugins module.
"""

from .autodetect import AutoDetectWatcherPlugin
from .scan import ScanFileSystemWatcherPlugin

__builtin_plugins__ = [AutoDetectWatcherPlugin, ScanFileSystemWatcherPlugin]

try:
    from .inotify import InotifyWatcherPlugin

    __builtin_plugins__.append(InotifyWatcherPlugin)
except ImportError:
    pass
