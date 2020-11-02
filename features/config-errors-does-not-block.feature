# Reflexec features

Feature: Config errors does not block program work

  Notify user if invalid config file is used.
  Don't stop program work.


  Scenario: Display error on invalid config file
    Given Reflexec config file is:
    """
    # INVALID CONFIG FILE
    [error
    @!#$
    """

    When Reflexec is executed with options: --max-execs=1
    Then Command finishes with return code 0
    And Command output contains the following strings:
    """
    Error while reading config file 'reflexec.ini'
    """


  Scenario: Display error on empty config file
    Given Reflexec config file is:
    """
    # empty config file
    """

    When Reflexec is executed with options: --max-execs=1
    Then Command finishes with return code 0
    And Command output contains the following strings:
    """
    Config file 'reflexec.ini' does not have section [reflexec]
    """


  Scenario: Display error on invalid config values
    Given Reflexec config file is:
    """
    [reflexec]
    # Invalid values
    log_level = INVALID
    delay = INVALID
    max_execs = INVALID
    start = INVALID
    type = INVALID

    unknown = INVALID

    [output-emtpy]
    """

    When Reflexec is executed with options: --max-execs=1
    Then Command finishes with return code 0
    And Command output contains the following strings:
    """
    Invalid value 'INVALID' for parameter 'log_level'
    Invalid value 'INVALID' for parameter 'delay'
    Invalid value 'INVALID' for parameter 'max_execs'
    Invalid value 'INVALID' for parameter 'start'
    Invalid value 'INVALID' for parameter 'type'

    Unknown config key 'unknown' in section [reflexec]
    """


  Scenario: Display error on invalid config integer values
    Given Reflexec config file is:
    """
    [reflexec]
    delay = -1
    max_execs = -1
    """

    When Reflexec is executed with options: --max-execs=1
    Then Command finishes with return code 0
    And Command output contains the following strings:
    """
    Invalid value '-1' for parameter 'delay'
    Invalid value '-1' for parameter 'max_execs'
    """
