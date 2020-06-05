"""Reflexec command output plugins module.

.. autoclass:: CommandOutputPlugin
   :members: cfg, name
   :show-inheritance:
"""

import shlex
import subprocess

from .base import EVENT_START_EXEC, OutputPlugin, log


class CommandOutputPlugin(OutputPlugin):
    """Command output plugin.

    Execute specified command if main command is finished. By default
    ``notify-send`` is used to generate desktop notifications.
    """

    name = "command"  #: Plugin name
    __descr__ = "Execute specified command"
    #: Plugin default configuration
    cfg = {
        # start execution
        EVENT_START_EXEC: "",
        # execution finished successfully
        "finish_exec_success": 'notify-send --expire-time=10000 --icon=face-smile "{cmd_name}" '
        '"#{exec_count} finished successfully\n'
        'Duration: {duration_str}"',
        # execution finished with error
        "finish_exec_error": 'notify-send --expire-time=10000 --icon=error "{cmd_name}" '
        '"#{exec_count} finished with error code {returncode}\n'
        'Duration: {duration_str}"',
    }

    def exec_cmd(self, event):
        """Execute command."""
        cmd = self.cfg[event]
        if cmd:
            cmd = cmd.format(**self._msg_params)
            try:
                subprocess.run(shlex.split(cmd), check=True)
            except OSError as err:
                log.error(
                    'Error while executing command for event "%s": %s',
                    event,
                    err.strerror,
                )

    def start_exec(self, cmd):
        """Handle command execution start event."""
        self.exec_cmd(EVENT_START_EXEC)

    def finish_exec(self, returncode, exec_msg):
        """Handle command execution finish event."""
        self.exec_cmd("finish_exec_error" if returncode else "finish_exec_success")
