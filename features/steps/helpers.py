"""Reflexec feature tests.

Scenario step implementations for simple helpers.
"""

import logging
import os
import subprocess
import time

from behave import given, then, when


@given('Directory "{dirname}" exist with RO permissions')
def create_directory(context, dirname):
    """Create directory."""
    dirpath = os.path.join(context.test_dir, dirname)
    try:
        os.mkdir(dirpath)
    except FileExistsError:
        pass
    os.chmod(dirpath, 0o444)


@given('File "{filename}" exist with permissions {mode:o}')
@given('File "{filename}" exists')
def ensure_file_exist(context, filename, mode=None):
    """Ensure specified file exist."""
    filepath = os.path.join(context.test_dir, filename)
    with open(filepath, "w") as fp:
        fp.write(f"Automatically created file (by {__file__})")
    if mode:
        os.chmod(filepath, mode)


@given('File "{filepath}" does not exist')
def ensure_file_does_not_exist(context, filepath):
    """Ensure specified file does not exist."""
    try:
        os.unlink(os.path.join(context.test_dir, filepath))
    except FileNotFoundError:
        pass


@then('File "{filepath}" is created within {timeout:d} seconds')
def check_file_existance(context, filepath, timeout):
    """Check that file is created within specified time."""
    filepath_full = os.path.join(context.test_dir, filepath)
    _timeout = timeout
    while _timeout > 0:
        if os.path.exists(filepath_full):
            break
        time.sleep(0.1)
        _timeout -= 0.1

    if not os.path.exists(filepath_full):
        assert isinstance(context.last_run, subprocess.Popen)
        if context.last_run.poll() is None:
            context.last_run.kill()
        logging.info("stdout %r:", context.last_run.stdout.read(-1))
        logging.info("stderr %r:", context.last_run.stderr.read(-1))
        assert os.path.exists(filepath_full), f"File {filepath_full!r} does not exist"


@when('File "{filepath}" is removed')
def remove_file(context, filepath):
    """Remove specified file from file system."""
    delay = 0.2
    logging.info(
        "Delay %r seconds before removing file to let reflexec set up watches", delay
    )
    time.sleep(delay)
    os.unlink(os.path.join(context.test_dir, filepath))


@then('File "{filepath}" does not exist')
def step_impl(context, filepath):
    """Check file absence."""
    assert not os.path.exists(filepath)


@when("Wait for {delay:g} second")
@when("Wait for {delay:g} seconds")
def wait_specified_time(context, delay):  # pylint: disable=unused-argument
    """Wait for specified amount of time."""
    time.sleep(delay)
