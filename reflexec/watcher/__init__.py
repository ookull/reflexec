"""Reflexec watcher module.
"""

import importlib
import logging

from .plugin import __builtin_plugins__

log = logging.getLogger("reflexec")

# register builtin watcher plugins
WATCHER_PLUGINS = dict(
    [plugin_class.name, plugin_class] for plugin_class in __builtin_plugins__
)


def get_watcher_plugin(plugin_name, **kw):
    """Get watcher plugin object by name.

    :param plugin_name: plugin name
    :param kw: parameters to pass for plugin class constructor
               :py:class:`reflexec.watcher.plugin.base.WatcherPlugin`
    """
    plugin_class = None
    if ":" in plugin_name:
        log.debug('Initializing external watcher plugin "%s"', plugin_name)
        module_name, class_name = plugin_name.split(":")
        try:
            module = importlib.import_module(module_name)
            plugin_class = getattr(module, class_name)
        except ImportError as err:
            log.error("Error while loading external watcher plugin: %s", err)
            raise SystemExit(1)
    else:
        log.debug('Initializing built-in watcher plugin "%s"', plugin_name)
        try:
            plugin_class = WATCHER_PLUGINS[plugin_name]
        except KeyError:
            log.error(
                'Specified built-in watcher plugin "%s" does not exist', plugin_name
            )
            log.info(
                "Execute reflexec with --list-plugins option to display plugin list"
            )
            raise SystemExit(1)

    if plugin_class:
        return plugin_class(**kw)

    return None
