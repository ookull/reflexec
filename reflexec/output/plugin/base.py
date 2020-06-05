"""Reflexec output plugins base.
"""

import logging

from ..helpers import ExecData, WatchData

log = logging.getLogger("reflexec")

# MAIN LOOP EVENTS
#: Command execution start event
EVENT_START_EXEC = "start_exec"
#: Command execution finish event
EVENT_FINISH_EXEC = "finish_exec"
#: Post exec pause start event
EVENT_START_DELAY = "start_delay"
#: Post exec pause update event
EVENT_UPDATE_DELAY = "update_delay"
#: Post exec pause finish event
EVENT_FINISH_DELAY = "finish_delay"
#: Filesystem watch start event
EVENT_START_WATCH = "start_watch"
#: Filesystem watcher event
EVENT_HANDLE_WATCH_EVENT = "handle_watch_event"
#: Filesystem watch finish event
EVENT_FINISH_WATCH = "finish_watch"
#: All main loop events
MAIN_LOOP_EVENTS = {
    EVENT_START_EXEC,
    EVENT_FINISH_EXEC,
    EVENT_START_DELAY,
    EVENT_UPDATE_DELAY,
    EVENT_FINISH_DELAY,
    EVENT_START_WATCH,
    EVENT_HANDLE_WATCH_EVENT,
    EVENT_FINISH_WATCH,
}

# MESSAGE EVENTS
#: Standard message for starting reflexec instance
MSG_START_REFLEXEC = "Starting reflexec instance: {cmd_name}"
#: Standard message for execution start
MSG_START_EXEC = "Executing command (round #{exec_count}): {command}"
#: Standard message for execution finish
MSG_FINISH_EXEC = "Duration of round #{exec_count}: {duration_str}"
#: Standard message for post-execution delay
MSG_DELAY = "Pause {delay} seconds"
#: Standard message for watcher start
MSG_START_WATCH = "Starting watcher for filesystem patterns"
#: Standard message for file change event
MSG_FILE_CHANGED = "Changed file: {filename}"
#: Standard message to instruct user sending QUIT signal using keyboard
MSG_SEND_QUIT_SIGNAL = "Send QUIT signal (press ^\\) to force execution"
#: Standard message for event processing
MSG_PROCESSING_EVENT = "Processing event: {event}"


class OutputPlugin:
    """Base class for all output plugins."""

    name = None  #: Plugin name
    __descr__ = None  #: Plugin description
    #: Watcher data (:py:class:`reflexec.output.helpers.WatchData`)
    watch_data = WatchData()
    #: Executor data (:py:class:`reflexec.output.helpers.ExecData`)
    exec_data = ExecData()
    cmd_name = None  #: Command display name
    _msg_params = None  #: Parameters store for current output message
    cfg = {}  #: Plugin default configuration

    def __init__(self, cmd_name, cfg):
        self.cmd_name = cmd_name
        self._cfg = self.cfg
        self._cfg.update(cfg)
        self.set_msg_params()

    def set_msg_params(self, **kw):
        """Set params for output messages."""
        self._msg_params = {
            "cmd_name": self.cmd_name,
            "exec_count": self.exec_data.count,
            "start_time": self.stats["exec"]["start_time"],
            "finish_time": self.stats["exec"]["finish_time"],
            "duration": self.exec_data.duration_dict,
            "duration_str": self.exec_data.duration_str,
        }
        self._msg_params.update(kw)

    def output(self, *args, **kw):
        """Standard output method."""

    @property
    def stats(self):
        """Watch and execution stats as dict."""
        return dict(watch=self.watch_data.as_dict, exec=self.exec_data.as_dict)

    def start_exec(self, cmd):
        """Handle command execution start event."""

    def finish_exec(self, returncode, exec_msg):
        """Handle command execution finish event."""

    def start_delay(self, delay):
        """Start post exec delay."""

    def update_delay(self, delay):
        """Update post exec delay."""

    def finish_delay(self):
        """Finish post exec delay."""

    def start_watch(self, patterns):
        """Handle filesystem watch start event."""

    def handle_watch_event(self, event):
        """Handle filesystem watch event."""

    def finish_watch(self, changed_file):
        """Handle filesystem watch finish event."""
