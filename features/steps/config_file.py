"""Reflexec feature tests.

Scenario step implementations for config file management.
"""

import configparser
import logging
import os
import re

from behave import given, then


@given("Reflexec config file is")
@given("Reflexec config file {filepath} is")
@given("Config file exist")
@given("File {filepath} is")
def create_reflexec_cfg_file(context, filepath="reflexec.ini"):
    """Create file with specified content."""
    with open(os.path.join(context.test_dir, filepath), "w") as fp:
        fp.write(context.text or "# empty file")


@then("Config file {filepath} contains the following data")
@then("Config file {filepath} is created")
def check_config_file_content(context, filepath):
    """Check config file content."""
    # check config values
    with open(os.path.join(context.test_dir, filepath)) as cfg_file:
        reflexec_cfg_src = cfg_file.read()
    reflexec_cfg = configparser.ConfigParser()
    reflexec_cfg.read_string(reflexec_cfg_src)

    expected_config = configparser.ConfigParser()
    expected_config.read_string(context.text)

    assert set(reflexec_cfg.sections()) == set(expected_config.sections())

    for section in expected_config.sections():
        for key, expeced_value in expected_config.items(section=section):
            assert reflexec_cfg.has_section(
                section
            ), f"Config file does not contain section {section!r}"
            assert key in reflexec_cfg.options(
                section
            ), f"Config file section [{section}] does not contain option {key!r}"
            actual_value = reflexec_cfg.get(section=section, option=key)
            assert actual_value == expeced_value, (
                f"Option {key!r} in section {section!r} "
                f"does not have expected value {expeced_value!r} ({actual_value!r})"
            )

    # check comments
    reflexec_cfg_lines = [_.strip() for _ in reflexec_cfg_src.split("\n")]
    for line in context.text.split("\n"):
        if re.match(r"^#\S+ =", line):
            logging.info("Checking line: %s", line)
            assert line in reflexec_cfg_lines, "Line does not exists"
