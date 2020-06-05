#!/usr/bin/python3
"""Reflexec main module.
"""

import logging
import subprocess
import sys

from . import EXIT_CODE_KBD_INTERRUPT, EXIT_CODE_SIGQUIT, config, signal_handler
from .cli import process_cli_args
from .output import OUTPUT_PLUGINS
from .output.plugin.chained import ChainedOutputPlugin
from .watcher import get_watcher_plugin

log = logging.getLogger("reflexec")


class Reflexec:
    """Reflexec main class.

    :param cli_cfg: CLI arguments
    :type cli_cfg: dict
    """

    #: Configuration manager object (:py:class:`reflexec.config.ConfigManager`)
    cfg_mgr = None
    cfg = None  #: Configuration (dict)
    #: Output plugins (:py:class:`reflexec.output.plugin.chained.ChainedOutputPlugin`)
    output = None
    watcher = None  #: Watcher plugin (object)
    returncode = None  #: Reflexec return code (int)
    changed_file = None  #: Name of changed file from watcher (str)

    def __init__(self, cli_cfg):
        self.cfg_mgr = config.ConfigManager(cli_cfg)
        self.load_config()

    def load_config(self):
        """(Re)load reflexec config.

        :raise: StopIteration
        """
        if self.output:  # reload config if some config file is changed
            if not self.cfg_mgr.check_cfg_change():
                return
            log.info("Reloading config...")

        # load config from config files
        cfg = self.cfg_mgr.load_config()
        self.cfg = cfg["main"]

        # change log level if debugging is set in config file but not in CLI
        log.setLevel(logging.DEBUG if self.cfg.get("debug") else logging.INFO)

        # initialize output plugins
        if "debug" in cfg["main"]:
            cfg["output"]["debug"] = cfg["main"]["debug"]
        self.output = ChainedOutputPlugin(cmd_name=self.cfg["name"], cfg=cfg["output"])
        self.output.add_plugins(self.cfg["output"], OUTPUT_PLUGINS)

        # initialize watcher plugin
        watcher_cfg_section = "watcher-{}".format(self.cfg["watcher"])
        watcher_cfg = cfg["watcher"].get(watcher_cfg_section, {})
        try:
            self.watcher = get_watcher_plugin(
                plugin_name=self.cfg["watcher"],
                patterns=self.cfg["watch"],
                output=self.output,
                cfg=watcher_cfg,
            )
        except SystemExit as err:
            log.error(
                "Cannot load watcher plugin, exiting with error code %d", err.code
            )
            sys.exit(err.code)

    def exec_cmd(self):
        """Execute command.

        :return: Command exit code
        :rtype: int
        """
        # prepare
        command = [
            _.replace("{changed_file}", self.changed_file or "")
            for _ in self.cfg["command"] or []
        ]
        self.output.start_exec(command)

        # execute command
        returncode = None
        exec_msg = None
        if command:
            try:
                returncode = subprocess.run(command, check=False).returncode
            except FileNotFoundError:
                exec_msg = "Command not found"
                returncode = -1
            except KeyboardInterrupt:
                exec_msg = "Keyboard interrupt"
                returncode = EXIT_CODE_KBD_INTERRUPT
            except signal_handler.SigQuitException:
                exec_msg = "Got QUIT signal"
                returncode = EXIT_CODE_SIGQUIT
            except OSError as err:
                exec_msg = err.strerror
                returncode = -1
            else:
                exec_msg = (
                    "Command finished with error code {}".format(returncode)
                    if returncode
                    else "Command finished successfully"
                )
            log.debug(exec_msg)
        else:
            exec_msg = "No command specified"
            log.info(exec_msg)

        # report result
        self.output.finish_exec(returncode, exec_msg)

        # post execution delay
        try:
            self.output.post_exec_delay(self.cfg["delay"])
        except signal_handler.SigQuitException:
            pass

        return returncode

    def watch(self):
        """Watch file system events."""
        self.output.start_watch(self.cfg["watch"])

        # watch
        self.changed_file = None
        log.debug("Starting watcher")
        try:
            self.watcher.watch()
            log.debug("Watcher finished")
        except signal_handler.SigQuitException as err:
            self.changed_file = ""
            self.output.handle_watch_event(err)
        except StopIteration as err:
            event, self.changed_file = str(err.value).split(":", 1)
            log.debug("Detected event %s for file %s", event, self.changed_file)
        finally:
            # stop notifier
            self.watcher.stop()

        # report result
        self.output.finish_watch(self.changed_file)

    def loop(self):
        """Main loop."""
        log.debug("Starting main loop with %s", self.cfg["start"])
        can_execute = self.cfg["start"] == "exec"
        limited_exec_count = self.cfg["max_execs"] > 0
        while self.returncode is None:
            returncode = None
            if can_execute:
                # execute command
                try:
                    returncode = self.exec_cmd()
                except KeyboardInterrupt:
                    sys.stderr.write("\nKeyboardInterrupt\n")
                    self.returncode = EXIT_CODE_KBD_INTERRUPT
                    raise StopIteration()
                if (
                    limited_exec_count
                    and self.output.exec_data.count >= self.cfg["max_execs"]
                ):
                    self.output.output(
                        "Reached maximum execution count ({}), exiting".format(
                            self.cfg["max_execs"]
                        )
                    )
                    self.returncode = 1 if returncode else 0
                    raise StopIteration()

                self.load_config()
            else:
                can_execute = True

            if not self.cfg["watch"]:
                if not limited_exec_count:
                    self.returncode = 1 if returncode else 0
                    raise StopIteration()
                continue

            # start watcher
            self.watch()
            if self.changed_file is None:  # keyboard interrupt ^C
                self.returncode = EXIT_CODE_KBD_INTERRUPT
                raise StopIteration()

            self.load_config()


def main():
    """Trigger COMMAND execution on file system events."""
    # parse and validate CLI arguments
    try:
        cli_cfg = process_cli_args()
    except ValueError as err:
        log.error(err)
        sys.exit(2)
    except OSError as err:
        log.error(err)
        sys.exit(3)

    # set logging config
    logging.basicConfig(
        format="{levelname}: {message}",
        style="{",
        level="DEBUG" if cli_cfg.get("debug") else "INFO",
    )
    log.debug(
        "CLI args: %s",
        " ".join(["{}={}".format(*arg) for arg in sorted(cli_cfg.items())]),
    )

    signal_handler.set_quit_signal_handler()

    # run reflexec
    reflexec = Reflexec(cli_cfg)
    try:
        reflexec.loop()
    except signal_handler.SigQuitException:
        log.warning("Got QUIT signal")
        sys.exit(1)
    except KeyboardInterrupt:
        log.info("Keyboard interrupt")
        sys.exit(1)
    except StopIteration:
        pass
    sys.exit(reflexec.returncode)


if __name__ == "__main__":
    main()
