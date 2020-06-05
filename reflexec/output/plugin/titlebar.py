"""Reflexec terminal titlebar output plugins module.

.. autoclass:: TerminalTitleOutputPlugin
   :members: cfg, name
   :show-inheritance:

.. autoclass:: FancyTerminalTitleOutputPlugin
   :members: cfg, name
   :show-inheritance:
"""

from .. import ansi
from .base import (
    EVENT_FINISH_EXEC,
    EVENT_START_DELAY,
    EVENT_START_EXEC,
    EVENT_START_WATCH,
    MSG_PROCESSING_EVENT,
    OutputPlugin,
)


class TerminalTitleOutputPlugin(OutputPlugin):
    """Terminal title bar output plugin.

    Modify terminal titlebar with escape sequences.
    """

    name = "titlebar"  #: Plugin name
    __descr__ = "Output status to terminal title bar"
    #: Plugin default configuration
    cfg = {
        "exit_str_success": "+",
        "exit_str_error": "!",
        EVENT_START_EXEC: "> {start_time:%H:%M:%S} #{exec_count} | {cmd_name}",
        EVENT_FINISH_EXEC: "F {exit_status} {duration_str} #{exec_count} | {cmd_name}",
        EVENT_START_DELAY: "P {exit_status} {duration_str} #{exec_count} | {cmd_name}",
        EVENT_START_WATCH: "W {exit_status} {duration_str} #{exec_count} | {cmd_name}",
    }

    @property
    def _exit_str(self):
        """Status string for command exit status."""
        return (
            self._cfg["exit_str_error"]
            if self.exec_data.exit_status_code
            else self._cfg["exit_str_success"]
        )

    def output(self, *args, **kw):
        """Standard output method."""
        if len(args) == 1 and args[0] in self._cfg:
            msg = self._cfg[args[0]].format(
                **self._msg_params, **self._cfg, exit_status=self._exit_str
            )
            print(ansi.set_title(msg), end="", flush=True)
            return

        if kw.pop("debug", False):
            if self.cfg.get("debug"):
                print("DEBUG[{}]: ".format(self.name), *args, **kw, flush=True)
            return

        print(ansi.set_title(" ".join(args)), end="", flush=True)

    def start_exec(self, cmd):
        """Handle command execution start event."""
        self.output(EVENT_START_EXEC)

    def finish_exec(self, returncode, exec_msg):
        """Handle command execution finish event."""
        self.output(EVENT_FINISH_EXEC)

    def start_delay(self, delay):
        """Start post exec delay."""
        self.update_delay(delay)

    def update_delay(self, delay):
        """Output delay message."""
        self.output(EVENT_START_DELAY)

    def finish_delay(self):
        """Finish post exec delay."""
        self.update_delay(0)

    def start_watch(self, patterns):
        """Handle filesystem watch start event."""
        self.output(EVENT_START_WATCH)

    def handle_watch_event(self, event):
        """Handle filesystem watch event."""
        self.output(MSG_PROCESSING_EVENT.format(event=event), debug=True)


class FancyTerminalTitleOutputPlugin(TerminalTitleOutputPlugin):
    """Fancy terminal title bar output plugin with UTF characters.

    Modify terminal titlebar with escape sequences.
    """

    name = "fancytitlebar"  #: Plugin name
    __descr__ = "Output fancy status to terminal title bar"
    #: Plugin default configuration
    cfg = {
        # U+2714 HEAVY CHECK MARK
        "exit_str_success": "\\xE2\\x9c\\x94",
        "exit_str_error": "!",
        EVENT_START_EXEC:
        # U+23F5 BLACK MEDIUM RIGHT-POINTING TRIANGLE
        "\\xE2\\x8F\\xB5 {start_time:%H:%M:%S} #{exec_count} "
        # U+2506 BOX DRAWINGS LIGHT TRIPLE DASH VERTICAL
        "\\xE2\\x94\\x86 {cmd_name}",
        EVENT_FINISH_EXEC:
        # U+1F3C1 CHEQUERED FLAG
        "\\xF0\\x9F\\x8F\\x81 {exit_status} {duration_str} #{exec_count} "
        # U+2506 BOX DRAWINGS LIGHT TRIPLE DASH VERTICAL
        "\\xE2\\x94\\x86 {cmd_name}",
        EVENT_START_DELAY:
        # U+23F8 DOUBLE VERTICAL BAR
        "\\xE2\\x8F\\xB8 {exit_status} {duration_str} #{exec_count} "
        # U+2506 BOX DRAWINGS LIGHT TRIPLE DASH VERTICAL
        "\\xE2\\x94\\x86 {cmd_name}",
        EVENT_START_WATCH:
        # U+23F9 BLACK SQUARE FOR STOP
        "\\xE2\\x8f\\xb9{exit_status} {duration_str} #{exec_count} "
        # U+2506 BOX DRAWINGS LIGHT TRIPLE DASH VERTICAL
        "\\xE2\\x94\\x86 {cmd_name}",
    }

    def __init__(self, cmd_name, cfg):
        """Constructor."""
        super().__init__(cmd_name, cfg)
        for key in self._cfg:
            self._cfg[key] = self._escape_utf8_str(self._cfg[key])

    @classmethod
    def _escape_utf8_str(cls, src_str):
        retval = bytes()
        pos = 0
        while pos < len(src_str):
            char = src_str[pos]
            pos += 1
            if char != "\\":
                retval += bytes(char, "UTF-8")
            else:
                assert src_str[pos] == "x"
                retval += bytes.fromhex(src_str[pos + 1 : pos + 3])
                pos += 3
            continue

        return retval.decode("UTF-8")
