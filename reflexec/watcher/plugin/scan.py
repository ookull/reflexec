"""Reflexec filesystem scanning watcher plugins module.

Checks file mtime and ctime with regular interval.

.. autoclass:: ScanFileSystemWatcherPlugin
   :members: cfg, name
   :show-inheritance:
"""

import os
import time

from .base import WatcherPlugin, convert_patterns_to_paths, log


class ScanFileSystemWatcherPlugin(WatcherPlugin):
    """Scan file system watcher plugin."""

    name = "scan"  #: Plugin name
    __descr__ = "File system scanner. Universal but slow."
    cfg = {"scan_interval": 1}  #: Plugin default configuration

    def __init__(self, patterns, output, cfg):
        super().__init__(patterns, output, cfg)
        try:
            self._cfg["scan_interval"] = float(self._cfg["scan_interval"])
        except ValueError as err:
            log.error("Value error while parsing scan_interval value: %s", err)
            raise SystemExit(1)

    def watch(self):
        """Watch file system.

        :raises: StopIteration
        """

        def generate_watch_event(event_name, path):
            """Generate watch event."""
            raise StopIteration(":".join([event_name, path]))

        # convert watch patterns to file list
        watch_timestamps = {}
        for path in convert_patterns_to_paths(self.watch_patterns):
            log.debug("Adding path to watch: %s", path)
            try:
                path_stat = os.stat(path, follow_symlinks=False)
            except FileNotFoundError:
                generate_watch_event("REMOVE", path)
            watch_timestamps[path] = path_stat.st_mtime, path_stat.st_ctime

        # scan file system changes
        while True:
            time.sleep(self._cfg["scan_interval"])
            log.debug("Scanning filesystem")
            for path, path_stat in watch_timestamps.items():
                try:
                    path_current_stat = os.stat(path, follow_symlinks=False)
                except FileNotFoundError:
                    generate_watch_event("REMOVE", path)
                if path_stat[0] != path_current_stat.st_mtime:
                    generate_watch_event("MODIFY", path)
                if path_stat[1] != path_current_stat.st_ctime:
                    generate_watch_event("CHANGE", path)
