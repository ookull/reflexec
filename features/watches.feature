# Reflexec features

Feature: File watches can be configured

  File watches can be configured by:
  - Shell file pattern lists (exclusions are supported)
  - File list read from command output

  Scenario: Define watches using shell patterns with exclusions
    Given Reflexec config file is:
    """
    [reflexec]
    watch =
      file*
      !file2
    command = touch {changed_file}.tmp
    max_execs = 2
    log_level = DEBUG
    """
    And File "file1" exists
    And File "file2" exists

    When Reflexec is executed in background
    Then File ".tmp" is created within 3 seconds
    When File "file2" is removed
    And File "file1" is removed
    Then File "file1.tmp" is created within 3 seconds
    And File "file2.tmp" does not exist

    # Reflexec will stop after 2 rounds
    And Command finishes with return code 0
    And Command output contains the following strings:
    """
    Solving shell pattern "!file2"
    Adding path to watch: ./file1
    """
    And Output does not contain the following strings:
    """
    Adding path to watch: ./file2
    """


  Scenario: Define watches with custom command
    Given Reflexec config file is:
    """
    [reflexec]
    type = command
    watch = ls -1
    command = touch {changed_file}.tmp
    max_execs = 2
    log_level = DEBUG
    """
    And File "touch-this" exists

    When Reflexec is executed in background
    Then File ".tmp" is created within 3 seconds
    When File "touch-this" is removed
    Then File "touch-this.tmp" is created within 3 seconds
    # Reflexec will stop after 2 rounds
    And Command finishes with return code 0
    And Command output contains the following strings:
    """
    Executing command 'ls -1' to generate watch paths
    """


  Scenario: Define command based watch without command
    Given Reflexec config file is:
    """
    [reflexec]
    type = command
    command = touch touch-this
    start = exec
    max_execs = 2
    log_level = DEBUG
    """
    And File "trigger" exists

    When Reflexec is executed in background
    Then File "touch-this" is created within 3 seconds
    When File "touch-this" is removed
    Then Command finishes with return code 0
    And Command output contains the following strings:
    """
    No command defined to generate list of watch paths
    """
