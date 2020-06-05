"""Reflexec output module.
"""

from .plugin import __builtin_plugins__

# register builtin output plugins
OUTPUT_PLUGINS = dict(
    [plugin_class.name, plugin_class] for plugin_class in __builtin_plugins__
)
