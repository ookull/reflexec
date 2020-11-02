"""Reflexec feature tests.

Scenario step implementations for Reflexec execution.
"""

import functools
import logging
import os
import shlex
import signal
import subprocess
import time

from behave import given, then, when


@given("Environment variable {name} is set to {value}")
def ensure_env_variable_set(context, name, value):
    """Set environment variable."""
    os.environ[name] = value


@when("Reflexec is executed with options: {options}")
@when("Reflexec is executed with options")
@when("User creates an empty config file using CLI")
def execute_reflexec_with_options(context, options=None):
    """Execute Reflexec with specified options."""
    optlist = shlex.split(options or context.text)
    if optlist and optlist[0] == "reflexec":
        optlist.pop(0)
    cmd = ["reflexec"] + optlist
    logging.info("Executing command %r", " ".join([shlex.quote(arg) for arg in cmd]))

    context.last_run = subprocess.run(
        cmd,
        timeout=3,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        universal_newlines=True,
        preexec_fn=functools.partial(os.chdir, context.test_dir),
    )
    if context.last_run.stdout:
        logging.info("STDOUT:")
        logging.info(context.last_run.stdout)
    if context.last_run.stderr:
        logging.info("STDERR:")
        logging.info(context.last_run.stderr)


@when("Reflexec is executed in background")
def execute_reflexec_in_background(context):
    """Start Reflexec in background."""
    cmd = ["reflexec", "reflexec.ini"]
    logging.info("Executing command %r", " ".join([shlex.quote(arg) for arg in cmd]))
    # pylint: disable=subprocess-popen-preexec-fn
    context.last_run = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        start_new_session=True,
        preexec_fn=functools.partial(os.chdir, context.test_dir),
    )
    context.last_run_stdout = None
    context.last_run_stderr = None


@when("{signal_name} signal is sent to Reflexec")
def send_quit_signal_to_reflexec(context, signal_name):
    """Send QUIT signal to Reflexec process."""
    assert isinstance(context.last_run, subprocess.Popen)
    assert signal_name in ("INT", "QUIT")
    signal_type = signal.SIGQUIT if signal_name == "QUIT" else signal.SIGINT
    context.last_run.send_signal(signal_type)


@then("Command finishes with return code {code:d}")
def check_command_return_code(context, code):
    """Check command return code."""
    if isinstance(context.last_run, subprocess.CompletedProcess):
        returncode = context.last_run.returncode
    else:
        assert isinstance(context.last_run, subprocess.Popen)

        # let the command to finish within 1 second
        for _ in range(0, 10):
            returncode = context.last_run.poll()
            if returncode is not None:
                break
            time.sleep(0.1)

        assert returncode is not None, "Command is not finished {}\n{}{}".format(
            context.last_run.returncode, *context.parse_command_output(context)
        )
    assert returncode == code, "Command finished with return code {}\n{}{}".format(
        context.last_run.returncode, *context.parse_command_output(context)
    )
