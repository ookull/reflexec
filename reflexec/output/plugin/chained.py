"""Reflexec output plugins - chain plugin to handle other plugins.

.. autoclass:: ChainedOutputPlugin
   :members:
   :show-inheritance:
"""

import datetime
import importlib
import time

from .base import OutputPlugin, log


class ChainedOutputPlugin(OutputPlugin):
    """Chained output plugin.

    Joins multiple output plugins to single bunch.
    """

    name = "chained"  #: Plugin name
    __descr__ = "Join multiple output plugins to chain"
    _plugins = None  #: List of output plugin instances

    def __init__(self, cmd_name, cfg):
        super().__init__(cmd_name, cfg)
        self._plugins = []

    def output(self, *args, **kw):
        """Standard output method."""
        for plugin in self._plugins:
            plugin.output(*args[:], **kw.copy())

    def add_plugins(self, plugins, builtin_plugins):
        """Add plugins to chain."""
        for plugin_name in plugins:
            if ":" in plugin_name:
                log.debug('Initializing external output plugin "%s"', plugin_name)
                module_name, class_name = plugin_name.split(":")
                try:
                    module = importlib.import_module(module_name)
                except ImportError as err:
                    log.error("Error while loading external output plugin: %s", err)
                    continue
                plugin_class = getattr(module, class_name)
            else:
                log.debug('Initializing built-in output plugin "%s"', plugin_name)
                try:
                    plugin_class = builtin_plugins[plugin_name]
                except KeyError:
                    log.error('Invalid output plugin "%s"', plugin_name)
                    continue
            self._plugins.append(
                plugin_class(cmd_name=self.cmd_name, cfg=self._cfg.get(plugin_name, {}))
            )

        if not self._plugins:
            log.info("No output plugins specified, using default")
            plugin_class = builtin_plugins["default"]
            self._plugins = [
                plugin_class(cmd_name=self.cmd_name, cfg=self._cfg.get("default", {}))
            ]

    def handle_plugin_event(self, plugin, event_name, params):
        """Handle plugin event."""
        plugin.exec_data = self.exec_data
        plugin.watch_data = self.watch_data

        event = getattr(plugin, event_name)
        try:
            event(*params)
        except KeyError as err:
            log.error(
                "Invalid key %s while formatting '%s' "
                "message for output plugin '%s'",
                err,
                event_name,
                plugin.name,
            )
        except Exception as err:  # pylint: disable=broad-except
            log.error(
                "%s while formatting '%s' message for output plugin '%s'",
                err,
                event_name,
                plugin.name,
            )

    def start_exec(self, cmd):
        """Handle command execution start event."""
        self.exec_data.start_time = datetime.datetime.now()
        self.exec_data.count += 1

        for plugin in self._plugins:
            plugin.set_msg_params(command=" ".join(cmd))
            self.handle_plugin_event(plugin, "start_exec", [cmd])

    def finish_exec(self, returncode, exec_msg):
        """Handle command execution finish event."""
        self.exec_data.exit_status_code = returncode
        self.exec_data.exit_status_msg = exec_msg
        self.exec_data.finish_time = datetime.datetime.now()
        self.exec_data.duration = self.exec_data.finish_time - self.exec_data.start_time

        # delay to let the command to flush output
        time.sleep(0.1)

        for plugin in self._plugins:
            plugin.set_msg_params(exec_msg=exec_msg, returncode=returncode)
            self.handle_plugin_event(plugin, "finish_exec", [returncode, exec_msg])

    def post_exec_delay(self, delay):
        """Handle post exec delay."""
        if not delay:
            return

        for plugin in self._plugins:
            plugin.set_msg_params(delay=int(delay) if int(delay) == delay else delay)
            self.handle_plugin_event(plugin, "start_delay", [delay])

        while delay > 0:
            _delay = delay % 1 or 1
            for plugin in self._plugins:
                plugin.set_msg_params(
                    delay=int(delay) if int(delay) == delay else delay
                )
                self.handle_plugin_event(plugin, "update_delay", [delay])
            time.sleep(_delay)
            delay -= _delay

        for plugin in self._plugins:
            self.handle_plugin_event(plugin, "finish_delay", [])

    def start_watch(self, patterns):
        """Handle filesystem watch start event."""
        self.watch_data.patterns = patterns
        for plugin in self._plugins:
            self.handle_plugin_event(plugin, "start_watch", [patterns])

    def handle_watch_event(self, event):
        """Handle filesystem watch event."""
        for plugin in self._plugins:
            plugin.set_msg_params(event=event)
            self.handle_plugin_event(plugin, "handle_watch_event", [event])

    def finish_watch(self, changed_file):
        """Handle filesystem watch finish event."""
        self.watch_data.changed_file = changed_file
        if changed_file is None:
            self.watch_data.error_msg = "Keyboard interrupt"
        elif changed_file == "":
            self.watch_data.error_msg = "Got QUIT signal"
        else:
            self.watch_data.error_msg = ""

        for plugin in self._plugins:
            plugin.set_msg_params(filename=changed_file)
            self.handle_plugin_event(plugin, "finish_watch", [changed_file])
