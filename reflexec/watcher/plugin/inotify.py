"""Reflexec Inotify watcher plugins module.

Implements file system watching using Inotify Linux kernel subsystem.

.. autoclass:: InotifyWatcherPlugin
   :members: name
   :show-inheritance:
"""

import re

import pyinotify

from .base import WatcherPlugin, convert_patterns_to_paths, log


class InotifyHandler(pyinotify.ProcessEvent):
    """Inotify handler to process inotify events."""

    def process_default(self, event):
        """Process inotify event."""
        self.output.handle_watch_event(event)

        # don't process directory and ignored events
        if event.dir or event.mask == pyinotify.IN_IGNORED:
            return
        if event.path.startswith(("/", "./")):
            path = event.path
        else:
            path = "./{}".format(event.path)

        raise StopIteration("{0}:{1}".format(event.maskname, path))


class InotifyWatcherPlugin(WatcherPlugin):
    """Inotify watcher plugin."""

    name = "inotify"  #: Plugin name
    __descr__ = "Inotify (Linux)"
    _notifier = None
    output = None  #: Output plugin
    #: Plugin default configuration
    cfg = {
        "watch_mask": (
            # File was modified
            pyinotify.IN_MODIFY
            |
            # Writeable file was closed
            pyinotify.IN_CLOSE_WRITE
            |
            # Watched item was deleted
            pyinotify.IN_DELETE_SELF
            |
            # File was moved from X
            pyinotify.IN_MOVED_FROM
            |
            # File was moved to Y
            pyinotify.IN_MOVED_TO
        )
    }

    def __init__(self, patterns, output, cfg):
        # validate "watch_mask" config value
        if "watch_mask" in cfg:
            cfg["watch_mask"] = re.sub(r"[\n]", " ", cfg["watch_mask"])
            try:
                cfg["watch_mask"] = int(eval(cfg["watch_mask"], pyinotify.__dict__))
            except (NameError, ValueError) as err:
                log.error(
                    'Error parsing config value "watch_mask" for %r: %s', self, err
                )
                raise SystemExit(1)
            log.debug(
                'Config value "watch_mask" for %r converted to %d',
                self,
                cfg["watch_mask"],
            )

        super().__init__(patterns, output, cfg)

    def watch(self):
        """Watch file system."""
        # prepare watch manager
        watchman = pyinotify.WatchManager()
        for path in convert_patterns_to_paths(self.watch_patterns):
            log.debug("Adding path to watch: %s", path)
            try:
                watchman.add_watch(path, self._cfg["watch_mask"], quiet=False)
            except pyinotify.WatchManagerError as err:
                # file may disappear during setup of watches
                log.error("Error while adding watch %s: %s", path, err)

        # create watch notifier
        handler = InotifyHandler()
        handler.output = self.output
        self._notifier = pyinotify.Notifier(watchman, default_proc_fun=handler)
        self._notifier.loop()

    def stop(self):
        """Stop watching file system."""
        self._notifier.stop()
