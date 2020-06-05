"""Reflexec simple output plugins module.

.. autoclass:: DefaultOutputPlugin
   :members: cfg, name
   :show-inheritance:

.. autoclass:: PlainOutputPlugin
   :members: cfg, name
   :show-inheritance:

.. autoclass:: NullOutputPlugin
   :members: cfg, name
   :show-inheritance:

.. autoclass:: JsonOutputPlugin
   :members: cfg, name
   :show-inheritance:

.. autoclass:: LoggerOutputPlugin
   :members: cfg, name
   :show-inheritance:
"""

import curses
import json
import logging
import sys

from ... import signal_handler
from .base import (
    EVENT_FINISH_EXEC,
    EVENT_FINISH_WATCH,
    EVENT_HANDLE_WATCH_EVENT,
    EVENT_START_DELAY,
    EVENT_START_EXEC,
    EVENT_START_WATCH,
    MAIN_LOOP_EVENTS,
    MSG_DELAY,
    MSG_FILE_CHANGED,
    MSG_FINISH_EXEC,
    MSG_PROCESSING_EVENT,
    MSG_SEND_QUIT_SIGNAL,
    MSG_START_EXEC,
    MSG_START_REFLEXEC,
    MSG_START_WATCH,
    OutputPlugin,
    log,
)


class DefaultOutputPlugin(OutputPlugin):
    """Default output plugin.

    Choose the best plugin for current terminal. :py:class:`PlainOutputPlugin`
    by default or :py:class:`ColorTerminalOutputPlugin` for color terminal.
    """

    name = "default"  #: Plugin name
    __descr__ = "Default output plugin"
    plugin = None  #: Actual output plugin

    def __init__(self, cmd_name, cfg):
        plugin_class = PlainOutputPlugin
        if hasattr(sys.stdout, "isatty") and sys.stdout.isatty():
            try:
                curses.setupterm()
                if curses.tigetnum("colors") > 2:
                    log.debug("Terminal supports %d colors", curses.tigetnum("colors"))
                    from .terminal import ColorTerminalOutputPlugin

                    plugin_class = ColorTerminalOutputPlugin
            except Exception:
                pass

        log.debug('Using output plugin "%s"', plugin_class.name)
        self.plugin = plugin_class(cmd_name=cmd_name, cfg=cfg)

        super().__init__(cmd_name, cfg)

    def __getattribute__(self, name):
        if name in MAIN_LOOP_EVENTS or name in ["output", "set_msg_params"]:
            return getattr(self.plugin, name)
        return super().__getattribute__(name)


class PlainOutputPlugin(OutputPlugin):
    """Plain output plugin.

    Output messages to stdout.
    """

    name = "plain"  #: Plugin name
    __descr__ = "Plain output to stdout"
    #: Plugin default configuration
    cfg = {
        "start_reflexec": MSG_START_REFLEXEC,
        EVENT_START_EXEC: MSG_START_EXEC,
        EVENT_FINISH_EXEC: MSG_FINISH_EXEC,
        EVENT_START_DELAY: MSG_DELAY,
        EVENT_START_WATCH: MSG_START_WATCH,
        "send_quit_signal": MSG_SEND_QUIT_SIGNAL,
        "process_event": MSG_PROCESSING_EVENT,
        "file_changed": MSG_FILE_CHANGED,
    }

    def __init__(self, cmd_name, cfg):
        super().__init__(cmd_name, cfg)
        self.output(self._cfg["start_reflexec"].format(**self._msg_params))

    def output(self, *args, **kw):
        """Standard output method."""
        if kw.pop("debug", False):
            if not self.cfg.get("debug"):
                return
            print("DEBUG: ", end="")
        assert len(args) == 1
        print(args[0], flush=True)

    def start_exec(self, cmd):
        """Handle command execution start event."""
        self.output(self._cfg[EVENT_START_EXEC].format(**self._msg_params))

    def finish_exec(self, returncode, exec_msg):
        """Handle command execution finish event."""
        self.output(exec_msg)
        self.output(self._cfg[EVENT_FINISH_EXEC].format(**self._msg_params))

    def start_delay(self, delay):
        """Start post exec delay."""
        self.output(self._cfg[EVENT_START_DELAY].format(**self._msg_params))

    def start_watch(self, patterns):
        """Handle filesystem watch start event."""
        self.output(self._cfg[EVENT_START_WATCH].format(**self._msg_params))
        self.output(self._cfg["send_quit_signal"])

    def handle_watch_event(self, event):
        """Handle filesystem watch event."""
        self.output(self._cfg["process_event"].format(**self._msg_params), debug=True)

    def finish_watch(self, changed_file):
        """Handle filesystem watch finish event."""
        if self.watch_data.error_msg:
            self.output(self.watch_data.error_msg)
            return
        self.output(self._cfg["file_changed"].format(**self._msg_params))


class NullOutputPlugin(OutputPlugin):
    """Null output plugin.

    Does not produce any output.
    """

    name = "null"  #: Plugin name
    __descr__ = "No output"


class JsonOutputPlugin(OutputPlugin):
    """JSON output plugin.

    Output JSON-formatted event info to stdout.
    """

    name = "json"  #: Plugin name
    __descr__ = "JSON output to stdout"

    def __init__(self, cmd_name, cfg):
        super().__init__(cmd_name, cfg)
        self.output(event="init", msg="Starting reflexec instance", name=cmd_name)

    def output(self, *args, **kw):
        """Standard output method."""
        if args:
            assert not kw
            assert len(args) == 1
            kw = dict(msg=args[0])
        json.dump(kw, sys.stdout, sort_keys=True)
        print(flush=True)

    def start_exec(self, cmd):
        """Handle command execution start event."""
        self.output(
            event=EVENT_START_EXEC,
            msg="Executing command",
            command=cmd,
            exec_count=self.exec_data.count,
        )

    def finish_exec(self, returncode, exec_msg):
        """Handle command execution finish event."""
        self.output(
            event=EVENT_FINISH_EXEC,
            msg=exec_msg,
            duration=self.exec_data.duration_dict,
            duration_str=self.exec_data.duration_str,
            exec_count=self.exec_data.count,
        )

    def start_delay(self, delay):
        """Start post exec delay."""
        self.output(event="post_exec_delay", delay=delay)

    def start_watch(self, patterns):
        """Handle filesystem watch start event."""
        self.output(event=EVENT_START_WATCH, msg=MSG_START_WATCH)

    def handle_watch_event(self, event):
        """Handle filesystem watch event."""
        # remove unused data from filesystem event
        if isinstance(event, signal_handler.SigQuitException):
            watch_event = "SIGQUIT"
        else:
            watch_event = event.__dict__.copy()
            del watch_event["wd"]

        # output data
        self.output(
            event=EVENT_HANDLE_WATCH_EVENT,
            msg="Processing event",
            watch_event=watch_event,
        )

    def finish_watch(self, changed_file):
        """Handle filesystem watch finish event."""
        if self.watch_data.error_msg:
            self.output(event=EVENT_FINISH_WATCH, msg=self.watch_data.error_msg)
            return
        self.output(
            event=EVENT_FINISH_WATCH,
            msg=MSG_FILE_CHANGED.format(filename=changed_file),
            changed_file=changed_file,
        )


class LoggerOutputPlugin(OutputPlugin):
    """Logger output plugin.

    Use standard logging for events.
    """

    name = "log"  #: Plugin name
    __descr__ = "Logging to stderr"
    logger = None  #: Logger instance
    #: Plugin default configuration
    cfg = {
        "start_reflexec": MSG_START_REFLEXEC,
        EVENT_START_EXEC: MSG_START_EXEC,
        EVENT_FINISH_EXEC: MSG_FINISH_EXEC,
        EVENT_START_DELAY: MSG_DELAY,
        EVENT_START_WATCH: MSG_START_WATCH,
        "send_quit_signal": MSG_SEND_QUIT_SIGNAL,
        "process_event": MSG_PROCESSING_EVENT,
        "file_changed": MSG_FILE_CHANGED,
    }

    def __init__(self, cmd_name, cfg):
        super().__init__(cmd_name, cfg)
        logging.basicConfig(
            level=logging.DEBUG if self.cfg.get("debug") else logging.INFO,
            format="%(asctime)s %(levelname)s: %(message)s",
        )
        self.logger = logging.getLogger("reflexec")
        self.output(self._cfg["start_reflexec"].format(**self._msg_params))

    def output(self, *args, **kw):
        """Standard output method."""
        self.logger.log(kw.pop("level", logging.INFO), *args, **kw)

    def start_exec(self, cmd):
        """Handle command execution start event."""
        self.output(self._cfg[EVENT_START_EXEC].format(**self._msg_params))

    def finish_exec(self, returncode, exec_msg):
        """Handle command execution finish event."""
        self.output(exec_msg, level=logging.ERROR if returncode else logging.INFO)
        self.output(self._cfg[EVENT_FINISH_EXEC].format(**self._msg_params))

    def start_delay(self, delay):
        """Start post exec delay."""
        self.output(self._cfg[EVENT_START_DELAY].format(**self._msg_params))

    def start_watch(self, patterns):
        """Handle filesystem watch start event."""
        self.output(self._cfg[EVENT_START_WATCH].format(**self._msg_params))
        self.output(self._cfg["send_quit_signal"], level=logging.DEBUG)

    def handle_watch_event(self, event):
        """Handle filesystem watch event."""
        self.output(
            self._cfg["process_event"].format(**self._msg_params), level=logging.DEBUG
        )

    def finish_watch(self, changed_file):
        """Handle filesystem watch finish event."""
        if self.watch_data.error_msg:
            self.output(self.watch_data.error_msg)
            return
        self.output(MSG_FILE_CHANGED.format(filename=changed_file))
