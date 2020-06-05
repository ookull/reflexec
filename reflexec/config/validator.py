"""Reflexec config validator module.
"""

import logging
import shlex
from distutils.util import strtobool

log = logging.getLogger("reflexec")


def validate_config_value(key, cfg):
    """Validate config value."""
    if key not in cfg:
        return
    validator_fn = globals()["validate_{}".format(key)]
    value = cfg[key]
    try:
        value = validator_fn(value)
    except ValueError as err:
        del cfg[key]
        raise ValueError(
            'Invalid value "{}" for parameter "{}": {}'.format(value, key, err)
        )
    if value is None:
        del cfg[key]
    else:
        cfg[key] = value


def validate_debug(value):
    """Validate "debug" parameter."""
    if isinstance(value, str):
        value = strtobool(value)
    return bool(value)


def validate_command(value):
    """Validate "command" parameter."""
    if isinstance(value, str):
        value = shlex.split(value)
    return list(value)


def validate_name(value):
    """Validate "name" parameter."""
    assert isinstance(value, str)
    return value


def validate_delay(value):
    """Validate "delay" parameter."""
    try:
        value = float(value)
        if int(value) == value:
            value = int(value)
    except ValueError:
        raise ValueError("Must be float")

    if value < 0:
        raise ValueError("Negative value is not allowed")

    return value


def validate_output(value):
    """Validate "output" parameter."""
    if value is not None:
        if isinstance(value, str):
            value = value.split(",")
        # filter out empty names
        value = list(filter(None, value))
    return value


def validate_start(value):
    """Validate "start" parameter."""
    if value not in ("watch", "exec"):
        raise ValueError('Must be "exec" or "watch"')
    return value


def validate_watcher(value):
    """Validate "watcher" parameter."""
    assert isinstance(value, str)
    return value


def validate_type(value):
    """Validate "type" parameter."""
    if value not in ("default", "command"):
        raise ValueError('Must be "default" or "command"')
    return value


def validate_watch(value):
    """Validate "watch" parameter."""
    if not value:
        return None
    if isinstance(value, str):
        value = [_ for _ in value.split("\n") if _]
    return value


def validate_max_execs(value):
    """Validate "max_execs" parameter."""
    try:
        value = int(value)
    except ValueError:
        raise ValueError("Must be integer")

    if value < 0:
        raise ValueError("Negative value is not allowed")

    return value
