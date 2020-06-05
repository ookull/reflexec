"""Reflexec command line parsing module.
"""

import argparse
import os
import shlex
import sys

from . import __version__
from .config.writer import write_config_file
from .output import OUTPUT_PLUGINS
from .watcher import WATCHER_PLUGINS


def validate_cli_args(args):
    """Validate CLI args."""
    # validate output plugins
    if args.get("output"):
        # convert output plugin args to single list of plugins
        output_plugins = []
        for plugin_names in args["output"]:
            output_plugins += plugin_names.split(",")
        args["output"] = output_plugins

    # try to handle single command as config file name
    if (
        "config_file" not in args
        and len(args.get("command", [])) == 1
        and os.path.exists(args["command"][0])
    ):
        args["config_file"] = args["command"][0]
        del args["command"]

    if args.get("max_execs", 0) < 0:
        raise ValueError("Negative value is not allowed for --max-execs")


def list_plugins():
    """Output list of output plugins."""
    print("Output plugins:")
    msg = " {name:>%d} - {descr}" % max(len(plugin) for plugin in OUTPUT_PLUGINS)
    for plugin_name, plugin in sorted(OUTPUT_PLUGINS.items()):
        print(msg.format(name=plugin_name, descr=plugin.__descr__))

    print()
    print("Watcher plugins:")
    msg = " {name:>%d} - {descr}" % max(len(plugin) for plugin in WATCHER_PLUGINS)
    for plugin_name, plugin in sorted(WATCHER_PLUGINS.items()):
        print(msg.format(name=plugin_name, descr=plugin.__descr__))


def parse_cli_args():
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Reflect file change with command execution."
    )
    parser.add_argument("command", nargs="?", help="command to execute")
    parser.add_argument("arg", nargs="*", help="arguments for command")
    parser.add_argument(
        "-n", "--name", help="command display name (Default: command)",
    )
    parser.add_argument(
        "-w",
        "--watch",
        default=[],
        action="append",
        help=(
            "Unix style pattern(s) to specify files to watch. "
            "Can be used multiple times. (Default: \*)"
        ),
    )
    parser.add_argument(
        "-W", "--watcher", help="set watcher plugin (Default: autodetect)"
    )
    parser.add_argument(
        "-o",
        "--output",
        default=[],
        action="append",
        help=(
            "set output plugin. Can be used multiple times. "
            "Comma separated list is allowed."
        ),
    )
    parser.add_argument(
        "-d",
        "--delay",
        type=float,
        help="pause length after command execution (Default: 0)",
    )
    parser.add_argument(
        "-s",
        "--start",
        choices=["exec", "watch"],
        help="start with specified action (Default: exec)",
    )
    parser.add_argument(
        "-m",
        "--max-execs",
        type=int,
        help="maximum count of command executions (Default: 0 == unlimited)",
    )
    parser.add_argument("-c", "--config-file", help="Specify config file")
    parser.add_argument(
        "--write-config",
        action="store_true",
        help="convert CLI arguments to config file and exit",
    )
    parser.add_argument(
        "-l",
        "--list-plugins",
        action="store_true",
        help="output list of output plugins and exit",
    )
    parser.add_argument("--debug", action="store_true", help="set debug mode")
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    args = parser.parse_args()
    if args.list_plugins:
        list_plugins()
        sys.exit(0)

    return {
        "command": tuple([args.command] + args.arg) if args.command else tuple(),
        "config_file": args.config_file,
        "debug": args.debug,
        "delay": args.delay,
        "max_execs": args.max_execs,
        "name": args.name,
        "output": tuple(args.output),
        "start": args.start,
        "watch": tuple(args.watch),
        "watcher": args.watcher,
        "write_config": args.write_config,
    }


def process_cli_args():
    """Process CLI arguments and generate config from CLI options and args.

    :param args: CLI arguments
    :type args: dict
    :return: Config values Empty dict if
    :rtype: dict
    :raises SystemExit: if options require process exit
    """
    args = parse_cli_args()

    # delete empty args
    if not args["debug"]:
        del args["debug"]
    for arg_name in list(args.keys()):
        if args[arg_name] in [None, tuple()]:
            del args[arg_name]

    # validate
    validate_cli_args(args)

    # --write-config
    if args.pop("write_config"):
        config_values = {}
        if args.get("command"):
            config_values["command"] = " ".join(
                shlex.quote(subval) for subval in args["command"]
            )
        if args.get("watch"):
            config_values["watch"] = "\n".join(args["watch"])
        if args.get("output"):
            config_values["output"] = ", ".join(args["output"])
        for arg_name in ["delay", "max_execs", "name", "start", "watcher"]:
            if arg_name in args:
                config_values[arg_name] = args[arg_name]

        write_config_file(args, config_values)
        sys.exit(0)

    return args
