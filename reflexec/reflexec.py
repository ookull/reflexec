#!/usr/bin/python3
"""Reflexec main module.
"""

import logging
import queue
import subprocess
import sys
import threading

from . import EXIT_CODE_KBD_INTERRUPT, EXIT_CODE_SIGQUIT, config, signal_handler
from .cli import process_cli_args
from .output import OUTPUT_PLUGINS
from .output.plugin.chained import ChainedOutputPlugin
from .watcher import get_watcher_plugin, watch_fs
from .watcher.kbd_watcher import watch_kbd

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
    key = None  #: Registered character from keyboard (char)

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
        watcher_cfg_section = f"watcher-{self.cfg['watcher']}"
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
                    f"Command finished with error code {returncode}"
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
        self.key = None
        log.debug("Starting watchers")

        event = threading.Event()
        event_queue = queue.Queue()

        log.debug("Creating keyboard watcher thread")
        kbd_watcher_thread = threading.Thread(
            target=watch_kbd,
            args=[event, event_queue],
            daemon=True,
        )
        kbd_watcher_thread.start()

        log.debug("Creating file system watcher thread")
        fs_watcher_thread = threading.Thread(
            target=watch_fs,
            args=[event, event_queue, self.watcher],
            daemon=True,
        )
        fs_watcher_thread.start()

        try:
            log.debug("Waiting for threads")
            event.wait()
        except KeyboardInterrupt:
            log.info("Keyboard interrupt")
        except signal_handler.SigQuitException as err:
            self.changed_file = ""
            self.output.handle_watch_event(err)
        finally:
            event.set()
            try:
                event_name, event_value = event_queue.get_nowait()
                log.debug(
                    "Registered watch event %s with value %r", event_name, event_value
                )
            except queue.Empty:
                event_name, event_value = None, None

            if event_name == "KEYBOARD":
                self.key = event_value
            elif event_name:
                self.changed_file = event_value
            log.debug("Joining threads")
            kbd_watcher_thread.join(timeout=0.2)
            fs_watcher_thread.join(timeout=0)

        # report result
        self.output.finish_watch(self.changed_file, self.key)

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
                        "Reached maximum execution count "
                        f"({self.cfg['max_execs']}), exiting"
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
            if self.key == "Q":  # quit
                self.returncode = 0
                raise StopIteration()
            elif self.key == "R":  # run
                pass
            elif self.changed_file is None:  # keyboard interrupt ^C
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
        " ".join([f"{key}={val}" for key, val in sorted(cli_cfg.items())]),
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
