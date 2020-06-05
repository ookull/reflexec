"""Reflexec watcher plugins base.
"""

import logging

log = logging.getLogger("reflexec")


class WatcherPlugin:
    """Base class for all watcher plugins.

    :param patterns: Patterns to watch
    :type patterns: list
    :param output: Output plugin
    :type output:
        :py:class:`reflexec.output.plugin.chained.ChainedOutputPlugin`
    :param debug: Debug mode
    :type debug: bool
    :param cfg: Plugin configuration
    :type cfg: dict
    """

    name = None  #: Plugin name
    __descr__ = None  #: Plugin description
    output = None  #: Output plugin
    watch_patterns = None  #: Patterns to watch
    cfg = {}  #: Plugin default configuration

    def __init__(self, patterns, output, cfg):
        self.watch_patterns = patterns
        self.output = output
        self._cfg = self.cfg
        self._cfg.update(cfg)

    def __repr__(self):
        return "{0.name} watcher plugin".format(self)

    def watch(self):
        """Watch file system."""
        raise NotImplementedError()

    def stop(self):
        """Stop watching file system."""


def convert_patterns_to_paths(patterns):
    """Convert pattern collections to file paths.

    Also filter paths:
    - remove path duplicates
    - remove excluded paths
    """
    paths = []
    for pattern in patterns:
        for path in pattern.paths:
            if path.startswith("-"):  # exclude
                if path[1:] in paths:
                    paths.remove(path[1:])
            else:  # include
                if path not in paths:
                    paths.append(path)

    return paths
