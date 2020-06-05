"""Reflexec config management module.
"""

import configparser
import logging
import os
from collections import OrderedDict

from .. import CONFIG_FILES, CONFIG_FILES_ENV_VAR
from .validator import validate_config_value
from .watch_config import WatchPatternCollection

log = logging.getLogger("reflexec")

#: Config parameter default values (list of [name, value] pairs)
DEFAULT_CONFIG = [
    ["name", None],
    ["start", "exec"],
    ["type", "default"],
    ["watch", None],
    ["watcher", "autodetect"],
    ["delay", 0],
    ["max_execs", 0],
    ["output", ["default"]],
    ["command", None],
]
#: Known config parameters
KNOWN_CONFIG_KEYS = [_[0] for _ in DEFAULT_CONFIG] + ["debug"]
#: Main secion name in config file
CONFIG_SECTION = "reflexec"


class ConfigManager:
    """Configuration manager.

    :param cli_cfg: CLI arguments
    :type cli_cfg: dict
    """

    _cli_cfg = None  #: CLI arguments with values (dict)
    _cfg_files = None  #: Config file paths (list)
    #: Timestamps to register last change of config file (dict)
    _cfg_timestamps = None

    def __init__(self, cli_cfg):
        self._cli_cfg = cli_cfg
        if CONFIG_FILES_ENV_VAR in os.environ:
            log.debug(
                "Use environment variable %s for config files", CONFIG_FILES_ENV_VAR
            )
            self._cfg_files = list(
                filter(None, os.environ.get(CONFIG_FILES_ENV_VAR).split(":"))
            )
        else:
            self._cfg_files = CONFIG_FILES
            if cli_cfg.get("config_file"):
                self._cfg_files[-1] = cli_cfg["config_file"]
        log.debug("Config files: %s", ", ".join(self._cfg_files))

    def load_config(self):
        """Load and validate config."""
        cfg, self._cfg_timestamps = load_cfg_files(self._cfg_files)
        cfg["main"][""] = self._cli_cfg.copy()
        consolidate_config(cfg)
        validate_config(cfg)

        # set command display name if not specified
        cfg["main"].setdefault(
            "name", " ".join(cfg["main"].get("command", ["No command"]))
        )

        # watch patterns
        if cfg["main"].get("watch") in [None, [""]]:
            log.info(
                "No watches defined, using shell pattern * "
                "to watch all files in current directory"
            )
            cfg["main"]["watch"] = ["*"]
        cfg["main"]["watch"] = [
            WatchPatternCollection(
                cfg["main"]["watch"], pattern_type=cfg["main"].get("type", "default")
            )
        ]

        # add config files to watch patterns
        if cfg["main"]["watch"] or cfg.get("max_execs") == 0:
            for filepath in self._cfg_files:
                if os.path.exists(filepath):
                    log.debug("Adding config file %s to watch patterns", filepath)
                    cfg["main"]["watch"].append(
                        WatchPatternCollection(patterns=[filepath])
                    )

        # max_execs
        if cfg["main"].get("max_execs") is None and not cfg["main"]["watch"]:
            log.debug("No watches and max_execs set, setting max_execs to 1")
            cfg["main"]["max_execs"] = 1

        # set default values
        for key, val in DEFAULT_CONFIG:
            if key not in cfg["main"]:
                cfg["main"][key] = val

        return cfg

    def check_cfg_change(self):
        """Check config file change.

        :return: True if any config file is changed
        :rtype: bool
        """
        for filepath, timestamp in self._cfg_timestamps.items():
            try:
                if timestamp and os.stat(filepath).st_mtime != timestamp:
                    log.info("Detected config file change (%s)", filepath)
                    return True
            except OSError:
                pass
        return False


def load_cfg_files(cfg_files):
    """Load config from config files."""
    cfg = {"main": OrderedDict(), "output": {}, "watcher": {}}
    cfg_timestamps = {}

    for filepath in cfg_files:
        cfg_timestamps[filepath] = None
        actual_filepath = os.path.expanduser(filepath)
        if not os.path.exists(actual_filepath):
            log.debug("Config file %s does not exist", filepath)
            continue

        # read config from file
        log.debug('Reading config file "%s"', filepath)
        try:
            config_parser = get_config_parser(actual_filepath)
        except OSError as err:
            log.error("Error while reading config file %s: %s", filepath, err.strerror)
        except configparser.Error as err:
            log.error("Error while reading config file %s: %s", filepath, err)
        except UnicodeDecodeError as err:
            log.error("Error while decoding config file %s: %s", filepath, err)
        else:
            cfg["main"][filepath] = read_config_file_main_section(
                config_parser, filepath
            )
            for section_name in config_parser.sections():
                if section_name == "reflexec":
                    continue
                if not section_name.startswith(("output-", "watcher-")):
                    log.debug("Skipping unknown config section [%s]", section_name)
                    continue
                if not config_parser[section_name]:
                    log.debug("Skipping empty config section [%s]", section_name)
                    continue
                load_config_section(section_name, cfg, filepath, config_parser)

        # register config file timestamp
        try:
            cfg_timestamps[filepath] = os.stat(actual_filepath).st_mtime
        except OSError as err:
            log.debug("Error while reading stat for config file %s: %s", filepath, err)

    return cfg, cfg_timestamps


def load_config_section(section_name, cfg, filepath, config_parser):
    """Load config section."""
    log.debug("Parsing section [%s]", section_name)
    section_type, plugin_name = section_name.split("-", 1)
    cfg[section_type].setdefault(plugin_name, {})
    try:
        cfg[section_type][plugin_name].update(config_parser[section_name])
    except configparser.Error as err:
        log.error(
            "Error while parsing section [%s] in config file %s: %s",
            section_name,
            filepath,
            err,
        )
    for key, val in cfg[section_type][plugin_name].items():
        log.debug("Loaded config value %s=%s", key, val)


def consolidate_config(cfg):
    """Consolidate configuration."""
    log.debug("Consolidating config values")

    main_cfg = {}
    for key in KNOWN_CONFIG_KEYS:
        for filepath in cfg["main"].keys():
            if key in cfg["main"][filepath]:
                main_cfg[key] = cfg["main"][filepath][key]

    cfg["main"] = main_cfg


def validate_config(cfg):
    """Validate configuration."""
    log.debug("Validating config values")
    for key in KNOWN_CONFIG_KEYS:
        try:
            validate_config_value(key, cfg["main"])
        except ValueError as err:
            log.error(err)


def get_config_parser(filepath):
    """Create parser for config file.

    :param filepath: Config file path
    :type filepath: str
    :return: configparser.ConfigParser instance
    """
    config_parser = configparser.ConfigParser(interpolation=None)
    # use read_file() instead of read() to catch possible OSError
    with open(filepath) as cfg_file:
        config_parser.read_file(cfg_file)

    return config_parser


def read_config_file_main_section(config_parser, filepath):
    """Read config main section [reflexec] from config file."""
    cfg = {}

    if CONFIG_SECTION not in config_parser:
        log.error("Config file %s does not have section [%s]", filepath, CONFIG_SECTION)
        return cfg

    log.debug("Parsing section [%s]", CONFIG_SECTION)
    for key in config_parser[CONFIG_SECTION].keys():
        if key not in KNOWN_CONFIG_KEYS:
            log.error('Unknown config key "%s" in section [%s]', key, CONFIG_SECTION)
            continue

        cfg[key] = config_parser.get(CONFIG_SECTION, key)
        try:
            validate_config_value(key, cfg)
        except ValueError as err:
            log.error("Error while parsing config file %s: %s", filepath, err)
            continue

        quoted_value = (
            cfg[key].replace("\n", " ") if isinstance(cfg[key], str) else cfg[key]
        )
        log.debug("Loaded config value %s=%s", key, quoted_value)

    return cfg
