"""Reflexec autodetect watcher plugins module.

Chooses the best built-in watcher plugin for current system. This plugin is
used with default configuration.

.. autoclass:: AutoDetectWatcherPlugin
   :members: name
   :show-inheritance:
"""

import sys

from .base import WatcherPlugin, log


class AutoDetectWatcherPlugin(WatcherPlugin):
    """AutoDetect watcher plugin."""

    name = "autodetect"  #: Plugin name
    __descr__ = "Choose best filesystem watcher for this OS (default)"
    _watcher = None  #: Watcher plugin

    def __init__(self, **kw):
        kw["cfg"] = {}
        super().__init__(**kw)

        # try to load watcher plugin class for this platform
        plugin_class = None
        try:
            if sys.platform == "linux":
                log.debug(
                    "Detected Linux platform: "
                    "trying to use built-in inotify watcher plugin"
                )
                from .inotify import InotifyWatcherPlugin as plugin_class
        except ImportError as err:
            log.error("Error while importing watcher module: %s", err)

        # fallback to generic filesystem watcher
        if plugin_class is None:
            log.debug("Use built-in universal filesystem watcher plugin as fallback")
            from .scan import ScanFileSystemWatcherPlugin as plugin_class

        self._watcher = plugin_class(**kw)

    def watch(self):
        """Watch file system."""
        self._watcher.watch()

    def stop(self):
        """Stop watching file system."""
        self._watcher.stop()
