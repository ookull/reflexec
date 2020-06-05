"""Reflexec terminal output plugins module.

.. autoclass:: ClearTerminalOutputPlugin
   :members: cfg, name
   :show-inheritance:

.. autoclass:: ColorTerminalOutputPlugin
   :members: cfg, name
   :show-inheritance:
"""


from .. import ansi
from .base import (
    EVENT_FINISH_DELAY,
    EVENT_FINISH_WATCH,
    EVENT_START_DELAY,
    EVENT_START_EXEC,
    EVENT_START_WATCH,
    MSG_FILE_CHANGED,
    MSG_PROCESSING_EVENT,
    MSG_SEND_QUIT_SIGNAL,
    OutputPlugin,
    log,
)


class ClearTerminalOutputPlugin(OutputPlugin):
    """Clear terminal output plugin.

    Clear terminal after configuration loading and after file change.
    """

    name = "clear"  #: Plugin name
    __descr__ = "Clear terminal after configuration loading and after file change"

    def __init__(self, cmd_name, cfg):
        super().__init__(cmd_name, cfg)
        print(ansi.clear_screen(), flush=True)

    def finish_watch(self, changed_file):
        """Handle filesystem watch finish event."""
        if changed_file is not None:  # don't clear on keyboard interrupt
            print(ansi.clear_screen(), flush=True)


class ColorTerminalOutputPlugin(OutputPlugin):
    """Color terminal output plugin.

    Output fancy event info to stdout. Terminal must support colors.
    """

    name = "colorterm"  #: Plugin name
    __descr__ = "Colored output to stdout"
    #: standard set of formatting arguments for output templates
    _fmt_args = None
    #: Plugin default configuration
    cfg = {
        # start execution
        EVENT_START_EXEC: "{style.reset_all}{bg.yellow}{fg.black}{start_time:%H:%M:%S}"
        "{bg.cyan} #{exec_count} "
        "{bg.white}{style.dim}{fg.blue} Starting {fg.black}{cmd_name}"
        "{clear_eol}{style.reset_all}",
        # execution finished successfully
        "finish_exec_success": "{style.reset_all}{bg.yellow}{fg.black}{finish_time:%H:%M:%S}"
        "{bg.cyan} #{exec_count} "
        "{bg.green}{fg.black} "
        "Duration {style.bright}{fg.white}{duration_str}"
        "{style.bright}{fg.yellow} | {style.normal}"
        "{fg.black}No error"
        "{style.bright}{fg.yellow} | {style.normal}"
        "{fg.black}{cmd_name}"
        "{clear_eol}{style.reset_all}",
        # execution finished with error
        "finish_exec_error": "{style.reset_all}{bg.yellow}{fg.black}{finish_time:%H:%M:%S}"
        "{bg.cyan} #{exec_count} "
        "{bg.red}{fg.white} "
        "Duration {style.bright}{duration_str}"
        "{style.bright}{fg.yellow} | {style.normal}"
        "{fg.white}{error_msg}"
        "{style.bright}{fg.yellow} | {style.normal}"
        "{fg.black}{cmd_name}"
        "{clear_eol}{style.reset_all}",
        # delay message
        EVENT_START_DELAY: "{cr}{bg.blue}{fg.white}{style.bright}Paused for {delay} seconds... "
        "{clear_eol}{style.reset_all}",
        # finish delay
        EVENT_FINISH_DELAY: "{cr}{clear_eol}",
        # start watching
        EVENT_START_WATCH: "{bg.lightblack}{fg.yellow}{style.bright}"
        "{cr}Waiting... "
        "{fg.white}{style.dim}"
        + MSG_SEND_QUIT_SIGNAL
        + " {clear_eol}{style.reset_all}",
        # changed file name from watcher
        EVENT_FINISH_WATCH: "{cr}{fg.yellow}"
        + MSG_FILE_CHANGED
        + "{style.reset_all}{clear_eol}",
        # notification message
        "notification": "\n{bg.black}{fg.red}{style.bright}"
        "{msg}"
        "{clear_eol}{style.reset_all}",
        # handle event (debug message)
        "process_event": "{cr}" + MSG_PROCESSING_EVENT + "{clear_eol}",
    }

    def __init__(self, cmd_name, cfg):
        self._fmt_args = {
            "fg": ansi.AnsiFore(),
            "bg": ansi.AnsiBack(),
            "style": ansi.AnsiStyle(),
            "clear_eol": ansi.clear_line(0),
            # ASCII control codes
            "tab": "\011",
            "lf": "\012",
            "cr": "\015",
        }
        # make ASCII characters available using codes (e.g. \007 for BEL)
        self._fmt_args.update(
            [["\\{:03d}".format(code), chr(code)] for code in range(0, 256)]
        )
        super().__init__(cmd_name, cfg)

    def set_msg_params(self, **kw):
        """Set params for output messages."""
        super().set_msg_params(**kw)
        self._msg_params.update(self._fmt_args)

    def output(self, *args, **kw):
        """Format and output message."""
        msg = args[0]
        if kw.pop("debug", False):
            if not self.cfg.get("debug"):
                return
            msg = (
                "{bg.black}{fg.cyan}{style.bright}DEBUG[{name}]: {msg}{clear_eol}"
            ).format(name=self.name, msg=msg, **self._fmt_args)
        print(msg, end=kw.get("_end", "\n"), flush=True)

    def output_fmt(self, event, fmt_params=None, **kw):
        """Format and output message from config."""
        fmt_params = fmt_params or {}
        msg = self._cfg[event].replace("\n", "")
        try:
            self.output(msg.format(**self._msg_params, **fmt_params), **kw)
        except AttributeError as err:
            log.error(
                "Error while formatting '%s' message for output plugin '%s': %s ",
                event,
                self.name,
                err,
            )

    def start_exec(self, cmd):
        """Handle command execution start event."""
        self.output_fmt(EVENT_START_EXEC)

    def finish_exec(self, returncode, exec_msg):
        """Handle command execution finish event."""
        if returncode:
            if returncode < 0:
                self.output_fmt("notification", fmt_params={"msg": exec_msg})
            template_name = "finish_exec_error"
            error_msg = (
                exec_msg
                if returncode == -1
                else "Error code {style.bright}{returncode}".format(
                    returncode=returncode, **self._fmt_args
                )
            )
        else:
            template_name = "finish_exec_success"
            error_msg = None

        self.output_fmt(template_name, fmt_params={"error_msg": error_msg})

    def start_delay(self, delay):
        """Start post exec delay."""
        self.update_delay(delay)

    def update_delay(self, delay):
        """Output delay message."""
        self.output_fmt(EVENT_START_DELAY, _end="")

    def finish_delay(self):
        """Finish post exec delay."""
        self.output_fmt(EVENT_FINISH_DELAY, _end="")

    def start_watch(self, patterns):
        """Handle filesystem watch start event."""
        self.output_fmt(EVENT_START_WATCH, _end="")

    def handle_watch_event(self, event):
        """Handle filesystem watch event."""
        if self.cfg.get("debug"):
            self.output("\n", _end="")
        self.output_fmt("process_event", debug=True)

    def finish_watch(self, changed_file):
        """Handle filesystem watch finish event."""
        if self.watch_data.error_msg:
            self.output_fmt(
                "notification", fmt_params={"msg": self.watch_data.error_msg}
            )
            return
        self.output_fmt(EVENT_FINISH_WATCH)
