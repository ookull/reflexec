"""Reflexec feature tests.

Scenario step implementations for CLI output check.
"""

import json
import re

from behave import then


@then("Command output contains the following strings")
def check_command_str_in_output(context):
    """Check string occurs in Reflexec output."""
    stdout, stderr = context.parse_command_output(context)
    for substr in context.text.split("\n"):
        assert substr in stdout or substr in stderr, (
            f"Command output does not contain the following substring: {substr!r}\n"
            f"STDOUT:\n{stdout}\n"
            f"STDERR:\n{stderr}\n"
        )


@then("Output does not contain the following strings")
def check_command_str_not_in_output(context):
    """Check string does not occur in Reflexec output."""
    stdout, stderr = context.parse_command_output(context)
    for substr in context.text.split("\n"):
        assert substr not in stdout and substr not in stderr, (
            f"Command output contains the following substring: {substr!r}\n"
            f"STDOUT:\n{stdout}\n"
            f"STDERR:\n{stderr}\n"
        )


@then("Output matches with the following patterns")
def check_command_output_match(context):
    """Check pattern in Reflexec output."""
    stdout, stderr = context.parse_command_output(context)
    for pattern in context.text.split("\n"):
        assert re.search(pattern, stdout, re.MULTILINE) or re.search(
            pattern, stderr, re.MULTILINE
        ), ("Command output does not match pattern %r" % pattern)


@then("Output contains the following JSON value")
def check_json_in_command_output(context):
    """
    Check JSON value in Reflexec standard output.

    Value must be presented in one line.
    """
    expected_value = json.loads(context.text)
    for line in context.last_run.stdout.split("\n"):
        try:
            line_value = json.loads(line)
        except json.decoder.JSONDecodeError:
            continue

        # handle timing issues. sometimes command execution duration must be
        # modified before comparing values
        try:
            assert "seconds" in expected_value["duration"]
            assert "seconds" in line_value["duration"]
            expected_value["duration"]["seconds"] = line_value["duration"]["seconds"]
            expected_value["duration_str"] = line_value["duration_str"]
        except KeyError:
            pass

        if expected_value == line_value:
            return

    raise AssertionError("Command output does not contain expected value")
