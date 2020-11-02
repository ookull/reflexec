"""Reflexec feature tests.

Environmental controls for behave test environment.
"""

import os
import shutil
import subprocess

TEMP_DIR_NAME = "tmp"


def before_all(context):
    """Hook to run before whole shooting match."""
    context.parse_command_output = parse_command_output
    context.test_dir = TEMP_DIR_NAME


def before_scenario(context, scenario):
    """Hook to run before scenario."""
    # create empty directory for temporary data
    if os.path.exists(context.test_dir):
        shutil.rmtree(context.test_dir)
    os.mkdir(context.test_dir)

    # remove last executed command data
    context.last_run = None

    # override system config files
    os.environ["REFLEXEC_CONFIG"] = "reflexec.ini"


def after_all(context):
    """Hook to run after whole shooting match."""
    if not context.failed:
        shutil.rmtree(context.test_dir)


def parse_command_output(context):
    """Get stdout and stderr strings from command output."""

    def escape_chars(src):
        """Replace some ANSI escape sequences with human-readable strings."""
        if not src:
            return ''
        return (
            src.replace("\033[", "<CSI>")
            .replace("\033]", "<OSC>")
            .replace("\033", "<ESC>")
            .replace("\007", "<BEL>")
        )

    if isinstance(context.last_run, subprocess.CompletedProcess):
        return (
            escape_chars(context.last_run.stdout),
            escape_chars(context.last_run.stderr),
        )

    assert isinstance(context.last_run, subprocess.Popen)

    if context.last_run_stdout is None:
        context.last_run_stdout = escape_chars(context.last_run.stdout.read())
        context.last_run_stderr = escape_chars(context.last_run.stderr.read())

    return context.last_run_stdout, context.last_run_stderr
